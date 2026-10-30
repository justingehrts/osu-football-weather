"""Playcalling (pass share of plays, plays per game): pipeline numbers, neutral wording, neutral chart, on-air sentence,
and that the page shows it as 'how they play, not how well'. Offline."""
import numpy as np
import pandas as pd

from lib import charts, config, logic, plain
from pipeline import compute_splits as cs
from test_app import BINS, TEAMS, card_game, make_stats, run_page
from test_plain import result

TYPICAL = {"pass_eff": {"mean_other": 9.3}, "pass_att": {"mean_other": 32.0}, "points": {"mean_other": 42.0},
           "pass_rate": {"mean_other": 45.0}, "plays": {"mean_other": 70.0}}


# --------------------------------------------------------------------------- pipeline
def test_pass_rate_is_passes_per_100_plays_and_plays_is_pace():
    df = pd.DataFrame({"pass_att": [30, 20, 0], "rush_att": [40, 30, 0], "plays": [70, 50, 0]})
    assert list(cs.game_values(df, "pass_rate")[:2]) == [100 * 30 / 70, 100 * 20 / 50]
    assert np.isnan(cs.game_values(df, "pass_rate")[2])                       # no plays: no number, not zero
    assert list(cs.game_values(df, "plays")) == [70, 50, 0]
    assert np.isnan(cs.game_values(pd.DataFrame({"x": [1]}), "pass_rate")).all()   # columns missing: skipped, not a crash


def test_playcalling_is_not_part_of_any_quality_tier():
    assert set(cs.PLAYCALL_METRICS) <= set(cs.METRICS) and not set(cs.PLAYCALL_METRICS) & set(cs.CORE_METRICS)
    assert not any(m in ms for ms in cs.GROUPS.values() for m in cs.PLAYCALL_METRICS)


# --------------------------------------------------------------------------- neutral wording
def test_words_for_playcalling_never_say_better_or_worse():
    assert plain.words(result("pass_rate", -4.1, n=21, label=logic.LEANS)) == ("4.1 points less passing", None)
    assert plain.words(result("pass_rate", 2.0, n=21, label=logic.LEANS)) == ("2.0 points more passing", None)
    assert plain.words(result("plays", -3.0, n=21, label=logic.NONE)) == ("3.0 fewer plays", None)
    assert plain.GOOD["pass_rate"] == 0 and plain.GOOD["plays"] == 0


def test_game_sized_terms_for_playcalling():
    r = result("pass_rate", -4.1, n=21, label=logic.LEANS)
    assert plain.game_terms(r, TYPICAL) == \
        "passes on about 41% of plays vs. usually 45% in other games · about 3 fewer passes a game"
    assert plain.game_terms_short(r, TYPICAL) == "≈3 fewer passes/game"
    p = result("plays", 5.2, n=21, label=logic.NONE)
    assert plain.game_terms(p, TYPICAL) == "about 5 more plays a game (+7%) · usually 70 in other games"
    assert plain.game_terms(result("pass_rate", -4.1, team=logic.POOLED), TYPICAL) is None
    assert "passes a game" not in plain.game_terms(r, {"pass_rate": {"mean_other": 45.0}})          # no plays average: no guess


# --------------------------------------------------------------------------- neutral chart
def test_playcalling_chart_is_not_flipped_and_does_not_say_better():
    rows = [result("pass_rate", -4.0, -8.0, -1.0, n=21, label=logic.LEANS)]
    df, _ = plain.chart_frame(rows, "Ohio State", "USC", 6, ["pass_rate"])
    row = df.iloc[0]
    assert (row.better, row.lo, row.hi) == (-4.0, -8.0, -1.0)                 # lower-is-better flipping does not apply
    assert "threw more" in row.axis and "better" not in row.axis and "worse" not in row.axis
    spec = charts.condition_chart(df)[0].to_dict()
    assert "threw more" in str(spec)
    assert "(better)" not in row.in_words and "(worse)" not in row.in_words


