"""Incremental pipeline, in dependency order. Safe to re-run any time.

  python -m pipeline.run_all [--sync] [--approve-large-plan]

  --sync                 first ask CFBD how many calls the month has used (costs 1 call) and trust it if
                         it is higher than our own counter (other tools share the quota)

Order matters for the CFBD budget: games first (they define what else is needed), then a
printed budget, then the calls. A plan bigger than `cfbd.ask_if_plan_exceeds` stops and waits
for --approve-large-plan; a run that would pass `cfbd.monthly_cap` aborts before sending.
"""
import sys

from . import (build_venues, compute_splits, ingest_games, ingest_obs, ingest_ratings, plan, report,
               resolve_opponents)
from .cfbd import BudgetExceeded, CfbdClient
from .common import CONFIG_DIR, connect, current_season, load_bins, load_yaml, tracked_teams


def main(argv, client=None):
    bins = load_bins()
    client = client or CfbdClient()
    if "--sync" in argv:
        client.info()
    start_calls = client.counter.used
    resolve_opponents.run(client=client)              # 1 call at most (reused by the games ingest)
    conn = connect()
    teams = tracked_teams()
    cfg = load_yaml("teams.yaml")
    cur = current_season()

    # --- stage 1: league-wide games (cheap), after printing the budget ---
    p, pending = plan.build(conn, client)
    text, total = plan.render(p, client.counter, bins)
    print(text)
    if total > bins["cfbd"]["ask_if_plan_exceeds"] and "--approve-large-plan" not in argv:
        raise SystemExit(f"Plan is {total} calls (> {bins['cfbd']['ask_if_plan_exceeds']}). "
                         "Ask the owner, then re-run with --approve-large-plan.")
    client.counter.check(p["/games"]["need"])
    ingest_games.run_stage1(conn, client, teams, cfg["first_season"], cur, bins)

    # --- stage 2: now the budget is exact; print it again and re-check before spending ---
    p, pending = plan.build(conn, client)
    text, total = plan.render(p, client.counter, bins)
    print("\nAfter stage 1 (exact):\n" + text)
    client.counter.check(total - p["/info"]["need"])   # raises BudgetExceeded before any stage-2 call
    ingest_games.run_stage2(conn, client, ingest_games.loadable_teams(conn, teams, bins), cur, bins)
    ingest_ratings.run(conn, client)
    build_venues.run(conn, client)
    ingest_obs.run(conn)                              # IEM: no CFBD calls
    compute_splits.run(conn)
    report.run(conn, calls_used=client.counter.used - start_calls, client=client)
    print(f"\nCFBD calls this run: {client.counter.used - start_calls}; month total: {client.counter.used} "
          f"(cap {client.counter.cap})")


if __name__ == "__main__":
    main(sys.argv[1:])
