"""Step 5: milestone-3 reports.

  reports/milestone3_scaled_splits.md   the readable report (tiers, pooled lines, summaries)
  reports/milestone3_detail.md          every team x metric x bin with full intervals
"""
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from .common import COUNTER_PATH, DATA_DIR, REPORT_DIR, connect, deferred_teams, load_bins, load_yaml, tracked_teams
from .compute_splits import POOLED, bin_masks, usable_games
from .weather_bins import confidence

METRICS = [("pass_eff", "Pass yds/att", 2, "higher = better"),
           ("rush_ypc", "Rush yds/carry", 2, "higher = better"),
           ("points", "Points scored", 1, "higher = better"),
           ("points_allowed", "Points allowed (defense)", 1, "LOWER = better"),
           ("turnovers", "Turnovers", 2, "LOWER = better"),
           ("ppa_off", "Offensive PPA/play", 3, "higher = better")]
KEY_METRICS = ["pass_eff", "points", "points_allowed", "ppa_off"]
DEC = {k: d for k, _, d, _ in METRICS}
LABEL = {k: l for k, l, _, _ in METRICS}
ORDER = {"wind": ["calm", "moderate", "windy"],
         "precip": ["none", "light", "steady", "wet"],
         "temp": ["cold", "mild", "warm", "hot", "warm_hot"]}
TIER_SHORT = {"clear": "**CLEAR**", "leans": "leans", "no_clear_effect": "none", "insufficient": "n/a",
              "context_only": "context"}
MONTH_NAMES = {8: "Aug–Sep", 9: "Aug–Sep", 10: "Oct", 11: "Nov", 12: "Dec–Jan", 1: "Dec–Jan"}
STAR = " \\*"
# (delta, lo, hi, sig) column names for each estimate on each yardstick
AVG, REST = "avg", "rest"
COLS = {AVG: {"raw": ("delta", "delta_lo", "delta_hi", "sig_raw"),
              "adj": ("adj_delta", "adj_lo", "adj_hi", "sig_adj"),
              "ctl": ("ctl_delta", "ctl_lo", "ctl_hi", "sig_ctl")},
        REST: {"raw": ("rest_delta", "rest_lo", "rest_hi", "sig_rest"),
               "adj": ("adj_rest", "adj_rest_lo", "adj_rest_hi", "sig_adj_rest"),
               "ctl": ("ctl_rest", "ctl_rest_lo", "ctl_rest_hi", "sig_ctl_rest")}}
BASIS_TITLE = {AVG: "A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)",
               REST: "B. vs ALL OTHER GAMES (the complement: games not in the bin)"}


def name(team, n_teams=None):
    return f"Pooled ({n_teams} teams)" if team == POOLED else team


def fmt(delta, lo, hi, sig, dec, hide=False):
    if hide or delta is None or pd.isna(delta):
        return "—"
    if pd.isna(lo) or pd.isna(hi):
        return f"{delta:+.{dec}f}"
    return f"{delta:+.{dec}f} [{lo:+.{dec}f}, {hi:+.{dec}f}]" + (STAR if sig else "")


def short(delta, sig, dec, hide=False):
    if hide or delta is None or pd.isna(delta):
        return "—"
    return f"{delta:+.{dec}f}" + ("\\*" if sig else "")


def triple(r, dec, bins, basis=AVG):
    """raw / adjusted / controlled in one cell, on one yardstick."""
    c = bins["confidence"]
    if r is None or r.n < c["suppress_below_n"]:
        return "—"
    out = []
    for kind, small in (("raw", False), ("adj", r.n_adj < c["suppress_below_n"]), ("ctl", r.n_ctl < c["suppress_below_n"])):
        d, _, _, sig = COLS[basis][kind]
        out.append(short(r[d], r[sig], dec, small))
    return " / ".join(out)


def bin_label(bt, bv):
    return f"{bt}: {bv}"


