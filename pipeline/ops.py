"""Operator entry points used by the (temporary) review-branch workflow.

  plan      sync the call counter with CFBD, resolve the team list (1 call, reused later), then
            print the exact call budget. Sends no other requests.
  run       the full incremental pipeline (run_all), which re-checks the budget before spending.
"""
import json
import shlex
import sys

from . import plan as plan_mod
from . import resolve_opponents, run_all
from .cfbd import CfbdClient
from .common import DATA_DIR, connect, load_bins


def main(request):
    mode, *flags = shlex.split(request)
    if mode == "forecast":                     # NWS / Open-Meteo only: no CFBD client, no CFBD calls
        from . import forecast
        forecast.run()
        return
    client = CfbdClient()
    info = client.info()                       # also pulls our counter up to CFBD's own count
    print("CFBD_INFO", json.dumps({k: info.get(k) for k in ("tierName", "monthlyLimit", "usedCalls", "remainingCalls", "resetAt")}))
    if mode == "info":
        pass                                   # the call above is the whole job
    elif mode == "plan":
        resolve_opponents.run(client=client)
        conn = connect()
        plan, pending = plan_mod.build(conn, client, skip_ratings='--skip-ratings' in flags)
        text, total = plan_mod.render(plan, client.counter, load_bins())
        print(text)
        (DATA_DIR / "last_plan.json").write_text(json.dumps(
            {"total": total, "used_before": client.counter.used, "plan": plan,
             "pending_games_requests": pending}, indent=1))
    elif mode == "run":
        run_all.main(flags, client=client)
    else:
        raise SystemExit(f"unknown mode {mode!r}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "plan")
