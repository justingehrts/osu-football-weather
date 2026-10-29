"""Paths and config for the app. The app only READS: the database is opened read-only and the
YAML files are never written."""
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.environ.get("OSU_DB_PATH", ROOT / "data" / "osu_weather.db"))
FORECAST_DB_PATH = Path(os.environ.get("OSU_FORECAST_DB_PATH", ROOT / "data" / "forecasts.sqlite"))
CONFIG_DIR = Path(os.environ.get("OSU_CONFIG_DIR", ROOT / "config"))


def _yaml(name):
    f = CONFIG_DIR / name
    return yaml.safe_load(f.read_text()) or {} if f.exists() else {}


def load_bins():
    return _yaml("bins.yaml")


def load_teams():
    """-> dict(focal, season, tracked, deferred, loaded)."""
    t, o = _yaml("teams.yaml"), _yaml("opponents.yaml")
    tracked = list(dict.fromkeys([t["focal_team"]] + list(o.get("opponents", [])) + list(t.get("extra_teams") or [])))
    tracked = [x for x in tracked if x not in set(t.get("exclude_teams") or [])]
    deferred = [x for x in (o.get("deferred") or []) if x in tracked]
    return {"focal": t["focal_team"], "season": t["season"], "tracked": tracked, "deferred": deferred,
            "loaded": [x for x in tracked if x not in deferred]}
