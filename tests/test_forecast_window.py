"""A game that has come into forecast range since the last pull must not be called 'beyond the forecast horizon'. Offline."""
from pathlib import Path

import yaml

from lib import logic
from test_app import BINS, TEAMS, card_game, windy_stats

# the real Oregon row from Sat Oct 31: pulled when the game was 7.6 days out
EARLY = {"status": "beyond_horizon", "snapshot_utc": "2026-10-31T07:04:27+00:00", "kickoff_utc": "2026-11-07T20:30:00+00:00",
         "hours_ahead": 181.4, "note": "kickoff is 7.6 days out; forecasts reach about 6.5 days"}


def test_an_early_beyond_horizon_row_is_recognised_once_the_game_is_in_range():
    assert logic.came_into_range_since(EARLY, BINS, now="2026-11-02T16:03:00Z")          # 148 h out: inside the 156 h horizon
    assert not logic.came_into_range_since(EARLY, BINS, now="2026-11-01T00:00:00Z")      # 164 h out: still beyond
    assert not logic.came_into_range_since(EARLY, BINS, now="2026-11-08T00:00:00Z")      # kickoff has passed


def test_a_row_made_inside_the_horizon_that_could_not_cover_the_window_is_still_beyond_the_forecast():
    far_end = {**EARLY, "hours_ahead": 150.0, "note": "nws: forecast covers only 40% of the game window"}
    assert not logic.came_into_range_since(far_end, BINS, now="2026-11-02T16:03:00Z")
    assert not logic.came_into_range_since({**EARLY, "status": "ok"}, BINS, now="2026-11-02T16:03:00Z")
    assert not logic.came_into_range_since(None, BINS)


def test_the_card_says_a_pull_is_due_instead_of_beyond_the_horizon():
    game = card_game(kickoff_utc="2026-11-07T20:30:00Z")
    now_in_range = logic.build_gameday_view(windy_stats(), BINS, TEAMS, game, EARLY, {}, now="2026-11-02T16:03:00Z")
    assert "come into forecast range since the last forecast pull (Sat Oct 31, 3:04 AM ET" in now_in_range["takeaway"]
    assert "7.6 days out" in now_in_range["takeaway"] and "beyond the forecast horizon" not in now_in_range["takeaway"]
    still_far = logic.build_gameday_view(windy_stats(), BINS, TEAMS, game, EARLY, {}, now="2026-10-31T08:00:00Z")
    assert "beyond the forecast horizon" in still_far["takeaway"]


def test_the_forecast_workflow_runs_every_day_including_sunday_and_monday():
    wf = yaml.safe_load((Path(__file__).resolve().parents[1] / ".github/workflows/forecast.yml").read_text())
    cron = (wf.get("on") or wf[True])["schedule"][0]["cron"]          # (YAML reads a bare `on` as True)
    minute, hours, dom, months, dow = cron.split()
    assert dow == "*", "Sunday and Monday pulls are what bring next Saturday's game into range"
    assert months == "8-12,1" and len(hours.split(",")) == 4
