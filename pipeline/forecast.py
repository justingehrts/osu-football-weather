"""Forecast ingestion: what will the weather be during each upcoming game?

For every upcoming game of a loaded team we look up the venue's coordinates and ask
  1. the National Weather Service (api.weather.gov) for its hourly GRIDPOINT forecast, and,
     only if that fails,
  2. Open-Meteo (a free global model service) as a fallback,
then boil the hours between kickoff and kickoff + 3.5 h (`game_window_hours`) down to the same
numbers the history uses -- strongest sustained wind, strongest gust, total rain, mean
temperature -- and put them in the same bins (calm/moderate/windy, none/light/steady, cold/...)
defined in config/bins.yaml. That is what lets the app say "games like this one".

Honesty rules:
* Every pull is stored as a NEW timestamped row in data/forecasts.sqlite. Rows are never updated
  or deleted, so we can always see what the forecast said and when.
* A game further out than `forecast.horizon_hours` (about 6.5 days -- as far as the NWS hourly
  grid goes) gets a row saying "beyond_horizon". We do not guess, and we do not stretch a longer
  model range to fill the gap.
* Indoor (dome) games never get a forecast; the app says "indoor, weather not a factor".
* A middle-of-the-road chance of rain (`precip_prob_middle`, 30-70%) is flagged `uncertain`
  so the app shows the dry and wet histories side by side instead of picking one.
"""
import json
import re
from datetime import datetime, timedelta, timezone

from .common import CACHE_DIR, connect, connect_forecasts, http_session, load_bins, step_summary
from .weather_bins import classify_precip, classify_temp, classify_wind

NWS = "https://api.weather.gov"
OPEN_METEO = "https://api.open-meteo.com/v1/forecast"
KMH_TO_MPH = 0.621371
POINTS_CACHE = CACHE_DIR / "nws_points.json"     # lat,lon -> gridpoint URL (a place's grid cell never changes)

_DUR = re.compile(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?)?$")


# --------------------------------------------------------------------------- NWS parsing
def parse_duration(text):
    """ISO-8601 duration such as 'PT1H', 'PT6H', 'P1DT6H' -> timedelta."""
    m = _DUR.match(text)
    if not m:
        raise ValueError(f"unrecognised duration {text!r}")
    d, h, mi = (int(x) if x else 0 for x in m.groups())
    return timedelta(days=d, hours=h, minutes=mi)


def parse_valid_time(text):
    """'2026-10-31T16:00:00+00:00/PT3H' -> (start, end) as UTC datetimes."""
    start_s, dur_s = text.split("/")
    start = datetime.fromisoformat(start_s.replace("Z", "+00:00")).astimezone(timezone.utc)
    return start, start + parse_duration(dur_s)


def _series(prop):
    """NWS grid property -> [(start, end, value)], dropping nulls."""
    out = []
    for v in (prop or {}).get("values", []):
        if v.get("value") is None:
            continue
        s, e = parse_valid_time(v["validTime"])
        out.append((s, e, float(v["value"])))
    return out


def _overlap_hours(a0, a1, b0, b1):
    return max(0.0, (min(a1, b1) - max(a0, b0)).total_seconds() / 3600)


