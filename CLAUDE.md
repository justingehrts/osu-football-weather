# OSU Football Weather Splits

Forecast-driven lookup: given a gameday forecast, show how Ohio State and
their opponent have historically performed in those conditions versus
their own baseline. Used by a TV weather team and sports team.

## Architecture
- /pipeline: Python ingest scripts, run by GitHub Actions (never by the app)
- /data: SQLite db + summary tables, committed by the Action
- /config: bins.yaml (all thresholds), venue/station overrides
- /app: Streamlit app, READ-ONLY on the databases (opened with `mode=ro`; a test proves writes fail)
- Heavy math is precomputed in the pipeline; the app only loads and displays.
- Two SQLite files: `data/osu_weather.db` (history + summary tables, changes after new games) and
  `data/forecasts.sqlite` (forecast snapshots only, tiny, committed often).

## Data sources
- Games/box scores/plays/ratings: CollegeFootballData API (key in CFBD_API_KEY) -- see
  "CFBD call budget" below; the free tier is only 1,000 calls a month
- Observations: Iowa Environmental Mesonet ASOS API (no key)
- Forecasts: NWS api.weather.gov hourly gridpoint (Open-Meteo as fallback)

## Rules
- Every displayed stat must carry its sample size (n games).
- n < 5 is suppressed, 5-9 is flagged "thin", 10+ is "solid" (set in bins.yaml).
- Stats are shown relative to that team's own baseline, not raw.
- Dome/indoor games are excluded from weather splits.
- Never hardcode thresholds; read them from /config/bins.yaml.
- Store forecast snapshots with timestamps; never overwrite them.
- The 2020 season is flagged (COVID-altered); keep it but make it filterable.
- Main branch is the live branch for Streamlit once deployed: work on branches
  and merge deliberately once the app exists.

## CFBD call budget (free tier = 1,000 calls/month)
- At the start of any session that will call CFBD, check the remaining calls first (the `/info`
  endpoint: `remainingCalls`, `usedCalls`, `resetAt`) and tell the owner before doing anything else.
  The sandbox cannot reach CFBD; use the GitHub Actions runner (secret `CFBD_API_KEY`).
- Before any backfill, compute and print an exact call budget per endpoint
  (`python -m pipeline.plan`). If the estimate exceeds 500 calls, stop and ask the owner.
- Prefer by-year and by-week requests over by-team requests when they cost about the same but
  return more of the league (box scores, PPA); postseason games need separate calls.
  `pipeline/ingest_games.py` picks the cheaper of by-week vs by-team per season.
- Cache every raw API response under `data/raw` and commit it. Never re-request anything whose
  cached file exists (only current-season requests carry a time limit, `current_season_ttl_hours`).
  Data already in the database counts too: `ingest_log` remembers finished team-seasons.
- `data/cfbd_calls.json` is a persistent call counter. A run aborts before any call that would take
  the month's total past `cfbd.monthly_cap` (600, in bins.yaml). Seed/sync it from CFBD's `/info`.
- Test any new endpoint with a single team-season (or single week) before looping. The ingest
  does this automatically: the first request of each new shape must store data or the run stops.
- All CFBD settings (caps, thresholds, TTLs) live in `config/bins.yaml` under `cfbd:`.

## Evidence tiers (computed in the pipeline, stored in `team_tiers`)
Judged on the CONTROLLED model (opponent SP+ strength, month bucket and home/away held fixed), per
team / bin / metric group, with 90% bootstrap intervals. Metric groups: passing = pass yds/att +
offensive PPA; scoring = points scored + offensive PPA.
- **clear**: n >= 10 and the controlled interval excludes zero (same direction) on 2+ related metrics.
- **leans**: the related metrics point the same way and the effect is at least `tiers.lean_min_z`
  standard errors in size, but the interval spans zero or n is 5-9.
- **no_clear_effect**: n >= 10 and nothing there.
- **insufficient**: n < 5 (also n 5-9 with no lean).
- **context_only**: temperature bins for a team whose controlled model has no "clear" temperature
  cell -- shown for context, not as evidence.
Everything is EXPLORATORY: hundreds of cells are tested, so about 1 in 10 intervals exclude zero by
luck. Tiers and stars are leads to check, not findings. Raw, opponent-adjusted and controlled deltas
all use the same yardstick ("bin vs the team's average game") so they can be compared.