# --------------------------------------------------------------------------- sections
def budget_section(calls_used, bins):
    out = ["## CFBD call budget", ""]
    if not COUNTER_PATH.exists():
        return out + ["_No call counter yet._", ""]
    st = json.loads(COUNTER_PATH.read_text())
    cap, limit = bins["cfbd"]["monthly_cap"], bins["cfbd"]["free_tier_monthly_limit"]
    run_f = DATA_DIR / "last_run.json"
    run = json.loads(run_f.read_text()) if run_f.exists() else None
    out += [f"- Month ({st['month']}) total so far: **{st['calls']}** of the {cap}-call cap "
            f"(free-tier limit {limit}); **{max(0, limit - st['calls'])}** calls remain before CFBD itself would stop us. "
            "CFBD's own `/info` count is the source of truth, and `/info` is not billed.",
            "- 437 of the month's calls were spent before the counter and raw cache existed (early un-cached runs)."]
    if run:
        out += [f"- **This session's backfill ({run['label']}): {run['calls']} calls** "
                f"(planned worst case {run['planned_total']}, threshold to ask first: {bins['cfbd']['ask_if_plan_exceeds']}). "
                f"Counter went {run['start']} → {run['end']}.", "",
                "| Endpoint | Planned (worst case) | Planned (exact, after /games) | Actually used |", "|---|---|---|---|"]
        for e in ("/games", "/games/teams", "/ppa/games", "/ratings/sp", "/venues"):
            out.append(f"| {e} | {run['plan_initial'].get(e, 0)} | {run['plan_exact'].get(e, 0)} | {run['by_endpoint'].get(e, 0)} |")
        out.append(f"| **Total** | **{run['planned_total']}** | **{run['exact_total']}** | **{run['calls']}** |")
        if run.get("notes"):
            out += ["", run["notes"]]
    out.append("")
    return out


def schedule_section(conn, bins):
    cfg = load_yaml("teams.yaml")
    q = pd.read_sql_query(
        """SELECT g.week, g.kickoff_utc, g.home_team, g.away_team, g.completed, g.home_points, g.away_points,
                  g.neutral_site, v.name venue FROM games g LEFT JOIN venues v ON v.venue_id = g.venue_id
           WHERE g.season = ? AND g.season_type = 'regular' AND (g.home_team = ? OR g.away_team = ?)
           ORDER BY g.kickoff_utc""", conn, params=(cfg["season"], cfg["focal_team"], cfg["focal_team"]))
    out = [f"## {cfg['season']} {cfg['focal_team']} schedule", ""]
    if q.empty:
        return out + ["_Schedule not loaded._", ""]
    played = int(q.completed.sum())
    out += [f"{played} played, {len(q) - played} remaining. Team list = {cfg['focal_team']} + every opponent "
            f"below ({len(tracked_teams())} teams, from `config/opponents.yaml`).", "",
            "| Wk | Date | Opponent | Site | Venue | Status |", "|---|---|---|---|---|---|"]
    for _, r in q.iterrows():
        home = r.home_team == cfg["focal_team"]
        opp = r.away_team if home else r.home_team
        day = (pd.Timestamp(r.kickoff_utc) - pd.Timedelta(hours=6)).strftime("%b %d") if r.kickoff_utc else "TBD"
        if r.completed:
            f_pts, o_pts = (r.home_points, r.away_points) if home else (r.away_points, r.home_points)
            status = f"played: {'W' if f_pts > o_pts else 'L'} {int(f_pts)}-{int(o_pts)}"
        else:
            status = "**remaining**"
        site = "neutral" if r.neutral_site else ("home" if home else "away")
        opp = opp + (" _(deferred)_" if opp in set(deferred_teams()) else "")
        out.append(f"| {int(r.week)} | {day} | {opp} | {site} | {r.venue or ''} | {status} |")
    return out + [""]


