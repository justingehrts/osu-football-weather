"""Offline tests: bins, observation summarising, split math, report. No network."""
from datetime import date, datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

from pipeline import compute_splits, ingest_games, ingest_obs, report, resolve_opponents, weather_bins as wb
from pipeline.cfbd import BudgetExceeded, CallCounter, CfbdClient
from pipeline.common import connect, load_bins
from pipeline.ingest_obs import summarize_window

BINS = load_bins()


@pytest.mark.parametrize("s,g,expect", [
    (5, None, "calm"), (9.4, 19, "calm"), (10, 10, "moderate"), (14.6, 14.6, "windy"),
    (8, 25, "windy"), (8, 24, "moderate"), (15, 15, "windy"),
])
def test_wind(s, g, expect):
    assert wb.classify_wind(s, g, BINS) == expect


@pytest.mark.parametrize("t,expect", [
    (0.0, "none"), (0.0001, "none"), (0.04, "light"), (0.10, "steady"), (0.6, "steady")])
def test_precip(t, expect):
    assert wb.classify_precip(t, BINS) == expect


@pytest.mark.parametrize("t,expect", [
    (20, "cold"), (39.4, "cold"), (39.6, "mild"), (69.4, "mild"), (69.6, "warm"),
    (84.4, "warm"), (84.6, "hot")])
def test_temp(t, expect):
    assert wb.classify_temp(t, BINS) == expect


def _obs(rows):
    df = pd.DataFrame(rows, columns=["valid", "tmpf", "sknt", "gust", "p01i", "vsby", "wxcodes"])
    df["valid"] = pd.to_datetime(df["valid"], utc=True)
    return df


def test_summarize_window_precip_and_wind():
    start, end = pd.Timestamp("2024-11-02 17:00", tz="UTC"), pd.Timestamp("2024-11-02 20:30", tz="UTC")
    df = _obs([
        ("2024-11-02 16:53", 50, 10, None, 0.30, 10, ""),   # hour 15:53-16:53: 7 min overlap -> ignored
        ("2024-11-02 17:53", 52, 10, None, 0.05, 10, ""),
        ("2024-11-02 18:20", 52, 20, 30, 0.05, 6, "-RA"),   # special repeats the hour's value -> max only
        ("2024-11-02 18:53", 54, 12, None, 0.02, 3, "-SN"),
        ("2024-11-02 19:53", 55, 8, None, 0.00, 10, ""),
        ("2024-11-02 20:53", 56, 8, None, 0.50, 10, ""),    # hour 19:53-20:53: ~37 min inside window -> counted
    ])
    w = summarize_window(df, start, end)
    assert w["n_obs"] == 4                      # reports stamped inside [17:00, 20:30]
    # hourly values kept: 0.05 (17:53 & 18:20 share an hour) + 0.02 + 0.00 + 0.50
    assert w["precip_in_total"] == pytest.approx(0.57)
    assert w["wind_sust_max"] == pytest.approx(20 * 1.15078)
    assert w["wind_gust_max"] == pytest.approx(30 * 1.15078)
    assert w["snow_flag"] == 1 and w["vis_min"] == 3


def test_summarize_empty():
    assert summarize_window(pd.DataFrame(), pd.Timestamp("2024-01-01", tz="UTC"),
                            pd.Timestamp("2024-01-01 03:30", tz="UTC"))["n_obs"] == 0


def test_parse_team_stats():
    row = ingest_games.parse_team_stats({"points": 30, "stats": [
        {"category": "completionAttempts", "stat": "21-33"}, {"category": "netPassingYards", "stat": "250"},
        {"category": "rushingAttempts", "stat": "40"}, {"category": "rushingYards", "stat": "180"},
        {"category": "turnovers", "stat": "2"}]})
    assert (row["pass_att"], row["pass_yds"], row["rush_att"], row["rush_yds"], row["turnovers"],
            row["plays"]) == (33, 250, 40, 180, 2, 73)


