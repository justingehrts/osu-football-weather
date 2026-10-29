"""In-season refresh: "did any tracked team finish a game since we last looked?"

Runs Saturday night through Monday (see .github/workflows/refresh.yml). The cost is deliberately tiny:

  ALWAYS    1 CFBD call: the league-wide games list for this season (never served from the cache,
            because the whole point is to see what changed). Before it, CFBD's own call count is read
            (the /info endpoint is not billed) so the month's budget is always the real one.
  ONLY IF new completed games turned up (a game of a loaded team that has no box score yet):
            box scores + PPA for just those games (by week or by team, whichever is cheaper),
            1 call to refresh the current-season SP+ ratings, then the airport weather windows
            (no CFBD calls), and a recompute of the summary tables and report.

If nothing is new it stops after the one call and leaves every data file untouched (the call
counter is rebuilt from CFBD at the start of every run, so it is not committed on its own), so a
quiet Sunday makes no commit. The month's call counter and hard cap apply as always.
"""
import json
import sys
from datetime import datetime, timezone

from . import build_venues, compute_splits, ingest_games, ingest_obs, ingest_ratings, report
from .cfbd import CfbdClient, pick
from .common import DATA_DIR, connect, current_season, load_bins, load_yaml, step_summary, tracked_teams


def new_completed_games(conn, games, teams):
    """Completed games of tracked teams in the CFBD response that we hold no box score for yet."""
    have = {(r[0], r[1]) for r in conn.execute("SELECT game_id, team FROM team_games")}
    out = []
    for g in games:
        if not g.get("completed"):
            continue
        for side in ("homeTeam", "awayTeam"):
            team = pick(g, side, side.replace("Team", "_team"))
            if team in teams and (g["id"], team) not in have:
                out.append((g["id"], team))
    return out


def describe_changes(before, after, limit=8):
    """Plain-English list of games whose kickoff time, completion or score changed between two snapshots."""
    keyed = lambda rows: {r["game_id"]: r for r in rows}   # noqa: E731
    b, out = keyed(before), []
    for gid, a in keyed(after).items():
        o = b.get(gid)
        label = f"{a['away_team']} at {a['home_team']}"
        if o is None:
            out.append(f"{label}: added to the schedule")
        elif o["kickoff_utc"] != a["kickoff_utc"]:
            out.append(f"{label}: kickoff {o['kickoff_utc'] or 'TBD'} -> {a['kickoff_utc'] or 'TBD'}")
        elif (o["completed"], o["home_points"], o["away_points"]) != (a["completed"], a["home_points"], a["away_points"]):
            out.append(f"{label}: result/score updated")
        elif tuple(o) != tuple(a):
            out.append(f"{label}: details updated (venue or status)")
    return out if len(out) <= limit else out[:limit] + [f"...and {len(out) - limit} more"]


def refresh_summary(new, changes, calls, month_total, cap, by_endpoint=None):
    """The markdown shown on the run page, so nobody has to dig through the log."""
    lines = ["## Refresh history after new games"]
    if new:
        teams = sorted({t for _, t in new})
        lines.append(f"**Result: {len(new)} new finished team-games ({', '.join(teams)}). History and summary tables were refreshed.**")
    else:
        lines.append("**Result: no new completed games.** Nothing to recompute.")
    if changes:
        lines += [f"- Schedule/score updates picked up from CFBD ({len(changes)}):"] + [f"  - {c}" for c in changes]
    elif not new:
        lines.append("- No schedule or score changes either.")
    ep = f" ({', '.join(f'{k} x{v}' for k, v in sorted((by_endpoint or {}).items()))})" if by_endpoint else ""
    lines.append(f"- CFBD calls this run: **{calls}**{ep}. Month total: **{month_total}** of the {cap}-call cap.")
    return "\n".join(lines)


def _games_snapshot(conn, teams, season):
    marks = ",".join("?" * len(teams))
    return conn.execute(f"SELECT * FROM games WHERE season=? AND (home_team IN ({marks}) OR away_team IN ({marks})) ORDER BY game_id",
                        [season, *teams, *teams]).fetchall()


def main(client=None, now=None):
    bins, cfg = load_bins(), load_yaml("teams.yaml")
    client = client or CfbdClient()
    conn = connect()
    cur = current_season()
    teams = ingest_games.loadable_teams(conn, tracked_teams(), bins)
    try:
        client.info()                                                  # free: sets our counter to CFBD's real count
    except Exception as e:  # noqa: BLE001 - never let a failed lookup stop the refresh; the saved count is the fallback
        print(f"(could not read CFBD's call count: {type(e).__name__}; using the saved counter)")
    start = client.counter.used

    games = client.games(cur, "regular", ttl_hours=0, rewrite_if_same=False)   # THE one call: ttl 0 = always fresh
    new = new_completed_games(conn, games, set(teams))
    before = _games_snapshot(conn, teams, cur)
    ingest_games.store_games(conn, games, set(teams), cur, "regular")  # picks up reschedules and final scores too
    after = _games_snapshot(conn, teams, cur)
    changed = [tuple(r) for r in after] != [tuple(r) for r in before]
    changes = describe_changes(before, after)
    if not new:
        if changed:
            conn.commit()
            print("No new completed games, but game times/scores were updated.")
        else:
            conn.rollback()
            print("No new completed games. Nothing to do.")
        calls = client.counter.used - start
        print(f"CFBD calls this run: {calls}")
        step_summary(refresh_summary([], changes, calls, client.counter.used, client.counter.cap, dict(client.by_endpoint)))
        return {"new_games": 0, "calls": calls}
    conn.commit()
    print(f"{len(new)} new completed team-games: {sorted({t for _, t in new})}")
    ingest_games.run_stage2(conn, client, teams, cur, bins)            # box scores + PPA for just those games
    ingest_ratings.run(conn, client)                                   # current-season SP+ (one call)
    build_venues.run(conn, client)                                     # cached; refreshes only if a new venue appears
    ingest_obs.run(conn)                                               # airport windows (not CFBD)
    compute_splits.run(conn)
    record = {"checked_utc": (now or datetime.now(timezone.utc)).isoformat(timespec="seconds"),
              "new_team_games": len(new), "calls": client.counter.used - start, "by_endpoint": dict(client.by_endpoint),
              "month_total": client.counter.used}
    (DATA_DIR / "last_refresh.json").write_text(json.dumps(record, indent=1))
    report.run(connect(), calls_used=record["calls"])
    print(f"CFBD calls this run: {record['calls']} {dict(client.by_endpoint)}; month total {client.counter.used}")
    step_summary(refresh_summary(new, changes, record["calls"], client.counter.used, client.counter.cap, dict(client.by_endpoint)))
    return record


if __name__ == "__main__":
    main()
