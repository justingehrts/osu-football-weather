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

from .logic import CLEAR, FEW, LEANS, METRIC_INFO, NONE, POOLED, PRECIP_NAME, RANK, WIND_NAME

# +1: higher is better for that team; -1: lower is better
# 0 = playcalling: neither better nor worse, so there is no good direction (and the chart is not flipped)
GOOD = {"pass_eff": 1, "points": 1, "points_allowed": -1, "ppa_off": 1, "rush_ypc": 1, "turnovers": -1,
        "pass_rate": 0, "plays": 0}
# how a change in each stat is said out loud
SAY = {"pass_eff": ("more", "fewer", "yards per pass"), "points": ("more", "fewer", "points"),
       "points_allowed": ("more", "fewer", "points allowed"), "ppa_off": ("higher", "lower", "expected points per play"),
       "rush_ypc": ("more", "fewer", "yards per carry"), "turnovers": ("more", "fewer", "turnovers"),
       "pass_rate": ("points more", "points less", "passing"), "plays": ("more", "fewer", "plays")}
SHORT = {"pass_eff": "yds/pass", "points": "pts", "points_allowed": "pts allowed", "ppa_off": "PPA/play",
         "rush_ypc": "yds/carry", "turnovers": "turnovers", "pass_rate": "passing", "plays": "plays"}
# x-axis wording for the neutral (playcalling) charts; everything else uses the "worse / better" axis
UNIT_WORDS = {"pass_eff": "yards per pass", "points": "points a game", "points_allowed": "points a game",
              "ppa_off": "expected points per play", "rush_ypc": "yards per carry", "turnovers": "turnovers a game",
              "pass_rate": "passes per 100 plays", "plays": "plays a game"}
NEUTRAL_AXIS = {"pass_rate": "◄ ran more  ·  threw more ►", "plays": "◄ fewer plays  ·  more plays ►"}
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
    if r.metric == "pass_rate":
        passes = _passes_a_game(r, typical)
        return f"≈{abs(round(passes))} {'more' if passes > 0 else 'fewer'} passes/game" if passes is not None and round(passes) else None
    return None


def _passes_a_game(r, typical):
    """A pass-share change (points of share) as passes a game, using the team's plain plays per game in its other games."""
    plays = (typical.get("plays") or {}).get("mean_other")
    return None if not plays else r.value / 100 * plays


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
    if r.metric == "pass_rate":
        said = f"passes on about {base + r.value:.0f}% of plays vs. usually {base:.0f}% in other games"
        passes = _passes_a_game(r, typical)
        k = abs(round(passes)) if passes is not None else 0
        return said + (f" · about {k} {'more' if passes > 0 else 'fewer'} {'pass' if k == 1 else 'passes'} a game" if k else "")
    if r.metric == "plays":
        if round(abs(r.value)) == 0:
            return f"about the usual {base:.0f} plays a game"
        k = abs(round(r.value))
        return f"about {k} {'more' if r.value > 0 else 'fewer'} {'play' if k == 1 else 'plays'} a game ({pct:+.0f}%) · usually {base:.0f} in other games"
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
        g = GOOD[r.metric] or 1                           # playcalling is not flipped: it has no better direction
        lo, hi = sorted((r.lo * g, r.hi * g))
        text, verdict = words(r, short=True)
        drawn.append({"metric": METRIC_INFO[r.metric][0], "metric_order": metrics.index(r.metric),
                      "title": f"{METRIC_INFO[r.metric][0]} · {UNIT_WORDS[r.metric]}",
                      "who": who_name[r.team], "who_order": order[r.team], "better": r.value * g, "lo": lo, "hi": hi,
                      "label": r.label, "n": r.n, "in_words": text + (f" ({verdict})" if verdict else ""), "zero": 0.0,
                      "axis": NEUTRAL_AXIS.get(r.metric, "◄ worse  ·  better ►")})
    return pd.DataFrame(drawn), missing


# --------------------------------------------------------------------------- 4. the on-air line
def _reason(label, n, bins):
    if label != LEANS:
        return ""
    return f"but that's only {n} games" if n < bins["app"]["clear_signal_min_n"] else "but it's not a consistent pattern"


def _playcall_sentence(stats, focal, opp, wind, precip, bins, scope="all"):
    """At most ONE playcalling sentence, only for a Leans finding (pass share has no second stat, so it can never be
    'Clear signal'). Wind before rain, focal team first. Not better or worse, so no value words: 'throw more/less'."""
    for dim, bv in (("wind", wind), ("precip", precip)):
        if not bv:
            continue
        for team in (focal, opp):
            if not team or not stats.loaded(team):
                continue
            r = stats.result(team, dim, bv, "pass_rate", scope)
            if r.label == LEANS and _shows(r) and abs(r.value) >= 0.5:
                up = r.value > 0
                return (f"{team} has tended to throw {'more' if up else 'less'} in {GAMES_WORD[bv]} games: about {abs(r.value):.0f} "
                        f"{'more' if up else 'fewer'} passes per 100 plays, {_reason(LEANS, r.n, bins)}.")
    return None