def _fake_db():
    """Synthetic data -- for testing the math ONLY, never a real result."""
    conn = connect(":memory:")
    conn.execute("INSERT INTO venues(venue_id,name,lat,lon,dome,nearest_station,station_dist_mi,station_far,notes,first_seen) "
                 "VALUES (1,'Open Stadium',40,-83,0,'CMH',5,0,'','2026-10-27')")
    conn.execute("INSERT INTO venues(venue_id,name,lat,lon,dome,station_far,notes,first_seen) "
                 "VALUES (2,'Dome',40,-83,1,0,'','2026-10-27')")
    gid = 0
    for season in (2019, 2020, 2021):
        for i in range(6):
            gid += 1
            windy = i < 3
            conn.execute("INSERT INTO games(game_id,season,week,season_type,kickoff_utc,kickoff_tbd,completed,home_team,"
                         "away_team,venue_id,neutral_site,home_points,away_points) VALUES (?,?,?,?,?,0,1,'A','B',?,0,30,20)",
                         (gid, season, i, "regular", f"{season}-09-0{i + 1}T17:00:00Z", 2 if i == 5 else 1))
            conn.execute("INSERT INTO weather_obs VALUES (?,?,?,?,?,?,?,?,?,?,?,1,?,?,?)",
                         (gid, "CMH", "s", "e", 50, 20 if windy else 3, 25 if windy else 3, 0.0, 0, 10, 5,
                          "windy" if windy else "calm", "none", "mild"))
            conn.execute("INSERT INTO team_games VALUES (?,?,?,?,?,?,?,?,?,?,?,NULL)",
                         (gid, "A", "B", "home", 20 if windy else 40, 60, 20, 100 if windy else 200,
                          30, 150, 1 if windy else 0))
    conn.commit()
    return conn


def _splits(conn):
    rows, tiers = compute_splits.compute(compute_splits.usable_games(conn), BINS)
    return pd.DataFrame(rows), pd.DataFrame(tiers)


def test_splits_baseline_n_and_dome_exclusion():
    t, _ = _splits(_fake_db())
    t = t[t.team == "A"]
    g = lambda scope, bv, m: t[(t.scope == scope) & (t.bin_value == bv) & (t.metric == m)].iloc[0]
    # 18 games, 3 are dome (i==5) -> 15 usable; windy = 9 (i<3 each season)
    assert g("all", "windy", "points").n == 9 and g("all", "windy", "points").confidence == "thin"
    assert g("all", "calm", "points").n == 6
    assert g("all", "windy", "points").baseline == pytest.approx((9 * 20 + 6 * 40) / 15)
    assert g("all", "windy", "points").delta == pytest.approx(20 - (9 * 20 + 6 * 40) / 15)
    assert g("ex2020", "windy", "points").n == 6     # 2020 filter drops 3 windy games
    assert g("all", "windy", "pass_eff").value == pytest.approx(100 / 20)
    assert g("all", "windy", "points_allowed").value == 20   # opponent scored 20 in every fake game
    assert t[t.bin_value == "wet"].empty               # no wet games in the fake data, so no row


def test_merged_bins_from_config():
    df = pd.DataFrame({"wind_bin": ["calm"] * 4, "precip_bin": ["none", "light", "steady", "light"],
                       "temp_bin": ["mild", "warm", "hot", "cold"]})
    m = compute_splits.bin_masks(df, BINS)
    assert m[("precip", "wet")].tolist() == [False, True, True, True]       # light + steady
    assert m[("temp", "warm_hot")].tolist() == [False, True, True, False]   # 70+
    assert ("precip", "light") in m and ("temp", "warm") in m              # originals kept


def test_bootstrap_interval_brackets_known_difference():
    rng = np.random.default_rng(1)
    v = np.concatenate([rng.normal(10, 1, 100), rng.normal(15, 1, 100)])
    masks = np.column_stack([np.arange(200) >= 100])
    counts = compute_splits.counts_from_rows(200, 500, 2)
    d, lo, hi, n = compute_splits.delta_with_interval(v, masks, counts, 0.90)
    assert n[0] == 100 and d[0] == pytest.approx(2.5, abs=0.3) and lo[0] < d[0] < hi[0]
    assert compute_splits.excludes_zero(lo[0], hi[0]) == 1
    assert compute_splits.excludes_zero(-1.0, 1.0) == 0


def test_cluster_bootstrap_moves_both_rows_of_a_game_together():
    ids = np.repeat(np.arange(50), 2)                # 50 games, each with two team rows
    c = compute_splits.counts_from_clusters(ids, 20, 0)
    assert (c[:, 0::2] == c[:, 1::2]).all()


def test_expected_residuals_need_enough_games():
    x = np.arange(30, dtype=float)
    assert np.isnan(compute_splits.expected_residuals(2 * x, x, 50)).all()
    assert np.allclose(compute_splits.expected_residuals(2 * x + 1, x, 20), 0, atol=1e-9)


