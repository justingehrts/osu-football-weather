"""Step 4: weather-bin splits per team (and pooled) -- raw, opponent-adjusted, controlled.

For every team / bin / metric we report THREE deltas, each with a 90% bootstrap interval:

  RAW         team's average in the bin  -  its average over ALL usable games.
  ADJUSTED    same, but each game is first measured against what we'd EXPECT given the
              opponent's SP+ rating (straight-line fit per team and metric). Removes
              opponent quality only.
  CONTROLLED  a regression per team and metric:
                  result = baseline + opponent rating + month bucket + home/away + [in this bin]
              The "[in this bin]" coefficient is the weather effect once opponent strength,
              time of season and home/away are held fixed. (It is rescaled by 1 - bin share so it
              measures "bin vs the team's average game", the same yardstick as RAW and ADJUSTED.) This is the number meant to answer
              "is this weather, or is it just that these games were early-season home games
              against weak teams?"

Games with no SP+ rating (FCS opponents) are left out of the ADJUSTED and CONTROLLED columns
(never guessed); RAW still uses them. `n_adj` / `n_ctl` say how many games each used.

POOLED ('__POOLED__'): every tracked team together, for a steadier estimate. RAW and ADJUSTED
are measured against each team's own baseline; CONTROLLED gives each team its own baseline
(team fixed effects) with common opponent/month/home controls. The bootstrap resamples whole
GAMES, because a game between two tracked teams appears once for each side.

Each of the three is reported on TWO yardsticks, and the report labels which is which:
  "vs the team's average"   bin result minus the team's overall average (the average includes the bin);
  "vs all other games"      bin result minus the average of every game NOT in the bin (the complement).
The second is larger by exactly 1/(1 - bin share) and is the more natural "windy vs not windy" reading.

The bootstrap re-draws games with replacement and recomputes each delta; the 5th-95th
percentiles are the interval. A starred interval excludes zero -- but with hundreds of cells
tested, about 1 in 10 will do so by luck. Everything here is EXPLORATORY.

EVIDENCE TIERS (per team / bin / metric group; metric groups share a physical story):
  passing = pass yds/att + offensive PPA        scoring = points scored + offensive PPA
  clear            n >= 10 and the CONTROLLED interval excludes zero (same sign) on 2+ metrics
  leans            same direction on every metric in the group and the effect is at least
                   `tiers.lean_min_z` standard errors in size, but not "clear" (intervals span
                   zero, or n is 5-9)
  no_clear_effect  n >= 10 and neither of the above
  insufficient     n < 5, or n is 5-9 with no lean
  context_only     temperature bins only, for a team whose controlled model has NO "clear" tier in
                   any temperature bin -- its temperature results are kept for context, not evidence.
                   (A bare "leans" doesn't count: with ten temperature cells per team, some lean by chance.)
"""
from statistics import NormalDist

import numpy as np
import pandas as pd

from .common import connect, load_bins
from .weather_bins import confidence

METRICS = ["pass_eff", "rush_ypc", "points", "points_allowed", "turnovers", "ppa_off"]
GROUPS = {"passing": ["pass_eff", "ppa_off"], "scoring": ["points", "ppa_off"]}
# Which opponent rating explains which metric: offense results vs their defense, and vice versa.
RATING_FOR = {m: "opp_sp_def" for m in METRICS}
RATING_FOR["points_allowed"] = "opp_sp_off"
BIN_COLS = {"wind": "wind_bin", "precip": "precip_bin", "temp": "temp_bin"}
CONFIG_KEYS = {"precip": "precip", "temp": "temperature"}  # bin_type -> key in merged_bins
POOLED = "__POOLED__"


# --------------------------------------------------------------------------- inputs
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


def month_bucket_columns(df, bins):
    """0/1 columns for each month bucket in bins.yaml (Aug-Sep is the omitted baseline)."""
    local = pd.to_datetime(df["kickoff_utc"], utc=True) - pd.Timedelta(hours=6)   # ~US local time
    month = local.dt.month.to_numpy()
    return np.column_stack([np.isin(month, months).astype(float)
                            for months in bins["controls"]["month_buckets"].values()])


