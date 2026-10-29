"""Methodology: how to read every number in the app, in plain language."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st                      # noqa: E402

from lib import ui                          # noqa: E402

ui.setup("Methodology", "📘")
res = ui.resources()
bins, teams, stats = res["bins"], res["teams"], res["stats"]
w, p, t, c = bins["wind"], bins["precip"], bins["temperature"], bins["confidence"]
pn = stats.pooled_n
min_clear = bins["app"]["clear_signal_min_n"]
ci = int(bins["stats"]["ci_level"] * 100)

st.title("Methodology")
st.markdown("How to read the numbers in this app, what they can tell you, and where they stop being reliable.")

st.header("What this is (and isn't)")
st.markdown(
    "This app looks **backwards**. Given the forecast for a game, it shows how Ohio State and their opponent have actually done in "
    "games with similar wind and rain since 2015, compared with how those teams did in their other games. It is **not a prediction** "
    "of the score, and every finding is **exploratory**: we look at many conditions and many stats, so some patterns will appear by chance alone.")

st.header("What counts as the weather of a game")
st.markdown(
    f"For every past game we take the airport weather station nearest the stadium and use its reports from **kickoff to {bins['game_window_hours']} hours later**. "
    "For an upcoming game we take the forecast for that same window from the National Weather Service (Open-Meteo if the NWS is unavailable). "
    "Each is boiled down to the strongest sustained wind, the strongest gust, total rain and average temperature, and then sorted into bins.")
st.markdown("**Games in domes or other indoor stadiums are left out** of the weather statistics, and a game in a dome shows \"indoor, weather not a factor\". "
            "Retractable-roof stadiums that the data lists as domes are treated as indoor.")

st.header("The bins")
st.markdown(f"""
| | Bin | Rule (from `config/bins.yaml`) |
|---|---|---|
| **Wind** | Calm | sustained ≤ {w['calm']['sustained_max']} mph and gusts ≤ {w['calm']['gust_max']} mph |
| | Moderate | in between |
| | Windy | sustained ≥ {w['windy']['sustained_min']} mph **or** gusts ≥ {w['windy']['or_gust_min']} mph |
| **Rain** | Dry | no measurable rain in the window |
| | Light rain | under {p['steady']['total_in_min']:.2f} in. |
| | Steady rain | {p['steady']['total_in_min']:.2f} in. or more |
| | Any rain | light + steady combined (a bigger sample, so steadier numbers) |
| **Temperature** | Cold / Mild / Warm / Hot | ≤{t['cold']['max']}°F / {t['mild']['min']}–{t['mild']['max']}°F / {t['warm']['min']}–{t['warm']['max']}°F / ≥{t['hot']['min']}°F |
| **Snow** | (not a bin) | too rare for statistics, so the actual snow games are listed on the **Evidence** page |
""")
lo, hi = bins["forecast"]["precip_prob_middle"]
st.markdown(f"If the forecast chance of rain is between **{lo}% and {hi}%**, the app doesn't pick: it shows the **dry and wet histories one above the other** (each with the two teams left to right). "
            f"If a game is more than about {bins['forecast']['horizon_hours'] / 24:.1f} days away (as far as the hourly forecast reaches), "
            "it says so instead of guessing.")

st.header("The two yardsticks (what the numbers are compared with)")
st.markdown(
    "Every number answers \"how did the team do in these conditions **compared with something**?\" There are two reasonable somethings:\n\n"
    "1. **Versus all other games** — *windy vs. not windy.* This is the one the cards use, always labelled. It is the easiest to read.\n"
    "2. **Versus the team's overall average** — the team's average over *all* its games, including the windy ones. This yardstick appears "
    "only here and inside the expanders marked \"other yardstick\".\n\n"
    "They describe the same finding at different sizes: the first is the second divided by (1 − the share of games in the condition). "
    "For a condition that covers about a quarter of a team's games, \"vs. all other games\" is about a third larger. "
    "The app never mixes the two on one card.")

st.header("Fairness adjustments: opponent strength, time of season, home/away")
st.markdown(
    "Raw comparisons can fool you. Warm games are mostly early-season, at home, against weaker opponents; cold games are late-season against tougher ones. "
    "So the numbers shown are **controlled**: for each team and stat, a simple model accounts for **how strong the opponent was** (their SP+ rating, "
    "offense or defense as appropriate), **which part of the season** the game was in (Aug–Sep, Oct, Nov, Dec–Jan), and **home vs. away**, "
    "and then asks what is left for the weather condition.")
st.markdown(
    "**Games against FCS opponents are excluded from the adjusted and controlled numbers**, because SP+ only rates FBS teams and we never guess a rating. "
    "They are still listed in the evidence lists and counted in the raw numbers. The adjustment cannot remove everything: injuries, a team's identity changing "
    "over the years, and weather that differs between the two sidelines are not captured.")

st.header("Evidence labels")
st.markdown(f"""
Each number carries one of four labels, always next to its **n** (the number of games behind it):

| Label | What it means |
|---|---|
| **Clear signal** | The pipeline's strongest tier **and** at least **{min_clear} games**. Two related stats (passing efficiency + offensive PPA, or points + PPA) both point the same way with a {ci}% range that stays on one side of zero. |
| **Leans** | The related stats point the same way and the effect isn't tiny, but the range includes zero or there are fewer than {min_clear} games. A single stat on its own (e.g. points allowed) can never be better than "Leans". |
| **No clear effect** | Enough games ({c['thin_below_n']}+) and nothing there. **This is a real finding**, not missing data. |
| **Not enough games** | Fewer than {c['suppress_below_n']} games (or {c['suppress_below_n']}–{c['thin_below_n'] - 1} with no lean), so we say nothing. |

