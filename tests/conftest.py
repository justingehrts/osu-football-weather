"""Shared test setup. The app reads its database paths from environment variables at import time, so
they are set HERE, before any app module is imported."""
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT))

_tmp = Path(tempfile.mkdtemp(prefix="osu-forecast-test-"))
FORECAST_FIXTURE = _tmp / "forecasts.sqlite"
os.environ["OSU_FORECAST_DB_PATH"] = str(FORECAST_FIXTURE)


def _build_forecast_fixture():
    from pipeline.common import connect_forecasts
    f = connect_forecasts(FORECAST_FIXTURE)
    db = sqlite3.connect(ROOT / "data" / "osu_weather.db")
    games = db.execute("""SELECT game_id FROM games WHERE season=2026 AND completed=0
                          AND (home_team='Ohio State' OR away_team='Ohio State') ORDER BY kickoff_utc""").fetchall()
    cols = ("snapshot_utc,game_id,status,source,hours_ahead,wind_sust,wind_gust,precip_prob,precip_amt,temp_f,"
            "wind_bin,precip_bin,temp_bin,precip_uncertain,note")
    if games:
        f.execute(f"INSERT INTO forecast_snapshots({cols}) VALUES ('2026-10-28T18:00:00',?, 'ok','nws',60,17,28,60,0.08,51,'windy','light','mild',0,NULL)", (games[0][0],))
    if len(games) > 1:
        f.execute(f"INSERT INTO forecast_snapshots({cols}) VALUES ('2026-10-28T18:00:00',?, 'beyond_horizon',NULL,210,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'kickoff is 8.8 days out')", (games[1][0],))
    if len(games) > 2:
        f.execute(f"INSERT INTO forecast_snapshots({cols}) VALUES ('2026-10-28T18:00:00',?, 'ok','nws',100,12,20,50,0.05,60,'moderate','uncertain','mild',1,NULL)", (games[2][0],))
    f.commit()


_build_forecast_fixture()


@pytest.fixture(autouse=True)
def _tests_never_write_the_real_run_summary(monkeypatch):
    """Inside GitHub Actions the variable GITHUB_STEP_SUMMARY points at the run's public Summary page.
    The refresh workflow runs these tests first, and the forecast tests exercise code that writes a summary --
    so without this, FAKE forecasts ("USC at Ohio State | windy") appeared on the real run page next to the real
    result. Every test now starts without it; a test that wants it sets it to its own temp file."""
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