def home_column(df):
    """1 = true home game. Neutral-site games count as not-home (CFBD labels a 'home' team there)."""
    return ((df["home_away"] == "home") & (df["neutral_site"] != 1)).to_numpy(float)[:, None]


# --------------------------------------------------------------------------- bootstrap helpers
def counts_from_rows(n, resamples, seed):
    """counts[b, i] = how many times game i appears in bootstrap sample b."""
    idx = np.random.default_rng(seed).integers(0, n, size=(resamples, n))
    return np.stack([np.bincount(r, minlength=n) for r in idx]).astype(float)


def counts_from_clusters(game_ids, resamples, seed):
    """Same, but resampling whole GAMES (rows sharing a game_id move together)."""
    uniq, inverse = np.unique(game_ids, return_inverse=True)
    g = len(uniq)
    draws = np.random.default_rng(seed).integers(0, g, size=(resamples, g))
    per_game = np.stack([np.bincount(r, minlength=g) for r in draws]).astype(float)
    return per_game[:, inverse]


def _interval(boot, level):
    alpha = (1 - level) / 2 * 100
    with np.errstate(all="ignore"):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)   # bins that are empty in a resample
            return np.nanpercentile(boot, [alpha, 100 - alpha], axis=0)


def expected_residuals(v, x, min_games):
    """Result minus what a straight-line fit on opponent strength predicts. NaN if not fittable."""
    ok = np.isfinite(v) & np.isfinite(x)
    res = np.full(len(v), np.nan)
    if ok.sum() >= min_games and np.ptp(x[ok]) > 0:
        slope, icept = np.polyfit(x[ok], v[ok], 1)
        res[ok] = v[ok] - (icept + slope * x[ok])
    return res


def delta_with_interval(v, masks, counts, level):
    """bin mean minus all-games mean, plus bootstrap interval.

    v (n,) values (NaN allowed); masks (n,k) bool; counts (B,n) bootstrap multiplicities.
    Returns delta (k,), lo (k,), hi (k,), n (k,).
    """
    ok = np.isfinite(v)
    vv = np.where(ok, v, 0.0)
    m = masks & ok[:, None]
    n = m.sum(0)
    base = vv[ok].mean() if ok.any() else np.nan
    with np.errstate(invalid="ignore", divide="ignore"):
        delta = np.where(n > 0, (m * vv[:, None]).sum(0) / np.maximum(n, 1) - base, np.nan)
        w = counts * ok
        boot_base = (w @ vv) / w.sum(1)
        boot = (w @ (m * vv[:, None])) / (w @ m) - boot_base[:, None]
    lo, hi = _interval(boot, level)
    return delta, lo, hi, n


def rest_delta_with_interval(v, masks, counts, level):
    """bin mean minus the mean of all OTHER games (the complement), plus bootstrap interval."""
    ok = np.isfinite(v)
    vv = np.where(ok, v, 0.0)
    m = masks & ok[:, None]
    o = (~masks) & ok[:, None]
    with np.errstate(invalid="ignore", divide="ignore"):
        delta = (m * vv[:, None]).sum(0) / m.sum(0) - (o * vv[:, None]).sum(0) / o.sum(0)
        w = counts * ok
        boot = (w @ (m * vv[:, None])) / (w @ m) - (w @ (o * vv[:, None])) / (w @ o)
    lo, hi = _interval(boot, level)
    return delta, lo, hi


