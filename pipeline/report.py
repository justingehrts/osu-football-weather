"""Step 5: markdown report -- sample sizes, confounding, raw vs adjusted deltas, snow games."""
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from .common import REPORT_DIR, connect, load_bins, tracked_teams
from .compute_splits import bin_masks, usable_games
from .weather_bins import confidence

METRICS = [("pass_eff", "Pass yds/att", 2, "higher = better"),
           ("rush_ypc", "Rush yds/carry", 2, "higher = better"),
           ("points", "Points scored", 1, "higher = better"),
           ("points_allowed", "Points allowed (defense)", 1, "LOWER = better"),
           ("turnovers", "Turnovers", 2, "LOWER = better"),
           ("ppa_off", "Offensive PPA/play", 3, "higher = better")]
ORDER = {"wind": ["calm", "moderate", "windy"],
         "precip": ["none", "light", "steady", "wet"],
         "temp": ["cold", "mild", "warm", "hot", "warm_hot"]}
MERGED_NOTE = "wet = light + steady · warm_hot = warm + hot (merged bins, see bins.yaml)"
MONTH_GROUPS = [("Aug–Sep", {8, 9}), ("Oct", {10}), ("Nov", {11}), ("Dec–Jan", {12, 1, 2})]


def fmt(delta, lo, hi, sig, dec, suppressed):
    if suppressed or delta is None or pd.isna(delta):
        return "—"
    if pd.isna(lo) or pd.isna(hi):
        return f"{delta:+.{dec}f}"
    return f"{delta:+.{dec}f} [{lo:+.{dec}f}, {hi:+.{dec}f}]" + (" **\\***" if sig else "")


def bin_label(bt, bv):
    return f"{bt}: {bv}"


def confounding_table(tdf, bins):
    """What is each bin secretly made of? Month mix, home/away mix, opponent strength."""
    local = pd.to_datetime(tdf["kickoff_utc"], utc=True) - pd.Timedelta(hours=6)  # ~US local
    month = local.dt.month.to_numpy()
    site = np.where(tdf["neutral_site"] == 1, "neutral", tdf["home_away"]).astype(object)
    opp = tdf["opp_sp"].to_numpy(float)
    masks = bin_masks(tdf.reset_index(drop=True), bins)
    all_opp = np.nanmean(opp) if np.isfinite(opp).any() else np.nan

    def row(label, m):
        n = int(m.sum())
        if n == 0:
            return None
        cells = [f"{100 * np.isin(month[m], list(mo)).mean():.0f}%" for _, mo in MONTH_GROUPS]
        cells += [f"{100 * (site[m] == s).mean():.0f}%" for s in ("home", "away", "neutral")]
        o = opp[m]
        o_avg = np.nanmean(o) if np.isfinite(o).any() else np.nan
        cells += ["—" if np.isnan(o_avg) else f"{o_avg:+.1f}",
                  "—" if np.isnan(o_avg) or np.isnan(all_opp) else f"{o_avg - all_opp:+.1f}"]
        flag = " (thin)" if confidence(n, bins) == "thin" else " (suppressed)" if confidence(n, bins) == "suppressed" else ""
        return f"| {label} | {n}{flag} | " + " | ".join(cells) + " |"

    head = ["Bin", "n"] + [g for g, _ in MONTH_GROUPS] + ["Home", "Away", "Neutral", "Opp SP+", "vs all games"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head),
             row("**all usable games**", np.ones(len(tdf), bool))]
    for bt, vals in ORDER.items():
        for bv in vals:
            if (bt, bv) in masks:
                r = row(bin_label(bt, bv), masks[(bt, bv)])
                if r:
                    lines.append(r)
    return lines


def snow_games(conn):
    """The actual snow games (any snow present-weather code in the game window)."""
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
           "Snow is no longer split into delta rows (too few games). These are the actual games where an "
           "observation in the kickoff-to-+3.5h window reported a snow weather code. A code can mean "
           "flurries, so read the precipitation and temperature columns.", ""]
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


