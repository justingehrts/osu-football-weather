"""Step 5: markdown report of n and delta per team and bin."""
from datetime import datetime, timezone

import pandas as pd

from .common import REPORT_DIR, connect, load_bins, tracked_teams
from .weather_bins import confidence

METRICS = [("pass_eff", "Pass yds/att"), ("rush_ypc", "Rush yds/carry"),
           ("points", "Points"), ("turnovers", "Turnovers")]
ORDER = {"wind": ["calm", "moderate", "windy"], "precip": ["none", "light", "steady"],
         "snow": ["snow", "no_snow"], "temp": ["cold", "mild", "warm", "hot"]}


def fmt_delta(v, conf):
    if conf == "suppressed" or v is None or pd.isna(v):
        return "—"
    return f"{v:+.2f}"


def build(conn, bins):
    sp = pd.read_sql_query("SELECT * FROM team_splits", conn)
    out = ["# Milestone 1: are the sample sizes workable?", "",
           f"_Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC._", "",
           "**How to read this.** *n* is the number of games in that weather bin. "
           "Deltas are the team's result in that bin minus the team's own average over all its "
           "outdoor games with usable weather (positive = better than usual for points / yards, "
           "worse for turnovers). Bins with n below "
           f"{bins['confidence']['suppress_below_n']} show “—”; n "
           f"{bins['confidence']['suppress_below_n']}-{bins['confidence']['thin_below_n'] - 1} is "
           f"**thin**; {bins['confidence']['thin_below_n']}+ is solid. The *n ex-2020* column "
           "drops the COVID season.", ""]
    if sp.empty:
        return "\n".join(out + ["**No splits yet** — the database has no usable weather games."])

    covid = ",".join(str(int(y)) for y in bins["flags"]["covid_seasons"]) or "-1"
    cov = pd.read_sql_query(
        f"""SELECT tg.team, COUNT(*) games,
                  SUM(v.dome = 1) dome, SUM(w.game_id IS NULL AND COALESCE(v.dome,0)=0) no_wx,
                  SUM(w.game_id IS NOT NULL AND w.weather_ok = 0) thin_obs,
                  SUM(COALESCE(v.dome,0)=0 AND w.weather_ok = 1) usable,
                  SUM(COALESCE(v.dome,0)=0 AND w.weather_ok = 1 AND v.station_far = 1) far,
                  SUM(g.season IN ({covid})) y2020
           FROM team_games tg JOIN games g USING(game_id)
           LEFT JOIN venues v ON v.venue_id = g.venue_id
           LEFT JOIN weather_obs w ON w.game_id = tg.game_id
           WHERE g.completed = 1 GROUP BY tg.team""", conn).set_index("team")

    have = set(sp["team"])
    teams = [t for t in tracked_teams() if t in have] + sorted(have - set(tracked_teams()))

    # headline: how many team-bin cells are solid / thin / suppressed
    cells = sp[(sp["scope"] == "all") & (sp["metric"] == "points")]
    out += ["## Summary", "", "| Team | Usable games | Solid bins | Thin bins | Suppressed bins |",
            "|---|---|---|---|---|"]
    for team in teams:
        c = cells[cells["team"] == team]["confidence"].value_counts()
        out.append(f"| {team} | {int(cov.loc[team, 'usable']) if team in cov.index else '?'} | "
                   f"{c.get('solid', 0)} | {c.get('thin', 0)} | {c.get('suppressed', 0)} |")
    out.append("")

    for team in teams:
        out += [f"## {team}", ""]
        if team in cov.index:
            c = cov.loc[team]
            out += [f"{int(c['games'])} completed games ingested · {int(c['usable'])} outdoor with usable "
                    f"weather · {int(c['dome'] or 0)} dome (excluded) · {int(c['no_wx'] or 0)} missing "
                    f"weather · {int(c['thin_obs'] or 0)} too few observations · "
                    f"{int(c['far'] or 0)} usable games use a station >{bins['quality']['far_station_miles']} mi "
                    f"away · {int(c['y2020'] or 0)} games in COVID season(s)", ""]
        t = sp[sp["team"] == team]
        header = ["Bin", "n", "n ex-2020", "Confidence"] + [f"Δ {lbl}" for _, lbl in METRICS]
        out += ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
        for bt, vals in ORDER.items():
            for bv in vals:
                a = t[(t.scope == "all") & (t.bin_type == bt) & (t.bin_value == bv)]
                if a.empty:
                    out.append(f"| {bt}: {bv} | 0 | 0 | suppressed |" + " — |" * len(METRICS))
                    continue
                n = int(a["n"].max())
                x = t[(t.scope == "ex2020") & (t.bin_type == bt) & (t.bin_value == bv)]
                n_x = int(x["n"].max()) if not x.empty else 0
                conf = confidence(n, bins)
                cells_ = []
                for m, _ in METRICS:
                    r = a[a.metric == m]
                    cells_.append(fmt_delta(r["delta"].iloc[0] if not r.empty else None, conf))
                out.append(f"| {bt}: {bv} | {n} | {n_x} | {conf} | " + " | ".join(cells_) + " |")
        out.append("")

    venues = pd.read_sql_query(
        "SELECT venue_id, name, dome, nearest_station, station_dist_mi, notes FROM venues "
        "WHERE notes != '' OR station_far = 1 OR dome = 1 ORDER BY station_dist_mi DESC", conn)
    out += ["## Venue / station flags", "",
            "| Venue | Dome | Station | Miles | Flags |", "|---|---|---|---|---|"]
    for _, v in venues.iterrows():
        out.append(f"| {v['name']} ({v['venue_id']}) | {'yes' if v['dome'] else ''} | "
                   f"{v['nearest_station'] or ''} | {'' if pd.isna(v['station_dist_mi']) else v['station_dist_mi']} "
                   f"| {v['notes']} |")
    return "\n".join(out) + "\n"


def run(conn=None):
    conn = conn or connect()
    REPORT_DIR.mkdir(exist_ok=True)
    text = build(conn, load_bins())
    (REPORT_DIR / "milestone1_sample_sizes.md").write_text(text)
    print("wrote reports/milestone1_sample_sizes.md")


if __name__ == "__main__":
    run()
