"""The app's decisions (labels, takeaway, exports) and a smoke test of every page. Offline."""
import io
import sqlite3
from datetime import datetime, timezone

import pandas as pd
import pytest
from PIL import Image
from streamlit.testing.v1 import AppTest

from lib import config, data, export, logic

BINS = config.load_bins()
TEAMS = {"focal": "Ohio State", "season": 2026, "tracked": ["Ohio State", "USC", "Ball State", "Nebraska"],
         "deferred": ["Ball State"], "loaded": ["Ohio State", "USC", "Nebraska"]}


# --------------------------------------------------------------------------- synthetic summary tables
def make_stats(cells, tiers):
    """cells: {(team, bt, bv, metric): (ctl_rest, lo, hi, n)}; tiers: {(team, bt, bv, grp): (tier, n)}."""
    rows = []
    for (team, bt, bv, m), (v, lo, hi, n) in cells.items():
        rows.append(dict(team=team, scope="all", bin_type=bt, bin_value=bv, metric=m, n=n, ctl_rest=v, ctl_rest_lo=lo,
                         ctl_rest_hi=hi, rest_delta=v, sig_ctl_rest=int(lo > 0 or hi < 0), confidence="solid", n_teams=6))
    trows = [dict(team=t, scope="all", bin_type=bt, bin_value=bv, grp=g, tier=tier, n=n) for (t, bt, bv, g), (tier, n) in tiers.items()]
    return logic.Stats(pd.DataFrame(rows), pd.DataFrame(trows), BINS, TEAMS)


def windy_stats(osu_tier="clear", osu_n=31, usc_tier="leans", usc_n=20):
    cells, tiers = {}, {}
    for team, tier, n in (("Ohio State", osu_tier, osu_n), ("USC", usc_tier, usc_n)):
        cells[(team, "wind", "windy", "pass_eff")] = (-1.2, -2.0, -0.4, n)
        cells[(team, "wind", "windy", "points")] = (-4.0, -7.0, -1.0, n)
        cells[(team, "wind", "windy", "ppa_off")] = (-0.08, -0.14, -0.02, n)
        cells[(team, "wind", "windy", "points_allowed")] = (1.0, -2.0, 4.0, n)
        for g in ("passing", "scoring"):
            tiers[(team, "wind", "windy", g)] = (tier, n)
    return make_stats(cells, tiers)


def card_game(**kw):
    g = dict(game_id=1, opponent="USC", home_team="USC", away_team="Ohio State", site="away", completed=0, dome=0,
             venue="Coliseum", kickoff_utc="2026-10-31T23:30:00Z")
    g.update(kw)
    return g


# --------------------------------------------------------------------------- evidence labels
@pytest.mark.parametrize("tier,n,label", [
    ("clear", 31, logic.CLEAR), ("clear", 30, logic.CLEAR), ("clear", 29, logic.LEANS),     # needs the CLEAR tier AND n >= 30
    ("leans", 200, logic.LEANS), ("no_clear_effect", 50, logic.NONE), ("insufficient", 3, logic.FEW),
    ("context_only", 40, logic.CONTEXT)])
def test_label_rules(tier, n, label):
    assert logic.evidence_label(tier, n, BINS) == label


def test_a_single_metric_can_never_be_clear_signal():
    assert logic.single_metric_label(-5.0, -1.0, 500, BINS) == logic.LEANS
    assert logic.single_metric_label(-1.0, 3.0, 50, BINS) == logic.NONE
    assert logic.single_metric_label(-5.0, -1.0, 3, BINS) == logic.FEW


def test_steady_rain_is_capped_at_leans_even_from_a_clear_tier():
    st = make_stats({("Ohio State", "precip", "steady", "pass_eff"): (-1.0, -2.0, -0.1, 12)},
                    {("Ohio State", "precip", "steady", "passing"): ("clear", 12), ("Ohio State", "precip", "steady", "scoring"): ("clear", 12)})
    assert st.result("Ohio State", "precip", "steady", "pass_eff").label == logic.LEANS


def test_ppa_takes_the_weaker_of_its_two_groups():
    st = make_stats({("Ohio State", "wind", "windy", "ppa_off"): (-0.08, -0.14, -0.02, 40)},
                    {("Ohio State", "wind", "windy", "passing"): ("clear", 40), ("Ohio State", "wind", "windy", "scoring"): ("no_clear_effect", 40)})
    assert st.result("Ohio State", "wind", "windy", "ppa_off").label == logic.NONE