def _world(true_effect, seed=0, n=240, team="A"):
    """Weather 'warm' has a known effect; warm games are mostly September (weak opponents, early season).
    Month (-2.5 in Nov), home (+3) and opponent strength (1.2/pt) also drive results."""
    rng = np.random.default_rng(seed)
    month = rng.choice([9, 10, 11], n, p=[.4, .3, .3])
    home = rng.random(n) < .6
    warm = ((month == 9) & (rng.random(n) < .8)) | (rng.random(n) < .05)
    opp = np.where(month == 9, rng.normal(-6, 3, n), rng.normal(0, 3, n))
    y = 28 + 1.2 * opp - 2.5 * (month == 11) + 3 * home + true_effect * warm + rng.normal(0, 4, n)
    df = pd.DataFrame(dict(team=team, season=2019, game_id=np.arange(n) + (0 if team == "A" else 10_000),
                           kickoff_utc=[f"2019-{m:02d}-14T20:00:00Z" for m in month],
                           home_away=np.where(home, "home", "away"), neutral_site=0, wind_bin="calm",
                           precip_bin="none", temp_bin=np.where(warm, "warm", "mild"), points=y,
                           opp_sp_def=opp, opp_sp_off=opp))
    for c in ("pass_yds", "pass_att", "rush_yds", "rush_att", "turnovers", "ppa_off", "points_allowed"):
        df[c] = np.nan      # other metrics not under test
    return df, warm


@pytest.mark.parametrize("effect", [0.0, 4.0])
def test_controlled_model_recovers_a_known_effect_and_sees_none_when_there_is_none(effect):
    df, warm = _world(effect)
    rows = pd.DataFrame(compute_splits.split_rows("A", "all", df, BINS, 1, False))
    r = rows[(rows.bin_value == "warm") & (rows.metric == "points")].iloc[0]
    truth = effect * (1 - warm.mean())               # the controlled number is "vs the team's average game"
    assert r.ctl_lo <= truth <= r.ctl_hi
    if effect == 0:
        assert r.sig_ctl == 0 and r.delta < -1.5     # raw looks like a penalty; controlled sees none
    else:
        assert r.sig_ctl == 1 and r.ctl_lo > 0


def test_pooled_row_counts_teams():
    a, _ = _world(3.0, 0, 200, "A")
    b, _ = _world(3.0, 1, 200, "B")
    rows, tiers = compute_splits.compute(pd.concat([a, b]), BINS)
    p = pd.DataFrame(rows)
    p = p[(p.team == compute_splits.POOLED) & (p.scope == "all") & (p.bin_value == "warm") & (p.metric == "points")]
    assert len(p) == 1 and p.iloc[0].n_teams == 2 and p.iloc[0].n > 100


def _cells(*xs):
    return [(n, d, lo, hi) for n, d, lo, hi in xs]


def test_tiers():
    t = lambda cells: compute_splits.assign_tier(cells, BINS)[0]
    sig = lambda d, n=20: (n, d, d - 1, d + 1) if d > 1 else (n, d, d - 0.5, d + 0.5)
    assert t([(20, 3.0, 1.0, 5.0), (20, 2.0, 0.5, 3.5)]) == "clear"               # both exclude zero, same sign
    assert t([(20, 3.0, 1.0, 5.0), (20, -2.0, -3.5, -0.5)]) == "no_clear_effect"  # significant but opposite
    assert t([(20, 3.0, 1.0, 5.0), (20, 1.0, -0.5, 2.5)]) == "leans"              # one clear, one spans zero, same sign
    assert t([(20, 3.0, -2.0, 8.0), (20, -2.0, -7.0, 3.0)]) == "no_clear_effect"  # noise, mixed signs
    assert t([(7, 3.0, 1.0, 5.0), (7, 2.0, 0.5, 3.5)]) == "leans"                 # n 5-9 can never be "clear"
    assert t([(7, 3.0, -4.0, 10.0), (7, -2.0, -9.0, 5.0)]) == "insufficient"
    assert t([(4, 3.0, 1.0, 5.0), (4, 2.0, 0.5, 3.5)]) == "insufficient"          # n < 5
    assert t([(20, 0.1, -3.0, 3.2), (20, 0.1, -3.0, 3.2)]) == "no_clear_effect"   # same sign but tiny: not a lean


