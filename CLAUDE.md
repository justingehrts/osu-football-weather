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
- Games/box scores/plays: CollegeFootballData API (key in CFBD_API_KEY)
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

## Style
- Plain, readable Python; comment the "why" for non-obvious steps.
- The owner is a meteorologist, not a developer: explain choices in plain language.