def venue_section(conn, bins):
    since = bins["report"]["new_venues_since"]
    v = pd.read_sql_query("""SELECT v.venue_id, v.name, v.dome, v.nearest_station, v.station_dist_mi, v.station_far,
                                    v.notes, v.first_seen,
                                    (SELECT COUNT(*) FROM games g WHERE g.venue_id = v.venue_id AND g.neutral_site = 1) neutral_games
                             FROM venues v""", conn)
    v["new"] = v.first_seen.fillna("") >= since
    v["abroad"] = v.notes.fillna("").str.contains("outside lower 48")
    out = ["## Venues: domes, far stations, neutral sites, non-US", "",
           f"{len(v)} venues in the table; {int(v.new.sum())} are NEW since {since} (marked **NEW**). "
           f"Far = nearest ASOS more than {bins['quality']['far_station_miles']} mi away.", ""]
    for title, mask in (("Domes (excluded from weather splits)", v.dome == 1),
                        (f"Far stations (> {bins['quality']['far_station_miles']} mi)", v.station_far == 1),
                        ("Neutral-site venues", v.neutral_games > 0),
                        ("Non-US venues (no US station used; those games are excluded)", v.abroad)):
        sub = v[mask]
        out += [f"**{title}:** " + ("none" if sub.empty else "; ".join(
            f"{r['name']}{' **NEW**' if r['new'] else ''}"
            + (f" ({r.station_dist_mi} mi to {r.nearest_station})" if title.startswith("Far") else "")
            + (f" ({int(r.neutral_games)} game(s))" if title.startswith("Neutral") else "")
            for _, r in sub.iterrows())), ""]
    return out


def rating_section(usable, bins):
    out = ["## Opponent ratings: which games have no SP+?", "",
           "SP+ covers FBS teams only. A game against an FCS opponent has no rating, so it is left out of the "
           "**Adjusted** and **Controlled** columns (it still counts in **Raw**). It is never guessed. "
           "*Raw shift* = how much the average |raw Δ| of the team's solid cells moves when the raw numbers "
           "are recomputed on rated games only -- a direct read on whether dropping those games matters.", "",
           "| Team | Usable games | No SP+ rating | Opponents without a rating | Raw shift |", "|---|---|---|---|---|"]
    for team, g in usable.groupby("team"):
        miss = g[g.opp_sp.isna()]
        shift = _raw_shift(g, bins)
        opps = ", ".join(sorted(miss.opponent.dropna().unique())[:6]) + (" …" if miss.opponent.nunique() > 6 else "")
        out.append(f"| {team} | {len(g)} | {len(miss)} | {opps or '—'} | {shift} |")
    return out + [""]


def _raw_shift(g, bins):
    from .compute_splits import CORE_METRICS as MET, game_values   # (playcalling metrics are in other units)
    masks = bin_masks(g.reset_index(drop=True), bins)
    g = g.reset_index(drop=True)
    diffs = []
    rated = g.opp_sp.notna().to_numpy()
    for m in MET:
        v = game_values(g, m)
        for k, mk in masks.items():
            a = mk & np.isfinite(v)
            b = a & rated
            if a.sum() >= bins["confidence"]["thin_below_n"] and b.sum() >= bins["confidence"]["thin_below_n"]:
                da = np.nanmean(v[a]) - np.nanmean(v)
                db = np.nanmean(v[b]) - np.nanmean(v[rated & np.isfinite(v)])
                diffs.append(abs(da - db))
    return f"{np.mean(diffs):.3f}" if diffs else "—"


def tier_section(tiers, teams, bins, k):
    out = ["## Evidence tiers (controlled model)", "",
           "Computed in the pipeline from the **controlled** intervals (opponent strength + month + home/away held fixed). "
           "Metric groups: **passing** = pass yds/att + offensive PPA; **scoring** = points scored + offensive PPA.", "",
           "- **CLEAR**: n ≥ 10 and the controlled interval excludes zero (same direction) on both metrics in the group.",
           "- **leans**: both metrics point the same way and the effect is at least "
           f"{bins['tiers']['lean_min_z']:g} standard error(s) in size, but not clear (an interval spans zero, or n is 5-9).",
           "- **none** (no_clear_effect): n ≥ 10 and nothing there.   **n/a** (insufficient): n < 5, or n 5-9 with no lean.",
           "- **context**: temperature results for a team whose controlled model finds no temperature effect in any bin -- kept "
           "for context, not as evidence.", ""]
    t = tiers[tiers.scope == "all"]
    cols = [(bt, bv) for bt, vs in ORDER.items() for bv in vs]
    for grp in ("passing", "scoring"):
        out += [f"### {grp.title()}", "", "| Team | " + " | ".join(bin_label(*c).replace(": ", ":<br>") for c in cols) + " |",
                "|---|" + "---|" * len(cols)]
        for team in teams:
            cells = []
            for bt, bv in cols:
                r = t[(t.team == team) & (t.bin_type == bt) & (t.bin_value == bv) & (t.grp == grp)]
                cells.append("n/a (0)" if r.empty else TIER_SHORT[r.iloc[0].tier] + f" ({int(r.iloc[0].n)})")
            out.append(f"| {name(team, k)} | " + " | ".join(cells) + " |")
        out.append("")
    ctx = t[(t.tier == "context_only")].groupby("team").size()
    keep = [tm for tm in teams if tm not in ctx.index and not t[(t.team == tm) & (t.bin_type == "temp")].empty]
    out += ["**Temperature:** a team's temperature tiers are kept as they are only if its controlled model has at least one "
            "CLEAR temperature cell; otherwise they are labelled context-only. Kept: "
            f"{', '.join(name(x, k) for x in keep) or 'no one'}. Context-only: "
            f"{', '.join(name(x, k) for x in ctx.index) or 'no one'}.", ""]
    return out