def on_air_line(stats, focal, opp, wind, precip, bins, typicals, first_season, precip_prob=None, max_items=2, scope="all"):
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
                label = stats.group_label(team, dim, bv, grp, scope)[0]
                r = stats.result(team, dim, bv, metric, scope)
                if label in (CLEAR, LEANS) and _shows(r):
                    found[grp] = (label, r.n, r)          # the card's own count, so the line and the card agree
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
    pc = _playcall_sentence(stats, focal, opp, wind, None if uncertain else precip, bins, scope)
    if pc:
        out.append(pc)
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
def forecast_values_text(fc):
    """The forecast's numbers as one phrase. NWS sometimes gives no rain AMOUNT (or another value) for a window, so every
    piece is optional: a missing value is skipped (or said to be missing), never formatted."""
    def have(k):
        return fc.get(k) is not None and not pd.isna(fc[k])
    bits = []
    if have("wind_sust"):
        bits.append(f"wind up to {fc['wind_sust']:.0f} mph" + (f" (gusts {fc['wind_gust']:.0f})" if have("wind_gust") else ""))
    if have("precip_prob"):
        bits.append(f"chance of rain {fc['precip_prob']:.0f}%")
    bits.append(f"{fc['precip_amt']:.2f} in. of rain" if have("precip_amt") else "rain amount not given")
    if have("temp_f"):
        bits.append(f"{fc['temp_f']:.0f}°F")
    return ", ".join(bits) + "."


def _num(fc, key):
    v = (fc or {}).get(key)
    return None if v is None or pd.isna(v) else v


def _distance_items(fc, bins):
    """Each forecast number vs. the nearest line that would change the card. Values are rounded EXACTLY as the pipeline
    rounds them before binning (whole mph, whole degrees, rain to 0.01 in.), so a 9.2 mph forecast is "9 mph, the top of
    calm" here too, never "between calm and windy" next to a Calm badge."""
    if not fc or fc.get("status") != "ok":
        return []
    w, b = bins["wind"], bins["forecast"]["borderline"]
    calm_s, windy_s = w["calm"]["sustained_max"], w["windy"]["sustained_min"]
    calm_g, windy_g = w["calm"]["gust_max"], w["windy"]["or_gust_min"]
    out = []

    def add(dim, what, shown, where, distance, margin, tag=None, note=None):
        near = distance is not None and abs(distance) <= margin
        out.append({"dim": dim, "what": what, "shown": shown, "where": where, "near": near,
                    "tag": tag if near else None, "note": note if near else None})

    s = _num(fc, "wind_sust")
    if s is not None:
        s = round(s)
        if s >= windy_s:
            add("wind", "Sustained wind", f"{s} mph", f"windy starts at {windy_s} mph ({s - windy_s} over)", s - windy_s, b["wind_mph"],
                "just windy", f"{s} mph sustained is just over the windy line ({windy_s} mph)")
        elif s <= calm_s:
            d = calm_s - s
            add("wind", "Sustained wind", f"{s} mph", f"calm is up to {calm_s} mph ({d} under)", d, b["wind_mph"], "top of calm",
                f"{s} mph sustained is the top of the calm range (calm runs up to {calm_s} mph; {calm_s + 1} to {windy_s - 1} is moderate)"
                if d == 0 else f"{s} mph sustained is {d} mph under the moderate-wind line (calm runs up to {calm_s} mph)")
        elif windy_s - s <= s - calm_s:
            d = windy_s - s
            add("wind", "Sustained wind", f"{s} mph", f"moderate; windy starts at {windy_s} mph ({d} under)", d, b["wind_mph"],
                "near windy", f"{s} mph sustained is moderate, {d} mph below the windy line ({windy_s} mph)")
        else:
            d = s - calm_s
            add("wind", "Sustained wind", f"{s} mph", f"moderate; calm is up to {calm_s} mph ({d} over)", d, b["wind_mph"],
                "near calm", f"{s} mph sustained is moderate, {d} mph above calm (calm runs up to {calm_s} mph)")
    g = _num(fc, "wind_gust")
    if g is not None:
        g = round(g)
        if g >= windy_g:
            add("wind", "Gusts", f"{g} mph", f"windy starts at {windy_g} mph gusts ({g - windy_g} over)", g - windy_g, b["gust_mph"],
                "gusts just windy", f"gusts of {g} mph are just over the windy line ({windy_g} mph)")
        elif g <= calm_g:
            add("wind", "Gusts", f"{g} mph", f"calm allows gusts up to {calm_g} mph ({calm_g - g} under)", calm_g - g, b["gust_mph"],
                "gusts near calm limit", f"gusts of {g} mph are near the top of calm (calm allows gusts up to {calm_g} mph)")
        elif windy_g - g <= g - calm_g:
            d = windy_g - g
            add("wind", "Gusts", f"{g} mph", f"moderate; windy starts at {windy_g} mph gusts ({d} under)", d, b["gust_mph"],
                "gusts near windy", f"gusts of {g} mph are {d} mph below the windy line ({windy_g} mph)")
        else:
            d = g - calm_g
            add("wind", "Gusts", f"{g} mph", f"moderate; calm allows gusts up to {calm_g} mph ({d} over)", d, b["gust_mph"],
                "gusts near calm", f"gusts of {g} mph are {d} mph above calm's limit ({calm_g} mph)")
    lo, hi = bins["forecast"]["precip_prob_middle"]
    pop = _num(fc, "precip_prob")
    if pop is not None:
        pop = round(pop)
        band = "toss-up band" if lo <= pop < hi else ("dry side" if pop < lo else "wet side")
        add("precip", "Chance of rain", f"{pop}%", f"{band} (toss-up is {lo}-{hi}%)", min(abs(pop - lo), abs(pop - hi)),
            b["rain_chance_pct"], "toss-up edge", f"{pop}% chance of rain is near the edge of the {lo}-{hi}% toss-up band")
    amt = _num(fc, "precip_amt")
    if amt is not None:
        amt = round(amt, 2)
        steady = bins["precip"]["steady"]["total_in_min"]
        add("precip", "Rain amount", f"{amt:.2f} in.", f"steady rain starts at {steady:.2f} in.", round(steady - amt, 2), b["rain_in"],
            "near steady rain", f"{amt:.2f} in. of rain is close to the steady-rain line ({steady:.2f} in.)")
    t = _num(fc, "temp_f")
    if t is not None:
        t = round(t)
        edges = [v for r in bins["temperature"].values() for v in (r.get("min"), r.get("max")) if v is not None]
        add("temp", "Temperature (context only)", f"{t}°F", f"nearest temperature line is {min(edges, key=lambda e: abs(t - e))}°F",
            min(abs(t - e) for e in edges), b["temp_f"])          # context only: never a borderline note or tag
    return out