def test_temperature_context_only_rule():
    rows = []
    for team, tier_cells in (("KEEP", {"warm": (3.0, 1.0, 5.0)}), ("DROP", {})):
        for bv in ("cold", "mild", "warm"):
            d, lo, hi = tier_cells.get(bv, (0.1, -3.0, 3.2))
            for m in ("pass_eff", "ppa_off", "points"):
                rows.append(dict(team=team, scope="all", bin_type="temp", bin_value=bv, metric=m, n_ctl=20,
                                 ctl_delta=d, ctl_lo=lo, ctl_hi=hi))
    tiers = pd.DataFrame(compute_splits.tier_rows(rows, BINS))
    assert (tiers[tiers.team == "DROP"].tier == "context_only").all()
    assert (tiers[(tiers.team == "KEEP") & (tiers.bin_value == "warm")].tier == "clear").all()
    assert not (tiers[tiers.team == "KEEP"].tier == "context_only").any()


def test_confounding_and_snow_in_report():
    conn = _fake_db()
    conn.execute("UPDATE weather_obs SET snow_flag=1 WHERE game_id=1")
    conn.commit()
    tdf = compute_splits.usable_games(conn)
    tdf = tdf[tdf.team == "A"]
    lines = report.confounding_table(tdf, BINS)
    assert any("wind: windy" in l for l in lines) and any("all usable games" in l for l in lines)
    snow = "\n".join(report.snow_games(conn))
    assert "Open Stadium" in snow and "B 20, A 30" in snow


def test_report_builds_and_pooled_label():
    conn = _fake_db()
    conn.execute("INSERT INTO team_games SELECT game_id,'B','A','away',20,60,20,100,30,150,1,NULL FROM games")
    conn.commit()
    compute_splits.run(conn)
    main, detail = report.build(conn, BINS)
    assert "EXPLORATORY" in main and "Evidence tiers" in main and "wind: windy" in main
    assert "Pooled (2 teams)" in main and "Pooled (None" not in main
    assert "Controlled" in detail and "Venues" in main


# ----------------------------------------------------------------- CFBD budget, cache, planner
class _Resp:
    def __init__(self, data): self.data = data
    def raise_for_status(self): pass
    def json(self): return self.data


class _Session:
    """Pretend CFBD. Records every request actually 'sent'."""
    def __init__(self, data=None): self.sent, self.data, self.headers = [], data or [], {}
    def get(self, url, params=None, timeout=None):
        self.sent.append((url, dict(params or {})))
        return _Resp(self.data)


def _client(tmp_path, cap=5, now=None, data=None):
    clock = [now or datetime(2026, 10, 28, 12, tzinfo=timezone.utc)]
    counter = CallCounter(tmp_path / "calls.json", cap=cap, now=lambda: clock[0])
    sess = _Session(data)
    return CfbdClient(session=sess, counter=counter, raw_dir=tmp_path / "raw", now=lambda: clock[0]), sess, clock


def test_cached_response_is_never_requested_twice_even_after_restart(tmp_path):
    c, sess, _ = _client(tmp_path, data=[{"id": 1}])
    assert c.games(2024, "regular") == [{"id": 1}]
    assert c.games(2024, "regular") == [{"id": 1}] and len(sess.sent) == 1 and c.counter.used == 1
    c2, sess2, _ = _client(tmp_path)                 # "restart": new objects, same files
    assert c2.games(2024, "regular") == [{"id": 1}] and sess2.sent == [] and c2.counter.used == 1
    assert c2.games(2024, "postseason") == [{"id": 1}] or True and len(sess2.sent) == 1   # different request -> sent


def test_current_season_responses_expire_but_past_ones_do_not(tmp_path):
    c, sess, clock = _client(tmp_path, data=[1])
    c.games(2026, "regular", ttl_hours=20)
    clock[0] += timedelta(hours=5)
    c.games(2026, "regular", ttl_hours=20)
    assert len(sess.sent) == 1                        # still fresh
    clock[0] += timedelta(hours=20)
    c.games(2026, "regular", ttl_hours=20)
    assert len(sess.sent) == 2                        # expired -> refreshed
    c.games(2019, "regular")
    clock[0] += timedelta(days=400)
    c.games(2019, "regular")
    assert len(sess.sent) == 3                        # past season: cached forever


