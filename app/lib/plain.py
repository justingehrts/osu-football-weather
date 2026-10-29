"""Plain-language helpers for broadcast use. No Streamlit here, so everything is unit tested.

Four jobs, all built on numbers the pipeline already computed (no new statistics):
  1. words()       "-1.72 yds/att"  ->  "1.72 fewer yards per pass", with better/worse for stats where lower is good
  2. game_terms()  put an adjusted change in game-sized terms, next to what the team usually does:
                   "about 55 fewer passing yards a game (-18%) · usually 9.3 yards per pass in other games"
  3. chart_frame() rows for the dot-and-range chart (right = better for every stat, so the eye never has to flip)
  4. on_air_line() one or two speakable sentences whose hedge words come straight from the evidence labels
  plus forecast helpers: how close the forecast is to each bin line, and how the forecast has trended.

Nuance kept on purpose: game-sized figures are labelled "about"/"roughly" because they combine the adjusted change
with the team's PLAIN average in its other games; the adjusted number itself is always shown too.
"""
import math

import pandas as pd

from .logic import CLEAR, FEW, LEANS, METRIC_INFO, NONE, POOLED, RANK

# +1: higher is better for that team; -1: lower is better
GOOD = {"pass_eff": 1, "points": 1, "points_allowed": -1, "ppa_off": 1, "rush_ypc": 1, "turnovers": -1}
# how a change in each stat is said out loud
SAY = {"pass_eff": ("more", "fewer", "yards per pass"), "points": ("more", "fewer", "points"),
       "points_allowed": ("more", "fewer", "points allowed"), "ppa_off": ("higher", "lower", "expected points per play"),
       "rush_ypc": ("more", "fewer", "yards per carry"), "turnovers": ("more", "fewer", "turnovers")}
SHORT = {"pass_eff": "yds/pass", "points": "pts", "points_allowed": "pts allowed", "ppa_off": "PPA/play",
         "rush_ypc": "yds/carry", "turnovers": "turnovers"}
GAMES_WORD = {"calm": "calm", "moderate": "moderate-wind", "windy": "windy", "none": "dry", "light": "light-rain",
              "steady": "steady-rain", "wet": "rainy"}


def _shows(r):
    return r is not None and r.status == "ok" and r.value is not None and r.label != FEW


# --------------------------------------------------------------------------- 2. words and direction
def words(r, short=False):
    """'1.72 fewer yards per pass' / '0.9 more points allowed' -> (text, verdict) where verdict is 'better',
    'worse' or None (None when the stat's direction is obvious from the words, or the change is ~zero)."""
    if not _shows(r):
        return None, None
    _, _, dec, _ = METRIC_INFO[r.metric]
    up, down, noun = SAY[r.metric]
    if round(abs(r.value), dec) == 0:
        return f"about the same {SHORT[r.metric] if short else noun}", None
    more = r.value > 0
    text = f"{abs(r.value):.{dec}f} {up if more else down} {SHORT[r.metric] if short else noun}"
    better = (r.value > 0) == (GOOD[r.metric] > 0)
    # 'fewer points scored' is plainly worse; the ones people misread are those where LOWER is good
    verdict = ("better" if better else "worse") if GOOD[r.metric] < 0 else None
    return text, verdict


# --------------------------------------------------------------------------- 1. game-sized terms
def _round_yards(x):
    return int(5 * round(x / 5)) if abs(x) >= 10 else int(round(x))


def game_terms_short(r, typical):
    """Compact form for the TV graphic: '≈55 fewer pass yds/game', '15% below usual'."""
    if not _shows(r) or r.team == POOLED or not typical:
        return None
    base = (typical.get(r.metric) or {}).get("mean_other")
    if not base:
        return None
    if r.metric == "pass_eff":
        att = (typical.get("pass_att") or {}).get("mean_other")
        if not att:
            return None
        yds = r.value * att
        return f"≈{abs(_round_yards(yds))} {'more' if yds > 0 else 'fewer'} pass yds/game"
    if r.metric in ("points", "points_allowed"):
        pct = r.value / base * 100
        return f"{abs(pct):.0f}% {'above' if pct > 0 else 'below'} usual"
    return None


