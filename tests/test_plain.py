"""Plain-language layer for broadcast use: words, game-sized terms, the chart, the on-air line, and the forecast
helpers. Offline; synthetic numbers except where noted."""
import json

import pandas as pd

from lib import charts, logic, plain
from test_app import BINS, TEAMS, card_game, make_stats, run_page, windy_stats

TYPICAL = {"pass_eff": {"mean_other": 9.3}, "pass_att": {"mean_other": 32.0}, "points": {"mean_other": 42.0},
           "points_allowed": {"mean_other": 18.0}}


def result(metric, value, lo=None, hi=None, n=31, label=logic.CLEAR, team="Ohio State"):
    return logic.Result(team=team, bin_type="wind", bin_value="windy", metric=metric, status="ok", value=value, lo=lo, hi=hi,
                        n=n, label=label)


# --------------------------------------------------------------------------- words and direction
def test_words_replace_signs_and_say_better_or_worse_only_where_lower_is_good():
    assert plain.words(result("pass_eff", -1.72)) == ("1.72 fewer yards per pass", None)
    assert plain.words(result("points", 2.04)) == ("2.0 more points", None)
    assert plain.words(result("points_allowed", 0.9)) == ("0.9 more points allowed", "worse")
    assert plain.words(result("points_allowed", -3.0)) == ("3.0 fewer points allowed", "better")
    assert plain.words(result("pass_eff", -1.72), short=True)[0] == "1.72 fewer yds/pass"
    assert plain.words(result("pass_eff", 0.001))[0].startswith("about the same")


def test_words_are_withheld_when_there_are_not_enough_games():
    assert plain.words(result("pass_eff", -1.0, n=3, label=logic.FEW)) == (None, None)


# --------------------------------------------------------------------------- game-sized terms
def test_game_terms_put_the_change_next_to_what_the_team_usually_does():
    g = plain.game_terms(result("pass_eff", -1.72), TYPICAL)
    assert g.startswith("about 55 fewer passing yards a game")        # 1.72 x 32 attempts = 55, rounded to 5
    assert "(-18%)" in g and "usually 9.3 yards per pass in other games" in g
    assert plain.game_terms(result("points", -6.4), TYPICAL) == \
        "15% below the ~42 points a game they usually score in other games"
    assert "usually allow" in plain.game_terms(result("points_allowed", 2.0), TYPICAL)
    assert plain.game_terms_short(result("pass_eff", -1.72), TYPICAL) == "≈55 fewer pass yds/game"
    assert plain.game_terms_short(result("points", -6.4), TYPICAL) == "15% below usual"


def test_no_game_terms_for_the_pooled_line_thin_rows_or_missing_averages():
    assert plain.game_terms(result("pass_eff", -1.0, team=logic.POOLED), TYPICAL) is None
    assert plain.game_terms(result("pass_eff", -1.0, n=4, label=logic.FEW), TYPICAL) is None
    assert plain.game_terms(result("pass_eff", -1.0), {"pass_eff": {"mean_other": 9.0}}) is None   # no attempts
    assert plain.game_terms(result("points", -1.0), None) is None


# --------------------------------------------------------------------------- the chart
def test_chart_flips_lower_is_better_stats_so_right_is_always_better():
    rows = [result("pass_eff", -1.2, -2.0, -0.4), result("points_allowed", 1.0, -2.0, 4.0, label=logic.LEANS),
            result("points", -4.0, -7.0, -1.0, team="USC", label=logic.FEW, n=3)]
    df, missing = plain.chart_frame(rows, "Ohio State", "USC", 6, ["pass_eff", "points", "points_allowed"])
    pa = df[df.metric == logic.METRIC_INFO["points_allowed"][0]].iloc[0]
    assert pa.better == -1.0 and (pa.lo, pa.hi) == (-4.0, 2.0)          # more points allowed = worse = LEFT
    pe = df[df.metric == logic.METRIC_INFO["pass_eff"][0]].iloc[0]
    assert pe.better == -1.2 and (pe.lo, pe.hi) == (-2.0, -0.4)
    assert "(worse)" in pa.in_words
    assert len(df) == 2                                                   # the thin USC row is listed, not drawn
    assert len(missing) == 1 and missing[0].startswith("USC: ") and "(not enough games, n=3)" in missing[0]


def test_chart_tooltips_never_show_interval_numbers():
    rows = [result("pass_eff", -1.2, -2.0, -0.4)]
    df, _ = plain.chart_frame(rows, "Ohio State", "USC", 6, ["pass_eff"])
    drawn = charts.condition_chart(df)
    spec = json.dumps(drawn[0].to_dict())
    tips = [t["field"] for layer in drawn[0].to_dict()["layer"] for t in (layer.get("encoding", {}).get("tooltip") or [])]
    assert tips and not {"lo", "hi"} & set(tips)
    assert "worse" in spec and "better" in spec and '"zero": true' in spec      # the no-difference line is always on the axis
    assert charts.condition_chart(pd.DataFrame()) == []


# --------------------------------------------------------------------------- the on-air line
def test_on_air_hedges_follow_the_labels():
    clear = plain.on_air_line(windy_stats(), "Ohio State", "USC", "windy", None, BINS, {("Ohio State", "wind", "windy"): TYPICAL},
                              2015)
    assert "Ohio State has clearly been less effective on offense" in clear
    assert "roughly 40 fewer passing yards" in clear and "(31 games)" in clear      # 1.2 x 32 = 38 -> 40
    assert "USC has tended to" in clear and "but that's only 20 games" in clear     # Leans because n=20 < 30
    steady = plain.on_air_line(windy_stats(usc_tier="leans", usc_n=40), "Ohio State", "USC", "windy", None, BINS, {}, 2015)
    assert "but it's not a consistent pattern" in steady                             # Leans with plenty of games
    thin = plain.on_air_line(windy_stats(osu_tier="leans", osu_n=9, usc_tier="no_clear_effect"), "Ohio State", "USC", "windy",
                             None, BINS, {}, 2015)
    assert "has tended to" in thin and "but that's only 9 games" in thin and "clearly" not in thin