def control_effect_section(sp, bins):
    s = sp[(sp.scope == "all") & (sp.confidence == "solid") & sp.ctl_delta.notna() & sp.adj_delta.notna()
           & (sp.team != POOLED)]
    out = ["## How much do the controls change things?", "",
           f"Solid cells, per-team (not pooled), all seasons. *Sign flips* = adjusted and controlled point opposite ways. "
           "*Excl. 0* = intervals excluding zero (about 1 in 10 expected by luck).", "",
           "| Metric | Cells | Avg \\|raw\\| | Avg \\|adj\\| | Avg \\|ctl\\| | Adj→Ctl sign flips | Raw excl. 0 | Adj excl. 0 | Ctl excl. 0 |",
           "|---|---|---|---|---|---|---|---|---|"]
    for key, label, dec, _ in METRICS:
        m = s[s.metric == key]
        if m.empty:
            continue
        out.append(f"| {label} | {len(m)} | {m.delta.abs().mean():.{dec}f} | {m.adj_delta.abs().mean():.{dec}f} | "
                   f"{m.ctl_delta.abs().mean():.{dec}f} | {int(((m.adj_delta * m.ctl_delta) < 0).sum())} | "
                   f"{int(m.sig_raw.sum())} | {int(m.sig_adj.sum())} | {int(m.sig_ctl.sum())} |")
    return out + [""]


def pooled_section(sp, tiers, bins):
    p = sp[(sp.team == POOLED) & (sp.scope == "all")]
    if p.empty:
        return ["## Pooled reference line", "", "_Needs two or more teams._", ""]
    k = int(p.n_teams.iloc[0])
    out = [f"## Pooled reference line (all {k} loaded teams together)", "",
           f"Every team-game from the **{k} teams** in the pool, each measured against its own team's baseline. "
           "Raw / Adjusted / Controlled as defined above; brackets are 90% intervals from a bootstrap over whole games. "
           "The same numbers are shown on two yardsticks; **steady** rain is kept as its own bin next to the merged **wet** bin.", ""]
    for basis in (AVG, REST):
        out += [f"### {BASIS_TITLE[basis]}", ""]
        for bt, vals in (("wind", ["calm", "moderate", "windy"]), ("precip", ["none", "light", "steady", "wet"]),
                         ("temp", ["cold", "mild", "warm_hot"])):
            out += [f"**{bt}** (pooled across {k} teams)", "",
                    "| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |", "|---|---|---|---|---|---|"]
            for bv in vals:
                for m in KEY_METRICS:
                    r = p[(p.bin_type == bt) & (p.bin_value == bv) & (p.metric == m)]
                    if r.empty:
                        continue
                    r = r.iloc[0]
                    d = DEC[m]
                    cells = []
                    for kind in ("raw", "adj", "ctl"):
                        dn, lo, hi, sg = COLS[basis][kind]
                        n_used = {"raw": r.n, "adj": r.n_adj, "ctl": r.n_ctl}[kind]
                        cells.append(fmt(r[dn], r[lo], r[hi], r[sg], d, n_used < bins["confidence"]["suppress_below_n"]))
                    out.append(f"| {bin_label(bt, bv)} | {LABEL[m]} | {r.n} | " + " | ".join(cells) + " |")
            out.append("")
    return out


