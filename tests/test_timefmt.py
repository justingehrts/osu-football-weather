"""Game times shown in the stadium's local time, with ET in brackets when they differ. Offline."""
import sqlite3

import pytest

from lib import charts, config, data, timefmt
from pipeline import venue_tz
from test_app import AppTest_game_ids, run_page

LA, CHI, NYC = "America/Los_Angeles", "America/Chicago", "America/New_York"
BINS = config.load_bins()


def test_eastern_games_just_say_et():
    assert timefmt.game_time("2026-10-31T23:30:00Z", NYC) == "Sat Oct 31, 7:30 PM ET"
    assert timefmt.game_time("2026-10-31T23:30:00Z", "America/Detroit") == "Sat Oct 31, 7:30 PM ET"


def test_other_zones_show_local_time_then_et_in_brackets():
    assert timefmt.game_time("2026-10-31T23:30:00Z", LA) == "Sat Oct 31, 4:30 PM PT (7:30 PM ET)"
    assert timefmt.game_time("2026-10-31T23:30:00Z", CHI) == "Sat Oct 31, 6:30 PM CT (7:30 PM ET)"
    assert timefmt.game_time("2026-10-31T23:30:00Z", "America/Denver") == "Sat Oct 31, 5:30 PM MT (7:30 PM ET)"


def test_the_zone_name_is_the_everyday_one_all_year():
    assert timefmt.game_time("2026-11-07T21:30:00Z", LA) == "Sat Nov 07, 1:30 PM PT (4:30 PM ET)"      # after the clocks change
    assert timefmt.game_time("2026-11-07T21:30:00Z", "America/Phoenix").endswith("MT (4:30 PM ET)")


def test_a_late_kickoff_out_west_names_the_et_day_when_it_is_already_tomorrow_there():
    t = "2026-11-01T05:30:00Z"
    assert timefmt.game_time(t, LA) == "Sat Oct 31, 10:30 PM PT (Sun 1:30 AM ET)"
    assert timefmt.local_day(t, LA) == "Oct 31"                       # the stadium's date, not ET's


def test_overseas_and_missing_zones():
    assert timefmt.game_time("2026-08-29T16:00:00Z", "Europe/Dublin").endswith("IST (12:00 PM ET)")
    assert timefmt.game_time("2026-10-31T23:30:00Z", None) == "Sat Oct 31, 7:30 PM ET"          # no zone stored: ET, no bracket
    assert timefmt.game_time("2026-10-31T23:30:00Z", float("nan")) == "Sat Oct 31, 7:30 PM ET"


def test_hourly_chart_uses_local_hours_with_et_in_brackets():
    hours = [{"time": "2026-11-01T01:00:00+00:00", "wind": 10, "gust": 15, "pop": 20, "rain_in": 0.0, "temp_f": 60}]
    local = [c.to_dict() for c in charts.hourly_charts(hours, BINS, LA)]
    bottom = local[1]["encoding"]["x"]
    assert bottom["title"] == "Hour (PT, with ET in brackets)"
    assert "6 PM PT|(9 PM ET)" in str(local) and "split(datum.label" in str(bottom)
    east = [c.to_dict() for c in charts.hourly_charts(hours, BINS, NYC)]
    assert east[1]["encoding"]["x"]["title"] == "Hour (ET)" and "9 PM" in str(east) and "|(" not in str(east)


def test_every_venue_has_a_time_zone_and_new_ones_get_filled():
    conn = data.connect_ro(config.DB_PATH)
    assert conn.execute("SELECT COUNT(*) FROM venues WHERE tz IS NULL AND lat IS NOT NULL").fetchone()[0] == 0
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE venues(venue_id INTEGER, lat REAL, lon REAL, tz TEXT)")
    db.executemany("INSERT INTO venues VALUES (?,?,?,?)", [(1, 34.014, -118.288, None), (2, 40.0, -83.02, "kept"), (3, None, None, None)])
    pytest.importorskip("timezonefinder")
    assert venue_tz.fill_missing(db) == 1
    assert dict(db.execute("SELECT venue_id, tz FROM venues").fetchall()) == {1: LA, 2: "kept", 3: None}


def test_gameday_card_shows_kickoff_in_the_stadiums_local_time():
    at = run_page("app/streamlit_app.py")
    usc = [g for g in AppTest_game_ids() if g[1] == "USC"][0][0]                # Ohio State at USC (Los Angeles)
    at.selectbox[0].set_value(usc).run()
    assert not at.exception
    meta = [c.value for c in at.caption if "Coliseum" in c.value][0]
    assert "PT (" in meta and "ET)" in meta