# --------------------------------------------------------------------------- on-air sentence
def _stats_with_pass_rate(osu=(-4.0, -8.0, -1.0, 21), usc=(0.5, -3.0, 4.0, 40)):
    cells = {}
    for team, (v, lo, hi, n) in (("Ohio State", osu), ("USC", usc)):
        cells[(team, "wind", "windy", "pass_rate")] = (v, lo, hi, n)
        cells[(team, "wind", "windy", "pass_eff")] = (-1.0, -3.0, 1.0, n)
        cells[(team, "wind", "windy", "points")] = (-1.0, -5.0, 3.0, n)
    tiers = {(t, "wind", "windy", g): ("no_clear_effect", 30) for t in ("Ohio State", "USC") for g in ("passing", "scoring")}
    return make_stats(cells, tiers)


def test_on_air_adds_one_playcalling_sentence_only_for_a_leans_finding():
    line = plain.on_air_line(_stats_with_pass_rate(), "Ohio State", "USC", "windy", None, BINS, {}, 2015)
    assert "Ohio State has tended to throw less in windy games: about 4 fewer passes per 100 plays, but that's only 21 games." in line
    assert "no weather angle" not in line and "USC has tended" not in line     # USC's pass share: no clear effect, no sentence
    none = plain.on_air_line(_stats_with_pass_rate(osu=(-4.0, -9.0, 1.0, 21)), "Ohio State", "USC", "windy", None, BINS, {}, 2015)
    assert "throw" not in none                                                  # interval crosses zero: not a finding
    big = plain.on_air_line(_stats_with_pass_rate(osu=(-4.0, -8.0, -1.0, 40)), "Ohio State", "USC", "windy", None, BINS, {}, 2015)
    assert "but it's not a consistent pattern" in big


def test_on_air_playcalling_keeps_the_toss_up_sentence_last():
    line = plain.on_air_line(_stats_with_pass_rate(), "Ohio State", "USC", "windy", "uncertain", BINS, {}, 2015, precip_prob=50)
    assert "throw less in windy games" in line and line.endswith("so there's no single rain story yet.")


# --------------------------------------------------------------------------- real data and the page
def test_playcalling_can_never_be_a_clear_signal_in_the_real_data():
    res = run_page("app/streamlit_app.py")
    assert not res.exception
    from lib import ui
    stats = ui.resources()["stats"]
    seen = 0
    for team in list(TEAMS["loaded"]) + [logic.POOLED]:
        for bt, bv in (("wind", "windy"), ("wind", "calm"), ("precip", "wet"), ("precip", "steady")):
            r = stats.result(team, bt, bv, "pass_rate")
            seen += r.status == "ok"
            assert r.label != logic.CLEAR            # one stat has no partner to agree with it: at most Leans
    assert seen


def test_gameday_page_shows_a_neutral_playcalling_block_under_each_condition():
    at = run_page("app/streamlit_app.py")
    assert not at.exception
    page = " ".join(m.value for m in at.markdown)
    assert page.count("Playcalling: how they play, not how well") >= 2          # wind + at least one rain scenario
    assert "not better or worse" in page and "Pass share of plays" in page
    assert "points less passing" in page or "points more passing" in page or "about the same passing" in page
    for col in at.columns:                                                      # never good/bad words in a playcalling row
        for m in col.markdown:
            if "Pass share of plays" in m.value:
                assert "(better)" not in m.value and "(worse)" not in m.value


def test_exports_carry_playcalling():
    view = logic.build_gameday_view(_stats_with_pass_rate(), BINS, TEAMS, card_game(), None, {"wind": "windy"},
                                    typicals={("Ohio State", "wind", "windy"): TYPICAL}, first_season=2015)
    assert view["playcall_metrics"] == ["pass_rate", "plays"]
    text = logic.blurb(view)
    assert "Ohio State playcalling (not better or worse): Pass share of plays 4.0 points less passing (n=21, Leans)" in text
    rows = [r for r in logic.view_rows(view) if r["metric"] == "Pass share of plays"]
    assert rows and rows[0]["in_words"] == "4.0 points less passing"
    assert logic.anecdote_text("pass_rate", {"mean_in": 41.2, "n_in": 9, "mean_other": 44.9, "n_other": 120}) == \
        "<b>41.2% passes</b> in these 9 games vs. 44.9 in this team's other 120 games"