def summary_section(sp, tiers, teams, bins):
    """Plain-language summary written from the numbers (re-generated every run)."""
    p = sp[(sp.team == POOLED) & (sp.scope == "all")]
    t = tiers[tiers.scope == "all"]
    k = int(p.n_teams.iloc[0]) if not p.empty else len([x for x in teams if x != POOLED])
    out = ["## Plain-language summary", ""]

    def pooled(bt, bv, m):
        r = p[(p.bin_type == bt) & (p.bin_value == bv) & (p.metric == m)]
        return None if r.empty else r.iloc[0]

    def cell(bt, bv, label, effects):
        parts = []
        for m, unit in effects:
            r = pooled(bt, bv, m)
            if r is not None and pd.notna(r.ctl_delta):
                parts.append(f"{LABEL[m]} {r.ctl_delta:+.{DEC[m]}f}{unit} [{r.ctl_lo:+.{DEC[m]}f}, {r.ctl_hi:+.{DEC[m]}f}]"
                             + (" (interval excludes zero)" if r.sig_ctl else " (interval spans zero)"))
        clear = t[(t.bin_type == bt) & (t.bin_value == bv) & (t.tier == "clear") & (t.team != POOLED)]
        lean = t[(t.bin_type == bt) & (t.bin_value == bv) & (t.tier == "leans") & (t.team != POOLED)]
        who = lambda d: ", ".join(sorted(set(d.team)))  # noqa: E731
        s = f"- **{label}** -- pooled across {k} teams, controlled for opponent, month and home/away: " + "; ".join(parts) + ". "
        s += ("Clear evidence for: " + who(clear) + ". ") if len(clear) else "No team clears the bar. "
        s += ("Leans: " + who(lean) + ".") if len(lean) else ""
        out.append(s)

    cell("wind", "windy", "Wind (windy vs not)", [("pass_eff", " yds/att"), ("points", " pts"), ("ppa_off", " PPA")])
    cell("precip", "wet", "Wet (light + steady rain)", [("pass_eff", " yds/att"), ("points", " pts"), ("ppa_off", " PPA")])
    temps = bins["temperature"]
    cell("temp", "warm_hot", f"Warm/hot ({temps['warm']['min']}°F and up)",
         [("pass_eff", " yds/att"), ("points", " pts"), ("ppa_off", " PPA")])
    cell("temp", "cold", f"Cold ({temps['cold']['max']}°F and below)",
         [("pass_eff", " yds/att"), ("points", " pts"), ("ppa_off", " PPA")])
    ctx = t[(t.tier == "context_only") & (t.team != POOLED)].team.unique()
    kept = sorted(set(teams) - {POOLED} - set(ctx))
    out += ["", "Temperature: " + (f"the controlled model finds no clear temperature effect for {', '.join(sorted(ctx))}, so their "
                                    "temperature results are labelled context-only" if len(ctx) else
                                    "every team's controlled model still shows a clear temperature effect") +
            (f"; it still shows one (kept as is) for {', '.join(kept)}." if len(ctx) and kept else "."),
            "", "_Exploratory: tiers and stars are leads to check, not findings._", ""]
    return out