def game_terms(r, typical):
    """Adjusted change in game-sized terms, next to the team's plain average in its OTHER games.
    `typical` is data.raw_block_averages(...) for this team and bin. Returns None if it can't be said honestly."""
    if not _shows(r) or r.team == POOLED or not typical:
        return None
    t = typical.get(r.metric) or {}
    base = t.get("mean_other")
    if base is None or base == 0:
        return None
    pct = r.value / base * 100
    if r.metric == "pass_eff":
        att = (typical.get("pass_att") or {}).get("mean_other")
        if not att:
            return None
        yds = r.value * att
        word = "more" if yds > 0 else "fewer"
        return (f"about {abs(_round_yards(yds))} {word} passing yards a game ({pct:+.0f}%) · usually {base:.1f} yards per pass "
                f"in other games")
    if r.metric == "points":
        return f"{abs(pct):.0f}% {'above' if pct > 0 else 'below'} the ~{base:.0f} points a game they usually score in other games"
    if r.metric == "points_allowed":
        return f"{abs(pct):.0f}% {'above' if pct > 0 else 'below'} the ~{base:.0f} points a game they usually allow in other games"
    return None


# --------------------------------------------------------------------------- 3. chart
def chart_frame(rows, focal, opponent, pooled_n, metrics):
    """Rows for the dot-and-range chart of one condition. 'better' flips stats where lower is good, so RIGHT is
    always better. Rows without a usable estimate are returned separately (listed under the chart, not drawn)."""
    who_name = {focal: focal, opponent: opponent, POOLED: f"All {pooled_n} loaded teams"}
    order = {focal: 0, opponent: 1, POOLED: 2}
    drawn, missing = [], []
    for r in rows:
        if r.metric not in metrics or r.team not in who_name:
            continue
        if not _shows(r) or r.lo is None or r.hi is None:
            if r.status == "ok":
                missing.append(f"{who_name[r.team]}: {METRIC_INFO[r.metric][0].lower()} ({r.label.lower()}, n={r.n})")
            continue
        g = GOOD[r.metric]
        lo, hi = sorted((r.lo * g, r.hi * g))
        text, verdict = words(r, short=True)
        drawn.append({"metric": METRIC_INFO[r.metric][0], "metric_order": metrics.index(r.metric),
                      "who": who_name[r.team], "who_order": order[r.team], "better": r.value * g, "lo": lo, "hi": hi,
                      "label": r.label, "n": r.n, "in_words": text + (f" ({verdict})" if verdict else ""), "zero": 0.0})
    return pd.DataFrame(drawn), missing


# --------------------------------------------------------------------------- 4. the on-air line
def _reason(label, n, bins):
    if label != LEANS:
        return ""
    return f"but that's only {n} games" if n < bins["app"]["clear_signal_min_n"] else "but it's not a consistent pattern"


