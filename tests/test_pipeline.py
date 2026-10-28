"""Offline tests: bins, observation summarising, split math, report. No network."""
import numpy as np
import pandas as pd
import pytest

from pipeline import compute_splits, ingest_games, report, weather_bins as wb
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
    conn.execute("INSERT INTO venues VALUES (1,'Open Stadium',40,-83,0,'CMH',5,0,'t','')")
    conn.execute("INSERT INTO venues VALUES (2,'Dome',40,-83,1,NULL,NULL,0,'t','')")
    gid = 0
    for season in (2019, 2020, 2021):
        for i in range(6):
            gid += 1
            windy = i < 3
            conn.execute("INSERT INTO games VALUES (?,?,?,?,?,0,1,'A','B',?,0,30,20)",
                         (gid, season, i, "regular", "2020-01-01T17:00:00Z", 2 if i == 5 else 1))
            conn.execute("INSERT INTO weather_obs VALUES (?,?,?,?,?,?,?,?,?,?,?,1,?,?,?)",
                         (gid, "CMH", "s", "e", 50, 20 if windy else 3, 25 if windy else 3, 0.0, 0, 10, 5,
                          "windy" if windy else "calm", "none", "mild"))
            conn.execute("INSERT INTO team_games VALUES (?,?,?,?,?,?,?,?,?,?,?,NULL)",
                         (gid, "A", "B", "home", 20 if windy else 40, 60, 20, 100 if windy else 200,
                          30, 150, 1 if windy else 0))
    conn.commit()
    return conn


COLS = ["team", "scope", "bin_type", "bin_value", "metric", "value", "baseline", "delta", "delta_lo",
        "delta_hi", "adj_delta", "adj_lo", "adj_hi", "n", "n_adj", "confidence", "sig_raw", "sig_adj"]


def _splits(conn):
    return pd.DataFrame(compute_splits.compute(compute_splits.usable_games(conn), BINS), columns=COLS)


def test_splits_baseline_n_and_dome_exclusion():
    conn = _fake_db()
    t = _splits(conn)
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
    idx = np.random.default_rng(2).integers(0, 200, size=(500, 200))
    d, lo, hi, n = compute_splits.delta_with_interval(v, masks, idx, 0.90)
    assert n[0] == 100 and d[0] == pytest.approx(2.5, abs=0.3) and lo[0] < d[0] < hi[0]
    assert compute_splits.excludes_zero(lo[0], hi[0]) == 1
    assert compute_splits.excludes_zero(-1.0, 1.0) == 0


def test_expected_residuals_need_enough_games():
    x = np.arange(30, dtype=float)
    assert np.isnan(compute_splits.expected_residuals(2 * x, x, 50)).all()
    assert np.allclose(compute_splits.expected_residuals(2 * x + 1, x, 20), 0, atol=1e-9)


def test_adjustment_removes_schedule_effect():
    """Weather has NO effect here: results depend only on opponent quality, and the 'warm' games
    happen to be against weak opponents. Raw delta should look big; adjusted should be ~zero."""
    rng = np.random.default_rng(0)
    n = 160
    warm = np.arange(n) < 60
    opp_def = np.where(warm, rng.normal(-8, 2, n), rng.normal(0, 2, n))   # weak (low) vs average defenses
    pts = 30 + 1.5 * opp_def + rng.normal(0, 3, n)
    df = pd.DataFrame({"team": "A", "season": 2019, "wind_bin": "calm", "precip_bin": "none",
                       "temp_bin": np.where(warm, "warm", "mild"), "points": pts,
                       "opp_sp_def": opp_def, "opp_sp_off": opp_def})
    for c in ("pass_yds", "pass_att", "rush_yds", "rush_att", "turnovers", "ppa_off", "points_allowed"):
        df[c] = np.nan      # other metrics not under test
    rows = pd.DataFrame(compute_splits.compute(df, BINS), columns=COLS)
    r = rows[(rows.scope == "all") & (rows.bin_value == "warm") & (rows.metric == "points")].iloc[0]
    assert r.delta < -5 and r.sig_raw == 1       # looks like warm weather "hurts"... but it's the schedule
    assert abs(r.adj_delta) < 1.5 and r.sig_adj == 0


def test_confounding_and_snow_in_report():
    conn = _fake_db()
    conn.execute("UPDATE weather_obs SET snow_flag=1 WHERE game_id=1")
    conn.execute("UPDATE games SET home_points=30, away_points=20 WHERE game_id=1")
    conn.commit()
    tdf = compute_splits.usable_games(conn)
    tdf = tdf[tdf.team == "A"]
    lines = report.confounding_table(tdf, BINS)
    assert any("wind: windy" in l for l in lines) and any("all usable games" in l for l in lines)
    snow = "\n".join(report.snow_games(conn))
    assert "Open Stadium" in snow and "B 20, A 30" in snow


def test_report_builds():
    conn = _fake_db()
    conn.executemany("INSERT INTO team_splits VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                     compute_splits.compute(compute_splits.usable_games(conn), BINS))
    text = report.build(conn, BINS)
    assert "EXPLORATORY" in text and "## A" in text and "wind: windy" in text
    assert "Snow games" in text and "Venue / station flags" in text


class _FakeClient:
    """Two tracked teams; A-vs-B is game 1, B's other game is game 2 (B only has it if B's own
    schedule is pulled)."""
    def games(self, season, team, st):
        if st != "regular" or season != 2019:
            return []
        g = {1: ("A", "B"), 2: ("B", "C")}
        return [{"id": i, "week": i, "completed": True, "homeTeam": h, "awayTeam": a, "venueId": 1,
                 "startDate": "2019-09-01T17:00:00Z"} for i, (h, a) in g.items() if team in (h, a)]

    def game_team_stats(self, season, team, st):
        if st != "regular" or season != 2019:
            return []
        g = {1: ("A", "B"), 2: ("B", "C")}
        return [{"id": i, "teams": [{"school": h, "homeAway": "home", "points": 1, "stats": []},
                                    {"school": a, "homeAway": "away", "points": 0, "stats": []}]}
                for i, (h, a) in g.items() if team in (h, a)]

    def ppa_games(self, season, team):
        return []


def test_second_team_not_skipped_when_first_team_created_its_rows(monkeypatch):
    # Regression: B already has game 1 (created while pulling A) but its season isn't done.
    monkeypatch.setattr(ingest_games, "tracked_teams", lambda: ["A", "B"])
    monkeypatch.setattr(ingest_games, "load_yaml", lambda n: {"first_season": 2019})
    monkeypatch.setattr(ingest_games, "current_season", lambda: 2026)
    conn = connect(":memory:")
    ingest_games.run(conn, _FakeClient())
    assert conn.execute("SELECT COUNT(*) FROM team_games WHERE team='B'").fetchone()[0] == 2
