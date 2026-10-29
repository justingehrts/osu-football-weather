"""All the app's decisions in plain Python (no Streamlit), so they can be tested.

The pipeline already did the statistics. This module only (1) looks numbers up, (2) turns the
pipeline's evidence tiers into the four plain-language labels, and (3) writes sentences that
never claim more than the label supports.

THE YARDSTICK. Every card number is the CONTROLLED "vs. all other games" estimate -- "windy vs.
not windy" with opponent strength, time of season and home/away held fixed. The other yardstick
("vs. the team's overall average") appears only on the Methodology page and inside expanders.
"""
import io
import csv
from dataclasses import dataclass, field

import pandas as pd

POOLED = "__POOLED__"
CLEAR, LEANS, NONE, FEW, CONTEXT = "Clear signal", "Leans", "No clear effect", "Not enough games", "Context only"
RANK = {CLEAR: 4, LEANS: 3, NONE: 2, FEW: 1, CONTEXT: 0}

# metric -> (plain name, unit, decimals, tier group that judges it)
METRIC_INFO = {
    "pass_eff": ("Passing efficiency", "yds/att", 2, ["passing"]),
    "points": ("Points scored", "pts", 1, ["scoring"]),
    "points_allowed": ("Points allowed", "pts", 1, []),
    "ppa_off": ("Offense: expected points per play", "PPA", 3, ["passing", "scoring"]),
    "rush_ypc": ("Rushing", "yds/carry", 2, []),
    "turnovers": ("Turnovers", "per game", 2, []),
}
WIND_NAME = {"calm": "Calm", "moderate": "Moderate wind", "windy": "Windy"}
PRECIP_NAME = {"none": "Dry", "light": "Light rain", "steady": "Steady rain", "wet": "Any rain (light + steady)",
               "uncertain": "Rain possible"}
VS_NOT = {"calm": "calm vs. not calm", "moderate": "moderate wind vs. other winds", "windy": "windy vs. not windy",
          "none": "dry vs. not dry", "light": "light rain vs. other games", "steady": "steady rain vs. other games",
          "wet": "any rain vs. dry games"}


# --------------------------------------------------------------------------- labels
def evidence_label(tier, n, bins):
    """Pipeline tier -> the plain label. 'Clear signal' needs the CLEAR tier AND n >= clear_signal_min_n."""
    if tier == "context_only":
        return CONTEXT
    if tier == "clear":
        return CLEAR if n >= bins["app"]["clear_signal_min_n"] else LEANS
    if tier == "leans":
        return LEANS
    if tier == "no_clear_effect":
        return NONE
    return FEW


def single_metric_label(lo, hi, n, bins):
    """Metrics the pipeline has no tier for (defense, rushing, turnovers): one metric can never be
    'Clear signal' (that takes two related metrics agreeing), so at best 'Leans'."""
    c = bins["confidence"]
    if n < c["suppress_below_n"] or lo is None or hi is None or pd.isna(lo) or pd.isna(hi):
        return FEW
    if n >= c["thin_below_n"] and (lo > 0 or hi < 0):
        return LEANS
    return NONE if n >= c["thin_below_n"] else FEW


@dataclass
class Result:
    team: str
    bin_type: str
    bin_value: str
    metric: str
    status: str = "ok"               # ok | not_loaded | no_games
    value: float = None              # controlled, vs. ALL OTHER GAMES
    lo: float = None
    hi: float = None
    raw_value: float = None          # uncontrolled, vs. all other games (cold-game expander only)
    n: int = 0
    label: str = FEW
    tier: str = None
    significant: bool = False
    extra: dict = field(default_factory=dict)

    @property
    def metric_name(self):
        return METRIC_INFO[self.metric][0]

    def text(self):
        if self.status == "not_loaded":
            return "data not loaded yet"
        if self.value is None or self.label == FEW:
            return "—"
        _, unit, dec, _ = METRIC_INFO[self.metric]
        return f"{self.value:+.{dec}f} {unit}"