def controlled_effect(y, X0, mask, counts, ridge, level):
    """Effect of `mask` in  y ~ X0 + mask, with a bootstrap interval (see the rescaling note below).

    X0 must already include the baseline (an intercept column, or one dummy per team).
    counts is (B, n). Returns (coef, lo, hi, coef_rest, lo_rest, hi_rest): the first three on the
    "vs the team's average" yardstick, the last three on "vs all other games" (the raw coefficient).
    NaNs if the bin is empty / everything.
    """
    n = len(y)
    nj = int(mask.sum())
    if nj == 0 or nj == n:
        return (np.nan,) * 6
    X = np.column_stack([X0, mask.astype(float)])
    p = X.shape[1]
    XX = (X[:, :, None] * X[:, None, :]).reshape(n, p * p)     # each game's x xᵀ
    Xy = X * y[:, None]
    eye = ridge * np.eye(p)

    def solve(c):                                              # c: (B, n) game multiplicities
        xtx = (c @ XX).reshape(-1, p, p) + eye
        xty = c @ Xy
        return np.linalg.solve(xtx, xty[..., None])[..., 0]

    # The regression compares the bin with the games OUTSIDE it. Raw/Adjusted compare the bin with the
    # team's overall average (which includes the bin). The two differ by exactly (1 - bin share), so we
    # rescale: all three columns then answer the same question -- "bin vs the team's average game".
    coef_rest = solve(np.ones((1, n)))[0, -1]
    in_bin = counts @ mask.astype(float)
    share = in_bin / counts.sum(1)
    beta = solve(counts)[:, -1]
    present = (in_bin > 0) & (counts @ (1.0 - mask) > 0)
    b_rest = np.where(present, beta, np.nan)
    b_avg = np.where(present, beta * (1 - share), np.nan)
    lo, hi = _interval(b_avg[:, None], level)
    lo_r, hi_r = _interval(b_rest[:, None], level)
    return (float(coef_rest * (1 - nj / n)), float(lo[0]), float(hi[0]),
            float(coef_rest), float(lo_r[0]), float(hi_r[0]))


def excludes_zero(lo, hi):
    return int(lo is not None and hi is not None and np.isfinite(lo) and np.isfinite(hi) and (lo > 0 or hi < 0))


def _f(x):
    return float(x) if x is not None and np.isfinite(x) else None


