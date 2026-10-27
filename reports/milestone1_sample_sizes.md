# Milestone 1: are the sample sizes workable?

_Generated 2026-10-27 19:50 UTC._

**How to read this.** *n* is the number of games in that weather bin. Deltas are the team's result in that bin minus the team's own average over all its outdoor games with usable weather (positive = better than usual for points / yards, worse for turnovers). Bins with n below 5 show “—”; n 5-9 is **thin**; 10+ is solid. The *n ex-2020* column drops the COVID season.

## Summary

| Team | Usable games | Solid bins | Thin bins | Suppressed bins |
|---|---|---|---|---|
| Ohio State | 133 | 9 | 2 | 1 |
| USC | 131 | 6 | 3 | 2 |
| Oregon | 132 | 7 | 3 | 1 |
| Northwestern | 136 | 9 | 1 | 2 |

## Ohio State

152 completed games ingested · 133 outdoor with usable weather · 16 dome (excluded) · 0 missing weather · 3 too few observations · 1 usable games use a station >25 mi away · 8 games in COVID season(s)

| Bin | n | n ex-2020 | Confidence | Δ Pass yds/att | Δ Rush yds/carry | Δ Points | Δ Turnovers |
|---|---|---|---|---|---|---|---|
| wind: calm | 61 | 55 | solid | +0.57 | +0.22 | +1.29 | -0.06 |
| wind: moderate | 41 | 41 | solid | +0.01 | -0.14 | +0.20 | +0.09 |
| wind: windy | 31 | 31 | solid | -1.08 | -0.23 | -2.80 | -0.01 |
| precip: none | 111 | 106 | solid | +0.02 | +0.03 | -0.17 | -0.03 |
| precip: light | 13 | 12 | solid | +0.03 | -0.14 | -2.13 | -0.01 |
| precip: steady | 9 | 9 | thin | -0.38 | -0.17 | +5.11 | +0.44 |
| snow: snow | 4 | 4 | suppressed | — | — | — | — |
| snow: no_snow | 129 | 123 | solid | +0.02 | +0.01 | +0.28 | +0.01 |
| temp: cold | 21 | 19 | solid | -0.58 | +0.12 | -2.23 | +0.04 |
| temp: mild | 71 | 67 | solid | -0.28 | -0.13 | -1.64 | -0.01 |
| temp: warm | 35 | 35 | solid | +0.92 | +0.12 | +4.76 | -0.06 |
| temp: hot | 6 | 6 | thin | -0.19 | +0.55 | -0.56 | +0.33 |

## USC

145 completed games ingested · 131 outdoor with usable weather · 7 dome (excluded) · 0 missing weather · 7 too few observations · 0 usable games use a station >25 mi away · 6 games in COVID season(s)

| Bin | n | n ex-2020 | Confidence | Δ Pass yds/att | Δ Rush yds/carry | Δ Points | Δ Turnovers |
|---|---|---|---|---|---|---|---|
| wind: calm | 88 | 85 | solid | +0.10 | -0.01 | +0.76 | -0.10 |
| wind: moderate | 34 | 33 | solid | +0.09 | -0.01 | +0.29 | +0.13 |
| wind: windy | 9 | 8 | thin | -1.33 | +0.12 | -8.51 | +0.49 |
| precip: none | 124 | 119 | solid | +0.02 | +0.02 | +0.14 | -0.03 |
| precip: light | 2 | 2 | suppressed | — | — | — | — |
| precip: steady | 5 | 5 | thin | +0.34 | -0.20 | +1.14 | +0.00 |
| snow: snow | 0 | 0 | suppressed | — | — | — | — |
| snow: no_snow | 131 | 126 | solid | +0.00 | +0.00 | +0.00 | +0.00 |
| temp: cold | 4 | 3 | suppressed | — | — | — | — |
| temp: mild | 74 | 71 | solid | -0.41 | -0.23 | -2.52 | +0.04 |
| temp: warm | 43 | 42 | solid | +0.57 | +0.35 | +4.08 | -0.12 |
| temp: hot | 9 | 9 | thin | +0.99 | +0.51 | +8.61 | -0.06 |

