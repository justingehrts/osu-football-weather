"""Streamlit building blocks shared by all pages. Presentation only: no statistics here."""
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # so `lib.*` imports work from pages/
from lib import charts, colors, config, data, logic, plain      # noqa: E402

CHIP_CLASS = {logic.CLEAR: "clear", logic.LEANS: "leans", logic.NONE: "none", logic.FEW: "few", logic.CONTEXT: "ctx"}
CSS = """
<style>
.block-container {max-width: 1100px; padding-top: 1.6rem;}
.chip {display:inline-block; padding:1px 9px; border-radius:11px; font-size:0.78rem; font-weight:600; white-space:nowrap;}
.chip-clear {background:#0b4f8a; color:#fff;} .chip-leans {background:#f2b134; color:#222;}
.chip-none {background:#d9dde3; color:#222;} .chip-few {background:#f0f1f3; color:#555; border:1px solid #cfd3d9;}
.chip-ctx {background:#e6dcf2; color:#3b2a57;}
.badge {display:inline-block; padding:4px 12px; margin:0 6px 6px 0; border-radius:14px; background:#1d2733; color:#fff; font-weight:600;}
.small {font-size:0.85rem; color:#5b6470;}
.team-chip {display:inline-block; padding:.15rem .7rem; border-radius:.45rem; font-weight:700; font-size:1.15rem; line-height:1.5;}
.matchup {font-size:1.7rem; margin:.2rem 0 .4rem 0;} .matchup .team-chip {font-size:1.7rem; padding:.1rem .8rem;}
.matchup .at {margin:0 .5rem; font-weight:600; color:#5b6470;}
.anecdote {border:1px dashed #8a929c; border-radius:.4rem; padding:.35rem .6rem; margin:0 0 .55rem 0;}
.num {font-size:1.25rem; font-weight:700;}
.verdict {font-size:.9rem; font-weight:600; color:#5b6470;}
.gt {font-size:.85rem; color:#3b4652; margin-top:.1rem;}
.onair {border-left:4px solid #0b4f8a; background:#f3f6fa; padding:.6rem .9rem; border-radius:.3rem; font-size:1.08rem; line-height:1.5; color:#16202b;}
</style>
"""


def setup(title, icon="🌬️"):
    st.set_page_config(page_title=title, page_icon=icon, layout="wide", initial_sidebar_state="collapsed")
    st.markdown(CSS, unsafe_allow_html=True)


def chip(label):
    return f'<span class="chip chip-{CHIP_CLASS.get(label, "few")}">{label}</span>'


def badges(items):
    return "".join(f'<span class="badge">{b}</span>' for b in items)


@st.cache_resource(show_spinner=False)
def _resources(db_key, fdb_key):
    bins, teams = config.load_bins(), config.load_teams()
    conn = data.connect_ro(config.DB_PATH)
    fconn = data.connect_ro(config.FORECAST_DB_PATH)
    stats = logic.Stats(data.load_splits(conn), data.load_tiers(conn), bins, teams) if conn else None
    return {"conn": conn, "fconn": fconn, "bins": bins, "teams": teams, "stats": stats}


def resources():
    """Open the (read-only) databases once; reload automatically when the files change."""
    def key(p):
        return (str(p), os.path.getmtime(p)) if os.path.exists(p) else (str(p), 0)
    res = _resources(key(config.DB_PATH), key(config.FORECAST_DB_PATH))
    if res["conn"] is None:
        st.error("The database hasn't been built yet (data/osu_weather.db is missing).")
        st.stop()
    return res


def qp(name, default=None):
    v = st.query_params.get(name, default)
    return v if v != "" else default


def set_qp(**kv):
    """Keep the address bar in step with the controls so any view can be shared by copying the link."""
    for k, v in kv.items():
        if v in (None, "", False):
            if k in st.query_params:
                del st.query_params[k]
        elif st.query_params.get(k) != str(v):
            st.query_params[k] = str(v)