def test_numbers_are_the_vs_all_other_games_estimate():
    st = windy_stats()
    r = st.result("Ohio State", "wind", "windy", "pass_eff")
    assert r.value == -1.2 and r.text() == "-1.20 yds/att" and r.n == 31


def test_deferred_team_is_data_not_loaded_not_an_error():
    st = windy_stats()
    r = st.result("Ball State", "wind", "windy", "points")
    assert r.status == "not_loaded" and r.text() == "data not loaded yet" and not st.loaded("Ball State")


# --------------------------------------------------------------------------- takeaway
def test_takeaway_wording_follows_the_label():
    st = windy_stats()
    t = logic.takeaway(st, "Ohio State", "USC", "windy", None, BINS)
    assert "Ohio State shows a clear signal of lower passing efficiency and scoring in windy games (n=31)" in t
    assert "USC leans toward lower" in t and "(n=20)" in t
    assert t.count(".") == 1 or t.endswith(".")            # one sentence


def test_one_teams_findings_merge_into_one_clause_with_each_labels_own_verb():
    st = windy_stats(osu_tier="clear", osu_n=40)
    st.t.loc[("Ohio State", "all", "wind", "windy", "scoring"), "tier"] = "leans"          # passing clear, scoring only leans
    t = logic.takeaway(st, "Ohio State", "USC", "windy", None, BINS)
    assert "Ohio State shows a clear signal of lower passing efficiency and leans toward lower scoring in windy games (n=40)" in t
    assert t.count("Ohio State") == 1


def test_a_toss_up_rain_chance_makes_no_rain_claim_and_says_so():
    st = windy_stats()
    t = logic.takeaway(st, "Ohio State", "USC", "calm", "uncertain", BINS, precip_prob=67)
    assert "rain is a toss-up (67% chance)" in t and "dry games" not in t and "wet games" not in t
    only_rain = logic.takeaway(st, "Ohio State", "USC", None, "uncertain", BINS, precip_prob=50)
    assert only_rain.startswith("Rain is a toss-up (50% chance)")


def test_takeaway_never_says_clear_when_n_is_under_30():
    st = windy_stats(osu_tier="clear", osu_n=25)
    t = logic.takeaway(st, "Ohio State", "USC", "windy", None, BINS)
    assert "clear signal" not in t.lower() and "Ohio State leans toward" in t


def test_takeaway_is_silent_about_temperature_and_calls_no_effect_a_result():
    st = windy_stats(osu_tier="no_clear_effect", usc_tier="no_clear_effect")
    t = logic.takeaway(st, "Ohio State", "USC", "windy", None, BINS)
    assert "no clear effect" in t.lower() and "real result" in t
    for word in ("cold", "warm", "hot", "temperature", "mild"):
        assert word not in logic.takeaway(windy_stats(), "Ohio State", "USC", "windy", None, BINS).lower()


def test_takeaway_with_too_little_history():
    st = windy_stats(osu_tier="insufficient", osu_n=3, usc_tier="insufficient", usc_n=2)
    assert "aren't enough past games" in logic.takeaway(st, "Ohio State", "USC", "windy", None, BINS)


def test_wind_findings_come_before_rain():
    st = windy_stats()
    st.s = pd.concat([st.s.reset_index(), pd.DataFrame([dict(team="Ohio State", scope="all", bin_type="precip", bin_value="light", metric="points", n=40,
                                                              ctl_rest=-3.0, ctl_rest_lo=-5.0, ctl_rest_hi=-1.0, rest_delta=-3.0, sig_ctl_rest=1, confidence="solid", n_teams=6)])]).set_index(
        ["team", "scope", "bin_type", "bin_value", "metric"]).sort_index()
    st.t = pd.concat([st.t.reset_index(), pd.DataFrame([dict(team="Ohio State", scope="all", bin_type="precip", bin_value="light", grp="scoring", tier="clear", n=40)])]).set_index(
        ["team", "scope", "bin_type", "bin_value", "grp"]).sort_index()
    t = logic.takeaway(st, "Ohio State", "USC", "windy", "light", BINS)
    assert t.index("windy games") < t.index("light-rain games")


