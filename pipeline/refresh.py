"""In-season refresh: "did any tracked team finish a game since we last looked?"

Runs Saturday night through Monday (see .github/workflows/refresh.yml). The cost is deliberately tiny:

  ALWAYS    1 CFBD call: the league-wide games list for this season (never served from the cache,
            because the whole point is to see what changed).
  ONLY IF new completed games turned up (a game of a loaded team that has no box score yet):
            box scores + PPA for just those games (by week or by team, whichever is cheaper),
            1 call to refresh the current-season SP+ ratings, then the airport weather windows
            (no CFBD calls), and a recompute of the summary tables and report.

If nothing is new it stops after the one call and leaves every file untouched, so a quiet
Sunday makes no commit. The month's call counter and hard cap apply as always.
"""
import json
import sys
from datetime import datetime, timezone

from . import build_venues, compute_splits, ingest_games, ingest_obs, ingest_ratings, report
from .cfbd import CfbdClient, pick
from .common import DATA_DIR, connect, current_season, load_bins, load_yaml, tracked_teams


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
    start = client.counter.used

    games = client.games(cur, "regular", ttl_hours=0)                  # THE one call: ttl 0 = always fresh
    new = new_completed_games(conn, games, set(teams))
    before = _games_snapshot(conn, teams, cur)
    ingest_games.store_games(conn, games, set(teams), cur, "regular")  # picks up reschedules and final scores too
    changed = [tuple(r) for r in _games_snapshot(conn, teams, cur)] != [tuple(r) for r in before]
    if not new:
        if changed:
            conn.commit()
            print("No new completed games, but game times/scores were updated.")
        else:
            conn.rollback()
            print("No new completed games. Nothing to do.")
        print(f"CFBD calls this run: {client.counter.used - start}")
        return {"new_games": 0, "calls": client.counter.used - start}
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
    return record


if __name__ == "__main__":
    main()