def snow_games(conn):
    q = pd.read_sql_query(
        """SELECT g.game_id, g.kickoff_utc, g.home_team, g.away_team, g.home_points, g.away_points,
                  v.name venue, w.temp_f_mean t, w.wind_sust_max ws, w.wind_gust_max wg,
                  w.precip_in_total p, w.vis_min vis
           FROM weather_obs w JOIN games g ON g.game_id = w.game_id
           LEFT JOIN venues v ON v.venue_id = g.venue_id
           WHERE w.snow_flag = 1 AND w.weather_ok = 1 AND g.completed = 1
             AND g.game_id IN (SELECT game_id FROM team_games)
           ORDER BY g.kickoff_utc""", conn)
    out = ["## Snow games", "",
           "Snow is not split into delta rows (too few games). These are the games where an observation in the "
           "kickoff-to-+3.5h window reported a snow weather code. A code can mean flurries, so read the precipitation "
           "and temperature columns.", ""]
    if q.empty:
        return out + ["_None found._", ""]
    out += ["| Date | Game | Venue | Observed in window | Score |", "|---|---|---|---|---|"]
    for _, r in q.iterrows():
        day = (pd.Timestamp(r.kickoff_utc) - pd.Timedelta(hours=6)).strftime("%Y-%m-%d")
        wind = "—" if pd.isna(r.ws) else f"wind {r.ws:.0f} mph" + (f" (gust {r.wg:.0f})" if pd.notna(r.wg) and r.wg > r.ws + 1 else "")
        obs = f"{r.t:.0f}°F, {wind}, precip {r.p:.2f} in" + ("" if pd.isna(r.vis) else f", vis {r.vis:.1f} mi")
        score = "—" if pd.isna(r.home_points) else f"{r.away_team} {int(r.away_points)}, {r.home_team} {int(r.home_points)}"
        out.append(f"| {day} | {r.away_team} @ {r.home_team} | {r.venue or ''} | {obs} | {score} |")
    return out + [""]


def confounding_table(tdf, bins):
    """What is each bin made of? Month mix, home/away mix, opponent strength."""
    local = pd.to_datetime(tdf["kickoff_utc"], utc=True) - pd.Timedelta(hours=6)
    month = local.dt.month.to_numpy()
    site = np.where(tdf["neutral_site"] == 1, "neutral", tdf["home_away"]).astype(object)
    opp = tdf["opp_sp"].to_numpy(float)
    masks = bin_masks(tdf.reset_index(drop=True), bins)
    all_opp = np.nanmean(opp) if np.isfinite(opp).any() else np.nan
    groups = [("Aug–Sep", {8, 9}), ("Oct", {10}), ("Nov", {11}), ("Dec–Jan", {12, 1, 2})]

    def row(label, m):
        n = int(m.sum())
        if n == 0:
            return None
        cells = [f"{100 * np.isin(month[m], list(mo)).mean():.0f}%" for _, mo in groups]
        cells += [f"{100 * (site[m] == s).mean():.0f}%" for s in ("home", "away", "neutral")]
        o = opp[m]
        o_avg = np.nanmean(o) if np.isfinite(o).any() else np.nan
        cells += ["—" if np.isnan(o_avg) else f"{o_avg:+.1f}",
                  "—" if np.isnan(o_avg) or np.isnan(all_opp) else f"{o_avg - all_opp:+.1f}"]
        c = confidence(n, bins)
        return f"| {label} | {n}{'' if c == 'solid' else f' ({c})'} | " + " | ".join(cells) + " |"

    head = ["Bin", "n"] + [g for g, _ in groups] + ["Home", "Away", "Neutral", "Opp SP+", "vs all games"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head), row("**all usable games**", np.ones(len(tdf), bool))]
    for bt, vals in ORDER.items():
        for bv in vals:
            if (bt, bv) in masks:
                r = row(bin_label(bt, bv), masks[(bt, bv)])
                if r:
                    lines.append(r)
    return lines


def team_compact(sp, tdf, team, bins):
    ts = sp[(sp.team == team) & (sp.scope == "all")]
    cols = ["pass_eff", "points", "points_allowed", "ppa_off"]
    out = ["Each cell: **Raw / Adjusted / Controlled** delta (\\* = 90% interval excludes zero). Two yardsticks are "
           "shown; intervals are in `milestone3_detail.md`.", ""]
    for basis in (AVG, REST):
        out += [f"**{BASIS_TITLE[basis]}**", "",
                "| Bin | n | " + " | ".join(LABEL[m] for m in cols) + " |", "|---|---|" + "---|" * len(cols)]
        for bt, vals in ORDER.items():
            for bv in vals:
                r0 = ts[(ts.bin_type == bt) & (ts.bin_value == bv)]
                if r0.empty:
                    continue
                n = int(r0.n.max())
                conf = confidence(n, bins)
                cells = []
                for m in cols:
                    r = r0[r0.metric == m]
                    cells.append(triple(r.iloc[0] if not r.empty else None, DEC[m], bins, basis))
                out.append(f"| {bin_label(bt, bv)} | {n}{'' if conf == 'solid' else f' ({conf})'} | " + " | ".join(cells) + " |")
        out.append("")
    return out