## Oregon

149 completed games ingested · 132 outdoor with usable weather · 10 dome (excluded) · 1 missing weather · 6 too few observations · 0 usable games use a station >25 mi away · 7 games in COVID season(s)

| Bin | n | n ex-2020 | Confidence | Δ Pass yds/att | Δ Rush yds/carry | Δ Points | Δ Turnovers |
|---|---|---|---|---|---|---|---|
| wind: calm | 78 | 74 | solid | -0.04 | -0.05 | +0.29 | +0.06 |
| wind: moderate | 33 | 32 | solid | +0.40 | +0.15 | +1.18 | -0.01 |
| wind: windy | 21 | 21 | solid | -0.52 | -0.06 | -2.94 | -0.19 |
| precip: none | 118 | 113 | solid | +0.07 | -0.04 | +0.14 | +0.05 |
| precip: light | 9 | 9 | thin | -0.29 | -0.08 | +0.37 | -0.77 |
| precip: steady | 5 | 5 | thin | -1.40 | +1.08 | -4.05 | +0.30 |
| snow: snow | 0 | 0 | suppressed | — | — | — | — |
| snow: no_snow | 132 | 127 | solid | +0.00 | +0.00 | +0.00 | +0.00 |
| temp: cold | 7 | 5 | thin | +0.26 | +0.43 | -1.71 | +0.47 |
| temp: mild | 93 | 90 | solid | -0.31 | -0.11 | -2.06 | +0.08 |
| temp: warm | 29 | 29 | solid | +1.06 | +0.46 | +7.74 | -0.34 |
| temp: hot | 3 | 3 | suppressed | — | — | — | — |

## Northwestern

143 completed games ingested · 136 outdoor with usable weather · 4 dome (excluded) · 1 missing weather · 2 too few observations · 0 usable games use a station >25 mi away · 9 games in COVID season(s)

| Bin | n | n ex-2020 | Confidence | Δ Pass yds/att | Δ Rush yds/carry | Δ Points | Δ Turnovers |
|---|---|---|---|---|---|---|---|
| wind: calm | 56 | 54 | solid | +0.06 | -0.05 | +0.30 | -0.03 |
| wind: moderate | 46 | 44 | solid | +0.06 | -0.14 | -0.90 | +0.20 |
| wind: windy | 34 | 30 | solid | -0.18 | +0.26 | +0.73 | -0.21 |
| precip: none | 121 | 115 | solid | +0.02 | +0.02 | +0.00 | +0.03 |
| precip: light | 12 | 10 | solid | +0.04 | -0.15 | +1.07 | -0.14 |
| precip: steady | 3 | 3 | suppressed | — | — | — | — |
| snow: snow | 3 | 3 | suppressed | — | — | — | — |
| snow: no_snow | 133 | 125 | solid | +0.01 | -0.01 | +0.08 | -0.01 |
| temp: cold | 18 | 16 | solid | -0.31 | +0.29 | +0.24 | +0.08 |
| temp: mild | 80 | 76 | solid | -0.03 | -0.06 | +0.19 | -0.10 |
| temp: warm | 33 | 31 | solid | +0.32 | -0.05 | +0.09 | +0.16 |
| temp: hot | 5 | 5 | thin | -0.90 | +0.17 | -4.50 | +0.32 |

## Venue / station flags

| Venue | Dome | Station | Miles | Flags |
|---|---|---|---|---|
| Lane Stadium (3799) |  | ROA | 25.3 | FAR STATION: 25.3 mi (> 25) |
| Caesars Superdome (3493) | yes |  |  |  |
| Aviva Stadium (3504) |  |  |  | outside lower 48 (53.33523, -6.228447) -- no US station used, no weather splits |
| Alamodome (3604) | yes |  |  |  |
| AT&T Stadium (3687) | yes |  |  |  |
| Ford Field (3727) | yes |  |  |  |
| Lucas Oil Stadium (3812) | yes |  |  |  |
| State Farm Stadium (3970) | yes |  |  |  |
| Mercedes-Benz Stadium (5348) | yes |  |  |  |
| Allegiant Stadium (6501) | yes |  |  |  |