def summarize_nws(grid, start, end):
    """Boil an NWS gridpoint response down to the game window.

    Temperature is averaged (weighted by hours in the window); wind, gust and chance of rain take
    the window MAXIMUM (a gust anywhere in the game matters); rain amounts are added up, with
    multi-hour amounts split in proportion to how much of their period falls inside the window.
    `coverage` = share of the window the temperature series actually covers.
    """
    props = grid["properties"] if "properties" in grid else grid
    window_h = (end - start).total_seconds() / 3600

    def window_items(name):
        return [(s, e, v, _overlap_hours(s, e, start, end)) for s, e, v in _series(props.get(name)) if _overlap_hours(s, e, start, end) > 0]

    temps = window_items("temperature")
    covered = sum(o for *_, o in temps)
    temp_f = None
    if covered:
        temp_c = sum(v * o for _, _, v, o in temps) / covered
        temp_f = temp_c * 9 / 5 + 32
    winds = [v for _, _, v, _ in window_items("windSpeed")]
    gusts = [v for _, _, v, _ in window_items("windGust")]
    pops = [v for _, _, v, _ in window_items("probabilityOfPrecipitation")]
    qpf = window_items("quantitativePrecipitation")
    amount_mm = sum(v * o / max((e - s).total_seconds() / 3600, 1e-9) for s, e, v, o in qpf)
    hours = []
    h = start.replace(minute=0, second=0, microsecond=0)
    series = {k: _series(props.get(k)) for k in ("temperature", "windSpeed", "windGust", "probabilityOfPrecipitation",
                                               "quantitativePrecipitation")}

    def at(name, t):
        return next((v for s_, e_, v in series[name] if s_ <= t < e_), None)
    while h < end:
        rain_mm = sum(v * _overlap_hours(s_, e_, h, h + timedelta(hours=1)) / max((e_ - s_).total_seconds() / 3600, 1e-9)
                      for s_, e_, v in series["quantitativePrecipitation"])
        t_c, w, g = at("temperature", h), at("windSpeed", h), at("windGust", h)
        hours.append({"time": h.isoformat(), "wind": None if w is None else round(w * KMH_TO_MPH, 1),
                      "gust": None if g is None else round(g * KMH_TO_MPH, 1), "pop": at("probabilityOfPrecipitation", h),
                      "rain_in": round(rain_mm / 25.4, 3), "temp_f": None if t_c is None else round(t_c * 9 / 5 + 32, 1)})
        h += timedelta(hours=1)
    return {
        "hours": hours,
        "wind_sust": max(winds) * KMH_TO_MPH if winds else None,
        "wind_gust": max(gusts) * KMH_TO_MPH if gusts else None,
        "precip_prob": max(pops) if pops else None,
        "precip_amt": amount_mm / 25.4 if qpf else None,
        "temp_f": temp_f,
        "coverage": min(1.0, covered / window_h) if window_h else 0.0,
    }


# --------------------------------------------------------------------------- Open-Meteo parsing
def summarize_open_meteo(data, start, end):
    """Same summary from Open-Meteo's hourly arrays (times are UTC; rain at hour t covers the hour before t)."""
    h = data["hourly"]
    times = [datetime.fromisoformat(t).replace(tzinfo=timezone.utc) for t in h["time"]]
    hour0 = start.replace(minute=0, second=0, microsecond=0)
    idx = [i for i, t in enumerate(times) if hour0 <= t <= end]
    window_h = (end - start).total_seconds() / 3600

    def col(name):
        return [h[name][i] for i in idx if h.get(name) and h[name][i] is not None]

    rain = 0.0
    for i, t in enumerate(times):
        ov = _overlap_hours(t - timedelta(hours=1), t, start, end)
        if ov > 0 and h.get("precipitation") and h["precipitation"][i] is not None:
            rain += h["precipitation"][i] * ov
    temps, winds, gusts, pops = col("temperature_2m"), col("wind_speed_10m"), col("wind_gusts_10m"), col("precipitation_probability")
    expected = max(1, int(window_h) + 1)
    hours = [{"time": times[i].isoformat(), "wind": h["wind_speed_10m"][i], "gust": h["wind_gusts_10m"][i],
              "pop": h["precipitation_probability"][i], "rain_in": h["precipitation"][i], "temp_f": h["temperature_2m"][i]}
             for i in idx if times[i] < end]
    return {
        "hours": hours,
        "wind_sust": max(winds) if winds else None, "wind_gust": max(gusts) if gusts else None,
        "precip_prob": max(pops) if pops else None, "precip_amt": rain if h.get("precipitation") else None,
        "temp_f": sum(temps) / len(temps) if temps else None,
        "coverage": min(1.0, len(temps) / expected),
    }


# --------------------------------------------------------------------------- bins
def classify_forecast(sm, bins):
    """Window summary -> the bin labels the history uses (+ whether the rain call is a toss-up)."""
    lo, hi = bins["forecast"]["precip_prob_middle"]
    prob, amt = sm.get("precip_prob"), sm.get("precip_amt")
    wind = classify_wind(sm.get("wind_sust"), sm.get("wind_gust"), bins)
    temp = classify_temp(sm.get("temp_f"), bins)
    uncertain = prob is not None and lo <= prob < hi
    if uncertain:
        precip = "uncertain"                      # app shows dry AND wet
    elif prob is not None and prob < lo:
        precip = "none"
    else:
        precip = classify_precip(amt if amt is not None else 0.0, bins)
        if precip == "none" and prob is not None and prob >= hi:
            precip = "light"                      # a likely-rain forecast with ~0.00 in. still means wet
    return wind, precip, temp, int(uncertain)


