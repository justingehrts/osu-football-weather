"""Making the salient information stand out: the at-a-glance board, one summary, size by evidence, quiet blocks folded,
badges that carry the forecast numbers, and the three bug fixes (borderline rounding, one game count, wrapped copy box).
Offline."""
import re

from lib import logic, plain
from test_app import BINS, TEAMS, card_game, make_stats, run_page, takeaway_of, windy_stats
from test_playcalling import _stats_with_pass_rate

TYPICAL = {"pass_eff": {"mean_other": 9.3}, "pass_att": {"mean_other": 32.0}, "points": {"mean_other": 42.0}}


def view_for(stats, typicals=None, **game):
    return logic.build_gameday_view(stats, BINS, TEAMS, card_game(**game), None, {"wind": "windy"},
                                    typicals=typicals or {}, first_season=2015)


# --------------------------------------------------------------------------- bug: borderline used unrounded numbers
def test_borderline_rounds_like_the_pipeline_so_9_2_mph_is_the_top_of_calm():
    fc = {"status": "ok", "wind_sust": 9.206, "wind_gust": 13.809, "precip_prob": 15.0, "precip_amt": None, "temp_f": 55.3}
    rows, notes = plain.bin_distances(fc, BINS)
    wind = {r["Forecast"]: r for r in rows}["Sustained wind"]
    assert wind["Value"] == "9 mph" and wind["Where it sits"] == "calm is up to 9 mph (0 under)" and wind["Borderline"] == "yes"
    assert notes == ["9 mph sustained is the top of the calm range (calm runs up to 9 mph; 10 to 14 is moderate)"]
    assert not any("between calm and windy" in r["Where it sits"] for r in rows)


def test_borderline_notes_say_which_line_and_how_far():
    fc = {"status": "ok", "wind_sust": 13.4, "wind_gust": 20.0, "precip_prob": 64.0, "precip_amt": 0.081, "temp_f": 50}
    _, notes = plain.bin_distances(fc, BINS)
    assert "13 mph sustained is moderate, 2 mph below the windy line (15 mph)" in notes
    assert "64% chance of rain is near the edge of the 30-70% toss-up band" in notes
    assert "0.08 in. of rain is close to the steady-rain line (0.10 in.)" in notes


# --------------------------------------------------------------------------- 5: badges carry the numbers
def test_badges_carry_the_forecast_numbers_and_a_borderline_tag():
    fc = {"status": "ok", "wind_sust": 9.206, "wind_gust": 13.809, "precip_prob": 15.0, "precip_amt": None, "temp_f": 55.3}
    cond = {"wind": "calm", "precip": "none", "temp": "mild", "overridden": False}
    parts = plain.badge_parts(cond, fc, BINS)
    assert parts[0] == {"name": "Calm", "detail": "9 mph · gusts 14", "tag": "top of calm", "muted": False}
    assert parts[1] == {"name": "Dry", "detail": "15% chance of rain", "tag": None, "muted": False}
    assert parts[2] == {"name": "Mild", "detail": "55°F", "tag": None, "muted": True}           # temperature: context only
    what_if = plain.badge_parts({**cond, "overridden": True}, fc, BINS)
    assert [p["detail"] for p in what_if] == [None, None, None]                         # chosen conditions have no forecast numbers


# --------------------------------------------------------------------------- 1: the at-a-glance board
def test_glance_says_the_strongest_finding_in_a_few_words_with_its_label_and_n():
    rows = plain.glance(view_for(windy_stats(osu_n=31, usc_n=20), {("Ohio State", "wind", "windy"): TYPICAL}), windy_stats())
    (row,) = rows
    assert (row["kind"], row["cond"], row["anchor"]) == ("Wind", "Windy", "sec-wind-windy")
    osu, usc = row["cells"]
    assert (osu["label"], osu["text"], osu["n"]) == (logic.CLEAR, "Passes and scores worse", 31)
    assert (usc["label"], usc["text"], usc["n"]) == (logic.LEANS, "Tends to pass and score a bit worse", 20)


def test_glance_puts_a_weaker_second_finding_underneath_and_adds_game_sized_terms_to_a_clear_one():
    cells = {("Ohio State", "wind", "windy", "pass_eff"): (-1.2, -2.0, -0.4, 31), ("Ohio State", "wind", "windy", "points"): (-4.0, -7.0, -1.0, 31)}
    tiers = {("Ohio State", "wind", "windy", "passing"): ("clear", 31), ("Ohio State", "wind", "windy", "scoring"): ("leans", 31)}
    stats = make_stats(cells, tiers)
    osu = plain.glance(view_for(stats, {("Ohio State", "wind", "windy"): TYPICAL}), stats)[0]["cells"][0]
    assert osu["label"] == logic.CLEAR and osu["text"] == "Passes worse: about 40 fewer passing yards a game"
    assert osu["sub"] == "Also tends to score a bit less (Leans)"


def test_glance_says_no_clear_change_plainly_and_handles_a_team_without_data():
    stats = windy_stats(osu_tier="no_clear_effect", usc_tier="no_clear_effect")
    osu, _ = plain.glance(view_for(stats), stats)[0]["cells"]
    assert (osu["label"], osu["text"]) == (logic.NONE, "No clear change in passing or scoring")
    deferred = plain.glance(view_for(stats, opponent="Ball State", home_team="Ball State"), stats)[0]["cells"][1]
    assert (deferred["text"], deferred["n"]) == ("data not loaded yet", None)


