"""Incremental pipeline, in dependency order. Safe to re-run any time.

  python -m pipeline.run_all [--sync] [--skip-ratings] [--approve-large-plan]

  --sync                 first ask CFBD how many calls the month has used (costs 1 call) and trust it if
                         it is higher than our own counter (other tools share the quota)

Order matters for the CFBD budget: games first (they define what else is needed), then a
printed budget, then the calls. A plan bigger than `cfbd.ask_if_plan_exceeds` stops and waits
for --approve-large-plan; a run that would pass `cfbd.monthly_cap` aborts before sending.
"""
import json
import sys

from . import (build_venues, compute_splits, ingest_games, ingest_obs, ingest_ratings, plan, report,
               resolve_opponents)
from .cfbd import BudgetExceeded, CfbdClient
from .common import DATA_DIR, connect, current_season, load_bins, load_yaml, tracked_teams


def _plan_counts(p):
    return {e: v["need"] for e, v in p.items()}


def main(argv, client=None):
    bins = load_bins()
    client = client or CfbdClient()
    if "--sync" in argv:
        client.info()
    start_calls = client.counter.used
    record = {"label": " ".join(a for a in argv if a.startswith("--")) or "incremental", "start": start_calls,
              "end": start_calls, "calls": 0, "by_endpoint": {}, "plan_initial": {}, "plan_exact": {},
              "planned_total": 0, "exact_total": 0}
    try:
        _run(argv, client, bins, record)
    finally:                                   # write the record even if the budget stopped us
        record["end"] = client.counter.used
        record["calls"] = client.counter.used - start_calls
        record["by_endpoint"] = dict(client.by_endpoint)
        (DATA_DIR / "last_run.json").write_text(json.dumps(record, indent=1))
    report.run(connect(), calls_used=record["calls"])   # after the record, so the report can show planned vs used
    print(f"\nCFBD calls this run: {record['calls']}; month total: {client.counter.used} (cap {client.counter.cap})")


def _run(argv, client, bins, record):
    resolve_opponents.run(client=client)              # 1 call at most (reused by the games ingest)
    conn = connect()
    teams = ingest_games.loadable_teams(conn, tracked_teams(), bins)   # not deferred, not FCS (if configured)
    cfg = load_yaml("teams.yaml")
    cur = current_season()
    skip_ratings = "--skip-ratings" in argv

    # --- stage 1: league-wide games (cheap), after printing the budget ---
    p, pending = plan.build(conn, client, skip_ratings=skip_ratings)
    text, total = plan.render(p, client.counter, bins)
    print(text)
    record["plan_initial"], record["planned_total"] = _plan_counts(p), total
    if total > bins["cfbd"]["ask_if_plan_exceeds"] and "--approve-large-plan" not in argv:
        raise SystemExit(f"Plan is {total} calls (> {bins['cfbd']['ask_if_plan_exceeds']}). "
                         "Ask the owner, then re-run with --approve-large-plan.")
    client.counter.check(p["/games"]["need"])
    ingest_games.run_stage1(conn, client, teams, cfg["first_season"], cur, bins)

    # --- stage 2: now the budget is exact; print it again and re-check before spending ---
    p, pending = plan.build(conn, client, skip_ratings=skip_ratings)
    text, total = plan.render(p, client.counter, bins)
    print("\nAfter stage 1 (exact):\n" + text)
    record["plan_exact"], record["exact_total"] = _plan_counts(p), total + record["plan_initial"].get("/games", 0)
    client.counter.check(total)                         # raises BudgetExceeded before any stage-2 call
    ingest_games.run_stage2(conn, client, teams, cur, bins)
    ingest_ratings.run(conn, client, skip_current=skip_ratings)
    build_venues.run(conn, client)
    ingest_obs.run(conn)                              # IEM: no CFBD calls
    compute_splits.run(conn)


if __name__ == "__main__":
    main(sys.argv[1:])