# --------------------------------------------------------------------------- fetching
def _headers(bins):
    return {"User-Agent": bins["forecast"]["user_agent"], "Accept": "application/geo+json"}


def fetch_nws(session, lat, lon, bins, points_cache):
    key = f"{lat:.4f},{lon:.4f}"
    grid_url = points_cache.get(key)
    if grid_url is None:
        r = session.get(f"{NWS}/points/{lat:.4f},{lon:.4f}", headers=_headers(bins), timeout=30)
        r.raise_for_status()
        grid_url = r.json()["properties"]["forecastGridData"]
        points_cache[key] = grid_url
    r = session.get(grid_url, headers=_headers(bins), timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_open_meteo(session, lat, lon):
    params = {"latitude": lat, "longitude": lon, "timezone": "UTC", "forecast_days": 8,
              "temperature_unit": "fahrenheit", "wind_speed_unit": "mph", "precipitation_unit": "inch",
              "hourly": "temperature_2m,precipitation_probability,precipitation,wind_speed_10m,wind_gusts_10m"}
    r = session.get(OPEN_METEO, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def _load_points():
    return json.loads(POINTS_CACHE.read_text()) if POINTS_CACHE.exists() else {}


def _save_points(cache):
    POINTS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    POINTS_CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True))


# --------------------------------------------------------------------------- one game
def forecast_for_game(game, session, bins, now, points_cache):
    """-> dict of snapshot columns (status 'ok' or an explanation) for one outdoor game."""
    f = bins["forecast"]
    kickoff = datetime.fromisoformat(game["kickoff_utc"].replace("Z", "+00:00")).astimezone(timezone.utc)
    end = kickoff + timedelta(hours=bins["game_window_hours"])
    hours_ahead = (kickoff - now).total_seconds() / 3600
    base = {"kickoff_utc": kickoff.isoformat(), "hours_ahead": round(hours_ahead, 1),
            "window_start": kickoff.isoformat(), "window_end": end.isoformat()}
    if hours_ahead > f["horizon_hours"]:
        return {**base, "status": "beyond_horizon", "note": f"kickoff is {hours_ahead / 24:.1f} days out; "
                f"forecasts reach about {f['horizon_hours'] / 24:.1f} days"}
    attempts, summary, source = [], None, None
    for name, fetch in (("nws", lambda: summarize_nws(fetch_nws(session, game["lat"], game["lon"], bins, points_cache), kickoff, end)),
                        ("open-meteo", lambda: summarize_open_meteo(fetch_open_meteo(session, game["lat"], game["lon"]), kickoff, end))):
        try:
            sm = fetch()
        except Exception as e:  # noqa: BLE001 - any provider failure just moves us to the next one
            attempts.append(f"{name}: {type(e).__name__}")
            continue
        if sm["coverage"] < f["min_window_coverage"] or sm["wind_sust"] is None:
            attempts.append(f"{name}: forecast covers only {sm['coverage']:.0%} of the game window")
            continue
        summary, source = sm, name
        break
    if summary is None:
        if attempts and all("covers only" in a for a in attempts):
            return {**base, "status": "beyond_horizon", "note": "; ".join(attempts)}
        return {**base, "status": "error", "note": "; ".join(attempts) or "no forecast source answered"}
    wind, precip, temp, uncertain = classify_forecast(summary, bins)
    detail = json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in summary.items()})   # incl. hour-by-hour values
    return {**base, "status": "ok", "source": source, "detail": detail,
            **{k: summary[k] for k in ("wind_sust", "wind_gust", "precip_prob", "precip_amt", "temp_f")},
            "wind_bin": wind, "precip_bin": precip, "temp_bin": temp, "precip_uncertain": uncertain,
            "note": ("; ".join(attempts) + " -> used fallback") if attempts else None}


# --------------------------------------------------------------------------- the job
COLS = ["snapshot_utc", "game_id", "status", "source", "kickoff_utc", "hours_ahead", "window_start", "window_end",
        "wind_sust", "wind_gust", "precip_prob", "precip_amt", "temp_f", "wind_bin", "precip_bin", "temp_bin",
        "precip_uncertain", "detail", "note"]