# --------------------------------------------------------------------------- the card view
def test_view_for_each_forecast_situation():
    st = windy_stats()
    ok = {"status": "ok", "wind_bin": "windy", "precip_bin": "none", "temp_bin": "mild", "precip_prob": 10}
    v = logic.build_gameday_view(st, BINS, TEAMS, card_game(), ok, {})
    assert v["badges"] == ["Windy", "Dry", "Mild"] and v["sections"][0]["dim"] == "wind"        # wind leads
    far = logic.build_gameday_view(st, BINS, TEAMS, card_game(), {"status": "beyond_horizon", "note": "9 days out"}, {})
    assert far["sections"] == [] and "beyond the forecast horizon" in far["takeaway"]
    dome = logic.build_gameday_view(st, BINS, TEAMS, card_game(dome=1), None, {})
    assert dome["forecast_status"] == "indoor" and "Indoor game: weather is not a factor" in dome["takeaway"]
    played = logic.build_gameday_view(st, BINS, TEAMS, card_game(completed=1), None, {})
    assert played["forecast_status"] == "played" and played["sections"] == []
    none = logic.build_gameday_view(st, BINS, TEAMS, card_game(), None, {})
    assert "No forecast has been pulled" in none["takeaway"]


def test_what_if_overrides_the_forecast_and_can_fill_a_missing_one():
    st = windy_stats()
    ok = {"status": "ok", "wind_bin": "calm", "precip_bin": "none", "temp_bin": "mild"}
    v = logic.build_gameday_view(st, BINS, TEAMS, card_game(), ok, {"wind": "windy"})
    assert v["badges"][0] == "Windy" and v["conditions"]["overridden"] and v["forecast_status"] == "what_if"
    far = logic.build_gameday_view(st, BINS, TEAMS, card_game(), {"status": "beyond_horizon"}, {"wind": "windy"})
    assert far["sections"] and "Windy" in far["badges"]


def test_dry_and_wet_side_by_side():
    assert logic.precip_bins_to_show("uncertain", False) == ["none", "wet"]
    assert logic.precip_bins_to_show("none", True) == ["none", "wet"]
    assert logic.precip_bins_to_show("steady", False) == ["steady", "wet"]      # steady stays separate from light; 'any rain' is a reference
    assert logic.precip_bins_to_show("none", False) == ["none"]


def test_pooled_reference_is_labelled_with_the_team_count():
    st = windy_stats()
    st.pooled_n = 6
    v = logic.build_gameday_view(st, BINS, TEAMS, card_game(), {"status": "ok", "wind_bin": "windy", "precip_bin": "none", "temp_bin": "mild"}, {})
    assert "All 6 loaded teams" in logic.blurb(v) and any(r["team"] == "All 6 loaded teams" for r in logic.view_rows(v))


def test_exports_match_the_view():
    st = windy_stats()
    v = logic.build_gameday_view(st, BINS, TEAMS, card_game(), {"status": "ok", "wind_bin": "windy", "precip_bin": "none", "temp_bin": "mild"}, {})
    rows = logic.view_rows(v)
    csv = logic.csv_bytes(rows).decode()
    assert csv.splitlines()[0].startswith("game,team,condition,metric,vs_all_other_games") and "Clear signal" in csv
    assert "Clear signal" in logic.blurb(v) and v["takeaway"] in logic.blurb(v)
    img = Image.open(io.BytesIO(export.render_card_png(v)))
    assert img.size == (1920, 1080)


# --------------------------------------------------------------------------- read-only database
def test_the_app_cannot_write_to_the_database():
    conn = data.connect_ro(config.DB_PATH)
    with pytest.raises(sqlite3.OperationalError):
        conn.execute("DELETE FROM team_splits")
    assert data.connect_ro("/nonexistent/forecasts.sqlite") is None      # a missing forecast file is fine, not a crash


# --------------------------------------------------------------------------- pages, end to end (real database)
def run_page(path):
    from pathlib import Path
    return AppTest.from_file(str(Path(__file__).resolve().parents[1] / path), default_timeout=90).run()


def test_gameday_card_opens_on_the_next_ohio_state_game_with_forecast_badges():
    at = run_page("app/streamlit_app.py")
    assert not at.exception
    assert at.title[0].value == "Gameday Card"
    assert any("Windy" in m.value and "badge" in m.value for m in at.markdown)           # forecast prefilled as badges
    assert any("Reference: all" in m.value for m in at.markdown)                         # pooled line, labelled
    text = " ".join(m.value for m in at.markdown)
    assert "vs. all other games" in text or "other** games" in text
    assert "Temperature (context only): results differ by team" in [e.label for e in at.expander]