def anecdote_text(metric, a):
    """'Show anyway' wording for one metric: plain averages, no adjustment, named as what they are."""
    if a is None or a.get("mean_in") is None:
        return None
    _, unit, dec, _ = METRIC_INFO[metric]
    out = f"<b>{a['mean_in']:.{dec}f} {unit}</b> in these {a['n_in']} games"
    if a.get("mean_other") is not None:
        out += f" vs. {a['mean_other']:.{dec}f} in this team's other {a['n_other']} games"
    return out


class Stats:
    """Indexed lookups into the pipeline's summary tables."""

    def __init__(self, splits, tiers, bins, teams):
        self.bins, self.teams = bins, teams
        self.s = splits.set_index(["team", "scope", "bin_type", "bin_value", "metric"]).sort_index() if len(splits) else splits
        self.t = tiers.set_index(["team", "scope", "bin_type", "bin_value", "grp"]).sort_index() if len(tiers) else tiers
        self.pooled_n = int(splits[splits.team == POOLED].n_teams.max()) if len(splits) and (splits.team == POOLED).any() else 0

    def loaded(self, team):
        return team in self.teams["loaded"] and (len(self.s) and team in self.s.index.get_level_values(0))

    def _tier(self, team, scope, bt, bv, group):
        try:
            r = self.t.loc[(team, scope, bt, bv, group)]
            return r["tier"], int(r["n"])
        except KeyError:
            return None, 0

    def result(self, team, bt, bv, metric, scope="all"):
        if team != POOLED and team in self.teams["deferred"]:
            return Result(team, bt, bv, metric, status="not_loaded", label=FEW)
        try:
            r = self.s.loc[(team, scope, bt, bv, metric)]
        except KeyError:
            st = "not_loaded" if not self.loaded(team) and team != POOLED else "no_games"
            return Result(team, bt, bv, metric, status=st, label=FEW)
        n = int(r["n"])
        lo, hi = r["ctl_rest_lo"], r["ctl_rest_hi"]
        val = None if pd.isna(r["ctl_rest"]) else float(r["ctl_rest"])
        groups = METRIC_INFO[metric][3]
        if groups:
            labels = []
            tier = None
            for g in groups:
                tr, tn = self._tier(team, scope, bt, bv, g)
                if tr is None:
                    continue
                labels.append((evidence_label(tr, tn or n, self.bins), tr))
            if labels:
                label, tier = min(labels, key=lambda x: RANK[x[0]])        # the weaker of the related groups
            else:
                label, tier = FEW, None
        else:
            label, tier = single_metric_label(lo, hi, n, self.bins), None
        return Result(team, bt, bv, metric, value=val, lo=None if pd.isna(lo) else float(lo),
                      hi=None if pd.isna(hi) else float(hi),
                      raw_value=None if pd.isna(r["rest_delta"]) else float(r["rest_delta"]),
                      n=n, label=label, tier=tier,
                      significant=bool(r["sig_ctl_rest"]) if not pd.isna(r["sig_ctl_rest"]) else False,
                      extra={"confidence": r["confidence"]})

    def group_label(self, team, bt, bv, group, scope="all"):
        tr, tn = self._tier(team, scope, bt, bv, group)
        return (evidence_label(tr, tn, self.bins), tn, tr) if tr else (FEW, 0, None)


# --------------------------------------------------------------------------- conditions
def condition_badges(wind_bin, precip_bin, temp_bin, precip_prob=None, bins=None):
    """['Windy', 'Light rain', 'Mild'] -- the plain-language chips."""
    out = []
    if wind_bin:
        out.append(WIND_NAME.get(wind_bin, wind_bin))
    if precip_bin == "uncertain":
        out.append(f"Rain possible ({precip_prob:.0f}%)" if precip_prob is not None else "Rain possible")
    elif precip_bin:
        out.append(PRECIP_NAME.get(precip_bin, precip_bin))
    if temp_bin:
        out.append(temp_bin.replace("_", "/").title())
    return out