def upcoming_games(conn, now):
    """Games not yet finished whose kickoff is still ahead (or too uncertain to tell)."""
    rows = conn.execute(
        """SELECT g.game_id, g.kickoff_utc, g.kickoff_tbd, g.venue_id, v.lat, v.lon, v.dome, v.name venue
           FROM games g LEFT JOIN venues v ON v.venue_id = g.venue_id
           WHERE g.completed = 0 ORDER BY g.kickoff_utc""").fetchall()
    out = []
    for r in rows:
        if r["kickoff_utc"] and not r["kickoff_tbd"]:
            k = datetime.fromisoformat(r["kickoff_utc"].replace("Z", "+00:00"))
            if k < now - timedelta(hours=1):
                continue                      # already under way or long past
        out.append(dict(r))
    return out


def _recent_same(fconn, game_id, status, now, hours):
    last = fconn.execute("SELECT snapshot_utc, status FROM forecast_snapshots WHERE game_id=? "
                         "ORDER BY snapshot_utc DESC LIMIT 1", (game_id,)).fetchone()
    if not last or last["status"] != status:
        return False
    return (now - datetime.fromisoformat(last["snapshot_utc"])).total_seconds() < hours * 3600


def forecast_summary(conn, wrote):
    """Markdown for the run page: what was stored, game by game, without opening the log."""
    lines = ["## Forecast snapshots", ""]
    if not wrote:
        return "\n".join(lines + ["**No new snapshots** (the latest ones are recent enough, or no upcoming games).", ""])
    counts = {}
    for _, status, *_ in wrote:
        counts[status] = counts.get(status, 0) + 1
    lines.append("**Stored " + str(len(wrote)) + " new rows:** " + ", ".join(f"{n} {k.replace('_', ' ')}" for k, n in sorted(counts.items())) + ".")
    ok = [w for w in wrote if w[1] == "ok"]
    if ok:
        lines += ["", "| Game | Source | Wind | Rain | Temp |", "|---|---|---|---|---|"]
        for gid, _, src, wb, pb, tb in ok:
            g = conn.execute("SELECT away_team, home_team FROM games WHERE game_id=?", (gid,)).fetchone()
            lines.append(f"| {g['away_team']} at {g['home_team']} | {src} | {wb} | {pb} | {tb} |")
    errors = [w for w in wrote if w[1] == "error"]
    if errors:
        lines.append(f"\n:warning: {len(errors)} game(s) got NO forecast because every source failed; they are stored as errors and will be retried.")
    return "\n".join(lines)


def run(conn=None, fconn=None, session=None, now=None):
    conn = conn or connect()
    fconn = fconn or connect_forecasts()
    bins = load_bins()
    now = now or datetime.now(timezone.utc)
    session = session or http_session()
    points = _load_points()
    f = bins["forecast"]
    wrote = []
    for g in upcoming_games(conn, now):
        if g["dome"] == 1:
            continue                           # indoor: nothing to forecast; the app says so
        if g["kickoff_tbd"] or not g["kickoff_utc"]:
            snap = {"status": "no_kickoff_time", "note": "kickoff time not announced yet"}
        elif g["lat"] is None:
            snap = {"status": "no_venue", "note": "venue coordinates unknown"}
        else:
            snap = forecast_for_game(g, session, bins, now, points)
        hours = f["min_hours_between_beyond_horizon_rows"] if snap["status"] != "ok" else f["min_hours_between_snapshots"]
        if _recent_same(fconn, g["game_id"], snap["status"], now, hours):
            continue
        row = {c: snap.get(c) for c in COLS}
        row.update(snapshot_utc=now.isoformat(timespec="seconds"), game_id=g["game_id"])
        fconn.execute(f"INSERT INTO forecast_snapshots({','.join(COLS)}) VALUES ({','.join('?' * len(COLS))})",
                      [row[c] for c in COLS])
        wrote.append((g["game_id"], snap["status"], snap.get("source"), snap.get("wind_bin"), snap.get("precip_bin"), snap.get("temp_bin")))
    fconn.commit()
    _save_points(points)
    step_summary(forecast_summary(conn, wrote))
    print(f"forecast snapshots written: {len(wrote)}")
    for w in wrote:
        print("  game", *w)
    return wrote


if __name__ == "__main__":
    run()