def adjustment_summary(sp, bins):
    """How much does opponent adjustment change the picture? (solid cells, all seasons)"""
    s = sp[(sp.scope == "all") & (sp.confidence == "solid") & sp.adj_delta.notna()]
    out = ["## How much does opponent adjustment change things?", "",
           "Solid cells only (n ≥ " f"{bins['confidence']['thin_below_n']}), all seasons, cells that have an adjusted value. "
           "*Sign flips* = raw and adjusted deltas point in opposite directions. "
           "*Excl. 0* = how many intervals exclude zero (expect roughly 1 in 10 by luck alone).", "",
           "| Metric | Cells | Avg \\|raw Δ\\| | Avg \\|adj Δ\\| | Sign flips | Raw excl. 0 | Adj excl. 0 |",
           "|---|---|---|---|---|---|---|"]
    for key, label, dec, _ in METRICS:
        m = s[s.metric == key]
        if m.empty:
            continue
        flips = int(((m.delta * m.adj_delta) < 0).sum())
        out.append(f"| {label} | {len(m)} | {m.delta.abs().mean():.{dec}f} | {m.adj_delta.abs().mean():.{dec}f} "
                   f"| {flips} | {int(m.sig_raw.sum())} | {int(m.sig_adj.sum())} |")
    return out + [""]


