"""Incremental ingest, in dependency order. Safe to re-run any time.

  python -m pipeline.run_all [--resolve-if-missing] [--full]
"""
import sys

from . import build_venues, compute_splits, ingest_games, ingest_obs, ingest_ratings, report, resolve_opponents
from .common import CONFIG_DIR, connect


def main(argv):
    if not (CONFIG_DIR / "opponents.yaml").exists():
        if "--resolve-if-missing" in argv:
            resolve_opponents.run()
        else:
            raise SystemExit("config/opponents.yaml is missing. Run "
                             "`python -m pipeline.resolve_opponents` (or pass --resolve-if-missing).")
    conn = connect()
    ingest_games.run(conn, full="--full" in argv)   # games + box scores
    ingest_ratings.run(conn)                        # SP+ opponent strength
    build_venues.run(conn)                          # venues -> stations (needs games)
    ingest_obs.run(conn)                            # IEM weather (needs stations)
    compute_splits.run(conn)                        # baseline-relative splits
    report.run(conn)


if __name__ == "__main__":
    main(sys.argv[1:])