# --------------------------------------------------------------------------- evidence drawer
def games_frame(games):
    """Underlying games, laid out for reading."""
    if games.empty:
        return games
    d = pd.DataFrame({
        "Date": pd.to_datetime(games.kickoff_utc, utc=True).dt.tz_convert("America/New_York").dt.strftime("%b %d, %Y"),
        "Opponent": games.opponent, "Site": [("neutral" if n else h) for n, h in zip(games.neutral_site, games.home_away)],
        "Venue": games.venue,
        "Observed weather": [f"{t:.0f}°F, wind {w:.0f} mph" + (f" (gusts {g:.0f})" if pd.notna(g) and g > w + 1 else "") + f", rain {p:.2f} in" + (", snow" if s else "")
                             for t, w, g, p, s in zip(games.temp_f_mean, games.wind_sust_max, games.wind_gust_max, games.precip_in_total, games.snow_flag)],
        "Score (team–opp)": [f"{int(a)}–{int(b)}" if pd.notna(a) and pd.notna(b) else "" for a, b in zip(games.points, games.points_allowed)],
        "Pass yds/att": [round(y / a, 2) if pd.notna(a) and a else None for y, a in zip(games.pass_yds, games.pass_att)],
        "Rush yds/carry": [round(y / a, 2) if pd.notna(a) and a else None for y, a in zip(games.rush_yds, games.rush_att)],
        "Off. PPA": games.ppa_off.round(3),
        "Opp SP+": games.opp_sp.round(1),
    })
    return d


@st.dialog("The games behind this number", width="large")
def evidence_dialog(team, bin_type, bin_value, scope):
    res = resources()
    games = data.evidence_games(res["conn"], res["bins"], team, bin_type, bin_value, exclude_covid=(scope == "ex2020"))
    name = logic.PRECIP_NAME.get(bin_value) if bin_type == "precip" else logic.WIND_NAME.get(bin_value, bin_value)
    st.markdown(f"**{team}**, {name.lower()} games ({len(games)}), newest first.")
    st.caption("Every number for this condition is computed from exactly these games (games against opponents "
               "without an SP+ rating, e.g. FCS teams, are listed here but left out of the adjusted/controlled numbers).")
    st.dataframe(games_frame(games), width="stretch", hide_index=True)


def result_row(r):
    """One metric as ONE compact block, so it stays short on a phone:
    stat name / the change in words (+ better/worse where lower is good) / evidence chip, n and the adjusted number /
    a small line putting it in game-sized terms next to what the team usually does."""
    if r.status != "ok":
        body = '<span class="small">data not loaded yet</span>'
    else:
        said, verdict = r.extra.get("words"), r.extra.get("verdict")
        top = (f'<span class="num">{said}</span>' + (f' <span class="verdict">({verdict})</span>' if verdict else "")
               if said else f'<span class="num">{r.text()}</span>')
        exact = f' &middot; {r.text()}' if said else ""
        body = f'{top}<br>{chip(r.label)} &nbsp;<span class="small">n={r.n}{exact}</span>'
        if r.extra.get("game_terms"):
            body += f'<div class="gt">{r.extra["game_terms"]}</div>'
    st.markdown(f'<div style="margin:0 0 .7rem 0"><div class="small">{r.metric_name}</div>{body}</div>', unsafe_allow_html=True)


def anecdote_row(r, averages):
    """A thin row revealed by 'Show anyway': the plain average of those games, clearly NOT a finding."""
    text = logic.anecdote_text(r.metric, (averages or {}).get(r.metric))
    st.markdown(f'<div class="anecdote"><div class="small">{r.metric_name}</div>{text or "no games to average"}<br>'
                f'{chip(r.label)} <span class="small">anecdote, not a finding &middot; plain average, no adjustments</span></div>',
                unsafe_allow_html=True)


def team_block(rows, title, key_prefix):
    """A team's rows for one condition, plus the button that opens the games behind them.

    Rows labelled 'Not enough games' get a per-block 'Show anyway' switch. It starts OFF for everyone (it is
    session-only: not in the page address, so a shared link never carries it) and reveals the plain average of the
    few games instead of a model number. The takeaway, blurb, CSV and PNG never use revealed numbers."""
    st.markdown(f'<div style="margin:.3rem 0 .5rem 0">{colors.chip_html(title)}</div>', unsafe_allow_html=True)
    if rows and rows[0].status == "not_loaded":
        st.info("data not loaded yet")
        return
    thin = [r for r in rows if r.status == "ok" and r.label == logic.FEW and r.n > 0]
    show, averages = False, None
    if thin:
        r0 = thin[0]
        show = st.toggle("Show anyway", key=f"anyway-{key_prefix}-{r0.team}-{r0.bin_type}-{r0.bin_value}",
                         help=f"{len(thin)} of these numbers rest on too few games to trust. This shows the plain average "
                              "of those few games, with no adjustments, and clearly marks it as an anecdote.")
        if show:
            res = resources()
            averages = data.raw_block_averages(res["conn"], res["bins"], r0.team, r0.bin_type, r0.bin_value,
                                               exclude_covid=(st.session_state.get("scope") == "ex2020"))
    for r in rows:
        if show and r in thin:
            anecdote_row(r, averages)
        else:
            result_row(r)
    r0 = next((r for r in rows if r.status == "ok"), None)
    if r0 is not None and r0.n and r0.team != logic.POOLED:
        if st.button(f"See the {r0.n} games behind these numbers", key=f"{key_prefix}-{r0.team}-{r0.bin_type}-{r0.bin_value}",
                     type="tertiary"):
            evidence_dialog(r0.team, r0.bin_type, r0.bin_value, st.session_state.get("scope", "all"))