# --------------------------------------------------------------------------- one sample -> rows
def split_rows(label, scope, sdf, bins, n_teams, pooled):
    """All bins x metrics for one sample of team-games (one team, or every team pooled)."""
    st, ctl = bins["stats"], bins["controls"]
    sdf = sdf.reset_index(drop=True)
    masks = bin_masks(sdf, bins)
    keys = sorted(masks)
    M = np.column_stack([masks[k] for k in keys])
    n_rows = len(sdf)
    seed = st["bootstrap_seed"]
    counts = (counts_from_clusters(sdf["game_id"].to_numpy(), st["bootstrap_resamples"], seed) if pooled
              else counts_from_rows(n_rows, st["bootstrap_resamples"], seed))
    counts_c = counts[: ctl["bootstrap_resamples"]]            # the controlled model uses fewer resamples
    months, home = month_bucket_columns(sdf, bins), home_column(sdf)
    team_dummies = pd.get_dummies(sdf["team"]).to_numpy(float) if pooled else None
    out = []
    for metric in METRICS:
        v = game_values(sdf, metric)
        if not np.isfinite(v).any():
            continue
        x = sdf[RATING_FOR[metric]].to_numpy(float)
        if pooled:       # each team measured against its own baseline / own opponent line
            v_raw = v.copy()
            resid = np.full(n_rows, np.nan)
            for t, idx in sdf.groupby("team").indices.items():
                v_raw[idx] = v[idx] - np.nanmean(v[idx]) if np.isfinite(v[idx]).any() else np.nan
                resid[idx] = expected_residuals(v[idx], x[idx], st["min_games_for_adjustment"])
            base = 0.0
            value_mean = lambda col: float(np.nanmean(v_raw[col]))
        else:
            v_raw = v
            resid = expected_residuals(v, x, st["min_games_for_adjustment"])
            base = float(np.nanmean(v))
            value_mean = lambda col: float(np.nanmean(v[col]))
        d, lo, hi, n = delta_with_interval(v_raw, M, counts, st["ci_level"])
        ad, alo, ahi, n_adj = delta_with_interval(resid, M, counts, st["ci_level"])
        rd, rlo, rhi = rest_delta_with_interval(v_raw, M, counts, st["ci_level"])
        ard, arlo, arhi = rest_delta_with_interval(resid, M, counts, st["ci_level"])

        # controlled model: only games with a result AND an opponent rating
        use = np.isfinite(v) & np.isfinite(x)
        enough = use.sum() >= st["min_games_for_adjustment"]      # same bar as the adjusted column
        opp = x[use] if enough else np.zeros(1)
        opp = (opp - opp.mean()) / (opp.std() or 1.0)
        if enough:
            base_cols = team_dummies[use] if pooled else np.ones((use.sum(), 1))
            X0 = np.column_stack([base_cols, opp, months[use], home[use]])
        for j, (bt, bv) in enumerate(keys):
            if n[j] == 0:
                continue
            mj = M[use, j]
            c, clo, chi, cr, crlo, crhi = (np.nan,) * 6
            if enough and mj.sum() >= 2:
                c, clo, chi, cr, crlo, crhi = controlled_effect(v[use], X0, mj, counts_c[:, use],
                                                                ctl["ridge"], st["ci_level"])
            out.append(dict(
                team=label, scope=scope, bin_type=bt, bin_value=bv, metric=metric,
                value=value_mean(M[:, j]) if not pooled else float(np.nanmean(v[M[:, j]])),
                baseline=base if not pooled else float(np.nanmean(v)),
                delta=_f(d[j]), delta_lo=_f(lo[j]), delta_hi=_f(hi[j]),
                adj_delta=_f(ad[j]), adj_lo=_f(alo[j]), adj_hi=_f(ahi[j]),
                ctl_delta=_f(c), ctl_lo=_f(clo), ctl_hi=_f(chi),
                n=int(n[j]), n_adj=int(n_adj[j]), n_ctl=int(mj.sum()), n_teams=n_teams,
                confidence=confidence(int(n[j]), bins),
                sig_raw=excludes_zero(lo[j], hi[j]), sig_adj=excludes_zero(alo[j], ahi[j]),
                sig_ctl=excludes_zero(clo, chi),
                rest_delta=_f(rd[j]), rest_lo=_f(rlo[j]), rest_hi=_f(rhi[j]),
                adj_rest=_f(ard[j]), adj_rest_lo=_f(arlo[j]), adj_rest_hi=_f(arhi[j]),
                ctl_rest=_f(cr), ctl_rest_lo=_f(crlo), ctl_rest_hi=_f(crhi),
                sig_rest=excludes_zero(rlo[j], rhi[j]), sig_adj_rest=excludes_zero(arlo[j], arhi[j]),
                sig_ctl_rest=excludes_zero(crlo, crhi)))
    return out


# --------------------------------------------------------------------------- evidence tiers
def assign_tier(cells, bins):
    """cells: [(n_ctl_or_n, ctl_delta, lo, hi)] for each metric in the group. -> (tier, n, n_sig)."""
    c, t = bins["confidence"], bins["tiers"]
    n = min((x[0] for x in cells), default=0)
    usable = [x for x in cells if x[1] is not None and x[2] is not None and x[3] is not None]
    if n < c["suppress_below_n"] or not usable:
        return "insufficient", n, 0
    z_crit = NormalDist().inv_cdf(1 - (1 - bins["stats"]["ci_level"]) / 2)
    sig = [x for x in usable if x[2] > 0 or x[3] < 0]
    same_sign = len({np.sign(x[1]) for x in usable}) == 1 and len(usable) == len(cells)
    zs = [abs(x[1]) / max((x[3] - x[2]) / (2 * z_crit), 1e-12) for x in usable]
    leaning = same_sign and float(np.mean(zs)) >= t["lean_min_z"]
    sig_same = len(sig) >= 2 and len({np.sign(x[1]) for x in sig}) == 1
    if n >= c["thin_below_n"]:
        if sig_same:
            return "clear", n, len(sig)
        return ("leans" if leaning else "no_clear_effect"), n, len(sig)
    return ("leans" if leaning else "insufficient"), n, len(sig)