## How the app and the workflows fit together
```
CFBD ──(1 call/run: any new completed games?)──► refresh.yml ──► data/osu_weather.db ──┐
IEM ASOS (airport weather for each finished game) ──────────────┘   team_splits, team_tiers │
NWS (Open-Meteo fallback) ──► forecast.yml ──► data/forecasts.sqlite (append-only) ───────┼──► app/ (read-only)
config/bins.yaml, teams.yaml, opponents.yaml ───────────────────────────────────────────────┘
```
- `.github/workflows/refresh.yml`: Sunday and Monday (UTC 07:17 and 19:17) Aug-Jan. ONE CFBD call; only if a loaded
  team has a completed game with no box score does it fetch box scores + PPA, refresh the current-season SP+
  (1 call), pull the ASOS windows, recompute `team_splits`/`team_tiers`, and commit. Quiet runs commit nothing
  (the call counter is re-read from CFBD's free `/info` at the start of every run, so it is never committed alone).
  Budget: about 4 calls a week when quiet, about 8 on a game week. It is the only scheduled CFBD user.
- `.github/workflows/forecast.yml`: every 6 hours Tue-Sat in season; NWS hourly gridpoint (Open-Meteo only if NWS
  fails) for each upcoming game's venue, kickoff to +3.5 h, mapped to the same bins as the history. Each pull is a NEW
  row in `forecast_snapshots`; rows are never updated or deleted. A game beyond `forecast.horizon_hours` gets a
  `beyond_horizon` row (we say so, we do not guess); dome games get no row ("indoor, weather not a factor").
- `.github/workflows/ingest.yml` is manual-only (a full incremental run, e.g. after un-deferring a team).
- Deferred teams (`deferred:` in config/opponents.yaml) stay on the schedule but are never loaded; the app shows
  "data not loaded yet" for them and nothing may fail because they are missing.
- The app lives in `app/` (`streamlit_app.py` = Gameday Card, `pages/` = Team Explorer, Evidence, Methodology).
  Decisions (labels, takeaway, exports) are in `app/lib/logic.py` with no Streamlit import so they are unit tested.
  Run it locally: `pip install -r app/requirements.txt && streamlit run app/streamlit_app.py`.
  Do NOT deploy from a branch; main is the live branch once the owner has reviewed.

## App presentation rules (owner's rules; tests enforce several of them)
- **Default yardstick** is the controlled "vs. all other games" number ("windy vs. not windy"), labelled on every
  card. The "vs. the team's overall average" yardstick appears ONLY on the Methodology page and inside expanders;
  never mix the two on one card.
- Always compare the two teams LEFT to RIGHT (focal team left, opponent right), for every scenario; when there is more
  than one scenario (e.g. dry and wet), stack the scenarios top to bottom, each with its own left-right comparison.
- Lead with wind. Each team's own result comes first; the pooled line is a reference labelled "all N loaded teams".
- Evidence labels (plain language): **Clear signal**, **Leans**, **No clear effect**, **Not enough games**.
  "Clear signal" requires BOTH the pipeline's `clear` tier AND n >= `app.clear_signal_min_n` (30, in bins.yaml);
  otherwise show "Leans". So steady rain is "Leans" and stays a separate bin from light rain. A single metric with no
  tier (points allowed, rushing, turnovers) is at most "Leans". "No clear effect" is a real result: show it plainly.
- The one-sentence takeaway uses ONLY wind and precipitation, only Clear signal / Leans findings, names each
  finding's own condition, and never words anything stronger than its label.
- Temperature is context only: never in the takeaway or the Gameday headline. It lives in the Explorer and in an
  expander labelled "Temperature (context only): results differ by team".
- Cold: show the controlled number by default; in an expander show the raw number with the note that raw cold-game
  results look worse because cold games are late-season games against tougher opponents.
- Interval numbers appear only inside expanders. Every number carries its n.
- Team names in HEADER places only (the Gameday Card headers and the PNG) are chips in school colors from
  `config/team_colors.yaml`, each pair chosen for legibility (a test enforces contrast >= 4.5:1 and that every loaded
  team has colors). Teams without an entry get a neutral chip. The pooled "all N teams" reference stays neutral.
- "Not enough games" blocks get a per-block **Show anyway** switch. It starts OFF for every visitor (session-only; never
  in the page address), and when on it shows the PLAIN average of those few games next to the team's other games, in a
  dashed "anecdote, not a finding" box. The label stays "Not enough games"; the takeaway, blurb, CSV and PNG never use
  revealed numbers; a block with 0 games has nothing to reveal.
- FCS games are excluded from adjusted/controlled numbers (no SP+ rating); the Methodology page says so.
- Played games show results with observed weather; only upcoming games get a forecast. A game beyond the forecast
  horizon says so; a mid-range chance of rain (`forecast.precip_prob_middle`) shows both the dry and the wet history, stacked top to bottom.
- Broadcast clarity (helpers in `app/lib/plain.py`, charts in `app/lib/charts.py`; no Streamlit import, unit tested):
  - Numbers are said in words with direction ("1.72 fewer yards per pass"); stats where lower is good add "(better)/(worse)".
    The exact adjusted number stays beside it, small.
  - Game-sized translations ("about 55 fewer passing yards a game (-18%) · usually 9.3 yards per pass in other games") combine the
    adjusted change with the team's PLAIN average in its other games, so they always say "about". Never for Not enough games or
    the pooled line.
  - Each condition gets a dot-and-range chart: right is always better (lower-is-better stats are flipped), dashed zero line =
    no difference, colored by evidence label, pooled line included. Interval NUMBERS never appear in the chart or its tooltips.
  - The on-air line (wind first, never temperature) maps labels to hedges: Clear signal "has clearly", Leans "has tended to ...
    but that's only N games" (n < `app.clear_signal_min_n`) or "but it's not a consistent pattern". A toss-up rain chance always
    gets its own sentence.
  - Card metrics come from `app.headline_metrics`; offensive PPA (`app.under_the_hood_metrics`) is only in the "Under the hood"
    expander.
  - Playcalling (`pass_rate` = passes per 100 plays, `plays` = pace; `app.playcalling_metrics`) is NOT better or worse: it
    gets its own "Playcalling" block under each condition, a neutral chart (axis "ran more / threw more", never flipped, no
    good/bad words), and has no evidence tier, so it is at most Leans (never Clear signal). The on-air line gets one playcalling
    sentence only for a Leans finding. It is box-score playcalling (game script and sacks-as-rushes are mixed in; the
    Methodology page says so). Computed in the pipeline with the same controlled model; no extra CFBD calls.
  - Forecast details: distance to each bin line (borderline margins in `forecast.borderline`; borderline wind/rain shows a
    warning near the badges), trend across pulls, and the hour-by-hour window (`hours` in the snapshot's `detail` JSON).

## Style
- Plain, readable Python; comment the "why" for non-obvious steps.
- The owner is a meteorologist, not a developer: explain choices in plain language.
