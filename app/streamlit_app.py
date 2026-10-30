"""Gameday Card: the landing page. Opens on the next Ohio State game with the forecast prefilled."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd                                    # noqa: E402
import streamlit as st                                  # noqa: E402

from lib import charts, data, export, logic, plain, timefmt, ui  # noqa: E402

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
    """Eastern time. Used for when a forecast was PULLED (not a game time); game times use timefmt in local time."""
    return pd.to_datetime(ts, utc=True).tz_convert("America/New_York").strftime(fmt)


st.title("Gameday Card")
sched = data.schedule(conn, focal, teams["season"])
if sched.empty:
    st.warning(f"No {teams['season']} schedule is loaded yet.")
    st.stop()

# ---- which game -------------------------------------------------------------------------------
default_game = data.next_game(sched)
labels = {int(r.game_id): f"Wk {int(r.week)} · {'at' if r.site == 'away' else 'vs.'} {r.opponent} · "
          f"{timefmt.local_day(r.kickoff_utc, r.tz) if r.kickoff_utc else 'TBD'}"
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
    side_by_side = st.checkbox("Show both dry and wet histories", value=ui.qp("sbs") == "1",
                               help="Turned on automatically when the chance of rain is in the middle (30-70%).")
    scope_all = st.checkbox("Include the 2020 season (COVID-altered)", value=ui.qp("y2020", "1") != "0")
what_if = {"wind": WIND_OPTS[wind_pick], "precip": PRECIP_OPTS[precip_pick], "temp": TEMP_OPTS[temp_pick]}
scope = "all" if scope_all else "ex2020"
st.session_state["scope"] = scope
ui.set_qp(game=gid if gid != int(default_game["game_id"]) else None, wind=what_if["wind"], precip=what_if["precip"],
          temp=what_if["temp"], sbs="1" if side_by_side else None, y2020=None if scope_all else "0")

forecast = data.latest_forecast(fconn, gid)


def typicals_for(game, forecast):
    """Each shown team's PLAIN averages in its other games (for the game-sized translations). Only the bins the card
    will show, only loaded teams."""
    if game["completed"] or game.get("dome") == 1:
        return {}
    cond = logic.conditions_from(forecast, what_if)
    shown = ([("wind", cond["wind"])] if cond["wind"] else []) + [("precip", b) for b in logic.precip_bins_to_show(cond["precip"], side_by_side)]
    out = {}
    for team in (focal, game["opponent"]):
        if team in teams["deferred"] or not stats.loaded(team):
            continue
        for dim, bv in shown:
            out[(team, dim, bv)] = data.raw_block_averages(conn, bins, team, dim, bv, exclude_covid=(scope == "ex2020"))
    return out


view = logic.build_gameday_view(stats, bins, teams, game, forecast, what_if, side_by_side, scope,
                                typicals=typicals_for(game, forecast), first_season=teams.get("first_season"))
head_m, hood_m, play_m = view.get("headline_metrics", []), view.get("hood_metrics", []), view.get("playcall_metrics", [])
precip_uncertain = view.get("conditions", {}).get("precip") == "uncertain"

# ---- header, forecast, takeaway ---------------------------------------------------------------
ui.matchup_header(view)
meta = " · ".join(x for x in [view.get("venue"), timefmt.game_time(game["kickoff_utc"], game.get("tz")) if game.get("kickoff_utc") and not game.get("kickoff_tbd") else "kickoff time TBD"] if x)
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
            _, near = plain.bin_distances(forecast, bins)
            if near:
                st.warning("**Borderline forecast:** " + "; ".join(near) + ". A small change in the forecast could change "
                           "which history applies; see *Forecast details* below.", icon="⚠️")
    else:
        st.warning(view["takeaway"].split(" Choose conditions")[0])
    st.info(view["takeaway"])
    if view.get("on_air") and view["sections"]:
        ui.on_air_box(view["on_air"])
    if view["sections"]:
        st.caption("All numbers below compare a team's games in these conditions with its **other** games (for example, windy vs. not windy), "
                   "with opponent strength, time of season and home/away held fixed. Exploratory: not a prediction.")


def playcall_block(sec, prefix):
    """How each team CALLS plays in this condition (pass share, pace). Not better or worse, so its own neutral block."""
    if not play_m or not any(r.metric in play_m for r in sec["rows"]):
        return
    st.markdown("##### Playcalling: how they play, not how well")
    ui.condition_chart(sec["rows"], view, play_m, neutral=True)
    cols = st.columns(2)
    for col, team in zip(cols, (view["focal"], view["opponent"])):
        with col:
            ui.team_block([r for r in sec["rows"] if r.team == team and r.metric in play_m], team, prefix)
    ui.pooled_reference([r for r in sec["rows"] if r.team == logic.POOLED and r.metric in play_m], pn)


# ---- the comparison: wind first, then rain ----------------------------------------------------
pn = view["pooled_n"]
for sec in [s for s in view["sections"] if s["dim"] == "wind"]:
    st.markdown(f"### Wind: {sec['title']}")
    ui.condition_chart(sec["rows"], view, head_m)
    cols = st.columns(2)
    for col, team in zip(cols, (view["focal"], view["opponent"])):
        with col:
            ui.team_block([r for r in sec["rows"] if r.team == team and r.metric in head_m], team, "w")
    ui.pooled_reference([r for r in sec["rows"] if r.team == logic.POOLED and r.metric in head_m], pn)
    playcall_block(sec, "wpc")

psecs = [s for s in view["sections"] if s["dim"] == "precip"]
if psecs:
    st.markdown("### Precipitation" + (": " + " and ".join(logic.PRECIP_NAME.get(x["bin"], x["bin"]) for x in psecs).replace("Any rain (light + steady)", "any rain") if len(psecs) > 1 else ""))
    if precip_uncertain or (forecast and forecast.get("precip_uncertain") and not what_if["precip"]):
        st.caption("The chance of rain is in the middle, so both histories are shown rather than picking one.")
    # Same orientation as the wind section: the two teams are always left (focal) and right (opponent). When there is
    # more than one rain scenario, the scenarios are stacked top to bottom, each with its own left-right comparison.
    for sec in psecs:
        st.markdown(f"#### {logic.PRECIP_NAME.get(sec['bin'], sec['bin'])} ({sec['title']})")
        ui.condition_chart(sec["rows"], view, head_m)
        cols = st.columns(2)
        for col, team in zip(cols, (view["focal"], view["opponent"])):
            with col:
                ui.team_block([r for r in sec["rows"] if r.team == team and r.metric in head_m], team, f"p{sec['bin']}")
        ui.pooled_reference([r for r in sec["rows"] if r.team == logic.POOLED and r.metric in head_m], pn)
        playcall_block(sec, f"p{sec['bin']}pc")
    if any(s["bin"] == "steady" for s in psecs):
        st.caption("Steady rain is rare, so it is capped at **Leans** and kept separate from light rain.")

# ---- expanders --------------------------------------------------------------------------------
all_rows = [r for s in view["sections"] for r in s["rows"]]
if all_rows and hood_m:
    with st.expander("Under the hood: offensive PPA (for the stats crowd)"):
        st.markdown("**PPA** (predicted points added) is the change in expected points on each offensive play, from down, "
                    "distance and field position. It rates every snap, not just the scoring ones, so it is a steadier "
                    "measure of an offense than points. The pipeline already uses it: the passing and scoring evidence "
                    "labels each check PPA alongside yards per pass or points. It is kept off the main card because "
                    "it doesn't translate into an on-air sentence.")
        tbl = []
        for sec in view["sections"]:
            for r in sec["rows"]:
                if r.metric not in hood_m:
                    continue
                who = f"All {pn} loaded teams" if r.team == logic.POOLED else r.team
                if r.status != "ok":
                    tbl.append({"Condition": sec["title"], "Team": who, "Change": "data not loaded yet"})
                    continue
                tbl.append({"Condition": sec["title"], "Team": who, "Change": r.extra.get("words") or r.text(),
                            "Adjusted": r.text(), "n": r.n, "Evidence": r.label})
        st.markdown("**Offense: expected points per play** (PPA), vs. all other games")
        st.dataframe(pd.DataFrame(tbl), hide_index=True, width="stretch")
        st.caption("Same yardstick as the card: games in this condition vs. that team's other games, with opponent "
                   "strength, month and home/away held fixed. A typical offense averages roughly 0.1-0.3 PPA per play, "
                   "so a change of 0.05 is meaningful.")
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
        with st.expander("Forecast details: bin lines, trend and hour by hour", expanded=False):
            dist, _ = plain.bin_distances(forecast, bins)
            if dist:
                st.markdown("**How close is the forecast to the lines that change the card?**")
                st.dataframe(pd.DataFrame(dist), hide_index=True, width="stretch")
                st.caption("Borderline = within the margins set in config/bins.yaml (forecast.borderline). The history "
                           "is binned on the same lines, so a forecast near a line could fall into either history.")
            trend_text, ok_hist = plain.forecast_trend(hist)
            st.markdown("**How the forecast has moved**")
            if trend_text:
                st.markdown(trend_text)
                tc = charts.trend_chart(ok_hist)
                if tc is not None:
                    st.altair_chart(tc, width="stretch")
            else:
                st.caption("Only one usable forecast pull so far; the trend appears after the next one.")
            st.markdown("**Hour by hour, kickoff to +3.5 h** (latest pull, in the stadium's local time)")
            hours = []
            if forecast and forecast.get("detail"):
                try:
                    hours = (json.loads(forecast["detail"]) or {}).get("hours") or []
                except (TypeError, ValueError):
                    hours = []
            hcs = charts.hourly_charts(hours, bins, game.get("tz"))
            if hcs:
                for hc in hcs:
                    st.altair_chart(hc, width="stretch")
                st.caption("Top: bars = sustained wind, triangles = gusts, dashed red lines = where 'windy' starts. Bottom: chance of rain "
                           "each hour. The card uses the strongest wind and the total rain in the window.")
            else:
                st.caption("No hour-by-hour values in this pull yet (pulls made before this feature only kept the window summary).")
            st.markdown("**Every pull (kept, never overwritten)**")
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
    rows.append({"Wk": int(r.week), "Date": timefmt.local_day(r.kickoff_utc, r.tz) if r.kickoff_utc else "TBD", "Opponent": r.opponent,
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
