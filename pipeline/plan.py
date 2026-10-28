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


def _unloaded_seasons(conn, team, first, cur):
    done = {r[0] for r in conn.execute("SELECT season FROM ingest_log WHERE team=?", (team,))}
    return [s_ for s_ in range(first, cur) if s_ not in done]


def build(conn, client, today=None, skip_ratings=False):
    bins, cfg = load_bins(), load_yaml("teams.yaml")
    cur, first = current_season(today), cfg["first_season"]
    loadable = loadable_teams(conn, tracked_teams(), bins)
    pending = load_cached_stage1(conn, client, loadable, first, cur, bins, today)
    plan = OrderedDict((e, dict(need=0, exact=True)) for e in ENDPOINTS)
    plan["/games"]["need"] = len(pending)

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
            todo = [t for t in loadable if _unloaded_seasons(conn, t, first, cur)]
            past = sum(len(_unloaded_seasons(conn, t, first, cur)) for t in todo)      # one request per team-season
            post_years = len({s for s, st in pending if st == "postseason"})
            # a postseason year costs at most one request per not-yet-loaded team, or 3 weeks
            plan[path]["need"] += past + post_years * min(3, len(todo)) + len(todo)    # + current season by team
    plan["/ratings/sp"]["need"] = sum(
        0 if (s_ < cur and s_ in {r[0] for r in conn.execute("SELECT DISTINCT season FROM team_ratings")})
        or (skip_ratings) or client.is_cached("/ratings/sp", None if s_ < cur else bins["cfbd"]["current_season_ttl_hours"], year=s_)
        else 1 for s_ in range(first, cur + 1))
    if not client.is_cached("/venues"):
        plan["/venues"]["need"] += 1
    plan["/info"]["need"] = 0                              # /info is not billed by CFBD
    return plan, pending


def render(plan, counter, cfg_bins):
    total = sum(p["need"] for p in plan.values())
    lines = ["CFBD call budget for this run", "",
             f"{'endpoint':<14}{'calls':>7}   basis", "-" * 44]
    for e, p in plan.items():
        basis = 'free (not billed)' if e == '/info' else ('exact' if p['exact'] else 'worst case (exact once /games is loaded)')
        lines.append(f"{e:<14}{p['need']:>7}   {basis}")
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
    plan, pending = build(conn, client, skip_ratings='--skip-ratings' in argv)
    text, total = render(plan, client.counter, load_bins())
    print(text)
    return total


if __name__ == "__main__":
    main(sys.argv[1:])
