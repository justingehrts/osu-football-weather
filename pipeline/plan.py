"""The call budget: how many CFBD calls would a run take, per endpoint, BEFORE sending any.

Stage 1 (league-wide /games per season) is known exactly. Stage 2 (box scores, PPA) depends
on what stage 1 returns, so until stage 1 is on disk it is reported as a WORST CASE
(every missing team-season requested by team, every postseason up to 3 weeks); once stage 1
is cached it is exact. `python -m pipeline.plan` only reads local files and prints.
"""
import sys
from collections import OrderedDict

from .cfbd import CfbdClient
from .common import connect, current_season, load_bins, load_yaml, tracked_teams
from .ingest_games import (games_ttl, loadable_teams, request_is_cached, stage1_requests,
                           stats_requests, store_games, _unlogged_team_seasons)

ENDPOINTS = ["/games", "/games/teams", "/ppa/games", "/ratings/sp", "/venues", "/info"]


def load_cached_stage1(conn, client, teams, first, cur, bins, today=None):
    """Free: push already-cached /games responses into the database. Returns uncached requests."""
    tset, pending = set(teams), []
    for season, stype in stage1_requests(first, cur, today):
        ttl = games_ttl(season, cur, bins)
        if client.is_cached("/games", ttl, year=season, seasonType=stype):
            store_games(conn, client.games(season, stype, ttl_hours=ttl), tset, season, stype)
        else:
            pending.append((season, stype))
    conn.commit()
    return pending


def build(conn, client, today=None):
    bins, cfg = load_bins(), load_yaml("teams.yaml")
    cur, first = current_season(today), cfg["first_season"]
    teams = tracked_teams()
    pending = load_cached_stage1(conn, client, teams, first, cur, bins, today)
    plan = OrderedDict((e, dict(need=0, exact=True)) for e in ENDPOINTS)
    plan["/games"]["need"] = len(pending)

    loadable = loadable_teams(conn, teams, bins)
    if not pending:                                        # stage 2 is exactly knowable
        last_week = conn.execute("SELECT COALESCE(MAX(week),0) FROM games WHERE season=? AND completed=1 "
                                 "AND season_type='regular'", (cur,)).fetchone()[0]
        for r in stats_requests(conn, loadable, cur, bins):
            for endpoint, path in (("box", "/games/teams"), ("ppa", "/ppa/games")):
                cached, _ = request_is_cached(client, r, endpoint, cur, bins, last_week)
                plan[path]["need"] += 0 if cached else 1
    else:                                                  # worst case until stage 1 is loaded
        for path in ("/games/teams", "/ppa/games"):
            plan[path]["exact"] = False
        past = [s for s, _ in pending if s < cur]
        for team in loadable:
            # every past season of a not-yet-loaded team, assumed requested by team
            seasons = [s for s in range(first, cur) if s not in
                       {r[0] for r in conn.execute("SELECT season FROM ingest_log WHERE team=?", (team,))}]
            for path in ("/games/teams", "/ppa/games"):
                plan[path]["need"] += len(seasons)
        post_seasons = len({s for s, st in pending if st == "postseason"})
        for path in ("/games/teams", "/ppa/games"):
            plan[path]["need"] += 3 * post_seasons          # up to 3 postseason weeks a year
            plan[path]["need"] += 15                         # current-season weeks (upper bound)
        del past

    # ratings: seasons not already in the database and not cached
    have = {r[0] for r in conn.execute("SELECT DISTINCT season FROM team_ratings")}
    for season in range(first, cur + 1):
        if season < cur and season in have:
            continue
        ttl = bins["cfbd"]["current_season_ttl_hours"] if season >= cur else None
        if not client.is_cached("/ratings/sp", ttl, year=season):
            plan["/ratings/sp"]["need"] += 1
    if not client.is_cached("/venues"):
        plan["/venues"]["need"] += 1
    plan["/info"]["need"] = 1
    return plan, pending


def render(plan, counter, cfg_bins):
    total = sum(p["need"] for p in plan.values())
    lines = ["CFBD call budget for this run", "",
             f"{'endpoint':<14}{'calls':>7}   basis", "-" * 44]
    for e, p in plan.items():
        lines.append(f"{e:<14}{p['need']:>7}   {'exact' if p['exact'] else 'worst case (exact once /games is loaded)'}")
    lines += ["-" * 44, f"{'TOTAL':<14}{total:>7}", "",
              f"used this month so far : {counter.used}",
              f"after this run         : {counter.used + total}",
              f"hard cap (bins.yaml)   : {counter.cap}   -> {'OK' if counter.used + total <= counter.cap else 'OVER THE CAP: the run will abort'}",
              f"ask-the-owner threshold: {cfg_bins['cfbd']['ask_if_plan_exceeds']} calls in one plan -> "
              f"{'APPROVAL NEEDED' if total > cfg_bins['cfbd']['ask_if_plan_exceeds'] else 'not needed'}"]
    return "\n".join(lines), total


def main(argv):
    conn = connect()
    client = CfbdClient(offline=True)
    plan, pending = build(conn, client)
    text, total = render(plan, client.counter, load_bins())
    print(text)
    return total


if __name__ == "__main__":
    main(sys.argv[1:])