def matchup_header(view):
    """'Ohio State at USC' with each name in its school colors."""
    st.markdown(f'<div class="matchup">{colors.chip_html(view["away_team"])}<span class="at">{view["joiner"]}</span>'
                f'{colors.chip_html(view["home_team"])}</div>', unsafe_allow_html=True)


def pooled_reference(rows, pooled_n):
    with st.container(border=True):
        st.markdown(f"**Reference: all {pooled_n} loaded teams**" if pooled_n else "**Reference**")
        for r in rows:
            said = r.extra.get("words")
            v = f" ({r.extra['verdict']})" if r.extra.get("verdict") else ""
            num = f"**{said}**{v} &nbsp;(n={r.n} &middot; {r.text()})" if said else f"**{r.text()}** &nbsp;(n={r.n})"
            st.markdown(f"{r.metric_name}: {num} {chip(r.label)}", unsafe_allow_html=True)


def condition_chart(rows, view, metrics):
    """The dot-and-range picture for one condition: right is always better, the dashed line is 'no difference'."""
    df, missing = plain.chart_frame(rows, view["focal"], view["opponent"], view["pooled_n"], metrics)
    drawn = charts.condition_chart(df)
    if drawn:
        legend = " ".join(chip(l) for l in (logic.CLEAR, logic.LEANS, logic.NONE) if l in set(df.label))
        st.markdown(f'<div class="small">Dot = the change vs. that team\'s other games &middot; bar = how uncertain it is '
                    f'&middot; dashed line = no difference &middot; <b>right is always better</b>, even for points allowed '
                    f'&nbsp;{legend}</div><div style="height:.4rem"></div>', unsafe_allow_html=True)
        # side by side on a wide screen; Streamlit stacks columns on a phone
        for col, ch in zip(st.columns(len(drawn)), drawn):
            with col:
                st.altair_chart(ch, width="stretch")
        st.caption("A bar that crosses the dashed line means the data can't tell the direction.")
    if missing:
        st.caption("Not drawn: " + "; ".join(missing) + ".")


def on_air_box(text):
    st.markdown("**On-air line** <span class='small'>(hedges match the evidence labels)</span>", unsafe_allow_html=True)
    st.markdown(f'<div class="onair">{text}</div>', unsafe_allow_html=True)
    with st.expander("Copy the on-air line"):
        st.code(text, language=None, wrap_lines=True)


def intervals_table(rows, pooled_n):
    out = []
    for r in rows:
        if r.status != "ok" or r.lo is None:
            continue
        team = f"All {pooled_n} loaded teams" if r.team == logic.POOLED else r.team
        dec = logic.METRIC_INFO[r.metric][2]
        out.append({"Team": team, "Metric": r.metric_name, "Estimate": round(r.value, dec) if r.value is not None else None,
                    "90% interval": f"{r.lo:+.{dec}f} to {r.hi:+.{dec}f}", "n": r.n, "Evidence": r.label})
    return pd.DataFrame(out)


def footer(res):
    """How fresh is this? (History through the last finished game; time of the latest forecast pull.)"""
    h, f = data.history_through(res["conn"]), data.last_forecast_time(res["fconn"])
    fmt = lambda x: pd.to_datetime(x, utc=True).tz_convert("America/New_York")  # noqa: E731
    bits = []
    if h:
        bits.append(f"History through games played {fmt(h).strftime('%b %d, %Y')}")
    if f:
        bits.append(f"latest forecast pulled {fmt(f).strftime('%b %d, %-I:%M %p ET')}")
    st.divider()
    st.caption(" · ".join(bits + ["Exploratory history, not a prediction. See the Methodology page."]))
