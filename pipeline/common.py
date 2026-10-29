"""Shared helpers: paths, config, database, HTTP, distance."""
import math
import os
import sqlite3
from datetime import date
from pathlib import Path

import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
REPORT_DIR = ROOT / "reports"
RAW_DIR = DATA_DIR / "raw"            # every CFBD response, committed
COUNTER_PATH = DATA_DIR / "cfbd_calls.json"
FORECAST_DB_PATH = DATA_DIR / "forecasts.sqlite"   # small, separate file: forecast snapshots commit often
DB_PATH = DATA_DIR / "osu_weather.db"


def load_yaml(name):
    path = CONFIG_DIR / name
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def load_bins():
    return load_yaml("bins.yaml")


def connect(db_path=DB_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # team_splits is derived (rebuilt every run), so if its layout is old just drop it.
    cols = [r[1] for r in conn.execute("PRAGMA table_info(team_splits)")]
    if cols and "ctl_rest" not in cols:
        conn.execute("DROP TABLE team_splits")
    schema = (Path(__file__).parent / "schema.sql").read_text()
    split = schema.index("DROP VIEW IF EXISTS team_game_weather;")
    conn.executescript(schema[:split])                       # tables: CREATE ... IF NOT EXISTS, a no-op once they exist
    # The view is dropped and recreated ONLY if its definition changed. Doing it on every open rewrote the
    # database file each time, so even a run that changed no data produced a different 900 KB file to commit.
    wanted = "CREATE VIEW" + schema[split:].split("CREATE VIEW", 1)[1]
    have = conn.execute("SELECT sql FROM sqlite_master WHERE type='view' AND name='team_game_weather'").fetchone()
    norm = lambda t: " ".join(t.replace(";", " ").split())  # noqa: E731
    if have is None or norm(have[0]) != norm(wanted):
        conn.execute("DROP VIEW IF EXISTS team_game_weather")
        conn.executescript(wanted)
    # tables that already exist in the committed database get any newer columns added in place
    for table, cols_ in {"games": {"home_class": "TEXT", "away_class": "TEXT"},
                         "venues": {"first_seen": "TEXT"}}.items():
        have = {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}
        for col, typ in cols_.items():
            if col not in have:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typ}")
                if col == "first_seen":     # venues that existed before this column were loaded earlier
                    conn.execute("UPDATE venues SET first_seen = '2026-10-27' WHERE first_seen IS NULL")
    conn.commit()      # without this the in-place migration above was silently rolled back on close
    return conn


def http_session():
    """requests session that retries transient failures (IEM/CFBD hiccup now and then)."""
    s = requests.Session()
    retry = Retry(total=4, backoff_factor=2, status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods=("GET",))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers["User-Agent"] = "osu-football-weather (research; contact repo owner)"
    return s


def haversine_mi(lat1, lon1, lat2, lon2):
    r = 3958.8  # earth radius, miles
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dlmb = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def current_season(today=None):
    """CFB seasons run Aug-Jan, so January bowl games still belong to last year's season."""
    today = today or date.today()
    return today.year if today.month >= 6 else today.year - 1


def tracked_teams():
    """Focal team + every opponent on its configured season's schedule (+ extras - excluded)."""
    cfg = load_yaml("teams.yaml")
    res = load_yaml("opponents.yaml")
    if res and res.get("season") != cfg["season"]:
        raise SystemExit(f"config/opponents.yaml is for season {res.get('season')} but teams.yaml says "
                         f"{cfg['season']}. Run `python -m pipeline.resolve_opponents --force`.")
    teams = [cfg["focal_team"]] + list(res.get("opponents", [])) + list(cfg.get("extra_teams") or [])
    drop = set(cfg.get("exclude_teams") or [])
    return [t for t in dict.fromkeys(teams) if t not in drop]  # de-dupe, keep order


def deferred_teams():
    """Tracked teams whose history we have chosen NOT to load yet (config/opponents.yaml `deferred`).
    They stay on the team list (and in the schedule) but nothing is requested or computed for them."""
    return list(load_yaml("opponents.yaml").get("deferred") or [])


FORECAST_SCHEMA = """
-- One row per forecast pull per game. NEVER updated or deleted: forecasts change, and the history
-- (what we knew, and when) is the point.
CREATE TABLE IF NOT EXISTS forecast_snapshots (
  snapshot_utc TEXT NOT NULL, game_id INTEGER NOT NULL,
  status TEXT NOT NULL,            -- ok | beyond_horizon | no_kickoff_time | no_venue | error
  source TEXT,                     -- nws | open-meteo
  kickoff_utc TEXT, hours_ahead REAL, window_start TEXT, window_end TEXT,
  wind_sust REAL, wind_gust REAL,  -- mph, max over the game window
  precip_prob REAL,                -- %, max over the window
  precip_amt REAL,                 -- inches over the window
  temp_f REAL,                     -- mean over the window
  wind_bin TEXT, precip_bin TEXT, temp_bin TEXT,
  precip_uncertain INTEGER,        -- 1 = chance of rain is in the middle band: show dry AND wet
  detail TEXT,                     -- hourly values used, JSON
  note TEXT
);
CREATE INDEX IF NOT EXISTS idx_fs_game ON forecast_snapshots(game_id, snapshot_utc);
"""


def connect_forecasts(db_path=FORECAST_DB_PATH):
    db_path = Path(db_path)
    if str(db_path) != ":memory:":
        db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(FORECAST_SCHEMA)
    return conn


def step_summary(markdown):
    """Add text to the run's Summary page in GitHub Actions (the first thing you see when you open a run).
    Does nothing outside Actions, so local runs and tests are unaffected."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a") as f:
            f.write(markdown.rstrip() + "\n\n")