def conditions_from(forecast, what_if):
    """Combine the stored forecast with the user's What-If choices (a choice, when set, wins)."""
    f = forecast or {}
    ok = f.get("status") == "ok"
    wind = what_if.get("wind") or (f.get("wind_bin") if ok else None)
    precip = what_if.get("precip") or (f.get("precip_bin") if ok else None)
    temp = what_if.get("temp") or (f.get("temp_bin") if ok else None)
    overridden = any(what_if.get(k) for k in ("wind", "precip", "temp"))
    return {"wind": wind, "precip": precip, "temp": temp, "overridden": overridden,
            "precip_prob": f.get("precip_prob") if ok else None, "from_forecast": ok and not overridden}


def precip_bins_to_show(precip, side_by_side):
    """Which precipitation bins get a card. Mid-range chance of rain (or the toggle) = dry AND wet."""
    if precip == "uncertain" or side_by_side:
        return ["none", "wet"]
    if precip in ("light", "steady"):
        return [precip, "wet"]                    # steady/light stay separate; 'any rain' is a steadier reference
    return [precip] if precip else []


# --------------------------------------------------------------------------- takeaway
def _direction(metric, value):
    return "higher" if value > 0 else "lower"


NOUN = {"passing": "passing efficiency", "scoring": "scoring"}
PRIMARY = {"passing": "pass_eff", "scoring": "points"}


GAMES_WORD = {"calm": "calm", "moderate": "moderate-wind", "windy": "windy", "none": "dry", "light": "light-rain",
              "steady": "steady-rain", "wet": "wet", "uncertain": "rain-possible"}
VERB = {CLEAR: "shows a clear signal of", LEANS: "leans toward"}


def takeaway(stats, focal, opp, wind, precip, bins, precip_prob=None):
    """ONE sentence from WIND and PRECIPITATION results only (never temperature).

    * Each finding names its OWN condition ("in windy games"): the wind result is "windy vs. not windy"
      whatever the rain does, so wind and rain are never glued into one imagined condition.
    * Wording follows the label exactly: "shows a clear signal of" only for Clear signal, "leans toward"
      for Leans. No clear effect / Not enough games are never claimed as findings.
    * If the chance of rain is a toss-up (`precip == 'uncertain'`) we make NO rain claim -- we say it is a
      toss-up and point to the dry and wet histories shown below.
    """
    uncertain = precip == "uncertain"
    dims = (("wind", [wind] if wind else []), ("precip", [precip] if precip and not uncertain else []))
    grouped = {}                                  # (dim, bin, team) -> list of clauses
    for dim, bvs in dims:
        for bv in bvs:
            for team in (focal, opp):
                if team is None or not stats.loaded(team):
                    continue
                for grp in ("passing", "scoring"):
                    label, n, _ = stats.group_label(team, dim, bv, grp)
                    if label not in (CLEAR, LEANS):
                        continue
                    r = stats.result(team, dim, bv, PRIMARY[grp])
                    if r.value is None or not r.value:
                        continue
                    grouped.setdefault((dim, bv, team), []).append((label, _direction("", r.value), NOUN[grp], n))
    ordered = sorted(grouped.items(), key=lambda kv: (0 if kv[0][0] == "wind" else 1,
                                                      -max(RANK[c[0]] for c in kv[1]), 0 if kv[0][2] == focal else 1))
    parts = []
    for (dim, bv, team), clauses in ordered[:3]:
        clauses.sort(key=lambda c: (-RANK[c[0]], c[2]))
        pieces = []
        for (label, direction), group in _groupby(clauses):
            pieces.append(f"{VERB[label]} {direction} {' and '.join(group)}")
        parts.append(f"{team} {' and '.join(pieces)} in {GAMES_WORD[bv]} games (n={min(c[3] for c in clauses)})")
    toss_up = (f"rain is a toss-up ({precip_prob:.0f}% chance), so the dry and wet histories are both shown below"
               if uncertain and precip_prob is not None else
               "rain is a toss-up, so the dry and wet histories are both shown below" if uncertain else None)
    if parts:
        tail = ", each compared with that team's other games"
        return "; ".join(parts) + tail + (f"; {toss_up}" if toss_up else "") + "."
    loaded = [t for t in (focal, opp) if t and stats.loaded(t)]
    shown = [(d, b) for d, bs in dims for b in bs]
    if toss_up and not shown:
        return toss_up[0].upper() + toss_up[1:] + "."
    if not loaded or not shown:
        return "There is no loaded history for these teams and conditions yet, so there is nothing to say about wind or rain."
    words = " or ".join(dict.fromkeys(f"{GAMES_WORD[b]} games" for _, b in shown))
    if any(stats.group_label(t, d, b, g)[0] == NONE for t in loaded for d, b in shown for g in ("passing", "scoring")):
        return (f"Neither team shows a clear effect in {words} (\"no clear effect\" is a real result, not a missing one)"
                + (f"; {toss_up}" if toss_up else "") + ".")
    return "There aren't enough past games in these conditions to say anything about wind or rain" + (f"; {toss_up}" if toss_up else "") + "."