def on_air_line(stats, focal, opp, wind, precip, bins, typicals, first_season, precip_prob=None, max_items=2):
    """One or two sentences you could read on air. Rounded numbers, the evidence label turned into everyday hedges
    ('has clearly' only for Clear signal, 'has tended to ... but' for Leans), wind before rain, never temperature.
    A toss-up rain chance always gets its own short sentence, so findings leave room for it."""
    uncertain = precip == "uncertain"
    cands = []
    for dim, bv in (("wind", wind), ("precip", None if uncertain else precip)):
        if not bv:
            continue
        for team in (focal, opp):
            if not team or not stats.loaded(team):
                continue
            found = {}
            for grp, metric in (("passing", "pass_eff"), ("scoring", "points")):
                label, n, _ = stats.group_label(team, dim, bv, grp)
                r = stats.result(team, dim, bv, metric)
                if label in (CLEAR, LEANS) and _shows(r):
                    found[grp] = (label, n, r)
            if found:
                best = max(RANK[v[0]] for v in found.values())
                cands.append((0 if dim == "wind" else 1, -best, 0 if team == focal else 1, team, dim, bv, found))
    cands.sort(key=lambda c: c[:3])
    since = f" since {first_season}" if first_season else ""
    out = []
    for _, _, _, team, dim, bv, found in cands[:max_items]:
        cond = f"{GAMES_WORD[bv]} games"
        typ = (typicals or {}).get((team, dim, bv)) or {}
        p, s = found.get("passing"), found.get("scoring")
        same = p and s and p[0] == s[0] and (p[2].value > 0) == (s[2].value > 0)
        if same and p[0] == CLEAR:
            yds = (typ.get("pass_att") or {}).get("mean_other")
            yd = f"roughly {abs(_round_yards(p[2].value * yds))} {'more' if p[2].value > 0 else 'fewer'} passing yards and " if yds else ""
            out.append(f"In {cond}{since}, {team} has clearly been {'better' if p[2].value > 0 else 'less effective'} on offense: "
                       f"{yd}about {abs(s[2].value):.0f} {'more' if s[2].value > 0 else 'fewer'} points a game ({min(p[1], s[1])} games).")
            continue
        for grp in ("passing", "scoring"):
            if grp not in found:
                continue
            label, n, r = found[grp]
            up = r.value > 0
            if grp == "passing":
                yds = (typ.get("pass_att") or {}).get("mean_other")
                amount = f", roughly {abs(_round_yards(r.value * yds))} {'more' if up else 'fewer'} passing yards a game" if yds else ""
                if label == CLEAR:
                    out.append(f"In {cond}{since}, {team} has clearly passed {'better' if up else 'less effectively'}{amount} ({n} games).")
                else:
                    out.append(f"{team} has tended to pass {'a bit better' if up else 'a bit worse'} in {cond}, {_reason(label, n, bins)}.")
            else:
                if label == CLEAR:
                    out.append(f"In {cond}{since}, {team} has clearly scored {'more' if up else 'less'}: about "
                               f"{abs(r.value):.0f} {'more' if up else 'fewer'} points a game ({n} games).")
                else:
                    out.append(f"{team} has tended to score {'a bit more' if up else 'a bit less'} in {cond}, {_reason(label, n, bins)}.")
    out = out[:max_items - 1] if uncertain else out[:max_items]
    if uncertain:
        out.append(f"Rain is a toss-up{f' at {precip_prob:.0f}%' if precip_prob is not None else ''}, so there's no single rain story yet.")
    if not out:
        shown = [(d, b) for d, b in (("wind", wind), ("precip", precip)) if b and b != "uncertain"]
        loaded = [t for t in (focal, opp) if t and stats.loaded(t)]
        if loaded and shown and any(stats.group_label(t, d, b, g)[0] == NONE for t in loaded for d, b in shown
                                    for g in ("passing", "scoring")):
            return "Neither team's history shows a consistent wind or rain effect, so there's no weather angle to lean on."
        return "There aren't enough past games in these conditions to say anything about wind or rain."
    return " ".join(out)