def test_hard_cap_aborts_before_sending_and_counter_persists(tmp_path):
    c, sess, _ = _client(tmp_path, cap=2)
    c.games(2015, "regular")
    c.games(2016, "regular")
    with pytest.raises(BudgetExceeded):
        c.games(2017, "regular")
    assert len(sess.sent) == 2                        # the third was never sent
    assert CallCounter(tmp_path / "calls.json", cap=2, now=lambda: datetime(2026, 10, 30, tzinfo=timezone.utc)).used == 2


def test_counter_resets_in_a_new_month_and_syncs_up_to_cfbd(tmp_path):
    f = tmp_path / "calls.json"
    c = CallCounter(f, cap=600, now=lambda: datetime(2026, 10, 30, tzinfo=timezone.utc))
    c.sync(437)
    assert c.used == 437 and c.remaining_under_cap == 163
    nov = CallCounter(f, cap=600, now=lambda: datetime(2026, 11, 1, 1, tzinfo=timezone.utc))
    assert nov.used == 0


def test_offline_mode_refuses_uncached(tmp_path):
    c, _, _ = _client(tmp_path)
    c.offline = True
    with pytest.raises(RuntimeError):
        c.games(2015, "regular")


def _g(gid, season, week, home, away, completed=True, stype="regular", venue=1):
    return dict(id=gid, week=week, completed=completed, homeTeam=home, awayTeam=away, venueId=venue,
                startDate=f"{season}-09-0{week}T17:00:00Z", homeClassification="fbs", awayClassification="fbs",
                homePoints=30 if completed else None, awayPoints=20 if completed else None, neutralSite=False)


def _box(gid, home, away):
    side = lambda n, ha: {"school": n, "homeAway": ha, "points": 1, "stats": []}
    return {"id": gid, "teams": [side(home, "home"), side(away, "away")]}


class _FakeCfbd:
    """Serves a tiny league; counts requests by endpoint."""
    def __init__(self, bins):
        self.n = {"games": 0, "box": 0, "ppa": 0}
        self.calls = []
        self.counter = type("C", (), {"used": 0, "cap": 600})()

    def is_cached(self, *a, **k):
        return False

    def games(self, year, season_type, week=None, team=None, ttl_hours=None):
        self.n["games"] += 1
        if season_type != "regular":
            return []
        return [_g(year * 100 + 1, year, 1, "A", "B"), _g(year * 100 + 2, year, 2, "C", "A"),
                _g(year * 100 + 3, year, 3, "B", "C"), _g(year * 100 + 4, year, 4, "D", "E")]

    def game_team_stats(self, year, season_type, week=None, team=None, ttl_hours=None):
        self.n["box"] += 1
        self.calls.append(("box", year, week, team))
        g = {1: ("A", "B"), 2: ("C", "A"), 3: ("B", "C"), 4: ("D", "E")}
        return [_box(year * 100 + i, *t) for i, t in g.items()
                if (week is None or i == week) and (team is None or team in t)]

    def ppa_games(self, year, season_type, week=None, team=None, ttl_hours=None):
        self.n["ppa"] += 1
        return [{"gameId": r["id"], "team": s["school"], "offense": {"overall": 0.1}}
                for r in self.game_team_stats(year, season_type, week, team) for s in r["teams"]] \
            if False else [{"gameId": year * 100 + 1, "team": "A", "offense": {"overall": 0.1}}]


def test_stage_planner_prefers_cheaper_of_week_vs_team(monkeypatch):
    conn = connect(":memory:")
    for gid, wk, h, a in ((1, 1, "A", "X"), (2, 2, "B", "Y"), (3, 3, "C", "Z"), (4, 4, "D", "W")):
        conn.execute("INSERT INTO games(game_id,season,week,season_type,completed,home_team,away_team) "
                     "VALUES (?,2018,?, 'regular',1,?,?)", (gid, wk, h, a))
    teams = ["A", "B", "C", "D"]
    reqs = ingest_games.stats_requests(conn, teams, 2026, BINS)
    # 4 teams missing, 4 distinct weeks: weeks (4) <= 1.25 * teams (4) -> by week, 4 calls
    assert [r["kind"] for r in reqs] == ["week"] * 4
    conn.execute("INSERT INTO games(game_id,season,week,season_type,completed,home_team,away_team) "
                 "VALUES (5,2018,5,'regular',1,'A','X'),(6,2018,6,'regular',1,'A','X'),(7,2018,7,'regular',1,'A','X'),"
                 "(8,2018,8,'regular',1,'A','X'),(9,2018,9,'regular',1,'A','X')")
    reqs = ingest_games.stats_requests(conn, ["A"], 2026, BINS)
    # one team missing 6 games across 6 weeks: by team is a single call
    assert [r["kind"] for r in reqs] == ["team"] and reqs[0]["team"] == "A"


