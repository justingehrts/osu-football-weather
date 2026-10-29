"""Gameday Card: the landing page. Opens on the next Ohio State game with the forecast prefilled."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd                                    # noqa: E402
import streamlit as st                                  # noqa: E402

from lib import data, export, logic, ui                 # noqa: E402

ui.setup("Gameday Card")
res = ui.resources()
bins, teams, stats, conn, fconn = res["bins"], res["teams"], res["stats"], res["conn"], res["fconn"]
focal = teams["focal"]

WIND_OPTS = {"Use the forecast": None, "Calm": "calm", "Moderate wind": "moderate", "Windy": "windy"}
PRECIP_OPTS = {"Use the forecast": None, "Dry": "none", "Light rain": "light", "Steady rain": "steady",
               "Rain possible (show dry and wet)": "uncertain"}
TEMP_OPTS = {"Use the forecast": None, "Cold": "cold", "Mild": "mild", "Warm": "warm", "Hot": "hot"}


def _idx(opts, val):
    return list(opts.values()).index(val) if val in opts.values() else 0


def tz_local(ts, fmt="%a %b %d, %-I:%M %p ET"):
    return pd.to_datetime(ts, utc=True).tz_convert("America/New_York").strftime(fmt)


st.title("Gameday Card")
sched = data.schedule(conn, focal, teams["season"])
if sched.empty:
    st.warning(f"No {teams['season']} schedule is loaded yet.")
    st.stop()

# ---- which game -------------------------------------------------------------------------------
default_game = data.next_game(sched)
labels = {int(r.game_id): f"Wk {int(r.week)} · {'at' if r.site == 'away' else 'vs.'} {r.opponent} · "
          f"{tz_local(r.kickoff_utc, '%b %d') if r.kickoff_utc else 'TBD'}"
          + (" · played" if r.completed else "") for r in sched.itertuples()}
want = ui.qp("game")
gid = int(want) if want and want.isdigit() and int(want) in labels else int(default_game["game_id"])
gid = st.selectbox("Game", list(labels), index=list(labels).index(gid), format_func=labels.get,
                   help="Opens on the next game. Pick any game on the schedule.")
game = sched[sched.game_id == gid].iloc[0].to_dict()

# ---- What-If ----------------------------------------------------------------------------------
with st.expander("What-If: change the conditions", expanded=bool(ui.qp("wind") or ui.qp("precip") or ui.qp("temp"))):
    c1, c2, c3 = st.columns(3)
    wind_pick = c1.selectbox("Wind", list(WIND_OPTS), index=_idx(WIND_OPTS, ui.qp("wind")))
    precip_pick = c2.selectbox("Precipitation", list(PRECIP_OPTS), index=_idx(PRECIP_OPTS, ui.qp("precip")))
    temp_pick = c3.selectbox("Temperature (context only)", list(TEMP_OPTS), index=_idx(TEMP_OPTS, ui.qp("temp")))
    side_by_side = st.checkbox("Show dry and wet side by side", value=ui.qp("sbs") == "1",
                               help="Turned on automatically when the chance of rain is in the middle (30-70%).")
    scope_all = st.checkbox("Include the 2020 season (COVID-altered)", value=ui.qp("y2020", "1") != "0")
what_if = {"wind": WIND_OPTS[wind_pick], "precip": PRECIP_OPTS[precip_pick], "temp": TEMP_OPTS[temp_pick]}
scope = "all" if scope_all else "ex2020"
st.session_state["scope"] = scope
ui.set_qp(game=gid if gid != int(default_game["game_id"]) else None, wind=what_if["wind"], precip=what_if["precip"],
          temp=what_if["temp"], sbs="1" if side_by_side else None, y2020=None if scope_all else "0")

forecast = data.latest_forecast(fconn, gid)
view = logic.build_gameday_view(stats, bins, teams, game, forecast, what_if, side_by_side, scope)
precip_uncertain = view.get("conditions", {}).get("precip") == "uncertain"

# ---- header, forecast, takeaway ---------------------------------------------------------------
ui.matchup_header(view)
meta = " · ".join(x for x in [view.get("venue"), tz_local(game["kickoff_utc"]) if game.get("kickoff_utc") and not game.get("kickoff_tbd") else "kickoff time TBD"] if x)
st.caption(meta)

status = view["forecast_status"]
if status == "played":
    pts = (game["home_points"], game["away_points"]) if game["home_team"] == focal else (game["away_points"], game["home_points"])
    st.markdown(f"### Result: {focal} {int(pts[0])}, {game['opponent']} {int(pts[1])}")
    obs = []
    if game.get("weather_ok") == 1:
        obs = logic.condition_badges(game["wind_bin"], game["precip_bin"], game["temp_bin"])
        st.markdown("Observed weather: " + ui.badges(obs), unsafe_allow_html=True)
        st.caption(f"{game['temp_f_mean']:.0f}°F average, wind up to {game['wind_sust_max']:.0f} mph (gusts {game['wind_gust_max']:.0f}), "
                   f"{game['precip_in_total']:.2f} in. of rain" + (", snow reported" if game["snow_flag"] else "") + " (kickoff to +3.5 h, airport station).")
    elif game.get("dome") == 1:
        st.markdown("Indoor game: weather was not a factor.")
    else:
        st.caption("No usable observed weather for this game.")
    st.info(view["takeaway"])
elif status == "indoor":
    st.info("**Indoor, weather not a factor.**")
else:
    if view["badges"]:
        st.markdown(ui.badges(view["badges"]), unsafe_allow_html=True)
        c = view["conditions"]
        if c["overridden"]:
            st.caption("🔧 What-If: these are your chosen conditions, not the forecast.")
        elif forecast and forecast.get("status") == "ok":
            st.caption(f"{forecast['source'].upper()} forecast pulled {tz_local(forecast['snapshot_utc'])}, for kickoff to +3.5 h: "
                       f"wind up to {forecast['wind_sust']:.0f} mph (gusts {forecast['wind_gust']:.0f}), chance of rain {forecast['precip_prob']:.0f}%, "
                       f"{forecast['precip_amt']:.2f} in., {forecast['temp_f']:.0f}°F.")
    else:
        st.warning(view["takeaway"].split(" Choose conditions")[0])
    st.info(view["takeaway"])
    if view["sections"]:
        st.caption("All numbers below compare a team's games in these conditions with its **other** games (for example, windy vs. not windy), "
                   "with opponent strength, time of season and home/away held fixed. Exploratory: not a prediction.")

# ---- the comparison: wind first, then rain ----------------------------------------------------
pn = view["pooled_n"]
for sec in [s for s in view["sections"] if s["dim"] == "wind"]:
    st.markdown(f"### Wind: {sec['title']}")
    cols = st.columns(2)
    for col, team in zip(cols, (view["focal"], view["opponent"])):
        with col:
            ui.team_block([r for r in sec["rows"] if r.team == team], team, "w")
    ui.pooled_reference([r for r in sec["rows"] if r.team == logic.POOLED], pn)

psecs = [s for s in view["sections"] if s["dim"] == "precip"]
if psecs:
    st.markdown("### Precipitation" + (": " + " and ".join(logic.PRECIP_NAME.get(x["bin"], x["bin"]) for x in psecs).replace("Any rain (light + steady)", "any rain") + ", side by side" if len(psecs) > 1 else ""))
    if precip_uncertain or (forecast and forecast.get("precip_uncertain") and not what_if["precip"]):
        st.caption("The chance of rain is in the middle, so both histories are shown rather than picking one.")
    bin_cols = st.columns(len(psecs))
    for col, sec in zip(bin_cols, psecs):
        with col:
            st.markdown(f"**{logic.PRECIP_NAME.get(sec['bin'], sec['bin'])}** ({sec['title']})")
            for team in (view["focal"], view["opponent"]):
                ui.team_block([r for r in sec["rows"] if r.team == team], team, f"p{sec['bin']}")
            ui.pooled_reference([r for r in sec["rows"] if r.team == logic.POOLED], pn)
    if any(s["bin"] == "steady" for s in psecs):
        st.caption("Steady rain is rare, so it is capped at **Leans** and kept separate from light rain.")

# ---- expanders --------------------------------------------------------------------------------
all_rows = [r for s in view["sections"] for r in s["rows"]]
if all_rows:
    with st.expander("90% intervals (the ranges behind the labels)"):
        st.dataframe(ui.intervals_table(all_rows, pn), hide_index=True, width="stretch")
        st.caption("An interval that stays on one side of zero is what 'Clear signal' and 'Leans' are built from; "
                   "a range that crosses zero means the data can't tell the direction.")

if status not in ("played", "indoor"):
    tbin = (view.get("conditions") or {}).get("temp")
    with st.expander("Temperature (context only): results differ by team"):
        st.caption("Temperature is never used in the takeaway. Early-season games are warm and later ones cold, so temperature results "
                   "largely reflect the schedule; treat them as background, not as a forecast of how the game will go.")
        t_bins = [b for b in ([tbin] if tbin else []) + ["cold", "warm_hot"] if b]
        t_bins = list(dict.fromkeys(t_bins))
        for bv in t_bins:
            st.markdown(f"**{bv.replace('_', '/').title()}** (vs. all other games)")
            cc = st.columns(2)
            for col, team in zip(cc, (focal, game["opponent"])):
                with col:
                    st.markdown(f"##### {team}")
                    if team in teams["deferred"] or not stats.loaded(team):
                        st.info("data not loaded yet")
                        continue
                    for m in ("pass_eff", "points"):
                        r = stats.result(team, "temp", bv, m, scope)
                        st.markdown(f"{r.metric_name}: **{r.text()}** (n={r.n}) {ui.chip(r.label)}", unsafe_allow_html=True)
    with st.expander("Cold games: why the raw numbers look worse"):
        st.markdown("The card shows the **controlled** number for cold games. Here is the **raw** version beside it. "
                    "Raw cold-game results look worse because cold games are late-season games, usually against tougher opponents.")
        rows = []
        for team in (focal, game["opponent"], logic.POOLED):
            for m in ("pass_eff", "points"):
                r = stats.result(team, "temp", "cold", m, scope)
                if r.status == "ok":
                    dec = logic.METRIC_INFO[m][2]
                    rows.append({"Team": f"All {pn} loaded teams" if team == logic.POOLED else team, "Metric": r.metric_name, "n": r.n,
                                 "Raw (vs. other games)": None if r.raw_value is None else round(r.raw_value, dec),
                                 "Controlled (vs. other games)": None if r.value is None else round(r.value, dec)})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch") if rows else st.caption("No cold-game history to show.")
    hist = data.forecast_history(fconn, gid)
    if not hist.empty:
        with st.expander("Forecast history (every pull is kept)"):
            show = hist[["snapshot_utc", "source", "status", "wind_sust", "wind_gust", "precip_prob", "precip_amt", "temp_f", "wind_bin", "precip_bin", "temp_bin"]]
            st.dataframe(show.sort_values("snapshot_utc", ascending=False), hide_index=True, width="stretch")

# ---- season so far ----------------------------------------------------------------------------
st.markdown("### Season so far")
rows = []
for r in sched.itertuples():
    f = data.latest_forecast(fconn, int(r.game_id)) if not r.completed else None
    if r.completed:
        pts = (r.home_points, r.away_points) if r.home_team == focal else (r.away_points, r.home_points)
        result = f"{'W' if pts[0] > pts[1] else 'L'} {int(pts[0])}–{int(pts[1])}"
        weather = (", ".join(logic.condition_badges(r.wind_bin, r.precip_bin, r.temp_bin)) + f" (observed: {r.temp_f_mean:.0f}°F, wind {r.wind_sust_max:.0f} mph)") if r.weather_ok == 1 else ("indoor" if r.dome == 1 else "—")
    else:
        result = "upcoming"
        if r.dome == 1:
            weather = "indoor, weather not a factor"
        elif not f:
            weather = "no forecast yet"
        elif f["status"] == "ok":
            weather = "forecast: " + ", ".join(logic.condition_badges(f["wind_bin"], f["precip_bin"], f["temp_bin"], f["precip_prob"]))
        elif f["status"] == "beyond_horizon":
            weather = "beyond the forecast horizon"
        else:
            weather = f["status"].replace("_", " ")
    rows.append({"Wk": int(r.week), "Date": tz_local(r.kickoff_utc, "%b %d") if r.kickoff_utc else "TBD", "Opponent": r.opponent,
                 "Site": r.site, "Result": result, "Weather": weather})
st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=36 * (len(rows) + 1) + 3)

# ---- share / export ---------------------------------------------------------------------------
if view["sections"] or status in ("played", "indoor"):
    st.markdown("### Share this view")
    text = logic.blurb(view)
    st.caption("Copy-as-text (use the copy icon at the top right of the box):")
    st.code(text, language=None)
    c1, c2 = st.columns(2)
    c1.download_button("Download CSV", logic.csv_bytes(logic.view_rows(view)), file_name=f"gameday_{gid}.csv", mime="text/csv",
                       disabled=not view["sections"])
    if view["sections"]:
        c2.download_button("Download PNG for TV graphics (1920×1080)", export.render_card_png(view), file_name=f"gameday_{gid}.png", mime="image/png")
    st.caption("To share exactly this view, copy the page address: your game and What-If choices are part of the link.")

ui.footer(res)