def bin_distances(fc, bins):
    """How close is each forecast number to the line where the card would change? -> (rows, borderline_notes)."""
    items = _distance_items(fc, bins)
    rows = [{"Forecast": i["what"], "Value": i["shown"], "Where it sits": i["where"], "Borderline": "yes" if i["near"] else ""}
            for i in items]
    return rows, [i["note"] for i in items if i["note"]]


def badge_parts(cond, fc, bins):
    """The condition badges, now carrying the forecast numbers: [{name, detail, tag, muted}]. A What-If shows names
    only (no forecast numbers behind it). Temperature is a muted 'context only' badge."""
    use_fc = bool(fc) and fc.get("status") == "ok" and not cond.get("overridden")
    tags = {}
    for i in (_distance_items(fc, bins) if use_fc else []):
        if i["tag"] and i["dim"] not in tags:
            tags[i["dim"]] = i["tag"]
    out = []
    if cond.get("wind"):
        s, g = _num(fc, "wind_sust"), _num(fc, "wind_gust")
        detail = (f"{round(s)} mph" + (f" · gusts {round(g)}" if g is not None else "")) if use_fc and s is not None else None
        out.append({"name": WIND_NAME.get(cond["wind"], cond["wind"]), "detail": detail, "tag": tags.get("wind"), "muted": False})
    if cond.get("precip"):
        pop = _num(fc, "precip_prob")
        name = "Rain possible" if cond["precip"] == "uncertain" else PRECIP_NAME.get(cond["precip"], cond["precip"])
        detail = f"{round(pop)}% chance of rain" if use_fc and pop is not None else None
        out.append({"name": name, "detail": detail, "tag": tags.get("precip"), "muted": False})
    if cond.get("temp"):
        t = _num(fc, "temp_f")
        out.append({"name": cond["temp"].replace("_", "/").title(), "detail": (f"{round(t)}°F" if use_fc and t is not None else None),
                    "tag": None, "muted": True})
    return out


# --------------------------------------------------------------------------- the "at a glance" scoreboard
GLANCE_VERB = {CLEAR: {("passing", True): "passes better", ("passing", False): "passes worse",
                       ("scoring", True): "scores more", ("scoring", False): "scores less"},
               LEANS: {("passing", True): "tends to pass a bit better", ("passing", False): "tends to pass a bit worse",
                       ("scoring", True): "tends to score a bit more", ("scoring", False): "tends to score a bit less"}}