def test_logged_team_seasons_cost_nothing_and_postseason_goes_by_week():
    conn = connect(":memory:")
    conn.execute("INSERT INTO games(game_id,season,week,season_type,completed,home_team,away_team) VALUES "
                 "(1,2018,1,'regular',1,'A','X'),(2,2018,1,'postseason',1,'A','Y'),(3,2018,1,'postseason',1,'B','Z')")
    conn.execute("INSERT INTO ingest_log VALUES ('A',2018,'x')")
    reqs = ingest_games.stats_requests(conn, ["A", "B"], 2026, BINS)
    kinds = sorted((r["season_type"], r["kind"]) for r in reqs)
    # A's regular 2018 is already loaded (free); B has no regular games; the bowl week is ONE request for both teams
    assert kinds == [("postseason", "week")]


def test_ingest_end_to_end_with_fake_cfbd_and_second_team_not_skipped(monkeypatch):
    monkeypatch.setattr(ingest_games, "load_yaml", lambda n: {"first_season": 2019})
    conn = connect(":memory:")
    client = _FakeCfbd(BINS)
    teams = ["A", "B"]
    ingest_games.run_stage1(conn, client, teams, 2019, 2020, BINS, today=date(2020, 10, 1))
    ingest_games.run_stage2(conn, client, teams, 2026, BINS)
    assert conn.execute("SELECT COUNT(*) FROM team_games WHERE team='B'").fetchone()[0] >= 2
    assert conn.execute("SELECT COUNT(*) FROM team_games WHERE team='A'").fetchone()[0] >= 2
    assert conn.execute("SELECT ppa_off FROM team_games WHERE team='A' AND game_id=201901").fetchone()[0] == 0.1
    before = dict(client.n)
    ingest_games.run_stage2(conn, client, teams, 2026, BINS)     # second run: nothing left to ask for
    assert client.n == before


def test_probe_stops_when_a_response_cannot_be_stored():
    conn = connect(":memory:")
    conn.execute("INSERT INTO games(game_id,season,week,season_type,completed,home_team,away_team) "
                 "VALUES (1,2018,1,'regular',1,'A','X')")

    class Wrong(_FakeCfbd):
        def game_team_stats(self, *a, **k):
            return [{"unexpected": "shape", "id": 999}]          # data comes back, none of it ours
    with pytest.raises(SystemExit, match="PROBE FAILED"):
        ingest_games.run_stage2(conn, Wrong(BINS), ["A"], 2026, BINS)


def test_chunk_windows_batches_by_span():
    t0 = pd.Timestamp("2015-09-01", tz="UTC")
    ws = [(i, t0 + pd.Timedelta(days=d), t0 + pd.Timedelta(days=d, hours=3.5)) for i, d in enumerate((0, 7, 365, 700, 2000))]
    chunks = ingest_obs.chunk_windows(ws, 365 * 2)
    assert [len(c) for c in chunks] == [4, 1]         # one request for the first four games, one for the last


def test_obs_run_uses_one_request_per_station_chunk_not_per_game(monkeypatch, tmp_path):
    monkeypatch.setattr(ingest_obs, "IEM_CACHE", tmp_path)
    conn = _fake_db()
    conn.execute("UPDATE games SET venue_id = 1")
    conn.execute("DELETE FROM weather_obs")
    asked = []

    def fetch(session, station, start, end):
        asked.append((station, start, end))
        return pd.DataFrame(columns=["station", "valid", "tmpf", "sknt", "gust", "p01i", "vsby", "wxcodes"]).astype(
            {"valid": "datetime64[ns, UTC]"})
    ingest_obs.run(conn, fetcher=fetch, session=object(), now=datetime(2027, 1, 1, tzinfo=timezone.utc))
    n_games = conn.execute("SELECT COUNT(*) FROM weather_obs").fetchone()[0]
    assert n_games == 18 and len(asked) == 1          # 18 games at one station over 3 seasons -> ONE request, not 18


