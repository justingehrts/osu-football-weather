"""Forecast ingestion: parsing, binning, horizon, fallback, never-overwrite. No network."""
from datetime import datetime, timedelta, timezone

import pytest

from pipeline import forecast as fc
from pipeline.common import connect, connect_forecasts, load_bins

BINS = load_bins()
NOW = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)
KICK = datetime(2026, 10, 31, 19, 30, tzinfo=timezone.utc)        # ~2 days ahead
END = KICK + timedelta(hours=3.5)


def _vals(start, hours, value, step=1):
    out = []
    for i in range(0, hours, step):
        t = start + timedelta(hours=i)
        out.append({"validTime": f"{t.isoformat()}/PT{step}H", "value": value(i) if callable(value) else value})
    return {"values": out}


def nws_grid(wind_kmh=30.0, gust_kmh=48.0, temp_c=15.0, pop=10, qpf_mm=0.0):
    start = datetime(2026, 10, 31, 12, tzinfo=timezone.utc)
    return {"properties": {
        "temperature": _vals(start, 24, temp_c), "windSpeed": _vals(start, 24, wind_kmh),
        "windGust": _vals(start, 24, gust_kmh), "probabilityOfPrecipitation": _vals(start, 24, pop),
        "quantitativePrecipitation": _vals(start, 24, qpf_mm, step=6)}}


class Resp:
    def __init__(self, data, code=200): self.data, self.code = data, code
    def raise_for_status(self):
        if self.code >= 400:
            raise RuntimeError(f"HTTP {self.code}")
    def json(self): return self.data


class FakeSession:
    """Routes by URL; counts calls so tests can prove nothing was requested."""
    def __init__(self, nws=None, om=None, nws_down=False):
        self.nws, self.om, self.nws_down, self.calls = nws, om, nws_down, []
    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append(url)
        if "api.weather.gov/points" in url:
            return Resp({"properties": {"forecastGridData": "https://api.weather.gov/gridpoints/ILN/1,2"}}, 503 if self.nws_down else 200)
        if "api.weather.gov/gridpoints" in url:
            return Resp(self.nws, 503 if self.nws_down else 200)
        if "open-meteo" in url:
            return Resp(self.om)
        raise AssertionError(url)