def _groupby(clauses):
    """Merge clauses with the same label and direction: [(label, direction), [nouns...]]."""
    out = {}
    for label, direction, noun, _ in clauses:
        out.setdefault((label, direction), []).append(noun)
    return list(out.items())


# --------------------------------------------------------------------------- the card view
HEADLINE = ["pass_eff", "points", "points_allowed", "ppa_off"]      # fallback if bins.yaml has no app.headline_metrics


def card_metrics(bins):
    """(headline metrics shown to everyone, 'under the hood' metrics for the stats crowd), from bins.yaml."""
    app = bins.get("app", {})
    head = list(app.get("headline_metrics") or HEADLINE)
    hood = [m for m in (app.get("under_the_hood_metrics") or []) if m not in head]
    return head, hood


def build_gameday_view(stats, bins, teams, game, forecast, what_if, side_by_side=False, scope="all",
                       typicals=None, first_season=None):
    """Everything the Gameday Card shows, as plain data. The page renders it; the blurb, CSV and PNG
    are made from the very same object, so they can never disagree with what is on screen."""
    focal = teams["focal"]
    opp = game["opponent"]
    played = bool(game["completed"])
    indoor = game.get("dome") == 1
    view = {"focal": focal, "opponent": opp, "game_id": int(game["game_id"]), "played": played, "indoor": indoor,
            "title": f"{game['away_team']} at {game['home_team']}" if game["site"] != "neutral" else f"{game['away_team']} vs. {game['home_team']} (neutral site)",
            "away_team": game["away_team"], "home_team": game["home_team"], "joiner": "vs." if game["site"] == "neutral" else "at",
            "venue": game.get("venue"), "kickoff_utc": game.get("kickoff_utc"), "sections": [], "pooled_n": stats.pooled_n,
            "forecast_status": None, "badges": [], "takeaway": "", "notes": []}
    if played:
        view["forecast_status"] = "played"
        view["takeaway"] = "This game has been played; the result and its observed weather are shown below."
        return view
    if indoor:
        view["forecast_status"] = "indoor"
        view["takeaway"] = "Indoor game: weather is not a factor."
        view["notes"].append("indoor, weather not a factor")
        return view
    cond = conditions_from(forecast, what_if)
    status = (forecast or {}).get("status", "none")
    view["forecast_status"] = status if not cond["overridden"] else "what_if"
    view["conditions"] = cond
    if not (cond["wind"] or cond["precip"]):
        msgs = {"beyond_horizon": "This game is beyond the forecast horizon, so there is no forecast yet.",
                "none": "No forecast has been pulled for this game yet.",
                "no_kickoff_time": "The kickoff time isn't set yet, so there is no forecast.",
                "error": "The forecast services didn't answer; no forecast is available right now."}
        view["takeaway"] = msgs.get(status, "No forecast is available for this game.") + " Choose conditions under What-If to see how each team has done."
        view["notes"].append((forecast or {}).get("note"))
        return view
    from . import plain                                   # (imported here: plain builds on this module)
    precip_bins = precip_bins_to_show(cond["precip"], side_by_side)
    view["badges"] = condition_badges(cond["wind"], cond["precip"], cond["temp"], cond["precip_prob"], bins)
    head, hood = card_metrics(bins)
    view["headline_metrics"], view["hood_metrics"] = head, hood
    for dim, bvs in (("wind", [cond["wind"]] if cond["wind"] else []), ("precip", precip_bins)):
        for bv in bvs:
            rows = []
            for team in (focal, opp, POOLED):
                typical = (typicals or {}).get((team, dim, bv))
                for m in head + hood:
                    r = stats.result(team, dim, bv, m, scope)
                    text, verdict = plain.words(r)
                    r.extra.update(words=text, verdict=verdict, game_terms=plain.game_terms(r, typical),
                                   game_terms_short=plain.game_terms_short(r, typical), words_short=plain.words(r, short=True)[0])
                    rows.append(r)
            view["sections"].append({"dim": dim, "bin": bv, "title": VS_NOT.get(bv, bv), "rows": rows})
    view["takeaway"] = takeaway(stats, focal, opp, cond["wind"], cond["precip"], bins, cond.get("precip_prob"))
    view["on_air"] = plain.on_air_line(stats, focal, opp, cond["wind"], cond["precip"], bins, typicals, first_season,
                                       cond.get("precip_prob"))
    return view