def test_on_air_says_no_consistent_effect_plainly_and_never_mentions_temperature():
    s = windy_stats(osu_tier="no_clear_effect", usc_tier="no_clear_effect")
    line = plain.on_air_line(s, "Ohio State", "USC", "windy", None, BINS, {}, 2015)
    assert "no weather angle" in line or "consistent" in line
    for word in ("cold", "warm", "temperature", "degrees"):
        assert word not in plain.on_air_line(windy_stats(), "Ohio State", "USC", "windy", None, BINS, {}, 2015).lower()


def test_on_air_always_makes_room_for_a_toss_up_rain_chance():
    line = plain.on_air_line(windy_stats(), "Ohio State", "USC", "windy", "uncertain", BINS, {}, 2015, precip_prob=50)
    assert line.endswith("Rain is a toss-up at 50%, so there's no single rain story yet.")
    assert line.count(".") >= 2


# --------------------------------------------------------------------------- forecast helpers
def test_bin_distances_flag_a_forecast_near_a_line():
    fc = {"status": "ok", "wind_sust": 16, "wind_gust": 22, "precip_prob": 67, "precip_amt": 0.09, "temp_f": 51}
    rows, notes = plain.bin_distances(fc, BINS)
    by = {r["Forecast"]: r for r in rows}
    assert by["Sustained wind"]["Borderline"] == "yes" and "1 over" in by["Sustained wind"]["Where it sits"]
    assert by["Rain amount"]["Borderline"] == "yes" and by["Chance of rain"]["Value"] == "67%"
    assert "Temperature (context only)" in by and not any("temperature" in n for n in notes)   # never a headline flag
    assert plain.bin_distances({"status": "beyond_horizon"}, BINS) == ([], [])


def test_forecast_trend_compares_first_and_latest_pull_and_says_if_the_card_changed():
    h = pd.DataFrame([dict(snapshot_utc="2026-10-27T18:00:00", status="ok", wind_sust=12, wind_gust=21, precip_prob=40,
                           wind_bin="moderate", precip_bin="light"),
                      dict(snapshot_utc="2026-10-28T00:00:00", status="error", wind_sust=None, wind_gust=None, precip_prob=None,
                           wind_bin=None, precip_bin=None),
                      dict(snapshot_utc="2026-10-28T18:00:00", status="ok", wind_sust=17, wind_gust=28, precip_prob=60,
                           wind_bin="windy", precip_bin="light")])
    text, ok = plain.forecast_trend(h)
    assert len(ok) == 2 and "(2 pulls)" in text
    assert "wind up 5 mph (12 to 17)" in text and "rain chance up 20%" in text
    assert "Card changed: wind bin moderate to windy" in text
    assert plain.forecast_trend(h.iloc[:1])[0] is None


def test_hourly_chart_draws_the_windy_lines_from_config():
    hours = [{"time": "2026-10-31T23:00:00+00:00", "wind": 14, "gust": 24, "pop": 50, "rain_in": 0.02, "temp_f": 53}]
    spec = json.dumps(charts.hourly_chart(hours, BINS).to_dict())
    assert str(BINS["wind"]["windy"]["sustained_min"]) in spec and str(BINS["wind"]["windy"]["or_gust_min"]) in spec
    assert charts.hourly_chart([], BINS) is None


# --------------------------------------------------------------------------- PPA lives under the hood
def test_ppa_is_under_the_hood_not_on_the_headline_card():
    head, hood = logic.card_metrics(BINS)
    assert "ppa_off" in hood and "ppa_off" not in head
    view = logic.build_gameday_view(windy_stats(), BINS, TEAMS, card_game(), None, {"wind": "windy"},
                                    typicals={("Ohio State", "wind", "windy"): TYPICAL}, first_season=2015)
    r = [r for r in view["sections"][0]["rows"] if r.team == "Ohio State" and r.metric == "pass_eff"][0]
    assert r.extra["words"] == "1.20 fewer yards per pass" and r.extra["game_terms"].startswith("about 40 fewer")
    assert view["on_air"] and "On-air line: " + view["on_air"] in logic.blurb(view)


def test_gameday_page_shows_the_on_air_line_chart_forecast_details_and_hides_ppa_from_the_columns():
    at = run_page("app/streamlit_app.py")
    assert not at.exception
    page = " ".join(m.value for m in at.markdown)
    assert "On-air line" in page and 'class="onair"' in page
    labels = [e.label for e in at.expander]
    assert "Under the hood: offensive PPA (for the stats crowd)" in labels
    assert "Forecast details: bin lines, trend and hour by hour" in labels
    assert any("Borderline forecast" in w.value for w in at.warning)          # fixture: 0.08 in. vs the 0.10 line
    for col in at.columns:
        assert not any("PPA" in m.value or "expected points per play" in m.value for m in col.markdown), \
            "PPA belongs under the hood, not on the card"
    assert "fewer" in page or "more" in page                                  # words, not bare signs
    details = [e for e in at.expander if e.label.startswith("Forecast details")][0]
    assert any("pulls)" in m.value for m in details.markdown)                 # the trend sentence