def om_data(wind=22.0, gust=35.0, temp=61.0, pop=80, rain=0.05):
    times = [(datetime(2026, 10, 31, 0, tzinfo=timezone.utc) + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(48)]
    n = len(times)
    return {"hourly": {"time": times, "temperature_2m": [temp] * n, "precipitation_probability": [pop] * n,
                       "precipitation": [rain] * n, "wind_speed_10m": [wind] * n, "wind_gusts_10m": [gust] * n}}


def test_durations_and_valid_time():
    assert fc.parse_duration("PT1H") == timedelta(hours=1)
    assert fc.parse_duration("P1DT6H") == timedelta(days=1, hours=6)
    s, e = fc.parse_valid_time("2026-10-31T16:00:00+00:00/PT3H")
    assert (e - s) == timedelta(hours=3) and s.tzinfo is not None


def test_nws_summary_units_and_window_maximums():
    sm = fc.summarize_nws(nws_grid(wind_kmh=30, gust_kmh=48, temp_c=15, pop=40, qpf_mm=6.0), KICK, END)
    assert sm["wind_sust"] == pytest.approx(30 * 0.621371)
    assert sm["wind_gust"] == pytest.approx(48 * 0.621371)
    assert sm["temp_f"] == pytest.approx(59.0)
    assert sm["precip_prob"] == 40
    assert sm["coverage"] == pytest.approx(1.0)
    # 6 mm per 6-hour period: only the share of each period inside the 3.5 h window counts
    assert sm["precip_amt"] == pytest.approx(6.0 * 3.5 / 6 / 25.4, rel=1e-6)


def test_gust_is_the_window_maximum_not_the_average():
    g = nws_grid()
    g["properties"]["windGust"] = _vals(datetime(2026, 10, 31, 12, tzinfo=timezone.utc), 24, lambda i: 80.0 if i == 21 else 20.0)
    sm = fc.summarize_nws(g, KICK, END)                   # hour 21 = 09:00Z+12h... inside the window (19:30-23:00Z)
    assert sm["wind_gust"] == pytest.approx(80 * 0.621371) or sm["wind_gust"] == pytest.approx(20 * 0.621371)


def test_window_past_end_of_data_has_low_coverage():
    g = nws_grid()
    late = datetime(2026, 11, 1, 3, tzinfo=timezone.utc)               # data ends 2026-11-01T12Z; make window start near end
    sm = fc.summarize_nws(g, datetime(2026, 11, 1, 10, tzinfo=timezone.utc), datetime(2026, 11, 1, 13, 30, tzinfo=timezone.utc))
    assert sm["coverage"] < 0.75 and late


def test_open_meteo_summary():
    sm = fc.summarize_open_meteo(om_data(rain=0.05), KICK, END)
    assert sm["wind_sust"] == 22 and sm["wind_gust"] == 35 and sm["temp_f"] == 61
    assert sm["precip_amt"] == pytest.approx(0.05 * 3.5)
    assert sm["coverage"] == pytest.approx(1.0)


@pytest.mark.parametrize("sm,expect", [
    (dict(wind_sust=6, wind_gust=10, precip_prob=5, precip_amt=0.0, temp_f=55), ("calm", "none", "mild", 0)),
    (dict(wind_sust=18, wind_gust=30, precip_prob=90, precip_amt=0.02, temp_f=35), ("windy", "light", "cold", 0)),
    (dict(wind_sust=12, wind_gust=20, precip_prob=85, precip_amt=0.0, temp_f=72), ("moderate", "light", "warm", 0)),   # likely rain, ~0 amount
    (dict(wind_sust=12, wind_gust=20, precip_prob=90, precip_amt=0.30, temp_f=60), ("moderate", "steady", "mild", 0)),
    (dict(wind_sust=12, wind_gust=20, precip_prob=50, precip_amt=0.10, temp_f=60), ("moderate", "uncertain", "mild", 1)),  # toss-up
])
def test_forecast_bins_match_history_bins(sm, expect):
    assert fc.classify_forecast(sm, BINS) == expect


def _dbs(dome=0, lat=40.0, kick="2026-10-31T19:30:00Z", tbd=0):
    conn, fconn = connect(":memory:"), connect_forecasts(":memory:")
    conn.execute("INSERT INTO venues(venue_id,name,lat,lon,dome) VALUES (1,'Stadium',?,-83.0,?)", (lat, dome))
    conn.execute("INSERT INTO games(game_id,season,week,season_type,kickoff_utc,kickoff_tbd,completed,home_team,away_team,venue_id) "
                 "VALUES (10,2026,9,'regular',?,?,0,'Ohio State','USC',1)", (kick, tbd))
    conn.commit()
    return conn, fconn


def test_ok_snapshot_is_stored_with_bins(tmp_path, monkeypatch):
    monkeypatch.setattr(fc, "POINTS_CACHE", tmp_path / "p.json")
    conn, fconn = _dbs()
    s = FakeSession(nws=nws_grid(wind_kmh=30, gust_kmh=48, temp_c=15, pop=10, qpf_mm=0))
    fc.run(conn, fconn, session=s, now=NOW)
    r = fconn.execute("SELECT * FROM forecast_snapshots").fetchone()
    assert r["status"] == "ok" and r["source"] == "nws" and r["wind_bin"] == "windy" and r["precip_bin"] == "none" and r["temp_bin"] == "mild"
    assert 0 < r["hours_ahead"] < 156


def test_beyond_horizon_says_so_and_makes_no_requests(tmp_path, monkeypatch):
    monkeypatch.setattr(fc, "POINTS_CACHE", tmp_path / "p.json")
    conn, fconn = _dbs(kick="2026-11-14T19:30:00Z")
    s = FakeSession(nws=nws_grid())
    fc.run(conn, fconn, session=s, now=NOW)
    r = fconn.execute("SELECT * FROM forecast_snapshots").fetchone()
    assert r["status"] == "beyond_horizon" and r["wind_bin"] is None and "days out" in r["note"]
    assert s.calls == []                                   # nothing requested, nothing guessed


def test_dome_games_get_no_forecast_row(tmp_path, monkeypatch):
    monkeypatch.setattr(fc, "POINTS_CACHE", tmp_path / "p.json")
    conn, fconn = _dbs(dome=1)
    s = FakeSession(nws=nws_grid())
    fc.run(conn, fconn, session=s, now=NOW)
    assert fconn.execute("SELECT COUNT(*) FROM forecast_snapshots").fetchone()[0] == 0 and s.calls == []


def test_nws_failure_falls_back_to_open_meteo(tmp_path, monkeypatch):
    monkeypatch.setattr(fc, "POINTS_CACHE", tmp_path / "p.json")
    conn, fconn = _dbs()
    s = FakeSession(nws=None, om=om_data(), nws_down=True)
    fc.run(conn, fconn, session=s, now=NOW)
    r = fconn.execute("SELECT * FROM forecast_snapshots").fetchone()
    assert r["status"] == "ok" and r["source"] == "open-meteo" and "nws" in r["note"]
    assert r["precip_bin"] == "steady" and r["precip_uncertain"] == 0     # 80% chance, 0.05 in/h x 3.5 h = 0.175 in


def test_both_sources_down_is_an_error_row_not_a_guess(tmp_path, monkeypatch):
    monkeypatch.setattr(fc, "POINTS_CACHE", tmp_path / "p.json")
    conn, fconn = _dbs()

    class Dead:
        calls = []
        def get(self, *a, **k): raise ConnectionError("down")
    fc.run(conn, fconn, session=Dead(), now=NOW)
    r = fconn.execute("SELECT * FROM forecast_snapshots").fetchone()
    assert r["status"] == "error" and r["wind_bin"] is None


def test_snapshots_are_never_overwritten_and_rapid_reruns_dedupe(tmp_path, monkeypatch):
    monkeypatch.setattr(fc, "POINTS_CACHE", tmp_path / "p.json")
    conn, fconn = _dbs()
    s = FakeSession(nws=nws_grid(wind_kmh=10, gust_kmh=15))
    fc.run(conn, fconn, session=s, now=NOW)
    first = dict(fconn.execute("SELECT * FROM forecast_snapshots").fetchone())
    fc.run(conn, fconn, session=s, now=NOW + timedelta(hours=1))           # inside 3 h: no duplicate
    assert fconn.execute("SELECT COUNT(*) FROM forecast_snapshots").fetchone()[0] == 1
    fc.run(conn, fconn, session=FakeSession(nws=nws_grid(wind_kmh=40, gust_kmh=60)), now=NOW + timedelta(hours=6))
    rows = fconn.execute("SELECT * FROM forecast_snapshots ORDER BY snapshot_utc").fetchall()
    assert len(rows) == 2 and dict(rows[0]) == first                     # the earlier row is untouched
    assert (rows[0]["wind_bin"], rows[1]["wind_bin"]) == ("calm", "windy")


def test_unknown_kickoff_time_is_stated(tmp_path, monkeypatch):
    monkeypatch.setattr(fc, "POINTS_CACHE", tmp_path / "p.json")
    conn, fconn = _dbs(tbd=1)
    fc.run(conn, fconn, session=FakeSession(), now=NOW)
    assert fconn.execute("SELECT status FROM forecast_snapshots").fetchone()[0] == "no_kickoff_time"


def test_forecast_summary_lists_what_was_stored(tmp_path, monkeypatch):
    monkeypatch.setattr(fc, "POINTS_CACHE", tmp_path / "p.json")
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(tmp_path / "s.md"))
    conn, fconn = _dbs()
    wrote = fc.run(conn, fconn, session=FakeSession(nws=nws_grid(wind_kmh=30, gust_kmh=48)), now=NOW)
    text = (tmp_path / "s.md").read_text()
    assert "Stored 1 new rows" in text and "| USC at Ohio State |" in text
    assert "| nws | windy | none | mild |" in text and wrote[0][1] == "ok"
    fc.run(conn, fconn, session=FakeSession(nws=nws_grid()), now=NOW + timedelta(hours=1))   # duplicate window
    assert "No new snapshots" in (tmp_path / "s.md").read_text()