# --------------------------------------------------------------------------- exports
def view_rows(view):
    out = []
    for sec in view.get("sections", []):
        for r in sec["rows"]:
            team = f"All {view['pooled_n']} loaded teams" if r.team == POOLED else r.team
            out.append({"game": view["title"], "team": team, "condition": sec["title"], "metric": r.metric_name,
                        "vs_all_other_games": None if r.value is None else round(r.value, 3), "unit": METRIC_INFO[r.metric][1],
                        "in_words": (r.extra.get("words") or "") + (f" ({r.extra['verdict']})" if r.extra.get("verdict") else ""),
                        "in_game_terms": r.extra.get("game_terms") or "",
                        "n_games": r.n, "evidence": r.label if r.status == "ok" else "data not loaded yet",
                        "interval_90_lo": None if r.lo is None else round(r.lo, 3), "interval_90_hi": None if r.hi is None else round(r.hi, 3)})
    return out


def csv_bytes(rows):
    if not rows:
        return b""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode()


def blurb(view):
    """Plain-text version of the card for pasting into a script, chat or email."""
    lines = [f"{view['title']}" + (f" - {view['venue']}" if view.get("venue") else "")]
    if view["badges"]:
        lines.append("Forecast: " + ", ".join(view["badges"]))
    if view.get("on_air"):
        lines.append("On-air line: " + view["on_air"])
    lines += [view["takeaway"], ""]
    for sec in view.get("sections", []):
        lines.append(f"{sec['title'].upper()} (vs. all other games, controlled for opponent, month, home/away)")
        for team in (view["focal"], view["opponent"], POOLED):
            rs = [r for r in sec["rows"] if r.team == team and r.metric in ("pass_eff", "points")]
            name = f"All {view['pooled_n']} loaded teams" if team == POOLED else team
            if not rs or rs[0].status == "not_loaded":
                lines.append(f"  {name}: data not loaded yet")
                continue
            lines.append(f"  {name}: " + "; ".join(
                f"{r.metric_name} {r.extra.get('words') or r.text()} (n={r.n}, {r.label})" for r in rs))
        lines.append("")
    lines.append("Exploratory history, not a prediction. Source: OSU Football Weather Splits.")
    return "\n".join(lines).strip()