def detail_report(sp, teams, bins):
    out = ["# Milestone 3 detail: every metric, every bin, full intervals", "",
           "_EXPLORATORY._ Raw = vs team's flat average. Adj = given opponent strength. Controlled = opponent strength + month "
           "+ home/away held fixed. Brackets are 90% bootstrap intervals; \\* = excludes zero. n adj / n ctl exclude games "
           "without an SP+ rating (FCS opponents).", "",
           "Columns come in two groups: **vs team average** (the team's overall average, which includes the bin) and "
           "**vs all other games** (the complement). The second is the first divided by (1 - bin share).", ""]
    for team in teams:
        ts = sp[(sp.team == team) & (sp.scope == "all")]
        x20 = sp[(sp.team == team) & (sp.scope == "ex2020")].set_index(["bin_type", "bin_value", "metric"])["n"]
        out += [f"## {name(team, int(ts.n_teams.max()) if not ts.empty else None)}", ""]
        for key, label, dec, note in METRICS:
            out += [f"### {label} ({note})", "",
                    "| Bin | n | n ex-2020 | n adj | n ctl | Raw vs avg | Adj vs avg | Ctl vs avg | Raw vs others | Adj vs others | Ctl vs others |",
                    "|---|---|---|---|---|---|---|---|---|---|---|"]
            for bt, vals in ORDER.items():
                for bv in vals:
                    r = ts[(ts.bin_type == bt) & (ts.bin_value == bv) & (ts.metric == key)]
                    if r.empty:
                        continue
                    r = r.iloc[0]
                    c = bins["confidence"]
                    cells = []
                    for basis in (AVG, REST):
                        for kind, n_used in (("raw", r.n), ("adj", r.n_adj), ("ctl", r.n_ctl)):
                            dn, lo, hi, sg = COLS[basis][kind]
                            cells.append(fmt(r[dn], r[lo], r[hi], r[sg], dec, n_used < c["suppress_below_n"]))
                    out.append(f"| {bin_label(bt, bv)} | {r.n}{'' if r.confidence == 'solid' else f' ({r.confidence})'} | "
                               f"{int(x20.get((bt, bv, key), 0))} | {r.n_adj} | {r.n_ctl} | " + " | ".join(cells) + " |")
            out.append("")
    return "\n".join(out) + "\n"


def changes_section(conn, sp, bins):
    """What moved in the pooled lines when teams were added (needs the saved previous results)."""
    prev = pd.read_sql_query("SELECT * FROM team_splits_prev", conn)
    if prev.empty:
        return []
    old_teams = sorted(set(prev.team) - {POOLED})
    new_teams = sorted(set(sp.team) - {POOLED} - set(old_teams))
    pn = prev[prev.team == POOLED].n_teams
    k_old = int(pn.iloc[0]) if len(pn) else len(old_teams)
    k_new = int(sp[sp.team == POOLED].n_teams.iloc[0]) if (sp.team == POOLED).any() else len(old_teams) + len(new_teams)
    out = [f"## What changed in the pooled lines: {k_old} teams → {k_new} teams", "",
           f"Added: {', '.join(new_teams) or 'none'}. Controlled Δ **vs the team's overall average** (same yardstick as the pooled tables above); "
           "n is the pooled game count; \\* = 90% interval excludes zero.", "",
           "| Bin | Metric | Before: n | Before | After: n | After |", "|---|---|---|---|---|---|"]
    for bt, bv in (("wind", "windy"), ("precip", "wet"), ("precip", "steady"), ("temp", "cold"), ("temp", "warm_hot")):
        for m in KEY_METRICS:
            a = prev[(prev.team == POOLED) & (prev.scope == "all") & (prev.bin_type == bt) & (prev.bin_value == bv) & (prev.metric == m)]
            b = sp[(sp.team == POOLED) & (sp.scope == "all") & (sp.bin_type == bt) & (sp.bin_value == bv) & (sp.metric == m)]
            if a.empty or b.empty:
                continue
            a, b = a.iloc[0], b.iloc[0]
            out.append(f"| {bin_label(bt, bv)} | {LABEL[m]} | {a.n} | {fmt(a.ctl_delta, a.ctl_lo, a.ctl_hi, a.sig_ctl, DEC[m])} | "
                       f"{b.n} | {fmt(b.ctl_delta, b.ctl_lo, b.ctl_hi, b.sig_ctl, DEC[m])} |")
    return out + [""]


