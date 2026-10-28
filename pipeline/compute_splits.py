"""Step 4: weather-bin splits per team -- raw, opponent-adjusted, with uncertainty.

For every team / bin / metric we report two deltas:

  RAW delta       = team's average in the bin  -  team's average over ALL its usable games.
  ADJUSTED delta  = how far the team's results in the bin were from what we'd EXPECT given
                    the strength of the opponents it actually played. "Expected" comes from a
                    straight-line fit, per team and metric, of the game result against the
                    opponent's SP+ rating (opponent DEFENSE rating for offensive metrics,
                    opponent OFFENSE rating for points allowed). A 40-point day against a
                    weak September opponent therefore counts for less than 40 against a
                    top-10 defense.

Every delta also gets a 90% interval from a bootstrap: we re-draw the team's games with
replacement 2000 times, recompute the delta each time, and take the 5th-95th percentile.
If the interval excludes zero we mark it -- but with ~hundreds of cells tested, a few will
"pass" by luck alone (about 1 in 10 at this level). Treat everything as EXPLORATORY.

Things the adjustment does NOT remove: month/schedule effects, home vs away, injuries,
weather-by-opponent interactions. The confounding table in the report shows what each bin
is "secretly" made of.

Metrics (all per game; ratios are computed game-by-game and then averaged):
  pass_eff        pass yards per attempt          rush_ypc   rush yards per carry
  points          points scored                   points_allowed  points allowed (defense)
  turnovers       turnovers committed             ppa_off    offensive expected-points-added per play
"""
import warnings

import numpy as np
import pandas as pd

from .common import connect, load_bins
from .weather_bins import confidence

METRICS = ["pass_eff", "rush_ypc", "points", "points_allowed", "turnovers", "ppa_off"]
# Which opponent rating explains which metric: offense results vs their defense, and vice versa.
RATING_FOR = {m: "opp_sp_def" for m in METRICS}
RATING_FOR["points_allowed"] = "opp_sp_off"
BIN_COLS = {"wind": "wind_bin", "precip": "precip_bin", "temp": "temp_bin"}
CONFIG_KEYS = {"precip": "precip", "temp": "temperature"}  # bin_type -> key in merged_bins


def game_values(df, metric):
    """One number per game for this metric (NaN when the box score doesn't have it)."""
    if metric == "pass_eff":
        return (df["pass_yds"] / df["pass_att"].where(df["pass_att"] > 0)).to_numpy(float)
    if metric == "rush_ypc":
        return (df["rush_yds"] / df["rush_att"].where(df["rush_att"] > 0)).to_numpy(float)
    return df[metric].astype(float).to_numpy()


def bin_masks(df, bins):
    """{(bin_type, bin_value): boolean mask}. Original bins plus the merged ones from bins.yaml."""
    out = {}
    for bt, col in BIN_COLS.items():
        for bv in df[col].dropna().unique():
            out[(bt, str(bv))] = (df[col] == bv).to_numpy()
        for name, members in (bins.get("merged_bins", {}).get(CONFIG_KEYS.get(bt, bt)) or {}).items():
            out[(bt, name)] = df[col].isin(members).to_numpy()
    return out


def expected_residuals(v, x, min_games):
    """Result minus what a straight-line fit on opponent strength predicts. NaN if not fittable."""
    ok = np.isfinite(v) & np.isfinite(x)
    res = np.full(len(v), np.nan)
    if ok.sum() >= min_games and np.ptp(x[ok]) > 0:
        slope, icept = np.polyfit(x[ok], v[ok], 1)
        res[ok] = v[ok] - (icept + slope * x[ok])
    return res


def delta_with_interval(v, masks, idx, level):
    """bin mean minus all-games mean, plus bootstrap interval.

    v: (n,) values (NaN allowed). masks: (n,k) bool. idx: (B,n) resampled game indices.
    Returns delta (k,), lo (k,), hi (k,), n (k,).
    """
    ok = np.isfinite(v)
    vv = np.where(ok, v, 0.0)
    m = masks & ok[:, None]
    n = m.sum(0)
    base = vv[ok].mean() if ok.any() else np.nan
    with np.errstate(invalid="ignore", divide="ignore"):
        delta = np.where(n > 0, (m * vv[:, None]).sum(0) / np.maximum(n, 1) - base, np.nan)
        # bootstrap: counts[b, i] = how many times game i was drawn in resample b
        counts = np.stack([np.bincount(r, minlength=len(v)) for r in idx]).astype(float)
        w = counts * ok
        boot_base = (w @ vv) / w.sum(1)
        num, den = w @ (m * vv[:, None]), w @ m
        boot = num / den - boot_base[:, None]
    alpha = (1 - level) / 2 * 100
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)   # bins that are empty in a resample
        lo, hi = np.nanpercentile(boot, [alpha, 100 - alpha], axis=0)
    return delta, lo, hi, n


def excludes_zero(lo, hi):
    return int(np.isfinite(lo) and np.isfinite(hi) and (lo > 0 or hi < 0))


def compute(df, bins):
    """df: usable outdoor team-game rows (the team_game_weather view). -> team_splits tuples."""
    st = bins["stats"]
    covid = set(bins["flags"]["covid_seasons"])
    rows = []
    for team, tdf in df.groupby("team"):
        for scope, sdf in (("all", tdf), ("ex2020", tdf[~tdf["season"].isin(covid)])):
            sdf = sdf.reset_index(drop=True)
            if sdf.empty:
                continue
            masks = bin_masks(sdf, bins)
            keys = sorted(masks)
            M = np.column_stack([masks[k] for k in keys])
            rng = np.random.default_rng(st["bootstrap_seed"])
            idx = rng.integers(0, len(sdf), size=(st["bootstrap_resamples"], len(sdf)))
            for metric in METRICS:
                v = game_values(sdf, metric)
                if not np.isfinite(v).any():
                    continue
                x = sdf[RATING_FOR[metric]].to_numpy(float)
                resid = expected_residuals(v, x, st["min_games_for_adjustment"])
                d, lo, hi, n = delta_with_interval(v, M, idx, st["ci_level"])
                ad, alo, ahi, n_adj = delta_with_interval(resid, M, idx, st["ci_level"])
                base = np.nanmean(v)
                for j, (bt, bv) in enumerate(keys):
                    if n[j] == 0:
                        continue
                    rows.append((
                        team, scope, bt, bv, metric,
                        float(np.nanmean(v[M[:, j]])), float(base),
                        _f(d[j]), _f(lo[j]), _f(hi[j]), _f(ad[j]), _f(alo[j]), _f(ahi[j]),
                        int(n[j]), int(n_adj[j]), confidence(int(n[j]), bins),
                        excludes_zero(lo[j], hi[j]), excludes_zero(alo[j], ahi[j])))
    return rows


def _f(x):
    return float(x) if np.isfinite(x) else None


def usable_games(conn):
    return pd.read_sql_query(
        """SELECT * FROM team_game_weather
           WHERE dome = 0 AND weather_ok = 1 AND points IS NOT NULL""", conn)


def run(conn=None):
    conn = conn or connect()
    bins = load_bins()
    rows = compute(usable_games(conn), bins)
    conn.execute("DELETE FROM team_splits")  # derived table: fully rebuilt each run
    conn.executemany("INSERT INTO team_splits VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    conn.commit()
    print(f"team_splits: {len(rows)} rows")


if __name__ == "__main__":
    run()
