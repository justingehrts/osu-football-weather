"""Step 3: ASOS observations from IEM for each game window -> weather_obs rows."""
from datetime import datetime, timedelta, timezone
from io import StringIO

import pandas as pd

from .common import connect, http_session, load_bins
from .weather_bins import classify_all

IEM_ASOS = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"
KT_TO_MPH = 1.15078


def fetch_obs(session, station, start, end):
    """Routine (3) + special (4) METAR reports for one station, UTC."""
    params = {
        "station": station, "data": ["tmpf", "sknt", "gust", "p01i", "vsby", "wxcodes"],
        "year1": start.year, "month1": start.month, "day1": start.day,
        "hour1": start.hour, "minute1": start.minute,
        "year2": end.year, "month2": end.month, "day2": end.day,
        "hour2": end.hour, "minute2": end.minute,
        "tz": "UTC", "format": "onlycomma", "latlon": "no", "missing": "empty",
        "trace": "0.0001", "report_type": [3, 4],
    }
    r = session.get(IEM_ASOS, params=params, timeout=90)
    r.raise_for_status()
    df = pd.read_csv(StringIO(r.text))
    if df.empty:
        return df
    df["valid"] = pd.to_datetime(df["valid"], utc=True)
    for c in ("tmpf", "sknt", "gust", "p01i", "vsby"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def summarize_window(df, start, end):
    """Collapse observations to one row of game-window weather.

    Wind and temperature use every report inside [start, end]. Precipitation is
    trickier: p01i is the rain that fell in the hour *before* each report, and
    specials repeat it, so we keep one value per clock hour (the largest) and
    count an hourly value only if at least half of its hour overlaps the game window.
    """
    empty = {"temp_f_mean": None, "wind_sust_max": None, "wind_gust_max": None,
             "precip_in_total": None, "snow_flag": None, "vis_min": None, "n_obs": 0}
    if df is None or df.empty:
        return empty
    inw = df[(df["valid"] >= start) & (df["valid"] <= end)]
    if inw.empty:
        return empty

    precip = 0.0
    hourly = df.dropna(subset=["p01i"]).copy()
    if not hourly.empty:
        # a report at 16:53 covers 15:53-16:53 -> bucket by the hour it mostly describes
        hourly["bucket"] = (hourly["valid"] + pd.Timedelta(minutes=7)).dt.floor("h")
        for bucket, grp in hourly.groupby("bucket"):
            h_start, h_end = bucket - pd.Timedelta(hours=1), bucket
            overlap = min(h_end, end) - max(h_start, start)
            if overlap >= pd.Timedelta(minutes=30):
                precip += grp["p01i"].max()

    wx = inw["wxcodes"].fillna("").astype(str)
    gust = inw["gust"].max() * KT_TO_MPH if inw["gust"].notna().any() else None
    sust = inw["sknt"].max() * KT_TO_MPH if inw["sknt"].notna().any() else None
    return {
        "temp_f_mean": float(inw["tmpf"].mean()) if inw["tmpf"].notna().any() else None,
        "wind_sust_max": float(sust) if sust is not None else None,
        # no gust ever reported -> fall back to sustained, so the gust bin test still works
        "wind_gust_max": float(max(gust, sust)) if gust is not None and sust is not None else (float(sust) if sust is not None else None),
        "precip_in_total": round(float(precip), 2),
        # any snow-type present-weather code (SN, SHSN, BLSN, DRSN, SG)
        "snow_flag": int(wx.str.contains(r"SN|SG", regex=True).any()),
        "vis_min": float(inw["vsby"].min()) if inw["vsby"].notna().any() else None,
        "n_obs": int(len(inw)),
    }


def run(conn=None, refresh_bins_only=False):
    conn = conn or connect()
    bins = load_bins()
    hours, min_obs = bins["game_window_hours"], bins["quality"]["min_obs_in_window"]
    now = datetime.now(timezone.utc)

    if not refresh_bins_only:
        todo = conn.execute(
            """SELECT g.game_id, g.kickoff_utc, v.nearest_station FROM games g
               JOIN venues v ON v.venue_id = g.venue_id
               LEFT JOIN weather_obs w ON w.game_id = g.game_id
               WHERE g.completed = 1 AND g.kickoff_tbd = 0 AND g.kickoff_utc IS NOT NULL
                 AND v.dome = 0 AND v.nearest_station IS NOT NULL AND w.game_id IS NULL
                 AND g.game_id IN (SELECT game_id FROM team_games)""").fetchall()
        s = http_session()
        for i, row in enumerate(todo, 1):
            start = pd.Timestamp(row["kickoff_utc"]).tz_convert("UTC")
            end = start + timedelta(hours=hours)
            if end + timedelta(hours=3) > now:
                continue  # IEM can lag a bit; pick it up on the next run
            # pad the pull by 1h after the window so the last hourly precip report is included
            df = fetch_obs(s, row["nearest_station"], start - timedelta(hours=1), end + timedelta(hours=1))
            w = summarize_window(df, start, end)
            conn.execute(
                """INSERT OR REPLACE INTO weather_obs(game_id,station,window_start,window_end,
                      temp_f_mean,wind_sust_max,wind_gust_max,precip_in_total,snow_flag,vis_min,
                      n_obs,weather_ok) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                (row["game_id"], row["nearest_station"], start.isoformat(), end.isoformat(),
                 w["temp_f_mean"], w["wind_sust_max"], w["wind_gust_max"], w["precip_in_total"],
                 w["snow_flag"], w["vis_min"], w["n_obs"], int(w["n_obs"] >= min_obs)))
            if i % 25 == 0:
                conn.commit()
                print(f"  weather {i}/{len(todo)}")
        conn.commit()

    # Always re-label from the current bins.yaml, so editing thresholds needs no re-download.
    for r in conn.execute("SELECT * FROM weather_obs").fetchall():
        d = dict(r)
        wb, pb, tb = classify_all(d, bins) if d["weather_ok"] else (None, None, None)
        conn.execute("UPDATE weather_obs SET wind_bin=?, precip_bin=?, temp_bin=? WHERE game_id=?",
                     (wb, pb, tb, d["game_id"]))
    conn.commit()


if __name__ == "__main__":
    run()
