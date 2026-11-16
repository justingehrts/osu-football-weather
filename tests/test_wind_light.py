"""The lowest wind bin is now "light" (it was "calm"). Rain also has a "light" bin, so nothing may confuse the two.
Old forecast snapshots (append-only) and old shared links still say "calm" and must keep working. Offline."""
import sqlite3

from lib import config, data, logic, plain
from pipeline import common, weather_bins
from test_app import BINS, run_page, windy_stats


def test_config_and_classifier_use_light():
    assert "light" in BINS["wind"] and "calm" not in BINS["wind"]
    assert [weather_bins.classify_wind(s, g, BINS) for s, g in ((5, None), (9.4, 19), (10, 10), (14.6, 14.6))] == \
        ["light", "light", "moderate", "windy"]


def test_names_that_depend_on_the_bin_are_keyed_by_dimension():
    assert logic.WIND_NAME["light"] == "Light wind" and logic.PRECIP_NAME["light"] == "Light rain"
    assert logic.games_word("wind", "light") == "light-wind" and logic.games_word("precip", "light") == "light-rain"
    assert plain.games_word("wind", "light") == "light-wind" and plain.games_word("precip", "light") == "light-rain"
    assert logic.vs_not("wind", "light") == "light wind vs. other winds" and logic.vs_not("precip", "light") == "light rain vs. other games"
    assert logic.condition_badges("light", "light", None) == ["Light wind", "Light rain"]


def test_old_calm_labels_are_read_as_light_but_never_rewritten(tmp_path):
    assert logic.legacy_wind("calm") == "light" and logic.legacy_wind("windy") == "windy" and logic.legacy_wind(None) is None
    f = sqlite3.connect(tmp_path / "f.sqlite")
    f.row_factory = sqlite3.Row
    f.execute("CREATE TABLE forecast_snapshots(snapshot_utc TEXT, game_id INT, status TEXT, wind_bin TEXT)")
    f.executemany("INSERT INTO forecast_snapshots VALUES (?,?,?,?)", [("2026-11-01T00:00:00", 1, "ok", "calm"), ("2026-11-02T00:00:00", 1, "ok", "windy")])
    assert data.latest_forecast(f, 1)["wind_bin"] == "windy"
    assert list(data.forecast_history(f, 1).wind_bin) == ["light", "windy"]          # the trend sentence compares like with like
    assert [r[0] for r in f.execute("SELECT wind_bin FROM forecast_snapshots ORDER BY snapshot_utc")] == ["calm", "windy"]   # stored rows untouched
    cond = logic.conditions_from({"status": "ok", "wind_bin": "calm", "precip_bin": "none", "temp_bin": "mild"}, {})
    assert cond["wind"] == "light"
    assert plain.forecast_brief({"wind_bin": "calm", "precip_bin": "none"}) == "Light wind · Dry"


def test_history_database_is_relabelled_once_and_precipitation_light_is_left_alone():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE weather_obs(game_id INT, wind_bin TEXT)")
    db.execute("CREATE TABLE team_splits(team TEXT, bin_type TEXT, bin_value TEXT)")
    db.execute("CREATE TABLE team_tiers(team TEXT, bin_type TEXT, bin_value TEXT)")
    db.executemany("INSERT INTO weather_obs VALUES (?,?)", [(1, "calm"), (2, "windy")])
    for t in ("team_splits", "team_tiers"):
        db.executemany(f"INSERT INTO {t} VALUES (?,?,?)", [("A", "wind", "calm"), ("A", "precip", "light"), ("A", "wind", "windy")])
    common.rename_wind_bin(db, "calm", "light")
    common.rename_wind_bin(db, "calm", "light")                                       # idempotent
    assert [r[0] for r in db.execute("SELECT wind_bin FROM weather_obs ORDER BY game_id")] == ["light", "windy"]
    for t in ("team_splits", "team_tiers"):
        assert sorted(db.execute(f"SELECT bin_type, bin_value FROM {t}").fetchall()) == [("precip", "light"), ("wind", "light"), ("wind", "windy")]


def test_committed_database_has_no_calm_left():
    conn = data.connect_ro(config.DB_PATH)
    assert conn.execute("SELECT COUNT(*) FROM weather_obs WHERE wind_bin = 'calm'").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM team_splits WHERE bin_value = 'calm'").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM team_tiers WHERE bin_value = 'calm'").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM team_splits WHERE bin_type = 'wind' AND bin_value = 'light'").fetchone()[0] > 0


def test_old_shared_link_with_wind_calm_opens_the_light_wind_view():
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app/streamlit_app.py"), default_timeout=90)
    at.query_params["wind"] = "calm"
    at.run()
    assert not at.exception
    assert [s for s in at.selectbox if s.label == "Wind"][0].value == "Light wind"
    assert any("Wind: light wind vs. other winds" in m.value for m in at.markdown)


def test_gameday_page_says_light_wind_and_never_calm():
    at = run_page("app/streamlit_app.py")
    [s for s in at.selectbox if s.label == "Wind"][0].select("Light wind")
    [s for s in at.selectbox if s.label == "Precipitation"][0].select("Light rain")
    at.run()
    assert not at.exception
    page = " ".join(m.value for m in at.markdown).lower()
    assert "light wind" in page and "light rain" in page and "calm" not in page
    assert "light-wind games" in page or "light-rain games" in page