def season_counts_section(usable):
    out = ["## Games by season (usable outdoor team-games)", "",
           "Finished games from the in-progress season count exactly like any other season.", "",
           "| Season | " + " | ".join(sorted(usable.team.unique())) + " |", "|---|" + "---|" * usable.team.nunique()]
    for season, g in usable.groupby("season"):
        row = [str(int((g.team == t).sum())) for t in sorted(usable.team.unique())]
        out.append(f"| {season}{' (in progress)' if season == usable.season.max() and season >= 2026 else ''} | " + " | ".join(row) + " |")
    return out + [""]


def build(conn, bins, calls_used=None):
    sp = pd.read_sql_query("SELECT * FROM team_splits", conn)
    tiers = pd.read_sql_query("SELECT * FROM team_tiers", conn)
    tracked = tracked_teams()
    out = ["# Milestone 3: scaled splits, controlled model, evidence tiers", "",
           f"_Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC._", "",
           "> **EXPLORATORY.** This report tests many team × bin × metric cells. At a 90% level roughly 1 in 10 intervals will "
           "exclude zero by luck alone, so a starred (\\*) delta or a \"leans\" tier is a lead to check, not a finding.", "",
           "**Two yardsticks, always labelled.** *A. vs the team's overall average* compares a bin to all of the team's games, "
           "including the bin itself. *B. vs all other games* compares the bin to the games NOT in it (\"windy vs not windy\"); "
           "it is the A number divided by (1 − the bin's share of games). Evidence tiers use the controlled model, where the "
           "choice of yardstick does not change the verdict.", ""]
    if sp.empty:
        return "\n".join(out + ["**No splits yet.**"]), ""
    have = sorted(set(sp.team) - {POOLED})
    deferred = [t for t in tracked if t in set(deferred_teams())]
    missing = sorted(set(tracked) - set(have) - set(deferred))
    out += [f"**Teams loaded ({len(have)}):** {', '.join(have)}. **Deferred by choice ({len(deferred)}):** "
            f"{', '.join(deferred) or 'none'} -- not loaded (their 2026 games are already played, so they only matter for "
            "the Team Explorer); nothing here depends on them.", ""]
    if missing:
        out += [f"> ⚠️ **PREVIEW.** These tracked teams have no data yet: {', '.join(missing)}.", ""]
    teams = [t for t in tracked if t in have] + ([POOLED] if POOLED in set(sp.team) else [])
    usable = usable_games(conn)

    out += summary_section(sp, tiers, teams, bins)
    out += budget_section(calls_used, bins)
    out += changes_section(conn, sp, bins)
    out += schedule_section(conn, bins)
    k = int(sp[sp.team == POOLED].n_teams.iloc[0]) if POOLED in set(sp.team) else None
    out += tier_section(tiers, teams, bins, k)
    out += pooled_section(sp, tiers, bins)
    out += control_effect_section(sp, bins)
    out += rating_section(usable, bins)
    out += season_counts_section(usable)
    out += venue_section(conn, bins)
    out += ["## Per team", "", "Month/home/opponent mix of each bin first (what the bin is secretly measuring), then the effects.", ""]
    for team in [t for t in teams if t != POOLED]:
        tdf = usable[usable.team == team]
        out += [f"### {team}", ""] + confounding_table(tdf, bins) + [""] + team_compact(sp, tdf, team, bins)
    out += snow_games(conn)
    return "\n".join(out) + "\n", detail_report(sp, teams, bins)


def run(conn=None, calls_used=None, client=None):
    conn = conn or connect()
    REPORT_DIR.mkdir(exist_ok=True)
    main, detail = build(conn, load_bins(), calls_used)
    (REPORT_DIR / "milestone3_scaled_splits.md").write_text(main)
    (REPORT_DIR / "milestone3_detail.md").write_text(detail)
    print("wrote reports/milestone3_scaled_splits.md and milestone3_detail.md")


if __name__ == "__main__":
    run()
