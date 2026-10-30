"""Team Explorer: pick any team and condition and see its splits."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd                         # noqa: E402
import streamlit as st                      # noqa: E402

from lib import logic, ui                   # noqa: E402

ui.setup("Team Explorer", "🔎")
res = ui.resources()
bins, teams, stats = res["bins"], res["teams"], res["stats"]
focal = teams["focal"]

st.title("Team Explorer")
st.caption("Pick a team and a condition. Numbers compare the team's games in that condition with its **other** games "
           "(e.g. windy vs. not windy), controlled for opponent strength, time of season and home/away. Exploratory.")

options = teams["tracked"]
labels = {t: (f"{t} (data not loaded yet)" if t in teams["deferred"] else t) for t in options}
want = ui.qp("team", focal)
team = st.selectbox("Team", options, index=options.index(want) if want in options else options.index(focal), format_func=labels.get)

WIND = {"Any": None, "Calm": "calm", "Moderate wind": "moderate", "Windy": "windy"}
PRECIP = {"Any": None, "Dry": "none", "Light rain": "light", "Steady rain": "steady", "Any rain (light + steady)": "wet"}
TEMP = {"Any": None, "Cold": "cold", "Mild": "mild", "Warm": "warm", "Hot": "hot", "Warm or hot": "warm_hot"}
c1, c2, c3 = st.columns(3)
wind = WIND[c1.selectbox("Wind", list(WIND), index=list(WIND.values()).index(ui.qp("wind")) if ui.qp("wind") in WIND.values() else 0)]
precip = PRECIP[c2.selectbox("Precipitation", list(PRECIP), index=list(PRECIP.values()).index(ui.qp("precip")) if ui.qp("precip") in PRECIP.values() else 0)]
temp = TEMP[c3.selectbox("Temperature (context only)", list(TEMP), index=list(TEMP.values()).index(ui.qp("temp")) if ui.qp("temp") in TEMP.values() else 0)]
scope_all = st.checkbox("Include the 2020 season (COVID-altered)", value=ui.qp("y2020", "1") != "0")
scope = "all" if scope_all else "ex2020"
st.session_state["scope"] = scope
ui.set_qp(team=None if team == focal else team, wind=wind, precip=precip, temp=temp, y2020=None if scope_all else "0")

if team in teams["deferred"] or not stats.loaded(team):
    st.info(f"**{team}: data not loaded yet.** This team's history hasn't been loaded; the rest of the app is unaffected.")
    st.stop()

METRICS = ["pass_eff", "points", "points_allowed", "ppa_off", "rush_ypc", "turnovers", "pass_rate", "plays"]   # last two: playcalling (neutral)
pn = stats.pooled_n


def table(bt, bv):
    rows = []
    for m in METRICS:
        r, p = stats.result(team, bt, bv, m, scope), stats.result(logic.POOLED, bt, bv, m, scope)
        rows.append({"Metric": r.metric_name, f"{team}": r.text(), "n": r.n, "Evidence": r.label,
                     f"All {pn} loaded teams": p.text(), "n (all teams)": p.n, "Evidence (all teams)": p.label})
    return pd.DataFrame(rows)


def show(bt, bv, title):
    st.markdown(f"#### {title}")
    st.dataframe(table(bt, bv), hide_index=True, width="stretch")
    key = f"ev-{team}-{bt}-{bv}"
    n = stats.result(team, bt, bv, "points", scope).n
    if n and st.button(f"Show the {n} games behind these numbers", key=key):
        ui.evidence_dialog(team, bt, bv, scope)
    with st.expander(f"90% intervals and the other yardstick: {title}"):
        iv = ui.intervals_table([stats.result(team, bt, bv, m, scope) for m in METRICS] + [stats.result(logic.POOLED, bt, bv, m, scope) for m in METRICS], pn)
        st.dataframe(iv, hide_index=True, width="stretch")
        st.markdown("**The other yardstick** (vs. the team's overall average, which includes these games) - shown here for reference only:")
        other = []
        for m in METRICS:
            try:
                row = stats.s.loc[(team, scope, bt, bv, m)]
                dec = logic.METRIC_INFO[m][2]
                other.append({"Metric": logic.METRIC_INFO[m][0], "vs. team overall average (controlled)": None if pd.isna(row["ctl_delta"]) else round(row["ctl_delta"], dec), "n": int(row["n"])})
            except KeyError:
                continue
        st.dataframe(pd.DataFrame(other), hide_index=True, width="stretch")


shown = False
if wind:
    show("wind", wind, f"Wind: {logic.VS_NOT[wind]}")
    shown = True
if precip:
    show("precip", precip, f"Precipitation: {logic.VS_NOT[precip]}")
    shown = True
if temp:
    with st.expander("Temperature (context only): results differ by team", expanded=True):
        st.caption("Temperature mostly reflects the schedule (warm = early season, cold = late season), so it is context, not evidence.")
        show("temp", temp, f"Temperature: {temp.replace('_', '/')} vs. other games")
        if temp == "cold":
            st.markdown("**Cold: raw vs. controlled.** Raw cold-game results look worse because cold games are late-season games against tougher opponents.")
            raw = [{"Metric": logic.METRIC_INFO[m][0], "Raw (vs. other games)": stats.result(team, "temp", "cold", m, scope).raw_value,
                    "Controlled (vs. other games)": stats.result(team, "temp", "cold", m, scope).value} for m in ("pass_eff", "points")]
            st.dataframe(pd.DataFrame(raw), hide_index=True, width="stretch")
    shown = True
if not shown:
    st.info("Choose a wind, precipitation or temperature condition above. Wind is the one with the most evidence.")
else:
    from lib import data
    rows = []
    for bt, bv in (("wind", wind), ("precip", precip), ("temp", temp)):
        if bv:
            for m in METRICS:
                r = stats.result(team, bt, bv, m, scope)
                rows.append({"team": team, "condition": f"{bt}: {bv}", "metric": r.metric_name, "vs_all_other_games": None if r.value is None else round(r.value, 3),
                             "unit": logic.METRIC_INFO[m][1], "n_games": r.n, "evidence": r.label,
                             "interval_90_lo": None if r.lo is None else round(r.lo, 3), "interval_90_hi": None if r.hi is None else round(r.hi, 3)})
    st.download_button("Download CSV of this view", logic.csv_bytes(rows), file_name=f"explorer_{team.replace(' ', '_')}.csv", mime="text/csv")

ui.footer(res)