def test_gameday_card_what_if_changes_the_takeaway():
    at = run_page("app/streamlit_app.py")
    before = at.info[0].value
    sel = [s for s in at.selectbox if s.label == "Wind"][0]
    sel.set_value("Calm").run()
    assert not at.exception and at.info[0].value != before and "calm" in at.info[0].value.lower()


def AppTest_game_ids():
    conn = data.connect_ro(config.DB_PATH)
    sched = data.schedule(conn, "Ohio State", 2026)
    return [(int(r.game_id), r.opponent) for r in sched.itertuples()]


def test_gameday_card_game_beyond_horizon_says_so():
    at = run_page("app/streamlit_app.py")
    game = at.selectbox[0]
    opts = list(game.options)
    oregon_game = [g for g in AppTest_game_ids() if g[1] == "Oregon"][0][0]       # the Nov 6 game: beyond the horizon in the fixture
    game.set_value(oregon_game).run()
    assert not at.exception
    assert "beyond the forecast horizon" in at.info[0].value


def test_explorer_deferred_team_shows_data_not_loaded_and_does_not_break():
    at = run_page("app/pages/1_Team_Explorer.py")
    assert not at.exception
    team = at.selectbox[0]
    assert any("not loaded" in o for o in team.options)                          # deferred teams are listed, labelled
    team.set_value("Ball State").run()
    assert not at.exception and any("data not loaded yet" in i.value for i in at.info)


def test_explorer_shows_a_loaded_team_with_wind_first():
    at = run_page("app/pages/1_Team_Explorer.py")
    [s for s in at.selectbox if s.label == "Wind"][0].select("Windy").run()
    assert not at.exception and len(at.dataframe) >= 1
    assert any("Wind: windy vs. not windy" in m.value for m in at.markdown)


def test_evidence_and_methodology_pages_render():
    ev = run_page("app/pages/2_Evidence.py")
    assert not ev.exception and any("Snow games" in h.value for h in ev.markdown)
    me = run_page("app/pages/3_Methodology.py")
    assert not me.exception
    body = " ".join(m.value for m in me.markdown)
    for phrase in ("FCS opponents are excluded from the adjusted and controlled numbers", "Clear signal", "vs. all other games",
                   "Temperature is context only", "overall average"):
        assert phrase.lower() in body.lower() or phrase.lower() in " ".join(h.value for h in me.header).lower()


def test_shared_links_prefill_the_view():
    from pathlib import Path
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app/streamlit_app.py"), default_timeout=90)
    at.query_params["wind"] = "windy"
    at.query_params["precip"] = "steady"
    at.run()
    assert not at.exception
    assert [s for s in at.selectbox if s.label == "Wind"][0].value == "Windy"
    assert [s for s in at.selectbox if s.label == "Precipitation"][0].value == "Steady rain"
    assert "windy games" in at.info[0].value
    ex = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app/pages/1_Team_Explorer.py"), default_timeout=90)
    ex.query_params["team"] = "Nebraska"
    ex.run()
    assert not ex.exception and [s for s in ex.selectbox if s.label == "Team"][0].value == "Nebraska"


def test_pages_say_how_fresh_the_data_is():
    at = run_page("app/streamlit_app.py")
    assert any("History through games played" in c.value for c in at.caption)


# --------------------------------------------------------------------------- team colors
def test_every_team_color_pair_is_legible_and_loaded_teams_all_have_colors():
    from lib import colors
    pairs = colors.load_colors()
    assert pairs, "config/team_colors.yaml is empty"
    for team, c in pairs.items():
        assert colors.contrast_ratio(c["fg"], c["bg"]) >= 4.5, f"{team}: {c} is below the 4.5:1 legibility minimum"
    for team in config.load_teams()["loaded"]:
        assert team in pairs, f"{team} has no school colors in config/team_colors.yaml"


def test_unknown_teams_get_a_neutral_chip_and_names_are_escaped():
    from lib import colors
    assert colors.colors_for("Some New Team") == colors.NEUTRAL
    html = colors.chip_html("Ohio State")
    assert "#BB0000" in html and "#E3E3E3" in html                       # scarlet on light gray
    assert "&lt;b&gt;" in colors.chip_html("<b>x</b>") and "<b>" not in colors.chip_html("<b>x</b>")


def test_contrast_helper_matches_known_values():
    from lib import colors
    assert colors.contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21.0, abs=0.01)
    assert colors.contrast_ratio("#BB0000", "#666666") < 1.5            # scarlet on mid-gray: the unreadable combination


