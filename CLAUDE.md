# OSU Football Weather Splits

Forecast-driven lookup: given a gameday forecast, show how Ohio State and
their opponent have historically performed in those conditions versus
their own baseline. Used by a TV weather team and sports team.

## Architecture
- /pipeline: Python ingest scripts, run by GitHub Actions (never by the app)
- /data: SQLite db + summary tables, committed by the Action
- /config: bins.yaml (all thresholds), venue/station overrides
- /app: Streamlit app, READ-ONLY on the database
- Heavy math is precomputed in the pipeline; the app only loads and displays.

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

## Style
- Plain, readable Python; comment the "why" for non-obvious steps.
- The owner is a meteorologist, not a developer: explain choices in plain language.