# --------------------------------------------------------------------------- bug: one game count everywhere
def test_takeaway_and_on_air_use_the_cards_own_game_count():
    # the tier's count (33) can differ from the card's (31): e.g. PPA missing for a couple of games
    cells = {("Ohio State", "wind", "windy", "pass_eff"): (-1.2, -2.0, -0.4, 31), ("Ohio State", "wind", "windy", "points"): (-4.0, -7.0, -1.0, 31)}
    tiers = {("Ohio State", "wind", "windy", g): ("clear", 33) for g in ("passing", "scoring")}
    view = view_for(make_stats(cells, tiers))
    assert "(n=31)" in view["takeaway"] and "(n=33)" not in view["takeaway"]
    assert "(31 games)" in view["on_air"]


# --------------------------------------------------------------------------- playcalling summaries
def test_playcalling_summaries_only_report_leans_findings_in_plain_words():
    view = view_for(_stats_with_pass_rate())
    sec = view["sections"][0]
    assert plain.playcall_summary(sec, "Ohio State", "USC") == \
        "Ohio State has tended to throw less: about 4 fewer passes per 100 plays (Leans, 21 games)."
    assert plain.playcall_glance(view) == "Playcalling (not better or worse): Ohio State tends to throw less in windy games. All Leans."
    quiet = view_for(_stats_with_pass_rate(osu=(-4.0, -9.0, 1.0, 21)))
    assert plain.playcall_summary(quiet["sections"][0], "Ohio State", "USC") == "No clear playcalling change for either team in windy games."
    assert plain.playcall_glance(quiet) is None


def test_chart_titles_carry_units():
    rows = view_for(windy_stats())["sections"][0]["rows"]
    df, _ = plain.chart_frame(rows, "Ohio State", "USC", 6, ["pass_eff", "points_allowed"])
    assert set(df["title"]) == {"Passing efficiency · yards per pass", "Points allowed · points a game"}


# --------------------------------------------------------------------------- the page
def test_gameday_page_leads_with_the_board_and_one_summary():
    at = run_page("app/streamlit_app.py")
    assert not at.exception
    page = [m.value for m in at.markdown]
    board = [v for v in page if 'class="glance"' in v]
    assert len(board) == 1 and "At a glance" in board[0]
    for target in set(re.findall(r'href="#([^"]+)"', board[0])):                   # every link lands on a section
        assert any(f'id="{target}"' in v for v in page)
    summary = [v for v in page if 'class="onair-box"' in v]
    assert len(summary) == 1 and "Written summary:" in summary[0] and takeaway_of(at) in summary[0]
    assert not at.info                                                              # no second summary box
    assert sum(v.count("Dot = the change") for v in page) == 0                     # chart legend explained once (popover)


def test_non_findings_are_quiet_and_never_get_a_game_sized_line():
    at = run_page("app/streamlit_app.py")
    page = [m.value for m in at.markdown]
    assert any("res-clear" in v for v in page)
    for v in page:
        if "res-none" in v or "res-few" in v:
            assert 'class="gt"' not in v
    quiet = [v for v in page if 'class="quiet"' in v]
    assert quiet and all("No clear effect" in v and "games)" in v for v in quiet)
    toggles = [t for t in at.toggle if t.label == "Show the numbers"]
    assert toggles and all(t.value is False for t in toggles)                       # folded by default, session-only
    shown_before = sum("res-none" in v for v in page)
    toggles[0].set_value(True).run()
    assert not at.exception and sum("res-none" in m.value for m in at.markdown) > shown_before


def test_copy_as_text_box_wraps():
    at = run_page("app/streamlit_app.py")
    box = [c for c in at.code if c.value.startswith(("Ohio State", "Oregon")) or "Exploratory history" in c.value]
    assert box and all(c.proto.wrap_lines for c in box)


def test_season_table_forecast_line_carries_the_numbers():
    fc = {"wind_bin": "calm", "precip_bin": "none", "temp_bin": "mild", "wind_sust": 9.206, "wind_gust": 13.8,
          "precip_prob": 15.0, "temp_f": 55.3}
    assert plain.forecast_brief(fc) == "Calm 9 mph (gusts 14) · Dry 15% · Mild 55°F"
    assert plain.forecast_brief({**fc, "precip_bin": "uncertain", "precip_prob": 50.0, "wind_gust": None}) == \
        "Calm 9 mph · Rain possible 50% · Mild 55°F"
    at = run_page("app/streamlit_app.py")
    table = at.dataframe[-1].value
    upcoming = [w for w in table["Weather"] if w.startswith("forecast:")]
    assert upcoming and all("mph" in w for w in upcoming)


def test_copy_as_text_forecast_line_has_the_numbers_and_what_if_says_so():
    fc = {"status": "ok", "wind_bin": "windy", "precip_bin": "none", "temp_bin": "mild", "wind_sust": 17.2, "wind_gust": 28.4,
          "precip_prob": 10.0, "precip_amt": None, "temp_f": 51.0}
    view = logic.build_gameday_view(windy_stats(), BINS, TEAMS, card_game(), fc, {}, first_season=2015)
    assert "Forecast: Windy 17 mph (gusts 28) · Dry 10% · Mild 51°F" in logic.blurb(view)
    what_if = logic.build_gameday_view(windy_stats(), BINS, TEAMS, card_game(), fc, {"wind": "calm"}, first_season=2015)
    assert "Conditions (What-If): Calm" in logic.blurb(what_if) and "17 mph" not in logic.blurb(what_if)