# --------------------------------------------------------------------------- 5. the forecast: bin lines and trend
def bin_distances(fc, bins):
    """How close is each forecast number to the line where the card would change? -> (rows, borderline_notes)."""
    if not fc or fc.get("status") != "ok":
        return [], []
    w, b = bins["wind"], bins["forecast"]["borderline"]
    rows, notes = [], []

    def add(what, value, unit, text, distance, margin, flip):
        near = distance is not None and abs(distance) <= margin
        shown = f"{value:.2f} {unit}" if unit == "in." else (f"{value:.0f}{unit}" if unit in ("%", "°F") else f"{value:.0f} {unit}")
        rows.append({"Forecast": what, "Value": shown,
                     "Where it sits": text, "Borderline": "yes" if near else ""})
        if near and flip:
            notes.append(flip)

    s, g = fc.get("wind_sust"), fc.get("wind_gust")
    calm_s, windy_s = w["calm"]["sustained_max"], w["windy"]["sustained_min"]
    calm_g, windy_g = w["calm"]["gust_max"], w["windy"]["or_gust_min"]
    if s is not None:
        if s >= windy_s:
            add("Sustained wind", s, "mph", f"windy starts at {windy_s} mph ({s - windy_s:.0f} over)", s - windy_s, b["wind_mph"],
                "sustained wind is just over the windy line")
        elif s <= calm_s:
            add("Sustained wind", s, "mph", f"calm is up to {calm_s} mph ({calm_s - s:.0f} under)", calm_s - s, b["wind_mph"],
                "sustained wind is just inside calm")
        else:
            d = min(windy_s - s, s - calm_s)
            add("Sustained wind", s, "mph", f"between calm (up to {calm_s}) and windy (from {windy_s})", d, b["wind_mph"],
                "sustained wind is near a wind line")
    if g is not None:
        if g >= windy_g:
            add("Gusts", g, "mph", f"windy starts at {windy_g} mph gusts ({g - windy_g:.0f} over)", g - windy_g, b["gust_mph"],
                "gusts are just over the windy line")
        elif g <= calm_g:
            add("Gusts", g, "mph", f"calm allows gusts up to {calm_g} mph ({calm_g - g:.0f} under)", calm_g - g, b["gust_mph"],
                "gusts are near the top of calm")
        else:
            d = min(windy_g - g, g - calm_g)
            add("Gusts", g, "mph", f"between calm (up to {calm_g}) and windy (from {windy_g})", d, b["gust_mph"],
                "gusts are near a wind line")
    pop, amt = fc.get("precip_prob"), fc.get("precip_amt")
    lo, hi = bins["forecast"]["precip_prob_middle"]
    if pop is not None:
        band = "toss-up band" if lo <= pop < hi else ("dry side" if pop < lo else "wet side")
        d = min(abs(pop - lo), abs(pop - hi))
        add("Chance of rain", pop, "%", f"{band} (toss-up is {lo}-{hi}%)", d, b["rain_chance_pct"],
            f"rain chance is near the edge of the {lo}-{hi}% toss-up band")
    if amt is not None:
        steady = bins["precip"]["steady"]["total_in_min"]
        add("Rain amount", amt, "in.", f"steady rain starts at {steady:.2f} in.", steady - amt, b["rain_in"],
            "rain amount is close to the steady-rain line")
    t = fc.get("temp_f")
    if t is not None:
        edges = [v for r in bins["temperature"].values() for v in (r.get("min"), r.get("max")) if v is not None]
        d = min(abs(t - e) for e in edges)
        add("Temperature (context only)", t, "°F", "nearest temperature line is " + f"{min(edges, key=lambda e: abs(t - e))}°F", d,
            b["temp_f"], None)
    return rows, notes


def forecast_trend(history):
    """Compare the first and latest usable forecast pulls for a game. -> (sentence or None, DataFrame for a chart)."""
    if history is None or len(history) == 0:
        return None, pd.DataFrame()
    ok = history[history.status == "ok"].sort_values("snapshot_utc")
    if len(ok) < 2:
        return None, ok
    a, z = ok.iloc[0], ok.iloc[-1]
    bits = []

    def change(name, x0, x1, unit, minimum):
        if x0 is None or x1 is None or (isinstance(x0, float) and math.isnan(x0)) or (isinstance(x1, float) and math.isnan(x1)):
            return
        d = x1 - x0
        if abs(d) < minimum:
            bits.append(f"{name} steady (~{x1:.0f}{unit})")
        else:
            bits.append(f"{name} {'up' if d > 0 else 'down'} {abs(d):.0f}{unit} ({x0:.0f} to {x1:.0f})")
    change("wind", a.wind_sust, z.wind_sust, " mph", 2)
    change("gusts", a.wind_gust, z.wind_gust, " mph", 3)
    change("rain chance", a.precip_prob, z.precip_prob, "%", 10)
    bin_moves = [f"{k} {a[c]} to {z[c]}" for k, c in (("wind bin", "wind_bin"), ("rain bin", "precip_bin")) if a[c] != z[c]]
    when = pd.to_datetime(a.snapshot_utc, utc=True).tz_convert("America/New_York").strftime("%a %-I %p")
    text = f"Since {when} ({len(ok)} pulls): " + ", ".join(bits) + (". Card changed: " + "; ".join(bin_moves) + "." if bin_moves else ". Card unchanged.")
    return text, ok