**Show anyway.** On the Gameday Card, a block with "Not enough games" has a small **Show anyway** switch (off every time you open the page). It reveals the plain average of those few games next to the team's other games, boxed and marked "anecdote, not a finding": no adjustments, no model, and it never feeds the takeaway or the exports.

Steady rain is therefore always at most **Leans**: it is rare. The one-sentence takeaway at the top of the Gameday Card uses **only wind and rain**, only findings labelled
Clear signal or Leans, and its wording matches the label (it never says "will").
""")

st.header("Intervals")
st.markdown(f"Behind each number is a **{ci}% interval**: re-running the analysis on thousands of re-shuffled sets of the same games gives a range of plausible values. "
            "If the range stays on one side of zero the direction is trustworthy; if it crosses zero the data can't tell the direction. "
            "Intervals are in the expanders because the labels already summarise them.")

st.header("Reading the card: words, game-sized numbers, the chart and the on-air line")
st.markdown(f"""
- **Words instead of signs.** "1.72 fewer yards per pass" means the same as -1.72 yds/att (the exact number is shown beside it, small).
  For **points allowed**, where *fewer* is good, the card adds **(better)** or **(worse)** so nobody has to flip a sign in their head.
- **Game-sized numbers** ("about 55 fewer passing yards a game (-18%) · usually 9.3 yards per pass in other games") multiply the
  adjusted per-pass change by the team's *plain* average of pass attempts in its other games, and compare points with its plain
  average in other games. They are **approximate** (an adjusted change next to a plain average), which is why they say "about".
  They are never computed for "Not enough games" rows or for the all-teams reference line.
- **The chart** has one dot per team for each stat: the dot is the adjusted change, the bar is the {ci}% range, the dashed line is
  "no difference" and **right is always better** (the points-allowed axis is flipped). Colors match the evidence labels. A bar that
  crosses the dashed line means the data can't tell the direction. Rows with too few games are listed under the chart, not drawn.
- **The on-air line** is built only from wind and rain findings, wind first. Its hedges come straight from the labels:
  *Clear signal* -> "has clearly ..."; *Leans* -> "has tended to ... but that's only N games" (fewer than {bins['app']['clear_signal_min_n']})
  or "... but it's not a consistent pattern"; *No clear effect* -> "no consistent effect". A toss-up chance of rain always gets its
  own sentence. Numbers in it are rounded for speaking; the card has the exact ones.
- **Under the hood** holds offensive PPA (expected points added per play) for viewers who know it. It already feeds the passing and
  scoring labels, so moving it off the card changes no label.
- **Forecast details** shows how close each forecast number is to a bin line (within the margins in `forecast.borderline`, a small
  forecast change could switch the history used), how the forecast has moved across pulls, and the hour-by-hour game window.
""")

st.header("Temperature is context only")
st.markdown("Temperature results are mostly the calendar in disguise (warm = September, cold = November), and even after controls they differ a lot from team to team. "
            "So temperature is **never** in the takeaway or the card headline. You can find it in the Explorer and in an expander labelled "
            "\"Temperature (context only): results differ by team\". For a team whose model finds no clear temperature effect, its temperature rows are labelled **Context only**.")
st.markdown("**Cold games, specifically.** The card shows the *controlled* number. In the \"Cold games\" expander you can see the *raw* number beside it: raw cold-game results look worse because "
            "cold games are late-season games, usually against tougher opponents.")

st.header("Limits of each finding")
st.markdown(f"""
- **Wind** is the best-supported result: it shows up for several teams and in the combined line for **all {pn} loaded teams**. Even so, it is a historical tendency, not a guarantee for one game.
- **Rain** is mostly *no clear effect* on scoring; there is some sign it affects passing and defense. Samples are small, so read "Leans" as a nudge.
- **Steady rain** has very few games for any one team. Treat it as a hint.
- **Temperature**: context only (see above).
- **Snow**: too few games; see the list on the Evidence page.
- **Small samples**: any team's windy or rainy bin may hold only 5–30 games. The **n** beside every number is the honest size.
- **Many comparisons**: the app looks at many teams, conditions and stats. About 1 in 10 comparisons will look meaningful by luck at the {ci}% level, which is why labels need agreement between related stats and a minimum n.
- **The 2020 season** (COVID-altered) is included by default and can be excluded with the checkbox.
- **Weather source**: the airport station may be several miles from the stadium (a few are flagged as far), and a forecast is a forecast.
- **Reference line**: "all {pn} loaded teams" pools every loaded team's games as a steadier backdrop. Teams marked *data not loaded yet* are not in it.
""")

st.header("Where the data comes from, and when it updates")
st.markdown(
    "Games, box scores and play-by-play value (PPA): CollegeFootballData. Observed weather: the Iowa Environmental Mesonet's airport (ASOS) archive. "
    "Opponent strength: SP+ ratings. Forecasts: the National Weather Service hourly grid, with Open-Meteo as a fallback; **every forecast pull is saved with its timestamp** and never overwritten. "
    "The history refreshes after new games finish (Saturday night through Monday during the season); forecasts refresh several times a day in game week.")
