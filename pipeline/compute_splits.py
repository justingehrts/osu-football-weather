"""Step 4: baseline-relative splits per team / bin -> team_splits.

Baseline = the team's own average over ALL its usable outdoor games (dome games
and games without trustworthy weather are left out of both the baseline and the
bins, so the comparison is apples to apples). Delta = bin value - baseline.

Metrics:
  pass_eff   pass yards per attempt   (total yards / total attempts, i.e. attempt-weighted)
  rush_ypc   rush yards per carry     (same idea)
  points     points scored per game
  turnovers  turnovers committed per game
Each is computed twice: scope 'all' and scope 'ex2020' (COVID-altered season dropped).
"""
import pandas as pd

from .common import connect, load_bins
from .weather_bins import confidence

RATIOS = {"pass_eff": ("pass_yds", "pass_att"), "rush_ypc": ("rush_yds", "rush_att")}
MEANS = {"points": "points", "turnovers": "turnovers"}
BIN_COLS = {"wind": "wind_bin", "precip": "precip_bin", "temp": "temp_bin"}


def metric_value(df, metric):
    """Returns (value, n_games_with_data)."""
    if metric in RATIOS:
        num, den = RATIOS[metric]
        d = df.dropna(subset=[num, den])
        d = d[d[den] > 0]
        return (d[num].sum() / d[den].sum() if len(d) else None), len(d)
    col = MEANS[metric]
    d = df.dropna(subset=[col])
    return (d[col].mean() if len(d) else None), len(d)


def compute(df, bins):
    """df: usable outdoor team-game rows. Returns list of team_splits tuples."""
    covid = set(bins["flags"]["covid_seasons"])
    rows = []
    for team, tdf in df.groupby("team"):
        for scope, sdf in (("all", tdf), ("ex2020", tdf[~tdf["season"].isin(covid)])):
            if sdf.empty:
                continue
            base = {m: metric_value(sdf, m)[0] for m in [*RATIOS, *MEANS]}
            groups = [(bt, bv, g) for bt, col in BIN_COLS.items() for bv, g in sdf.groupby(col)]
            if bins["precip"].get("snow_flag"):
                groups += [("snow", "snow" if k else "no_snow", g) for k, g in sdf.groupby("snow_flag")]
            for bt, bv, g in groups:
                for m in [*RATIOS, *MEANS]:
                    val, n = metric_value(g, m)
                    if val is None:
                        continue
                    rows.append((team, scope, bt, str(bv), m, val, base[m],
                                 val - base[m] if base[m] is not None else None,
                                 n, confidence(n, bins)))
    return rows


def usable_games(conn):
    return pd.read_sql_query(
        """SELECT * FROM team_game_weather
           WHERE dome = 0 AND weather_ok = 1 AND points IS NOT NULL""", conn)


def run(conn=None):
    conn = conn or connect()
    bins = load_bins()
    rows = compute(usable_games(conn), bins)
    conn.execute("DELETE FROM team_splits")  # derived table: fully rebuilt each run
    conn.executemany("INSERT INTO team_splits VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
    conn.commit()
    print(f"team_splits: {len(rows)} rows")


if __name__ == "__main__":
    run()