def test_png_uses_school_colors_and_never_drops_words_from_a_long_takeaway():
    from lib import colors
    st = windy_stats()
    view = logic.build_gameday_view(st, BINS, TEAMS, card_game(), {"status": "ok", "wind_bin": "windy", "precip_bin": "none", "temp_bin": "mild"}, {})
    img = Image.open(io.BytesIO(export.render_card_png(view))).convert("RGB")
    gold = colors.rgb(colors.colors_for("USC")["bg"])
    assert any(img.getpixel((x, 80)) == gold for x in range(0, 1200, 4))            # the USC name chip is drawn in USC gold
    from PIL import ImageDraw
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    long_text = "word " * 120
    size, lines = export.fit_lines(d, long_text, 1760)
    assert " ".join(lines).split() == long_text.split()                              # nothing was cut off
    assert size <= 36


# --------------------------------------------------------------------------- Show anyway
def test_plain_averages_for_a_thin_block_are_just_arithmetic():
    from pipeline.common import connect
    db = connect(":memory:")
    db.execute("INSERT INTO venues(venue_id,name,dome) VALUES (1,'V',0)")
    rows = [("windy", 10, 100, 20, 1), ("windy", 20, 120, 20, 2), ("windy", 30, 140, 20, 3),
            ("calm", 40, 200, 20, 4), ("calm", 40, 200, 20, 5), ("calm", 40, 200, 20, 6), ("calm", 40, 200, 20, 7)]
    for wb, pts, yds, att, gid in rows:
        db.execute("INSERT INTO games(game_id,season,week,season_type,kickoff_utc,completed,home_team,away_team,venue_id,home_points,away_points)"
                   " VALUES (?,2025,?, 'regular','2025-10-01T17:00:00Z',1,'A','B',1,?,0)", (gid, gid, pts))
        db.execute("INSERT INTO weather_obs(game_id,weather_ok,wind_bin,precip_bin,temp_bin) VALUES (?,1,?, 'none','mild')", (gid, wb))
        db.execute("INSERT INTO team_games(game_id,team,opponent,home_away,points,pass_yds,pass_att) VALUES (?, 'A','B','home',?,?,?)", (gid, pts, yds, att))
    db.commit()
    a = data.raw_block_averages(db, BINS, "A", "wind", "windy")
    assert (a["points"]["mean_in"], a["points"]["n_in"]) == (20, 3) and (a["points"]["mean_other"], a["points"]["n_other"]) == (40, 4)
    assert a["pass_eff"]["mean_in"] == pytest.approx((5.0 + 6.0 + 7.0) / 3)           # per-game ratio, averaged
    assert logic.anecdote_text("points", a["points"]) == "<b>20.0 pts</b> in these 3 games vs. 40.0 in this team's other 4 games"
    assert logic.anecdote_text("points", {"mean_in": None}) is None


def _page_with_a_thin_block():
    """A Gameday Card state that has at least one 'Not enough games' block with some games behind it."""
    from pathlib import Path
    for wind, precip in (("Windy", "Steady rain"), ("Windy", "Light rain"), ("Calm", "Steady rain"), ("Moderate wind", "Steady rain")):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app/streamlit_app.py"), default_timeout=90).run()
        [s for s in at.selectbox if s.label == "Wind"][0].select(wind)
        [s for s in at.selectbox if s.label == "Precipitation"][0].select(precip)
        at.run()
        if any(t.label == "Show anyway" for t in at.toggle):
            return at
    pytest.skip("no thin block in the current data")


def test_show_anyway_starts_off_reveals_plain_averages_and_never_touches_the_takeaway():
    at = _page_with_a_thin_block()
    toggles = [t for t in at.toggle if t.label == "Show anyway"]
    assert all(t.value is False for t in toggles)                                   # everyone starts off
    page = " ".join(m.value for m in at.markdown)
    assert "anecdote, not a finding" not in page
    takeaway_before = at.info[0].value
    toggles[0].set_value(True).run()
    assert not at.exception
    page = " ".join(m.value for m in at.markdown)
    assert "anecdote, not a finding" in page and "plain average, no adjustments" in page
    assert "Not enough games" in page                                               # the label is never upgraded
    assert at.info[0].value == takeaway_before                                      # the takeaway never uses revealed numbers
    assert "anyway" not in " ".join(at.query_params.keys())                         # session-only: a shared link can't carry it
    fresh = _page_with_a_thin_block()
    assert all(t.value is False for t in fresh.toggle if t.label == "Show anyway")  # a new visitor starts off again