def tier_rows(splits, bins):
    df = pd.DataFrame(splits)
    rows = []
    for (team, scope, bt, bv), g in df.groupby(["team", "scope", "bin_type", "bin_value"]):
        by_metric = g.set_index("metric")
        for grp, metrics in GROUPS.items():
            cells = [(int(by_metric.loc[m, "n_ctl"]), by_metric.loc[m, "ctl_delta"],
                      by_metric.loc[m, "ctl_lo"], by_metric.loc[m, "ctl_hi"])
                     for m in metrics if m in by_metric.index]
            cells = [(n, *[None if pd.isna(a) else a for a in rest]) for n, *rest in cells]
            tier, n, n_sig = assign_tier(cells, bins)
            rows.append(dict(team=team, scope=scope, bin_type=bt, bin_value=bv, grp=grp, tier=tier,
                             n=n, n_sig=n_sig, note=""))
    out = pd.DataFrame(rows)
    # Temperature rule: if a team's controlled model has no CLEAR effect in any temperature bin,
    # its temperature results are context only (they are explained by schedule, not weather).
    for (team, scope), g in out[out.bin_type == "temp"].groupby(["team", "scope"]):
        if not (g.tier == "clear").any():
            m = (out.team == team) & (out.scope == scope) & (out.bin_type == "temp") & (out.tier != "insufficient")
            out.loc[m, "tier"] = "context_only"
            out.loc[m, "note"] = "controlled model finds no clear temperature effect for this team"
    return out.to_dict("records")


# --------------------------------------------------------------------------- driver
def compute(df, bins):
    """df: usable outdoor team-game rows (the team_game_weather view). -> (split rows, tier rows)."""
    covid = set(bins["flags"]["covid_seasons"])
    rows = []
    teams = sorted(df["team"].unique())
    for scope, sdf in (("all", df), ("ex2020", df[~df["season"].isin(covid)])):
        for team in teams:
            t = sdf[sdf.team == team]
            if not t.empty:
                rows += split_rows(team, scope, t, bins, 1, False)
        if len(teams) > 1 and not sdf.empty:
            rows += split_rows(POOLED, scope, sdf, bins, len(teams), True)
    return rows, tier_rows(rows, bins)


def usable_games(conn):
    return pd.read_sql_query(
        """SELECT * FROM team_game_weather
           WHERE dome = 0 AND weather_ok = 1 AND points IS NOT NULL""", conn)


SPLIT_COLS = ["team", "scope", "bin_type", "bin_value", "metric", "value", "baseline", "delta", "delta_lo",
              "delta_hi", "adj_delta", "adj_lo", "adj_hi", "ctl_delta", "ctl_lo", "ctl_hi", "n", "n_adj",
              "n_ctl", "n_teams", "confidence", "sig_raw", "sig_adj", "sig_ctl", "rest_delta", "rest_lo", "rest_hi",
              "adj_rest", "adj_rest_lo", "adj_rest_hi", "ctl_rest", "ctl_rest_lo", "ctl_rest_hi", "sig_rest",
              "sig_adj_rest", "sig_ctl_rest"]
TIER_COLS = ["team", "scope", "bin_type", "bin_value", "grp", "tier", "n", "n_sig", "note"]


def run(conn=None):
    conn = conn or connect()
    bins = load_bins()
    splits, tiers = compute(usable_games(conn), bins)
    # Keep a copy of the previous results whenever the set of loaded teams changes, so the report can
    # show what moved when teams were added.
    old = {r[0] for r in conn.execute("SELECT DISTINCT team FROM team_splits")}
    new = {r["team"] for r in splits}
    if old and old != new:
        conn.execute("DELETE FROM team_splits_prev")
        conn.execute("INSERT INTO team_splits_prev SELECT * FROM team_splits")
    for table, cols, rows in (("team_splits", SPLIT_COLS, splits), ("team_tiers", TIER_COLS, tiers)):
        conn.execute(f"DELETE FROM {table}")  # derived tables: fully rebuilt each run
        conn.executemany(f"INSERT INTO {table}({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                         [[r[c] for c in cols] for r in rows])
    conn.commit()
    print(f"team_splits: {len(splits)} rows, team_tiers: {len(tiers)} rows")


if __name__ == "__main__":
    run()