def _phrase(groups, label, found):
    ups = [found[g][1] for g in groups]
    if len(groups) == 2 and ups[0] == ups[1]:
        word = "better" if ups[0] else "worse"
        return f"passes and scores {word}" if label == CLEAR else f"tends to pass and score a bit {word}"
    return " but ".join(GLANCE_VERB[label][(g, found[g][1])] for g in groups)


def glance_cell(sec, team, stats, scope="all"):
    """One team x one condition: the strongest passing/scoring finding in a few words, its label and n."""
    rs = {r.metric: r for r in sec["rows"] if r.team == team}
    p, s = rs.get("pass_eff"), rs.get("points")
    if p is None or p.status != "ok":
        return {"label": FEW, "text": "data not loaded yet" if (p is None or p.status == "not_loaded") else "no games",
                "sub": "", "n": None}
    found, labels = {}, []
    for grp, r in (("passing", p), ("scoring", s)):
        label = stats.group_label(team, sec["dim"], sec["bin"], grp, scope)[0]
        labels.append(label)
        if label in (CLEAR, LEANS) and _shows(r) and r.value:
            found[grp] = (label, r.value > 0, r)
    if not found:
        if NONE in labels:
            return {"label": NONE, "text": "No clear change in passing or scoring", "sub": "", "n": p.n}
        return {"label": FEW, "text": "Not enough games to say", "sub": "", "n": p.n}
    best = max(found.values(), key=lambda v: RANK[v[0]])[0]
    top = [g for g in ("passing", "scoring") if g in found and found[g][0] == best]
    rest = [g for g in ("passing", "scoring") if g in found and g not in top]
    text = _phrase(top, best, found)
    if best == CLEAR and top == ["passing"] and p.extra.get("game_terms"):
        text += ": " + p.extra["game_terms"].split(" (")[0]            # "about 30 more passing yards a game"
    sub = f"Also {_phrase(rest, found[rest[0]][0], found)} ({found[rest[0]][0]})" if rest else ""
    return {"label": best, "text": text[0].upper() + text[1:], "sub": sub, "n": p.n}


def glance(view, stats, scope="all"):
    """Rows for the scoreboard at the top of the card: one per condition shown, focal team then opponent."""
    out = []
    for sec in view.get("sections", []):
        name = (WIND_NAME if sec["dim"] == "wind" else PRECIP_NAME).get(sec["bin"], sec["bin"])
        out.append({"kind": "Wind" if sec["dim"] == "wind" else "Rain", "cond": name, "anchor": f"sec-{sec['dim']}-{sec['bin']}",
                    "cells": [glance_cell(sec, t, stats, scope) for t in (view["focal"], view["opponent"])]})
    return out


def playcall_summary(sec, focal, opp):
    """One or two sentences for a condition's playcalling block: only Leans findings (it can't be stronger), plain words."""
    out = []
    for team in (focal, opp):
        rs = {r.metric: r for r in sec["rows"] if r.team == team}
        r = rs.get("pass_rate")
        if r is not None and r.label == LEANS and _shows(r) and abs(r.value) >= 0.5:
            up = r.value > 0
            out.append(f"{team} has tended to throw {'more' if up else 'less'}: about {abs(r.value):.0f} {'more' if up else 'fewer'} "
                       f"passes per 100 plays (Leans, {r.n} games).")
        r = rs.get("plays")
        if r is not None and r.label == LEANS and _shows(r) and round(abs(r.value)) >= 1:
            k = round(abs(r.value))
            out.append(f"{team} has tended to run about {k} {'more' if r.value > 0 else 'fewer'} {'play' if k == 1 else 'plays'} "
                       f"a game (Leans, {r.n} games).")
    return " ".join(out) or f"No clear playcalling change for either team in {GAMES_WORD.get(sec['bin'], sec['bin'])} games."


def playcall_glance(view):
    """The one line under the scoreboard: who tends to throw more or less, and where. None when there is nothing."""
    groups = {}
    for sec in view.get("sections", []):
        for team in (view["focal"], view["opponent"]):
            r = next((x for x in sec["rows"] if x.team == team and x.metric == "pass_rate"), None)
            if r is not None and r.label == LEANS and _shows(r) and abs(r.value) >= 0.5:
                groups.setdefault((GAMES_WORD.get(sec["bin"], sec["bin"]), r.value > 0), []).append(team)
    if not groups:
        return None
    bits = [f"{' and '.join(teams)} {'tends' if len(teams) == 1 else 'tend'} to throw {'more' if up else 'less'} in {cond} games"
            for (cond, up), teams in groups.items()]
    return "Playcalling (not better or worse): " + "; ".join(bits) + ". All Leans."


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
    text = f"Since {when} ET ({len(ok)} pulls): " + ", ".join(bits) + (". Card changed: " + "; ".join(bin_moves) + "." if bin_moves else ". Card unchanged.")
    return text, ok
