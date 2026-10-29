"""Read-only data access. Every function takes an open connection and returns plain pandas /
dicts; nothing here writes, and nothing here does statistics -- the pipeline already did."""
import sqlite3
from datetime import datetime, timezone

import pandas as pd


def connect_ro(path):
    """Open a SQLite file read-only (a write attempt raises). Returns None if the file is missing."""
    path = str(path)
    if path != ":memory:" and not __import__("os").path.exists(path):
        return None
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def load_splits(conn):
    return pd.read_sql_query("SELECT * FROM team_splits", conn)


def load_tiers(conn):
    return pd.read_sql_query("SELECT * FROM team_tiers", conn)


def schedule(conn, team, season):
    """The focal team's regular-season games with venue, result and OBSERVED weather (if played)."""
    q = pd.read_sql_query(
        """SELECT g.game_id, g.week, g.season_type, g.kickoff_utc, g.kickoff_tbd, g.completed, g.neutral_site,
                  g.home_team, g.away_team, g.home_points, g.away_points,
                  v.venue_id, v.name AS venue, v.dome, v.lat, v.lon,
                  w.temp_f_mean, w.wind_sust_max, w.wind_gust_max, w.precip_in_total, w.snow_flag, w.weather_ok,
                  w.wind_bin, w.precip_bin, w.temp_bin
           FROM games g LEFT JOIN venues v ON v.venue_id = g.venue_id
           LEFT JOIN weather_obs w ON w.game_id = g.game_id
           WHERE g.season = ? AND (g.home_team = ? OR g.away_team = ?)
           ORDER BY g.kickoff_utc""", conn, params=(season, team, team))
    q["opponent"] = [a if h == team else h for h, a in zip(q.home_team, q.away_team)]
    q["site"] = ["neutral" if n else ("home" if h == team else "away")
                 for n, h in zip(q.neutral_site, q.home_team)]
    return q


def next_game(sched, now=None):
    """The first game not yet played (kickoff still ahead, or unknown); else the last game."""
    now = now or datetime.now(timezone.utc)
    upcoming = sched[sched.completed == 0]
    return (upcoming if not upcoming.empty else sched).iloc[0] if not sched.empty else None


def latest_forecast(fconn, game_id):
    if fconn is None:
        return None
    r = fconn.execute("SELECT * FROM forecast_snapshots WHERE game_id=? ORDER BY snapshot_utc DESC LIMIT 1", (game_id,)).fetchone()
    return dict(r) if r else None


def forecast_history(fconn, game_id):
    if fconn is None:
        return pd.DataFrame()
    return pd.read_sql_query("SELECT * FROM forecast_snapshots WHERE game_id=? ORDER BY snapshot_utc", fconn, params=(game_id,))


def bin_members(bins, bin_type, bin_value):
    """Which stored labels make up a bin (merged bins like 'wet' = light + steady come from bins.yaml)."""
    key = {"precip": "precip", "temp": "temperature"}.get(bin_type, bin_type)
    merged = (bins.get("merged_bins", {}).get(key) or {})
    return list(merged.get(bin_value, [bin_value]))


def evidence_games(conn, bins, team, bin_type, bin_value, exclude_covid=False):
    """The actual games behind a number: one row per game the team played in that weather bin."""
    col = {"wind": "wind_bin", "precip": "precip_bin", "temp": "temp_bin"}[bin_type]
    members = bin_members(bins, bin_type, bin_value)
    marks = ",".join("?" * len(members))
    covid = bins.get("flags", {}).get("covid_seasons", [])
    extra = f" AND season NOT IN ({','.join(str(int(y)) for y in covid)})" if exclude_covid and covid else ""
    q = pd.read_sql_query(
        f"""SELECT t.game_id, t.season, t.kickoff_utc, t.opponent, t.home_away, t.neutral_site,
                   v.name AS venue, t.temp_f_mean, t.wind_sust_max, t.wind_gust_max, t.precip_in_total, t.snow_flag,
                   t.points, t.points_allowed, t.pass_yds, t.pass_att, t.rush_yds, t.rush_att, t.turnovers, t.ppa_off,
                   t.opp_sp
            FROM team_game_weather t LEFT JOIN venues v ON v.venue_id = t.venue_id
            WHERE t.team = ? AND t.dome = 0 AND t.weather_ok = 1 AND t.{col} IN ({marks}){extra}
            ORDER BY t.kickoff_utc DESC""", conn, params=[team, *members])
    return q


def snow_games(conn):
    return pd.read_sql_query(
        """SELECT g.game_id, g.kickoff_utc, g.home_team, g.away_team, g.home_points, g.away_points, v.name AS venue,
                  w.temp_f_mean, w.wind_sust_max, w.wind_gust_max, w.precip_in_total, w.vis_min
           FROM weather_obs w JOIN games g ON g.game_id = w.game_id LEFT JOIN venues v ON v.venue_id = g.venue_id
           WHERE w.snow_flag = 1 AND w.weather_ok = 1 AND g.completed = 1
             AND g.game_id IN (SELECT game_id FROM team_games) ORDER BY g.kickoff_utc""", conn)


def history_through(conn):
    """Date of the most recent finished game that is in the statistics."""
    r = conn.execute("""SELECT MAX(g.kickoff_utc) FROM games g WHERE g.completed = 1
                        AND g.game_id IN (SELECT game_id FROM team_games)""").fetchone()
    return r[0] if r and r[0] else None


def last_forecast_time(fconn):
    if fconn is None:
        return None
    r = fconn.execute("SELECT MAX(snapshot_utc) FROM forecast_snapshots").fetchone()
    return r[0] if r and r[0] else None


AVG_EXPR = {"pass_eff": "CASE WHEN t.pass_att > 0 THEN t.pass_yds * 1.0 / t.pass_att END",
            "points": "t.points", "points_allowed": "t.points_allowed", "ppa_off": "t.ppa_off",
            "pass_att": "t.pass_att"}      # attempts: turns a per-pass change into passing yards a game


def raw_block_averages(conn, bins, team, bin_type, bin_value, exclude_covid=False):
    """PLAIN averages for the 'Show anyway' view of a thin block: the team's average in the bin's games, and in all of
    its other usable games. No adjustment, no model -- just arithmetic on real games. Returns
    {metric: dict(mean_in, n_in, mean_other, n_other)}; means are None when there are no games."""
    col = {"wind": "wind_bin", "precip": "precip_bin", "temp": "temp_bin"}[bin_type]
    members = bin_members(bins, bin_type, bin_value)
    marks = ",".join("?" * len(members))
    covid = bins.get("flags", {}).get("covid_seasons", [])
    extra = f" AND t.season NOT IN ({','.join(str(int(y)) for y in covid)})" if exclude_covid and covid else ""
    out = {}
    for metric, expr in AVG_EXPR.items():
        r = conn.execute(
            f"""SELECT AVG(CASE WHEN t.{col} IN ({marks}) THEN {expr} END) AS mean_in,
                       COUNT(CASE WHEN t.{col} IN ({marks}) THEN {expr} END) AS n_in,
                       AVG(CASE WHEN t.{col} NOT IN ({marks}) THEN {expr} END) AS mean_other,
                       COUNT(CASE WHEN t.{col} NOT IN ({marks}) THEN {expr} END) AS n_other
                FROM team_game_weather t
                WHERE t.team = ? AND t.dome = 0 AND t.weather_ok = 1 AND t.points IS NOT NULL{extra}""",
            [*members, *members, *members, *members, team]).fetchone()
        out[metric] = dict(mean_in=r["mean_in"], n_in=r["n_in"], mean_other=r["mean_other"], n_other=r["n_other"])
    return out