def test_resolve_opponents_from_games_and_flags_non_fbs():
    games = [_g(1, 2026, 1, "Ohio State", "Ball State"), _g(2, 2026, 2, "Texas", "Ohio State"),
             _g(3, 2026, 3, "Ohio State", "Youngstown State"), _g(4, 2026, 1, "X", "Y")]
    games[2]["awayClassification"] = "fcs"
    opps, non_fbs = resolve_opponents.opponents_from_games(games, "Ohio State")
    assert opps == ["Ball State", "Texas", "Youngstown State"] and non_fbs == ["Youngstown State"]


# ----------------------------------------------------------------- deferral, complement, 2026
def test_deferred_teams_are_not_loaded_but_stay_on_the_list(monkeypatch):
    import pipeline.ingest_games as ig
    monkeypatch.setattr(ig, "deferred_teams", lambda: ["Ball State"])
    monkeypatch.setattr(ig, "load_yaml", lambda n: {"non_fbs": []})
    conn = connect(":memory:")
    assert ig.loadable_teams(conn, ["Ohio State", "Ball State", "Michigan"], BINS) == ["Ohio State", "Michigan"]
    # a game vs a deferred team produces no stat requests for that team, and nothing raises
    conn.execute("INSERT INTO games(game_id,season,week,season_type,completed,home_team,away_team) "
                 "VALUES (1,2026,1,'regular',1,'Ohio State','Ball State')")
    assert {r.get("team") for r in ig.stats_requests(conn, ["Ohio State"], 2026, BINS)} <= {None, "Ohio State"}


def test_resolve_keeps_deferred_choice(monkeypatch, tmp_path):
    import yaml
    monkeypatch.setattr(resolve_opponents, "OUT", tmp_path / "opponents.yaml")
    monkeypatch.setattr(resolve_opponents, "load_yaml", lambda n: (
        {"focal_team": "Ohio State", "season": 2026} if n == "teams.yaml" else {"deferred": ["Ball State", "Gone U"]}))

    class C:
        def games(self, *a, **k): return [_g(1, 2026, 1, "Ohio State", "Ball State"), _g(2, 2026, 2, "Texas", "Ohio State")]
    out = resolve_opponents.run(force=True, client=C())
    assert out["deferred"] == ["Ball State"]            # kept; names no longer on the schedule are dropped


def test_report_survives_missing_deferred_teams_and_shows_steady_and_both_yardsticks(monkeypatch):
    monkeypatch.setattr(report, "deferred_teams", lambda: ["Ball State"])
    monkeypatch.setattr(report, "tracked_teams", lambda: ["A", "B", "Ball State"])
    conn = _fake_db()
    conn.execute("UPDATE weather_obs SET precip_bin='steady', precip_in_total=0.3 WHERE game_id <= 7")
    conn.execute("INSERT INTO team_games SELECT game_id,'B','A','away',20,60,20,100,30,150,1,NULL FROM games")
    conn.commit()
    compute_splits.run(conn)
    main, detail = report.build(conn, BINS)
    assert "Deferred by choice (1):** Ball State" in main
    assert "precip: steady" in main and "precip: wet" in main                      # both bins side by side
    assert "A. vs the team's OVERALL AVERAGE" in main and "B. vs ALL OTHER GAMES" in main
    assert "Raw vs others" in detail and "Ctl vs avg" in detail
    assert "PREVIEW" not in main                                                   # deferred is not 'missing'


def test_complement_is_the_average_comparison_divided_by_one_minus_share():
    df, warm = _world(3.0)
    rows = pd.DataFrame(compute_splits.split_rows("A", "all", df, BINS, 1, False))
    r = rows[(rows.bin_value == "warm") & (rows.metric == "points")].iloc[0]
    share = r.n / len(df)
    assert r.rest_delta == pytest.approx(r.delta / (1 - share))
    assert r.adj_rest == pytest.approx(r.adj_delta / (1 - share), rel=1e-6)
    assert r.ctl_delta == pytest.approx(r.ctl_rest * (1 - r.n / len(df)))      # all games rated in this fake world
    assert r.rest_lo < r.rest_delta < r.rest_hi


