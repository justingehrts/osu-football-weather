"""CollegeFootballData client with a disk cache and a hard monthly call budget.

CFBD's free tier allows 1,000 calls a month, and an early version of this pipeline burned
437 of them by re-downloading the same seasons on every run. Three guards stop that:

1. CACHE   every response is saved under data/raw/ and committed. A request whose file
           exists is never sent again. (Only the CURRENT season can change, so those
           requests carry a time limit -- see `ttl_hours`; past seasons never expire.)
2. COUNTER data/cfbd_calls.json counts every call this month and survives restarts.
3. CAP     a run aborts BEFORE a call that would take the month past `monthly_cap`
           (600 in bins.yaml), leaving headroom under the real 1,000 limit.

Retries are limited to connection failures (which never reached CFBD), so the counter
stays accurate.
"""
import json
import os
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import quote

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .common import COUNTER_PATH, RAW_DIR, http_session, load_bins

BASE = os.environ.get("CFBD_BASE_URL", "https://api.collegefootballdata.com")


class BudgetExceeded(SystemExit):
    """Raised before a call that would break the monthly cap."""


def _utcnow():
    return datetime.now(timezone.utc)


class CallCounter:
    def __init__(self, path=COUNTER_PATH, cap=None, now=_utcnow):
        self.path, self.now = path, now
        self.cap = cap if cap is not None else load_bins()["cfbd"]["monthly_cap"]
        self.state = {"month": self._month(), "calls": 0, "log": []}
        if self.path.exists():
            self.state = json.loads(self.path.read_text())
        if self.state["month"] != self._month():     # CFBD's quota resets monthly
            self.state = {"month": self._month(), "calls": 0, "log": []}

    def _month(self):
        return self.now().strftime("%Y-%m")

    @property
    def used(self):
        return self.state["calls"]

    @property
    def remaining_under_cap(self):
        return self.cap - self.used

    def check(self, n=1):
        if self.used + n > self.cap:
            raise BudgetExceeded(
                f"Stopping: {n} more call(s) would take this month to {self.used + n}, past the "
                f"{self.cap}-call cap ({self.used} used so far). Nothing was sent. Raise "
                f"cfbd.monthly_cap in config/bins.yaml only if you mean to.")

    def record(self, label):
        self.state["calls"] += 1
        self.state["log"] = (self.state["log"] + [[self.now().isoformat(timespec="seconds"), label]])[-300:]
        self.save()

    def sync(self, api_used):
        """CFBD's own count is the truth (other tools share the quota; /info itself is not billed)."""
        self.state["calls"] = api_used
        self.state["synced_with_cfbd"] = self.now().isoformat(timespec="seconds")
        self.save()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.state, indent=1))

    def calls_this_run_since(self, start_calls):
        return self.used - start_calls


class CfbdClient:
    def __init__(self, session=None, counter=None, raw_dir=RAW_DIR, offline=False, now=_utcnow):
        self.raw_dir, self.offline, self.now = raw_dir, offline, now
        self.counter = counter or CallCounter(now=now)
        self.ttl_default = load_bins()["cfbd"]["current_season_ttl_hours"]
        self.session = session
        self.requests_sent = 0
        self.by_endpoint = Counter()      # calls actually sent by this client, per endpoint

    # ---- cache ----
    def cache_path(self, path, params):
        name = "&".join(f"{k}={quote(str(v), safe='')}" for k, v in sorted(params.items())) or "all"
        return self.raw_dir / path.strip("/").replace("/", "_") / f"{name}.json"

    def is_cached(self, path, ttl_hours=None, **params):
        f = self.cache_path(path, params)
        if not f.exists():
            return False
        if ttl_hours is None:
            return True
        age = self.now() - datetime.fromisoformat(json.loads(f.read_text())["fetched_at"])
        return age.total_seconds() < ttl_hours * 3600

    # ---- the one place a request can leave the building ----
    def get(self, path, ttl_hours=None, rewrite_if_same=True, **params):
        f = self.cache_path(path, params)
        if self.is_cached(path, ttl_hours, **params):
            return json.loads(f.read_text())["data"]
        if self.offline:
            raise RuntimeError(f"offline mode and no cache for {path} {params}")
        self.counter.check(1)
        self._ensure_session()
        self.counter.record(f"{path} {params}")       # count first: a failed call may still be billed
        self.requests_sent += 1
        self.by_endpoint[path] += 1
        r = self.session.get(f"{BASE}{path}", params=params, timeout=90)
        r.raise_for_status()
        data = r.json()
        if not rewrite_if_same and f.exists() and _canonical(json.loads(f.read_text())["data"]) == _canonical(data):
            return data      # same content: leave the file alone so a quiet check produces no change to commit
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps({"fetched_at": self.now().isoformat(timespec="seconds"),
                                 "params": params, "data": data}, separators=(",", ":")))
        return data

    def _ensure_session(self):
        if self.session is None:
            key = os.environ.get("CFBD_API_KEY")
            if not key:
                raise SystemExit("CFBD_API_KEY is not set (repository secret in Actions).")
            self.session = http_session()
            # connection-level retries only: a retry after an HTTP status might double-count
            self.session.mount("https://", HTTPAdapter(max_retries=Retry(total=3, connect=3, read=0,
                                                                         status=0, backoff_factor=2)))
            self.session.headers["Authorization"] = f"Bearer {key}"

    def info(self):
        """Remaining calls according to CFBD itself; also syncs our counter."""
        r = self._raw_get("/info")
        self.counter.sync(r.get("usedCalls", 0))
        return r

    def _raw_get(self, path):
        # uncached on purpose: the whole point is the live number
        self._ensure_session()
        r = self.session.get(f"{BASE}{path}", timeout=60)
        r.raise_for_status()
        return r.json()

    # ---- endpoints (names match CFBD) ----
    def games(self, year, season_type, week=None, team=None, ttl_hours=None, rewrite_if_same=True):
        p = {"year": year, "seasonType": season_type}
        p.update({k: v for k, v in (("week", week), ("team", team)) if v is not None})
        return self.get("/games", ttl_hours, rewrite_if_same, **p)

    def game_team_stats(self, year, season_type, week=None, team=None, ttl_hours=None):
        p = {"year": year, "seasonType": season_type}
        p.update({k: v for k, v in (("week", week), ("team", team)) if v is not None})
        return self.get("/games/teams", ttl_hours, **p)

    def ppa_games(self, year, season_type, week=None, team=None, ttl_hours=None):
        p = {"year": year, "seasonType": season_type, "excludeGarbageTime": "false"}
        p.update({k: v for k, v in (("week", week), ("team", team)) if v is not None})
        return self.get("/ppa/games", ttl_hours, **p)

    def sp_ratings(self, year, ttl_hours=None):
        return self.get("/ratings/sp", ttl_hours, year=year)

    def venues(self, ttl_hours=None):
        return self.get("/venues", ttl_hours)


def _canonical(data):
    """Order-insensitive form: CFBD returns the same games in a different order from one call to the next."""
    if isinstance(data, list) and all(isinstance(x, dict) and "id" in x for x in data):
        data = sorted(data, key=lambda x: x["id"])
    return json.dumps(data, sort_keys=True)


def pick(d, *names, default=None):
    """First present, non-None key among alternate spellings (camelCase / snake_case)."""
    for n in names:
        if d.get(n) is not None:
            return d[n]
    return default