def build(conn, bins):
    sp = pd.read_sql_query("SELECT * FROM team_splits", conn)
    c = bins["confidence"]
    out = ["# Milestone 2: weather splits, opponent-adjusted, with uncertainty", "",
           f"_Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC._", "",
           "> **EXPLORATORY.** This report tests hundreds of team × bin × metric cells. At a 90% level, "
           "roughly 1 in 10 intervals will exclude zero by luck alone, so a starred (\\*) delta is a lead to "
           "check, not a finding. Prefer patterns that show up across teams and across related metrics.", "",
           "**How to read this.**", "",
           "- *n* = games in the bin. Fewer than "
           f"{c['suppress_below_n']} is hidden (—), {c['suppress_below_n']}-{c['thin_below_n'] - 1} is **thin**, "
           f"{c['thin_below_n']}+ is solid. *n adj* is the number of those games with an opponent rating "
           "(FCS opponents have none).",
           "- **Raw Δ** = bin average minus the team's average over all its usable outdoor games.",
           "- **Adj Δ** = bin result minus what we'd expect *given the opponents actually played* "
           "(straight-line fit on the opponent's SP+ rating, per team and metric). It removes opponent "
           "quality only -- **not** month, home/away or anything else; see the confounding tables.",
           "- Brackets are a bootstrap 90% interval. **\\*** = interval excludes zero.",
           f"- {MERGED_NOTE}.", ""]
    if sp.empty:
        return "\n".join(out + ["**No splits yet** — the database has no usable weather games."])
    if sp.adj_delta.isna().all():
        out += ["> ⚠️ No opponent ratings are loaded, so every adjusted column is empty.", ""]

    have = set(sp["team"])
    teams = [t for t in tracked_teams() if t in have] + sorted(have - set(tracked_teams()))
    usable = usable_games(conn)
    covid = ",".join(str(int(y)) for y in bins["flags"]["covid_seasons"]) or "-1"
    cov = pd.read_sql_query(
        f"""SELECT tg.team, COUNT(*) games, SUM(v.dome = 1) dome,
                   SUM(w.game_id IS NULL AND COALESCE(v.dome,0)=0) no_wx,
                   SUM(w.game_id IS NOT NULL AND w.weather_ok = 0) thin_obs,
                   SUM(COALESCE(v.dome,0)=0 AND w.weather_ok = 1) usable,
                   SUM(COALESCE(v.dome,0)=0 AND w.weather_ok = 1 AND v.station_far = 1) far,
                   SUM(g.season IN ({covid})) y2020
            FROM team_games tg JOIN games g USING(game_id)
            LEFT JOIN venues v ON v.venue_id = g.venue_id
            LEFT JOIN weather_obs w ON w.game_id = tg.game_id
            WHERE g.completed = 1 GROUP BY tg.team""", conn).set_index("team")

    cells = sp[(sp.scope == "all") & (sp.metric == "points")]
    out += ["## Sample sizes", "", "| Team | Usable games | Solid bins | Thin bins | Suppressed bins |", "|---|---|---|---|---|"]
    for t in teams:
        cc = cells[cells.team == t].confidence.value_counts()
        out.append(f"| {t} | {int(cov.loc[t, 'usable']) if t in cov.index else '?'} | "
                   f"{cc.get('solid', 0)} | {cc.get('thin', 0)} | {cc.get('suppressed', 0)} |")
    out += ["", "_Bins counted include the merged ones._", ""]

    out += adjustment_summary(sp, bins)

    tested = sp[(sp.scope == "all") & (sp.n >= c["suppress_below_n"])]
    flagged = sp[(sp.scope == "all") & (sp.confidence == "solid") & ((sp.sig_raw == 1) | (sp.sig_adj == 1))]
    out += ["## Intervals that exclude zero (solid cells)", "",
            f"{len(tested)} team/bin/metric cells have n ≥ {c['suppress_below_n']}; "
            f"about {0.1 * len(tested):.0f} would be expected to exclude zero by chance alone. "
            f"Below are the {len(flagged)} solid cells where the raw or adjusted interval excludes zero "
            "(many are the same underlying effect seen through several metrics, and merged bins overlap "
            "their parents).", "",
            "| Team | Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] |", "|---|---|---|---|---|---|"]
    lab = {k: (l, d) for k, l, d, _ in METRICS}
    for t in teams:
        for _, r in flagged[flagged.team == t].sort_values(["metric", "bin_type", "bin_value"]).iterrows():
            l, d = lab[r.metric]
            out.append(f"| {t} | {bin_label(r.bin_type, r.bin_value)} | {l} | {r.n} | "
                       f"{fmt(r.delta, r.delta_lo, r.delta_hi, r.sig_raw, d, False)} | "
                       f"{fmt(r.adj_delta, r.adj_lo, r.adj_hi, r.sig_adj, d, r.n_adj < c['suppress_below_n'])} |")
    out.append("")

    for t in teams:
        out += [f"## {t}", ""]
        if t in cov.index:
            x = cov.loc[t]
            out += [f"{int(x['games'])} completed games ingested · {int(x['usable'])} outdoor with usable weather · "
                    f"{int(x['dome'] or 0)} dome (excluded) · {int(x['no_wx'] or 0)} missing weather · "
                    f"{int(x['thin_obs'] or 0)} too few observations · {int(x['far'] or 0)} usable games use a station "
                    f">{bins['quality']['far_station_miles']} mi away · {int(x['y2020'] or 0)} games in COVID season(s)", ""]
        tdf = usable[usable.team == t]
        out += [f"### {t}: what is each bin made of?", "",
                "Share of the bin's games by kickoff month (approx. local), site, and average opponent SP+ rating "
                "(*vs all games* = difference from this team's overall average opponent; positive = tougher "
                "opponents than usual).", ""] + confounding_table(tdf, bins) + [""]
        ts = sp[(sp.team == t) & (sp.scope == "all")]
        x20 = sp[(sp.team == t) & (sp.scope == "ex2020")].set_index(["bin_type", "bin_value", "metric"])["n"]
        for key, label, dec, note in METRICS:
            out += [f"### {t}: {label} ({note})", "",
                    "| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |", "|---|---|---|---|---|---|"]
            for bt, vals in ORDER.items():
                for bv in vals:
                    r = ts[(ts.bin_type == bt) & (ts.bin_value == bv) & (ts.metric == key)]
                    if r.empty:
                        continue
                    r = r.iloc[0]
                    supp = r.confidence == "suppressed"
                    conf = "" if r.confidence == "solid" else f" ({r.confidence})"
                    out.append(
                        f"| {bin_label(bt, bv)} | {r.n}{conf} | {int(x20.get((bt, bv, key), 0))} | {r.n_adj} | "
                        f"{fmt(r.delta, r.delta_lo, r.delta_hi, r.sig_raw, dec, supp)} | "
                        f"{fmt(r.adj_delta, r.adj_lo, r.adj_hi, r.sig_adj, dec, r.n_adj < c['suppress_below_n'])} |")
            out.append("")

    out += snow_games(conn)

    venues = pd.read_sql_query(
        "SELECT venue_id, name, dome, nearest_station, station_dist_mi, notes FROM venues "
        "WHERE notes != '' OR station_far = 1 OR dome = 1 ORDER BY station_dist_mi DESC", conn)
    out += ["## Venue / station flags", "", "| Venue | Dome | Station | Miles | Flags |", "|---|---|---|---|---|"]
    for _, v in venues.iterrows():
        out.append(f"| {v['name']} ({v['venue_id']}) | {'yes' if v['dome'] else ''} | "
                   f"{'' if pd.isna(v['nearest_station']) else v['nearest_station']} | "
                   f"{'' if pd.isna(v['station_dist_mi']) else v['station_dist_mi']} | {v['notes']} |")
    return "\n".join(out) + "\n"


def run(conn=None):
    conn = conn or connect()
    REPORT_DIR.mkdir(exist_ok=True)
    (REPORT_DIR / "milestone2_weather_splits.md").write_text(build(conn, load_bins()))
    print("wrote reports/milestone2_weather_splits.md")


if __name__ == "__main__":
    run()
