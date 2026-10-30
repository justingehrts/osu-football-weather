"""Evidence drawer: the games behind any number, plus the snow games."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd                         # noqa: E402
import streamlit as st                      # noqa: E402

from lib import data, logic, timefmt, ui    # noqa: E402

ui.setup("Evidence", "🗂️")
res = ui.resources()
bins, teams, conn = res["bins"], res["teams"], res["conn"]

st.title("Evidence")
st.caption("Every number in the app is built from real games. Pick a team and a condition to see them: date, opponent, venue, "
           "observed weather and the stat line. You can also open this list from any number's **n=** button.")

team = st.selectbox("Team", teams["loaded"], index=0)
BT = {"Wind": "wind", "Precipitation": "precip", "Temperature": "temp"}
VALS = {"wind": ["calm", "moderate", "windy"], "precip": ["none", "light", "steady", "wet"], "temp": ["cold", "mild", "warm", "hot", "warm_hot"]}
c1, c2 = st.columns(2)
bt = BT[c1.selectbox("Condition type", list(BT))]
bv = c2.selectbox("Bin", VALS[bt])
exclude = not st.checkbox("Include the 2020 season", value=True)
games = data.evidence_games(conn, bins, team, bt, bv, exclude_covid=exclude)
members = data.bin_members(bins, bt, bv)
st.markdown(f"**{team}: {bt} = {bv}** {'(' + ' + '.join(members) + ')' if len(members) > 1 else ''} — {len(games)} games, newest first")
st.dataframe(ui.games_frame(games), hide_index=True, width="stretch")
if games.shape[0]:
    st.download_button("Download these games (CSV)", logic.csv_bytes(ui.games_frame(games).to_dict("records")), file_name=f"games_{team}_{bt}_{bv}.csv".replace(" ", "_"), mime="text/csv")

st.markdown("### Snow games")
st.caption("Snow is too rare to split into statistics, so here are the actual games where an observation between kickoff and +3.5 hours "
           "reported snow. A snow code can mean flurries, so read the precipitation and temperature columns.")
snow = data.snow_games(conn)
if snow.empty:
    st.info("No snow games found in the loaded history.")
else:
    d = pd.DataFrame({
        "Date": [timefmt.local_day(k, z, "%b %d, %Y") for k, z in zip(snow.kickoff_utc, snow.tz)],
        "Game": [f"{a} at {h}" for a, h in zip(snow.away_team, snow.home_team)], "Venue": snow.venue,
        "Observed": [f"{t:.0f}°F, wind {w:.0f} mph, rain/melted {p:.2f} in., visibility {v:.1f} mi" for t, w, p, v in zip(snow.temp_f_mean, snow.wind_sust_max, snow.precip_in_total, snow.vis_min)],
        "Score": [f"{a} {int(ap)}, {h} {int(hp)}" for a, ap, h, hp in zip(snow.away_team, snow.away_points, snow.home_team, snow.home_points)]})
    st.dataframe(d, hide_index=True, width="stretch")