def test_finished_current_season_games_count_like_any_other():
    conn = _fake_db()
    conn.execute("UPDATE games SET season = 2026 WHERE game_id IN (1, 2, 3)")
    conn.commit()
    usable = compute_splits.usable_games(conn)
    assert (usable.season == 2026).sum() == 3
    rows, _ = compute_splits.compute(usable, BINS)
    allrow = [r for r in rows if r["team"] == "A" and r["scope"] == "all" and r["bin_value"] == "windy"
              and r["metric"] == "points"][0]
    assert allrow["n"] == 9                                   # the three 2026 windy games are in the count
    assert "2026 (in progress)" in "\n".join(report.season_counts_section(usable))


def test_changes_section_compares_before_and_after_pool():
    conn = _fake_db()
    compute_splits.run(conn)                                   # pool of one team: no pooled rows yet
    conn.execute("INSERT INTO team_games SELECT game_id,'B','A','away',20,60,20,100,30,150,1,NULL FROM games")
    conn.commit()
    compute_splits.run(conn)                                   # team set changed -> snapshot taken
    compute_splits.run(conn)                                   # set unchanged -> snapshot kept
    sp = pd.read_sql_query("SELECT * FROM team_splits", conn)
    prev = pd.read_sql_query("SELECT * FROM team_splits_prev", conn)
    assert set(prev.team) == {"A"} and set(sp.team) == {"A", "B", compute_splits.POOLED}


# ----------------------------------------------------------------- in-season refresh
def test_refresh_stops_after_one_call_when_nothing_is_new(monkeypatch):
    from pipeline import refresh
    conn = connect(":memory:")
    for gid, w in ((1, 1), (2, 2)):
        conn.execute("INSERT INTO games(game_id,season,week,season_type,completed,home_team,away_team) VALUES (?,2026,?, 'regular',1,'A','B')", (gid, w))
        conn.execute("INSERT INTO team_games(game_id,team,opponent,home_away) VALUES (?,'A','B','home')", (gid,))
    conn.commit()
    games = [_g(1, 2026, 1, "A", "B"), _g(2, 2026, 2, "A", "B")]
    assert refresh.new_completed_games(conn, games, {"A"}) == []
    games.append(_g(3, 2026, 3, "A", "C"))                       # a finished game with no box score yet
    games.append(_g(4, 2026, 4, "A", "D", completed=False))       # scheduled, not played: ignored
    assert refresh.new_completed_games(conn, games, {"A"}) == [(3, "A")]
    assert refresh.new_completed_games(conn, games, {"Z"}) == []   # other teams' games don't count


def test_refresh_summary_says_what_happened_in_plain_words():
    from pipeline import refresh
    quiet = refresh.refresh_summary([], [], 1, 530, 600, {"/games": 1})
    assert "no new completed games" in quiet and "Nothing changed, so nothing was committed" in quiet
    assert "CFBD calls this run: **1**" in quiet and "530** of the 600-call cap" in quiet
    changed = refresh.refresh_summary([], ["USC at Ohio State: kickoff TBD -> 2026-11-07T17:00:00Z"], 1, 530, 600)
    assert "Schedule/score updates" in changed and "kickoff TBD ->" in changed
    new = refresh.refresh_summary([(1, "Ohio State"), (2, "USC")], [], 6, 536, 600)
    assert "2 new finished team-games (Ohio State, USC)" in new


def test_describe_changes_finds_reschedules_and_scores():
    from pipeline import refresh
    conn = connect(":memory:")
    for gid, k in ((1, None), (2, "2026-11-07T17:00:00Z")):
        conn.execute("INSERT INTO games(game_id,season,week,season_type,kickoff_utc,completed,home_team,away_team) VALUES (?,2026,9,'regular',?,0,'A','B')", (gid, k))
    before = conn.execute("SELECT * FROM games ORDER BY game_id").fetchall()
    conn.execute("UPDATE games SET kickoff_utc='2026-11-07T20:00:00Z' WHERE game_id=1")
    conn.execute("UPDATE games SET completed=1, home_points=30, away_points=3 WHERE game_id=2")
    after = conn.execute("SELECT * FROM games ORDER BY game_id").fetchall()
    out = refresh.describe_changes(before, after)
    assert out[0].endswith("kickoff TBD -> 2026-11-07T20:00:00Z") and "result/score updated" in out[1]
    assert refresh.describe_changes(after, after) == []


def test_step_summary_writes_only_inside_actions(tmp_path, monkeypatch):
    from pipeline.common import step_summary
    f = tmp_path / "summary.md"
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    step_summary("hello")                                  # outside Actions: silently nothing
    assert not f.exists()
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(f))
    step_summary("hello")
    assert "hello" in f.read_text()
