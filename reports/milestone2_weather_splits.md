# Milestone 2: weather splits, opponent-adjusted, with uncertainty

_Generated 2026-10-28 00:42 UTC._

> **EXPLORATORY.** This report tests hundreds of team × bin × metric cells. At a 90% level, roughly 1 in 10 intervals will exclude zero by luck alone, so a starred (\*) delta is a lead to check, not a finding. Prefer patterns that show up across teams and across related metrics.

**How to read this.**

- *n* = games in the bin. Fewer than 5 is hidden (—), 5-9 is **thin**, 10+ is solid. *n adj* is the number of those games with an opponent rating (FCS opponents have none).
- **Raw Δ** = bin average minus the team's average over all its usable outdoor games.
- **Adj Δ** = bin result minus what we'd expect *given the opponents actually played* (straight-line fit on the opponent's SP+ rating, per team and metric). It removes opponent quality only -- **not** month, home/away or anything else; see the confounding tables.
- Brackets are a bootstrap 90% interval. **\*** = interval excludes zero.
- wet = light + steady · warm_hot = warm + hot (merged bins, see bins.yaml).

## Sample sizes

| Team | Usable games | Solid bins | Thin bins | Suppressed bins |
|---|---|---|---|---|
| Ohio State | 133 | 10 | 2 | 0 |
| USC | 131 | 6 | 4 | 2 |
| Oregon | 132 | 8 | 3 | 1 |
| Northwestern | 136 | 10 | 1 | 1 |

_Bins counted include the merged ones._

## How much does opponent adjustment change things?

Solid cells only (n ≥ 10), all seasons, cells that have an adjusted value. *Sign flips* = raw and adjusted deltas point in opposite directions. *Excl. 0* = how many intervals exclude zero (expect roughly 1 in 10 by luck alone).

| Metric | Cells | Avg \|raw Δ\| | Avg \|adj Δ\| | Sign flips | Raw excl. 0 | Adj excl. 0 |
|---|---|---|---|---|---|---|
| Pass yds/att | 34 | 0.35 | 0.32 | 4 | 12 | 12 |
| Rush yds/carry | 34 | 0.19 | 0.17 | 5 | 6 | 5 |
| Points scored | 34 | 1.7 | 1.5 | 10 | 8 | 4 |
| Points allowed (defense) | 34 | 1.6 | 1.5 | 6 | 8 | 8 |
| Turnovers | 34 | 0.11 | 0.12 | 3 | 4 | 2 |
| Offensive PPA/play | 34 | 0.032 | 0.028 | 7 | 10 | 10 |

## Intervals that exclude zero (solid cells)

264 team/bin/metric cells have n ≥ 5; about 26 would be expected to exclude zero by chance alone. Below are the 55 solid cells where the raw or adjusted interval excludes zero (many are the same underlying effect seen through several metrics, and merged bins overlap their parents).

| Team | Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| Ohio State | temp: warm | Pass yds/att | 35 | +0.85 [+0.29, +1.39] **\*** | +0.69 [+0.15, +1.21] **\*** |
| Ohio State | temp: warm_hot | Pass yds/att | 41 | +0.68 [+0.18, +1.16] **\*** | +0.49 [+0.01, +0.95] **\*** |
| Ohio State | wind: calm | Pass yds/att | 61 | +0.55 [+0.17, +0.92] **\*** | +0.60 [+0.23, +0.96] **\*** |
| Ohio State | wind: windy | Pass yds/att | 31 | -1.15 [-1.87, -0.39] **\*** | -1.27 [-1.98, -0.53] **\*** |
| Ohio State | temp: warm | Points scored | 35 | +4.8 [+1.0, +8.6] **\*** | +3.2 [-0.2, +6.6] |
| Ohio State | temp: warm_hot | Points scored | 41 | +4.0 [+0.7, +7.4] **\*** | +2.0 [-0.9, +4.9] |
| Ohio State | wind: windy | Points scored | 31 | -2.8 [-7.0, +1.8] | -4.5 [-8.3, -0.7] **\*** |
| Ohio State | temp: warm | Points allowed (defense) | 35 | -3.0 [-5.4, -0.6] **\*** | -2.4 [-4.6, -0.2] **\*** |
| Ohio State | temp: warm_hot | Points allowed (defense) | 41 | -2.8 [-5.0, -0.6] **\*** | -1.9 [-3.9, -0.0] **\*** |
| Ohio State | precip: none | Offensive PPA/play | 111 | +0.011 [-0.002, +0.026] | +0.014 [+0.001, +0.029] **\*** |
| Ohio State | precip: wet | Offensive PPA/play | 22 | -0.058 [-0.134, +0.013] | -0.071 [-0.142, -0.005] **\*** |
| Ohio State | temp: mild | Offensive PPA/play | 71 | -0.036 [-0.063, -0.011] **\*** | -0.034 [-0.058, -0.010] **\*** |
| Ohio State | temp: warm | Offensive PPA/play | 35 | +0.082 [+0.039, +0.126] **\*** | +0.063 [+0.023, +0.102] **\*** |
| Ohio State | temp: warm_hot | Offensive PPA/play | 41 | +0.073 [+0.034, +0.112] **\*** | +0.050 [+0.015, +0.086] **\*** |
| Ohio State | wind: calm | Offensive PPA/play | 61 | +0.053 [+0.022, +0.084] **\*** | +0.057 [+0.029, +0.086] **\*** |
| Ohio State | wind: windy | Offensive PPA/play | 31 | -0.067 [-0.128, -0.007] **\*** | -0.081 [-0.138, -0.026] **\*** |
| Ohio State | wind: calm | Rush yds/carry | 61 | +0.26 [+0.01, +0.52] **\*** | +0.27 [+0.04, +0.51] **\*** |
| Ohio State | wind: windy | Rush yds/carry | 31 | -0.28 [-0.70, +0.11] | -0.43 [-0.80, -0.08] **\*** |
| USC | temp: mild | Pass yds/att | 74 | -0.39 [-0.66, -0.12] **\*** | -0.27 [-0.51, -0.03] **\*** |
| USC | temp: warm | Pass yds/att | 43 | +0.60 [+0.14, +1.05] **\*** | +0.42 [+0.00, +0.84] **\*** |
| USC | temp: warm_hot | Pass yds/att | 52 | +0.65 [+0.26, +1.03] **\*** | +0.43 [+0.10, +0.78] **\*** |
| USC | temp: mild | Points scored | 74 | -2.5 [-4.2, -0.8] **\*** | -1.3 [-2.6, -0.1] **\*** |
| USC | temp: warm | Points scored | 43 | +4.1 [+1.3, +6.9] **\*** | +2.5 [+0.3, +4.7] **\*** |
| USC | temp: warm_hot | Points scored | 52 | +4.9 [+2.5, +7.2] **\*** | +2.9 [+1.1, +4.7] **\*** |
| USC | temp: mild | Points allowed (defense) | 74 | +2.9 [+1.5, +4.5] **\*** | +2.4 [+1.1, +3.8] **\*** |
| USC | temp: warm | Points allowed (defense) | 43 | -3.7 [-6.2, -1.4] **\*** | -3.1 [-5.2, -1.0] **\*** |
| USC | temp: warm_hot | Points allowed (defense) | 52 | -4.0 [-6.1, -2.0] **\*** | -2.8 [-4.7, -1.0] **\*** |
| USC | precip: none | Offensive PPA/play | 124 | +0.005 [+0.000, +0.012] **\*** | +0.003 [-0.001, +0.007] |
| USC | temp: warm_hot | Offensive PPA/play | 52 | +0.051 [+0.012, +0.088] **\*** | +0.023 [-0.009, +0.055] |
| USC | temp: mild | Rush yds/carry | 74 | -0.29 [-0.53, -0.05] **\*** | -0.17 [-0.39, +0.05] |
| USC | temp: warm | Rush yds/carry | 43 | +0.43 [+0.01, +0.86] **\*** | +0.27 [-0.11, +0.63] |
| USC | temp: warm_hot | Rush yds/carry | 52 | +0.47 [+0.12, +0.82] **\*** | +0.26 [-0.06, +0.57] |
| Oregon | precip: none | Pass yds/att | 118 | +0.10 [+0.00, +0.22] **\*** | +0.11 [+0.00, +0.23] **\*** |
| Oregon | precip: wet | Pass yds/att | 14 | -0.88 [-1.74, -0.03] **\*** | -0.92 [-1.80, -0.04] **\*** |
| Oregon | temp: mild | Pass yds/att | 93 | -0.32 [-0.53, -0.13] **\*** | -0.24 [-0.44, -0.06] **\*** |
| Oregon | temp: warm | Pass yds/att | 29 | +1.07 [+0.52, +1.61] **\*** | +0.93 [+0.27, +1.57] **\*** |
| Oregon | temp: warm_hot | Pass yds/att | 32 | +0.87 [+0.34, +1.39] **\*** | +0.78 [+0.17, +1.39] **\*** |
| Oregon | temp: mild | Points scored | 93 | -2.1 [-3.7, -0.6] **\*** | -0.7 [-1.7, +0.4] |
| Oregon | temp: warm | Points scored | 29 | +7.7 [+3.1, +12.4] **\*** | +3.0 [-1.0, +6.7] |
| Oregon | temp: warm_hot | Points scored | 32 | +6.4 [+2.2, +10.6] **\*** | +2.8 [-1.0, +6.3] |
| Oregon | wind: calm | Points allowed (defense) | 78 | +2.0 [+0.4, +3.6] **\*** | +1.0 [-0.5, +2.4] |
| Oregon | wind: windy | Points allowed (defense) | 21 | -5.0 [-8.8, -0.9] **\*** | -4.6 [-8.4, -0.7] **\*** |
| Oregon | temp: mild | Offensive PPA/play | 93 | -0.038 [-0.060, -0.017] **\*** | -0.022 [-0.041, -0.004] **\*** |
| Oregon | temp: warm | Offensive PPA/play | 29 | +0.129 [+0.073, +0.186] **\*** | +0.085 [+0.023, +0.144] **\*** |
| Oregon | temp: warm_hot | Offensive PPA/play | 32 | +0.102 [+0.048, +0.158] **\*** | +0.069 [+0.009, +0.127] **\*** |
| Oregon | temp: warm | Rush yds/carry | 29 | +0.54 [+0.07, +1.03] **\*** | +0.20 [-0.34, +0.71] |
| Oregon | wind: moderate | Rush yds/carry | 33 | +0.27 [-0.13, +0.71] | +0.39 [+0.00, +0.79] **\*** |
| Oregon | precip: none | Turnovers | 118 | +0.05 [+0.00, +0.10] **\*** | +0.04 [-0.00, +0.10] |
| Oregon | precip: wet | Turnovers | 14 | -0.38 [-0.75, -0.00] **\*** | -0.37 [-0.76, +0.02] |
| Oregon | temp: warm | Turnovers | 29 | -0.34 [-0.59, -0.08] **\*** | -0.35 [-0.62, -0.06] **\*** |
| Oregon | temp: warm_hot | Turnovers | 32 | -0.35 [-0.58, -0.11] **\*** | -0.37 [-0.63, -0.10] **\*** |
| Northwestern | wind: moderate | Points allowed (defense) | 46 | +2.4 [-0.1, +4.9] | +3.5 [+1.2, +5.9] **\*** |
| Northwestern | wind: windy | Points allowed (defense) | 34 | -3.6 [-6.3, -0.8] **\*** | -4.9 [-7.5, -2.3] **\*** |
| Northwestern | temp: cold | Rush yds/carry | 18 | +0.28 [-0.23, +0.83] | +0.50 [+0.10, +0.90] **\*** |
| Northwestern | wind: windy | Rush yds/carry | 34 | +0.38 [+0.03, +0.75] **\*** | +0.41 [+0.12, +0.69] **\*** |

## Ohio State

152 completed games ingested · 133 outdoor with usable weather · 16 dome (excluded) · 0 missing weather · 3 too few observations · 1 usable games use a station >25 mi away · 8 games in COVID season(s)

### Ohio State: what is each bin made of?

Share of the bin's games by kickoff month (approx. local), site, and average opponent SP+ rating (*vs all games* = difference from this team's overall average opponent; positive = tougher opponents than usual).

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 133 | 33% | 31% | 33% | 3% | 59% | 38% | 2% | +5.7 | +0.0 |
| wind: calm | 61 | 33% | 34% | 26% | 7% | 57% | 39% | 3% | +5.7 | +0.0 |
| wind: moderate | 41 | 37% | 22% | 41% | 0% | 56% | 44% | 0% | +8.9 | +3.2 |
| wind: windy | 31 | 29% | 35% | 35% | 0% | 68% | 29% | 3% | +1.5 | -4.1 |
| precip: none | 111 | 32% | 32% | 32% | 4% | 59% | 38% | 3% | +6.0 | +0.4 |
| precip: light | 13 | 23% | 31% | 46% | 0% | 38% | 62% | 0% | +6.2 | +0.5 |
| precip: steady | 9 (thin) | 56% | 22% | 22% | 0% | 89% | 11% | 0% | +0.5 | -5.2 |
| precip: wet | 22 | 36% | 27% | 36% | 0% | 59% | 41% | 0% | +3.9 | -1.8 |
| temp: cold | 21 | 0% | 24% | 67% | 10% | 43% | 57% | 0% | +10.1 | +4.5 |
| temp: mild | 71 | 21% | 34% | 42% | 3% | 56% | 39% | 4% | +6.4 | +0.7 |
| temp: warm | 35 | 66% | 34% | 0% | 0% | 74% | 26% | 0% | +2.8 | -2.9 |
| temp: hot | 6 (thin) | 100% | 0% | 0% | 0% | 67% | 33% | 0% | -1.8 | -7.4 |
| temp: warm_hot | 41 | 71% | 29% | 0% | 0% | 73% | 27% | 0% | +2.1 | -3.5 |

### Ohio State: Pass yds/att (higher = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 61 | 55 | 61 | +0.55 [+0.17, +0.92] **\*** | +0.60 [+0.23, +0.96] **\*** |
| wind: moderate | 41 | 41 | 39 | +0.05 [-0.45, +0.53] | +0.07 [-0.40, +0.57] |
| wind: windy | 31 | 31 | 31 | -1.15 [-1.87, -0.39] **\*** | -1.27 [-1.98, -0.53] **\*** |
| precip: none | 111 | 106 | 109 | +0.05 [-0.13, +0.23] | +0.07 [-0.10, +0.25] |
| precip: light | 13 | 12 | 13 | +0.15 [-0.98, +1.26] | +0.16 [-0.97, +1.26] |
| precip: steady | 9 (thin) | 9 | 9 | -0.81 [-2.69, +0.97] | -1.08 [-2.79, +0.54] |
| precip: wet | 22 | 21 | 22 | -0.24 [-1.17, +0.66] | -0.35 [-1.22, +0.52] |
| temp: cold | 21 | 19 | 21 | -0.60 [-1.32, +0.10] | -0.26 [-0.96, +0.41] |
| temp: mild | 71 | 67 | 70 | -0.22 [-0.54, +0.11] | -0.20 [-0.52, +0.11] |
| temp: warm | 35 | 35 | 34 | +0.85 [+0.29, +1.39] **\*** | +0.69 [+0.15, +1.21] **\*** |
| temp: hot | 6 (thin) | 6 | 6 | -0.30 [-1.60, +0.96] | -0.65 [-1.87, +0.56] |
| temp: warm_hot | 41 | 41 | 40 | +0.68 [+0.18, +1.16] **\*** | +0.49 [+0.01, +0.95] **\*** |

### Ohio State: Rush yds/carry (higher = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 61 | 55 | 61 | +0.26 [+0.01, +0.52] **\*** | +0.27 [+0.04, +0.51] **\*** |
| wind: moderate | 41 | 41 | 39 | -0.18 [-0.50, +0.18] | -0.09 [-0.40, +0.24] |
| wind: windy | 31 | 31 | 31 | -0.28 [-0.70, +0.11] | -0.43 [-0.80, -0.08] **\*** |
| precip: none | 111 | 106 | 109 | +0.03 [-0.06, +0.12] | +0.05 [-0.03, +0.13] |
| precip: light | 13 | 12 | 13 | -0.02 [-0.70, +0.68] | -0.05 [-0.65, +0.59] |
| precip: steady | 9 (thin) | 9 | 9 | -0.30 [-0.95, +0.39] | -0.58 [-1.13, -0.04] **\*** |
| precip: wet | 22 | 21 | 22 | -0.14 [-0.59, +0.34] | -0.27 [-0.67, +0.16] |
| temp: cold | 21 | 19 | 21 | +0.00 [-0.58, +0.57] | +0.28 [-0.26, +0.83] |
| temp: mild | 71 | 67 | 70 | -0.11 [-0.33, +0.10] | -0.10 [-0.30, +0.10] |
| temp: warm | 35 | 35 | 34 | +0.12 [-0.26, +0.51] | -0.01 [-0.37, +0.35] |
| temp: hot | 6 (thin) | 6 | 6 | +0.55 [-0.95, +2.11] | +0.18 [-1.27, +1.79] |
| temp: warm_hot | 41 | 41 | 40 | +0.19 [-0.18, +0.54] | +0.02 [-0.32, +0.35] |

### Ohio State: Points scored (higher = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 61 | 55 | 61 | +1.3 [-1.0, +3.7] | +1.5 [-0.5, +3.4] |
| wind: moderate | 41 | 41 | 39 | +0.2 [-3.1, +3.6] | +1.3 [-1.7, +4.2] |
| wind: windy | 31 | 31 | 31 | -2.8 [-7.0, +1.8] | -4.5 [-8.3, -0.7] **\*** |
| precip: none | 111 | 106 | 109 | -0.2 [-1.2, +0.9] | +0.1 [-0.7, +1.0] |
| precip: light | 13 | 12 | 13 | -2.1 [-7.5, +3.5] | -2.4 [-6.8, +1.9] |
| precip: steady | 9 (thin) | 9 | 9 | +5.1 [-7.3, +17.2] | +1.7 [-7.5, +10.5] |
| precip: wet | 22 | 21 | 22 | +0.8 [-4.5, +6.2] | -0.7 [-4.8, +3.3] |
| temp: cold | 21 | 19 | 21 | -2.2 [-7.5, +2.9] | +1.2 [-3.4, +5.7] |
| temp: mild | 71 | 67 | 70 | -1.6 [-3.7, +0.4] | -1.5 [-3.3, +0.2] |
| temp: warm | 35 | 35 | 34 | +4.8 [+1.0, +8.6] **\*** | +3.2 [-0.2, +6.6] |
| temp: hot | 6 (thin) | 6 | 6 | -0.6 [-11.0, +8.5] | -4.9 [-12.0, +0.9] |
| temp: warm_hot | 41 | 41 | 40 | +4.0 [+0.7, +7.4] **\*** | +2.0 [-0.9, +4.9] |

### Ohio State: Points allowed (defense) (LOWER = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 61 | 55 | 61 | -0.9 [-2.8, +1.0] | -1.1 [-2.6, +0.5] |
| wind: moderate | 41 | 41 | 39 | +2.1 [-0.6, +4.7] | +1.2 [-1.1, +3.5] |
| wind: windy | 31 | 31 | 31 | -0.9 [-3.7, +1.9] | +0.6 [-1.5, +2.8] |
| precip: none | 111 | 106 | 109 | +0.0 [-0.7, +0.8] | +0.1 [-0.5, +0.7] |
| precip: light | 13 | 12 | 13 | +2.1 [-3.2, +7.7] | +1.1 [-2.9, +5.1] |
| precip: steady | 9 (thin) | 9 | 9 | -3.2 [-8.2, +2.3] | -2.4 [-8.4, +3.2] |
| precip: wet | 22 | 21 | 22 | -0.1 [-3.8, +3.8] | -0.3 [-3.5, +2.7] |
| temp: cold | 21 | 19 | 21 | +3.1 [-0.9, +7.5] | +2.3 [-0.7, +5.6] |
| temp: mild | 71 | 67 | 70 | +0.7 [-1.0, +2.3] | +0.4 [-0.9, +1.7] |
| temp: warm | 35 | 35 | 34 | -3.0 [-5.4, -0.6] **\*** | -2.4 [-4.6, -0.2] **\*** |
| temp: hot | 6 (thin) | 6 | 6 | -1.4 [-7.2, +4.3] | +0.9 [-2.3, +4.0] |
| temp: warm_hot | 41 | 41 | 40 | -2.8 [-5.0, -0.6] **\*** | -1.9 [-3.9, -0.0] **\*** |

### Ohio State: Turnovers (LOWER = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 61 | 55 | 61 | -0.06 [-0.21, +0.10] | -0.06 [-0.22, +0.09] |
| wind: moderate | 41 | 41 | 39 | +0.09 [-0.12, +0.30] | +0.11 [-0.11, +0.33] |
| wind: windy | 31 | 31 | 31 | -0.01 [-0.29, +0.28] | -0.01 [-0.29, +0.27] |
| precip: none | 111 | 106 | 109 | -0.03 [-0.11, +0.04] | -0.03 [-0.11, +0.04] |
| precip: light | 13 | 12 | 13 | -0.01 [-0.48, +0.49] | -0.02 [-0.49, +0.48] |
| precip: steady | 9 (thin) | 9 | 9 | +0.44 [-0.29, +1.29] | +0.43 [-0.29, +1.28] |
| precip: wet | 22 | 21 | 22 | +0.17 [-0.22, +0.57] | +0.17 [-0.22, +0.56] |
| temp: cold | 21 | 19 | 21 | +0.04 [-0.24, +0.34] | +0.03 [-0.26, +0.33] |
| temp: mild | 71 | 67 | 70 | -0.01 [-0.15, +0.12] | -0.02 [-0.16, +0.11] |
| temp: warm | 35 | 35 | 34 | -0.06 [-0.31, +0.19] | -0.04 [-0.30, +0.20] |
| temp: hot | 6 (thin) | 6 | 6 | +0.33 [-0.31, +1.02] | +0.32 [-0.32, +1.01] |
| temp: warm_hot | 41 | 41 | 40 | -0.01 [-0.22, +0.21] | +0.01 [-0.20, +0.23] |

### Ohio State: Offensive PPA/play (higher = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 61 | 55 | 61 | +0.053 [+0.022, +0.084] **\*** | +0.057 [+0.029, +0.086] **\*** |
| wind: moderate | 41 | 41 | 39 | -0.028 [-0.067, +0.015] | -0.025 [-0.062, +0.014] |
| wind: windy | 31 | 31 | 31 | -0.067 [-0.128, -0.007] **\*** | -0.081 [-0.138, -0.026] **\*** |
| precip: none | 111 | 106 | 109 | +0.011 [-0.002, +0.026] | +0.014 [+0.001, +0.029] **\*** |
| precip: light | 13 | 12 | 13 | -0.042 [-0.124, +0.045] | -0.042 [-0.119, +0.036] |
| precip: steady | 9 (thin) | 9 | 9 | -0.081 [-0.244, +0.067] | -0.113 [-0.264, +0.021] |
| precip: wet | 22 | 21 | 22 | -0.058 [-0.134, +0.013] | -0.071 [-0.142, -0.005] **\*** |
| temp: cold | 21 | 19 | 21 | -0.020 [-0.087, +0.046] | +0.018 [-0.043, +0.080] |
| temp: mild | 71 | 67 | 70 | -0.036 [-0.063, -0.011] **\*** | -0.034 [-0.058, -0.010] **\*** |
| temp: warm | 35 | 35 | 34 | +0.082 [+0.039, +0.126] **\*** | +0.063 [+0.023, +0.102] **\*** |
| temp: hot | 6 (thin) | 6 | 6 | +0.021 [-0.084, +0.128] | -0.020 [-0.113, +0.085] |
| temp: warm_hot | 41 | 41 | 40 | +0.073 [+0.034, +0.112] **\*** | +0.050 [+0.015, +0.086] **\*** |

## USC

145 completed games ingested · 131 outdoor with usable weather · 7 dome (excluded) · 0 missing weather · 7 too few observations · 0 usable games use a station >25 mi away · 6 games in COVID season(s)

### USC: what is each bin made of?

Share of the bin's games by kickoff month (approx. local), site, and average opponent SP+ rating (*vs all games* = difference from this team's overall average opponent; positive = tougher opponents than usual).

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 131 | 36% | 30% | 28% | 6% | 56% | 40% | 4% | +5.8 | +0.0 |
| wind: calm | 88 | 33% | 28% | 30% | 9% | 58% | 36% | 6% | +5.2 | -0.5 |
| wind: moderate | 34 | 44% | 32% | 24% | 0% | 59% | 41% | 0% | +6.4 | +0.7 |
| wind: windy | 9 (thin) | 33% | 33% | 33% | 0% | 33% | 67% | 0% | +8.5 | +2.7 |
| precip: none | 124 | 35% | 31% | 27% | 6% | 58% | 38% | 4% | +5.5 | -0.3 |
| precip: light | 2 (suppressed) | 0% | 50% | 50% | 0% | 0% | 100% | 0% | +13.8 | +8.0 |
| precip: steady | 5 (thin) | 60% | 0% | 40% | 0% | 40% | 60% | 0% | +9.4 | +3.6 |
| precip: wet | 7 (thin) | 43% | 14% | 43% | 0% | 29% | 71% | 0% | +10.6 | +4.9 |
| temp: cold | 4 (suppressed) | 0% | 50% | 50% | 0% | 0% | 100% | 0% | +14.5 | +8.7 |
| temp: mild | 74 | 18% | 31% | 41% | 11% | 51% | 42% | 7% | +7.6 | +1.9 |
| temp: warm | 43 | 63% | 26% | 12% | 0% | 72% | 28% | 0% | +3.3 | -2.4 |
| temp: hot | 9 (thin) | 67% | 33% | 0% | 0% | 56% | 44% | 0% | -2.7 | -8.5 |
| temp: warm_hot | 52 | 63% | 27% | 10% | 0% | 69% | 31% | 0% | +2.3 | -3.5 |

### USC: Pass yds/att (higher = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 88 | 85 | 88 | +0.09 [-0.12, +0.30] | +0.04 [-0.14, +0.22] |
| wind: moderate | 34 | 33 | 34 | +0.16 [-0.33, +0.67] | +0.18 [-0.27, +0.62] |
| wind: windy | 9 (thin) | 8 | 9 | -1.48 [-2.22, -0.72] **\*** | -1.04 [-1.79, -0.38] **\*** |
| precip: none | 124 | 119 | 124 | +0.01 [-0.03, +0.07] | -0.01 [-0.05, +0.04] |
| precip: light | 2 (suppressed) | 2 | 2 | — | — |
| precip: steady | 5 (thin) | 5 | 5 | +0.27 [-0.72, +1.32] | +0.51 [-0.39, +1.34] |
| precip: wet | 7 (thin) | 7 | 7 | -0.23 [-1.16, +0.69] | +0.14 [-0.77, +0.98] |
| temp: cold | 4 (suppressed) | 3 | 4 | — | — |
| temp: mild | 74 | 71 | 74 | -0.39 [-0.66, -0.12] **\*** | -0.27 [-0.51, -0.03] **\*** |
| temp: warm | 43 | 42 | 43 | +0.60 [+0.14, +1.05] **\*** | +0.42 [+0.00, +0.84] **\*** |
| temp: hot | 9 (thin) | 9 | 9 | +0.89 [+0.06, +1.67] **\*** | +0.48 [-0.29, +1.21] |
| temp: warm_hot | 52 | 51 | 52 | +0.65 [+0.26, +1.03] **\*** | +0.43 [+0.10, +0.78] **\*** |

### USC: Rush yds/carry (higher = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 88 | 85 | 88 | -0.07 [-0.24, +0.10] | -0.12 [-0.29, +0.04] |
| wind: moderate | 34 | 33 | 34 | +0.09 [-0.32, +0.52] | +0.10 [-0.28, +0.49] |
| wind: windy | 9 (thin) | 8 | 9 | +0.37 [-0.27, +0.98] | +0.80 [-0.04, +1.61] |
| precip: none | 124 | 119 | 124 | +0.02 [-0.04, +0.08] | -0.00 [-0.06, +0.05] |
| precip: light | 2 (suppressed) | 2 | 2 | — | — |
| precip: steady | 5 (thin) | 5 | 5 | -0.27 [-1.58, +1.03] | -0.03 [-1.42, +1.24] |
| precip: wet | 7 (thin) | 7 | 7 | -0.36 [-1.44, +0.72] | +0.00 [-1.04, +1.04] |
| temp: cold | 4 (suppressed) | 3 | 4 | — | — |
| temp: mild | 74 | 71 | 74 | -0.29 [-0.53, -0.05] **\*** | -0.17 [-0.39, +0.05] |
| temp: warm | 43 | 42 | 43 | +0.43 [+0.01, +0.86] **\*** | +0.27 [-0.11, +0.63] |
| temp: hot | 9 (thin) | 9 | 9 | +0.64 [-0.43, +1.69] | +0.24 [-0.64, +1.15] |
| temp: warm_hot | 52 | 51 | 52 | +0.47 [+0.12, +0.82] **\*** | +0.26 [-0.06, +0.57] |

### USC: Points scored (higher = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 88 | 85 | 88 | +0.8 [-0.6, +2.1] | +0.3 [-0.7, +1.3] |
| wind: moderate | 34 | 33 | 34 | +0.3 [-2.9, +3.8] | +0.4 [-2.0, +3.0] |
| wind: windy | 9 (thin) | 8 | 9 | -8.5 [-14.3, -3.5] **\*** | -4.3 [-10.3, +0.3] |
| precip: none | 124 | 119 | 124 | +0.1 [-0.2, +0.5] | -0.1 [-0.3, +0.2] |
| precip: light | 2 (suppressed) | 2 | 2 | — | — |
| precip: steady | 5 (thin) | 5 | 5 | +1.1 [-6.2, +8.4] | +3.4 [-3.3, +9.9] |
| precip: wet | 7 (thin) | 7 | 7 | -2.5 [-8.6, +3.6] | +1.0 [-4.2, +6.1] |
| temp: cold | 4 (suppressed) | 3 | 4 | — | — |
| temp: mild | 74 | 71 | 74 | -2.5 [-4.2, -0.8] **\*** | -1.3 [-2.6, -0.1] **\*** |
| temp: warm | 43 | 42 | 43 | +4.1 [+1.3, +6.9] **\*** | +2.5 [+0.3, +4.7] **\*** |
| temp: hot | 9 (thin) | 9 | 9 | +8.6 [+2.7, +14.9] **\*** | +4.8 [+0.2, +9.3] **\*** |
| temp: warm_hot | 52 | 51 | 52 | +4.9 [+2.5, +7.2] **\*** | +2.9 [+1.1, +4.7] **\*** |

### USC: Points allowed (defense) (LOWER = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 88 | 85 | 88 | -0.5 [-1.8, +0.6] | -0.5 [-1.5, +0.6] |
| wind: moderate | 34 | 33 | 34 | +1.8 [-1.4, +4.8] | +1.3 [-1.4, +4.0] |
| wind: windy | 9 (thin) | 8 | 9 | -1.5 [-4.6, +1.8] | -0.2 [-3.8, +3.2] |
| precip: none | 124 | 119 | 124 | +0.1 [-0.1, +0.4] | +0.2 [-0.0, +0.4] |
| precip: light | 2 (suppressed) | 2 | 2 | — | — |
| precip: steady | 5 (thin) | 5 | 5 | -4.6 [-10.4, +0.9] | -4.9 [-9.5, -0.1] **\*** |
| precip: wet | 7 (thin) | 7 | 7 | -2.3 [-7.1, +2.5] | -3.1 [-6.9, +0.7] |
| temp: cold | 4 (suppressed) | 3 | 4 | — | — |
| temp: mild | 74 | 71 | 74 | +2.9 [+1.5, +4.5] **\*** | +2.4 [+1.1, +3.8] **\*** |
| temp: warm | 43 | 42 | 43 | -3.7 [-6.2, -1.4] **\*** | -3.1 [-5.2, -1.0] **\*** |
| temp: hot | 9 (thin) | 9 | 9 | -5.2 [-9.9, -0.4] **\*** | -1.8 [-7.5, +4.0] |
| temp: warm_hot | 52 | 51 | 52 | -4.0 [-6.1, -2.0] **\*** | -2.8 [-4.7, -1.0] **\*** |

### USC: Turnovers (LOWER = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 88 | 85 | 88 | -0.10 [-0.23, +0.02] | -0.08 [-0.19, +0.04] |
| wind: moderate | 34 | 33 | 34 | +0.13 [-0.17, +0.43] | +0.13 [-0.15, +0.40] |
| wind: windy | 9 (thin) | 8 | 9 | +0.49 [-0.19, +1.25] | +0.29 [-0.37, +0.99] |
| precip: none | 124 | 119 | 124 | -0.03 [-0.08, +0.02] | -0.02 [-0.06, +0.03] |
| precip: light | 2 (suppressed) | 2 | 2 | — | — |
| precip: steady | 5 (thin) | 5 | 5 | +0.00 [-1.14, +1.08] | -0.11 [-1.30, +1.01] |
| precip: wet | 7 (thin) | 7 | 7 | +0.46 [-0.48, +1.32] | +0.29 [-0.66, +1.14] |
| temp: cold | 4 (suppressed) | 3 | 4 | — | — |
| temp: mild | 74 | 71 | 74 | +0.04 [-0.11, +0.18] | -0.02 [-0.16, +0.11] |
| temp: warm | 43 | 42 | 43 | -0.12 [-0.34, +0.12] | -0.04 [-0.25, +0.18] |
| temp: hot | 9 (thin) | 9 | 9 | -0.06 [-0.60, +0.46] | +0.12 [-0.39, +0.69] |
| temp: warm_hot | 52 | 51 | 52 | -0.11 [-0.30, +0.09] | -0.01 [-0.19, +0.17] |

### USC: Offensive PPA/play (higher = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 88 | 85 | 88 | +0.015 [-0.006, +0.035] | +0.008 [-0.009, +0.026] |
| wind: moderate | 34 | 33 | 34 | -0.015 [-0.068, +0.039] | -0.013 [-0.055, +0.029] |
| wind: windy | 9 (thin) | 8 | 9 | -0.084 [-0.183, +0.010] | -0.027 [-0.147, +0.092] |
| precip: none | 124 | 119 | 124 | +0.005 [+0.000, +0.012] **\*** | +0.003 [-0.001, +0.007] |
| precip: light | 2 (suppressed) | 2 | 2 | — | — |
| precip: steady | 5 (thin) | 5 | 5 | -0.025 [-0.097, +0.056] | +0.006 [-0.047, +0.056] |
| precip: wet | 7 (thin) | 7 | 7 | -0.094 [-0.189, -0.004] **\*** | -0.046 [-0.114, +0.021] |
| temp: cold | 4 (suppressed) | 3 | 4 | — | — |
| temp: mild | 74 | 71 | 74 | -0.025 [-0.052, +0.002] | -0.009 [-0.031, +0.013] |
| temp: warm | 43 | 42 | 43 | +0.038 [-0.009, +0.084] | +0.016 [-0.022, +0.054] |
| temp: hot | 9 (thin) | 9 | 9 | +0.110 [+0.043, +0.183] **\*** | +0.057 [-0.016, +0.120] |
| temp: warm_hot | 52 | 51 | 52 | +0.051 [+0.012, +0.088] **\*** | +0.023 [-0.009, +0.055] |

## Oregon

149 completed games ingested · 132 outdoor with usable weather · 10 dome (excluded) · 1 missing weather · 6 too few observations · 0 usable games use a station >25 mi away · 7 games in COVID season(s)

### Oregon: what is each bin made of?

Share of the bin's games by kickoff month (approx. local), site, and average opponent SP+ rating (*vs all games* = difference from this team's overall average opponent; positive = tougher opponents than usual).

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 132 | 34% | 28% | 31% | 7% | 56% | 39% | 5% | +5.3 | +0.0 |
| wind: calm | 78 | 26% | 29% | 37% | 8% | 56% | 40% | 4% | +6.9 | +1.6 |
| wind: moderate | 33 | 55% | 30% | 15% | 0% | 67% | 33% | 0% | +2.8 | -2.5 |
| wind: windy | 21 | 33% | 19% | 33% | 14% | 38% | 48% | 14% | +3.3 | -2.0 |
| precip: none | 118 | 36% | 27% | 29% | 8% | 57% | 38% | 5% | +5.3 | +0.1 |
| precip: light | 9 (thin) | 22% | 44% | 33% | 0% | 56% | 44% | 0% | +5.4 | +0.1 |
| precip: steady | 5 (thin) | 0% | 20% | 80% | 0% | 40% | 60% | 0% | +3.7 | -1.6 |
| precip: wet | 14 | 14% | 36% | 50% | 0% | 50% | 50% | 0% | +4.7 | -0.5 |
| temp: cold | 7 (thin) | 0% | 0% | 100% | 0% | 71% | 29% | 0% | +5.9 | +0.6 |
| temp: mild | 93 | 19% | 35% | 35% | 10% | 54% | 40% | 6% | +6.1 | +0.8 |
| temp: warm | 29 | 83% | 14% | 3% | 0% | 62% | 38% | 0% | +1.5 | -3.8 |
| temp: hot | 3 (suppressed) | 100% | 0% | 0% | 0% | 33% | 67% | 0% | +9.2 | +4.0 |
| temp: warm_hot | 32 | 84% | 12% | 3% | 0% | 59% | 41% | 0% | +2.1 | -3.2 |

### Oregon: Pass yds/att (higher = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 78 | 74 | 71 | -0.03 [-0.30, +0.22] | -0.08 [-0.35, +0.18] |
| wind: moderate | 33 | 32 | 30 | +0.42 [-0.15, +1.01] | +0.53 [-0.05, +1.13] |
| wind: windy | 21 | 21 | 20 | -0.54 [-1.20, +0.12] | -0.50 [-1.13, +0.07] |
| precip: none | 118 | 113 | 108 | +0.10 [+0.00, +0.22] **\*** | +0.11 [+0.00, +0.23] **\*** |
| precip: light | 9 (thin) | 9 | 8 | -0.23 [-1.28, +0.78] | -0.32 [-1.47, +0.89] |
| precip: steady | 5 (thin) | 5 | 5 | -2.05 [-3.48, -0.49] **\*** | -1.90 [-3.24, -0.53] **\*** |
| precip: wet | 14 | 14 | 13 | -0.88 [-1.74, -0.03] **\*** | -0.92 [-1.80, -0.04] **\*** |
| temp: cold | 7 (thin) | 5 | 7 | +0.33 [-0.73, +1.40] | +0.25 [-0.86, +1.22] |
| temp: mild | 93 | 90 | 89 | -0.32 [-0.53, -0.13] **\*** | -0.24 [-0.44, -0.06] **\*** |
| temp: warm | 29 | 29 | 23 | +1.07 [+0.52, +1.61] **\*** | +0.93 [+0.27, +1.57] **\*** |
| temp: hot | 3 (suppressed) | 3 | 2 | — | — |
| temp: warm_hot | 32 | 32 | 25 | +0.87 [+0.34, +1.39] **\*** | +0.78 [+0.17, +1.39] **\*** |

### Oregon: Rush yds/carry (higher = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 78 | 74 | 71 | -0.08 [-0.29, +0.13] | -0.13 [-0.33, +0.06] |
| wind: moderate | 33 | 32 | 30 | +0.27 [-0.13, +0.71] | +0.39 [+0.00, +0.79] **\*** |
| wind: windy | 21 | 21 | 20 | -0.15 [-0.76, +0.49] | -0.12 [-0.70, +0.48] |
| precip: none | 118 | 113 | 108 | -0.03 [-0.11, +0.05] | -0.05 [-0.13, +0.03] |
| precip: light | 9 (thin) | 9 | 8 | -0.21 [-1.00, +0.62] | -0.16 [-0.86, +0.57] |
| precip: steady | 5 (thin) | 5 | 5 | +1.06 [-0.09, +2.19] | +1.23 [-0.10, +2.57] |
| precip: wet | 14 | 14 | 13 | +0.24 [-0.42, +0.92] | +0.38 [-0.28, +1.09] |
| temp: cold | 7 (thin) | 5 | 7 | +0.25 [-0.93, +1.37] | +0.19 [-0.68, +1.07] |
| temp: mild | 93 | 90 | 89 | -0.12 [-0.30, +0.05] | -0.03 [-0.18, +0.12] |
| temp: warm | 29 | 29 | 23 | +0.54 [+0.07, +1.03] **\*** | +0.20 [-0.34, +0.71] |
| temp: hot | 3 (suppressed) | 3 | 2 | — | — |
| temp: warm_hot | 32 | 32 | 25 | +0.30 [-0.16, +0.76] | +0.05 [-0.46, +0.53] |

### Oregon: Points scored (higher = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 78 | 74 | 71 | +0.3 [-1.6, +2.1] | -0.7 [-2.1, +0.7] |
| wind: moderate | 33 | 32 | 30 | +1.2 [-2.4, +5.0] | +2.8 [-0.2, +6.0] |
| wind: windy | 21 | 21 | 20 | -2.9 [-7.7, +1.8] | -1.8 [-5.2, +1.4] |
| precip: none | 118 | 113 | 108 | +0.1 [-0.5, +0.7] | +0.1 [-0.5, +0.5] |
| precip: light | 9 (thin) | 9 | 8 | +0.4 [-5.4, +5.9] | +0.1 [-3.3, +3.5] |
| precip: steady | 5 (thin) | 5 | 5 | -4.0 [-15.5, +10.4] | -1.4 [-10.7, +10.8] |
| precip: wet | 14 | 14 | 13 | -1.2 [-6.4, +4.6] | -0.5 [-4.3, +4.0] |
| temp: cold | 7 (thin) | 5 | 7 | -1.7 [-9.0, +5.7] | -1.3 [-7.6, +5.2] |
| temp: mild | 93 | 90 | 89 | -2.1 [-3.7, -0.6] **\*** | -0.7 [-1.7, +0.4] |
| temp: warm | 29 | 29 | 23 | +7.7 [+3.1, +12.4] **\*** | +3.0 [-1.0, +6.7] |
| temp: hot | 3 (suppressed) | 3 | 2 | — | — |
| temp: warm_hot | 32 | 32 | 25 | +6.4 [+2.2, +10.6] **\*** | +2.8 [-1.0, +6.3] |

### Oregon: Points allowed (defense) (LOWER = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 78 | 74 | 71 | +2.0 [+0.4, +3.6] **\*** | +1.0 [-0.5, +2.4] |
| wind: moderate | 33 | 32 | 30 | -1.6 [-5.1, +2.1] | +0.8 [-2.3, +4.1] |
| wind: windy | 21 | 21 | 20 | -5.0 [-8.8, -0.9] **\*** | -4.6 [-8.4, -0.7] **\*** |
| precip: none | 118 | 113 | 108 | +0.1 [-0.5, +0.7] | +0.1 [-0.4, +0.5] |
| precip: light | 9 (thin) | 9 | 8 | -2.4 [-8.1, +3.7] | -2.6 [-6.1, +1.2] |
| precip: steady | 5 (thin) | 5 | 5 | +2.0 [-7.1, +11.6] | +2.4 [-5.9, +11.2] |
| precip: wet | 14 | 14 | 13 | -0.8 [-5.5, +4.0] | -0.7 [-4.3, +3.4] |
| temp: cold | 7 (thin) | 5 | 7 | -2.2 [-9.4, +5.0] | -5.6 [-13.0, +2.2] |
| temp: mild | 93 | 90 | 89 | +0.7 [-0.4, +1.8] | +0.1 [-0.9, +1.0] |
| temp: warm | 29 | 29 | 23 | -2.1 [-5.4, +1.2] | +0.7 [-2.6, +3.9] |
| temp: hot | 3 (suppressed) | 3 | 2 | — | — |
| temp: warm_hot | 32 | 32 | 25 | -1.6 [-4.6, +1.4] | +1.3 [-1.9, +4.3] |

### Oregon: Turnovers (LOWER = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 78 | 74 | 71 | +0.06 [-0.07, +0.18] | +0.07 [-0.07, +0.21] |
| wind: moderate | 33 | 32 | 30 | -0.01 [-0.27, +0.27] | +0.03 [-0.23, +0.30] |
| wind: windy | 21 | 21 | 20 | -0.19 [-0.52, +0.15] | -0.30 [-0.65, +0.06] |
| precip: none | 118 | 113 | 108 | +0.05 [+0.00, +0.10] **\*** | +0.04 [-0.00, +0.10] |
| precip: light | 9 (thin) | 9 | 8 | -0.77 [-1.14, -0.35] **\*** | -0.75 [-1.17, -0.29] **\*** |
| precip: steady | 5 (thin) | 5 | 5 | +0.30 [-0.11, +0.75] | +0.24 [-0.23, +0.74] |
| precip: wet | 14 | 14 | 13 | -0.38 [-0.75, -0.00] **\*** | -0.37 [-0.76, +0.02] |
| temp: cold | 7 (thin) | 5 | 7 | +0.47 [-0.20, +1.20] | +0.45 [-0.23, +1.17] |
| temp: mild | 93 | 90 | 89 | +0.08 [-0.01, +0.18] | +0.07 [-0.03, +0.16] |
| temp: warm | 29 | 29 | 23 | -0.34 [-0.59, -0.08] **\*** | -0.35 [-0.62, -0.06] **\*** |
| temp: hot | 3 (suppressed) | 3 | 2 | — | — |
| temp: warm_hot | 32 | 32 | 25 | -0.35 [-0.58, -0.11] **\*** | -0.37 [-0.63, -0.10] **\*** |

### Oregon: Offensive PPA/play (higher = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 78 | 74 | 71 | -0.004 [-0.031, +0.023] | -0.013 [-0.038, +0.011] |
| wind: moderate | 33 | 32 | 30 | +0.032 [-0.027, +0.093] | +0.049 [-0.007, +0.104] |
| wind: windy | 21 | 21 | 20 | -0.037 [-0.096, +0.020] | -0.026 [-0.076, +0.021] |
| precip: none | 118 | 113 | 108 | +0.002 [-0.006, +0.010] | +0.001 [-0.007, +0.009] |
| precip: light | 9 (thin) | 9 | 8 | +0.016 [-0.084, +0.109] | +0.020 [-0.075, +0.113] |
| precip: steady | 5 (thin) | 5 | 5 | -0.074 [-0.148, +0.022] | -0.046 [-0.138, +0.043] |
| precip: wet | 14 | 14 | 13 | -0.016 [-0.085, +0.053] | -0.005 [-0.072, +0.060] |
| temp: cold | 7 (thin) | 5 | 7 | +0.032 [-0.098, +0.153] | +0.032 [-0.096, +0.166] |
| temp: mild | 93 | 90 | 89 | -0.038 [-0.060, -0.017] **\*** | -0.022 [-0.041, -0.004] **\*** |
| temp: warm | 29 | 29 | 23 | +0.129 [+0.073, +0.186] **\*** | +0.085 [+0.023, +0.144] **\*** |
| temp: hot | 3 (suppressed) | 3 | 2 | — | — |
| temp: warm_hot | 32 | 32 | 25 | +0.102 [+0.048, +0.158] **\*** | +0.069 [+0.009, +0.127] **\*** |

## Northwestern

143 completed games ingested · 136 outdoor with usable weather · 4 dome (excluded) · 1 missing weather · 2 too few observations · 0 usable games use a station >25 mi away · 9 games in COVID season(s)

### Northwestern: what is each bin made of?

Share of the bin's games by kickoff month (approx. local), site, and average opponent SP+ rating (*vs all games* = difference from this team's overall average opponent; positive = tougher opponents than usual).

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 136 | 30% | 32% | 33% | 4% | 49% | 39% | 12% | +6.3 | +0.0 |
| wind: calm | 56 | 39% | 36% | 21% | 4% | 48% | 45% | 7% | +4.5 | -1.8 |
| wind: moderate | 46 | 33% | 24% | 37% | 7% | 48% | 39% | 13% | +8.5 | +2.2 |
| wind: windy | 34 | 12% | 38% | 47% | 3% | 50% | 29% | 21% | +6.6 | +0.3 |
| precip: none | 121 | 32% | 32% | 32% | 3% | 48% | 39% | 13% | +5.9 | -0.4 |
| precip: light | 12 | 8% | 33% | 42% | 17% | 42% | 50% | 8% | +11.4 | +5.1 |
| precip: steady | 3 (suppressed) | 33% | 33% | 33% | 0% | 100% | 0% | 0% | +1.5 | -4.8 |
| precip: wet | 15 | 13% | 33% | 40% | 13% | 53% | 40% | 7% | +9.4 | +3.1 |
| temp: cold | 18 | 0% | 6% | 78% | 17% | 28% | 50% | 22% | +8.3 | +2.0 |
| temp: mild | 80 | 19% | 42% | 38% | 1% | 48% | 42% | 10% | +7.3 | +1.0 |
| temp: warm | 33 | 67% | 24% | 3% | 6% | 64% | 21% | 15% | +4.0 | -2.3 |
| temp: hot | 5 (thin) | 80% | 20% | 0% | 0% | 40% | 60% | 0% | -3.4 | -9.7 |
| temp: warm_hot | 38 | 68% | 24% | 3% | 5% | 61% | 26% | 13% | +2.9 | -3.4 |

### Northwestern: Pass yds/att (higher = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 56 | 54 | 55 | -0.00 [-0.36, +0.34] | -0.09 [-0.40, +0.22] |
| wind: moderate | 46 | 44 | 42 | +0.13 [-0.27, +0.53] | +0.22 [-0.16, +0.59] |
| wind: windy | 34 | 30 | 31 | -0.17 [-0.56, +0.26] | -0.14 [-0.55, +0.29] |
| precip: none | 121 | 115 | 113 | +0.02 [-0.08, +0.10] | -0.02 [-0.11, +0.07] |
| precip: light | 12 | 10 | 12 | +0.02 [-0.78, +1.00] | +0.25 [-0.54, +1.18] |
| precip: steady | 3 (suppressed) | 3 | 3 | — | — |
| precip: wet | 15 | 13 | 15 | -0.12 [-0.81, +0.65] | +0.12 [-0.54, +0.87] |
| temp: cold | 18 | 16 | 18 | -0.26 [-0.89, +0.43] | -0.10 [-0.69, +0.52] |
| temp: mild | 80 | 76 | 77 | -0.03 [-0.27, +0.21] | +0.00 [-0.21, +0.22] |
| temp: warm | 33 | 31 | 28 | +0.36 [-0.19, +0.94] | +0.30 [-0.24, +0.84] |
| temp: hot | 5 (thin) | 5 | 5 | -0.95 [-2.30, +0.54] | -1.31 [-2.37, -0.22] **\*** |
| temp: warm_hot | 38 | 36 | 33 | +0.19 [-0.30, +0.72] | +0.05 [-0.42, +0.53] |

### Northwestern: Rush yds/carry (higher = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 56 | 54 | 55 | -0.09 [-0.37, +0.21] | -0.20 [-0.43, +0.02] |
| wind: moderate | 46 | 44 | 42 | -0.18 [-0.51, +0.18] | -0.04 [-0.30, +0.24] |
| wind: windy | 34 | 30 | 31 | +0.38 [+0.03, +0.75] **\*** | +0.41 [+0.12, +0.69] **\*** |
| precip: none | 121 | 115 | 113 | +0.05 [-0.04, +0.13] | +0.01 [-0.07, +0.08] |
| precip: light | 12 | 10 | 12 | -0.42 [-1.24, +0.44] | -0.11 [-0.80, +0.59] |
| precip: steady | 3 (suppressed) | 3 | 3 | — | — |
| precip: wet | 15 | 13 | 15 | -0.38 [-1.07, +0.33] | -0.05 [-0.64, +0.52] |
| temp: cold | 18 | 16 | 18 | +0.28 [-0.23, +0.83] | +0.50 [+0.10, +0.90] **\*** |
| temp: mild | 80 | 76 | 77 | -0.09 [-0.28, +0.09] | +0.00 [-0.15, +0.15] |
| temp: warm | 33 | 31 | 28 | +0.06 [-0.33, +0.46] | -0.24 [-0.61, +0.12] |
| temp: hot | 5 (thin) | 5 | 5 | +0.02 [-1.51, +1.51] | -0.46 [-1.53, +0.56] |
| temp: warm_hot | 38 | 36 | 33 | +0.06 [-0.31, +0.44] | -0.28 [-0.61, +0.04] |

### Northwestern: Points scored (higher = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 56 | 54 | 55 | +0.3 [-1.9, +2.4] | -0.6 [-2.3, +1.1] |
| wind: moderate | 46 | 44 | 42 | -0.9 [-3.3, +1.5] | +0.1 [-1.9, +2.2] |
| wind: windy | 34 | 30 | 31 | +0.7 [-2.0, +3.7] | +0.8 [-1.7, +3.5] |
| precip: none | 121 | 115 | 113 | +0.0 [-0.6, +0.6] | -0.3 [-0.9, +0.3] |
| precip: light | 12 | 10 | 12 | +1.1 [-4.2, +6.7] | +3.0 [-1.8, +8.3] |
| precip: steady | 3 (suppressed) | 3 | 3 | — | — |
| precip: wet | 15 | 13 | 15 | -0.0 [-5.3, +5.4] | +2.0 [-2.7, +6.9] |
| temp: cold | 18 | 16 | 18 | +0.2 [-4.2, +4.6] | +1.6 [-1.7, +5.0] |
| temp: mild | 80 | 76 | 77 | +0.2 [-1.2, +1.6] | +0.6 [-0.6, +1.8] |
| temp: warm | 33 | 31 | 28 | +0.1 [-2.6, +2.9] | -1.2 [-3.7, +1.3] |
| temp: hot | 5 (thin) | 5 | 5 | -4.5 [-14.2, +7.3] | -8.0 [-16.5, +0.5] |
| temp: warm_hot | 38 | 36 | 33 | -0.5 [-3.1, +2.2] | -2.2 [-4.6, +0.0] |

### Northwestern: Points allowed (defense) (LOWER = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 56 | 54 | 55 | +0.2 [-1.9, +2.3] | +0.1 [-1.9, +2.0] |
| wind: moderate | 46 | 44 | 42 | +2.4 [-0.1, +4.9] | +3.5 [+1.2, +5.9] **\*** |
| wind: windy | 34 | 30 | 31 | -3.6 [-6.3, -0.8] **\*** | -4.9 [-7.5, -2.3] **\*** |
| precip: none | 121 | 115 | 113 | +0.2 [-0.4, +0.8] | +0.4 [-0.3, +1.0] |
| precip: light | 12 | 10 | 12 | +0.3 [-5.3, +6.7] | -1.9 [-6.8, +3.8] |
| precip: steady | 3 (suppressed) | 3 | 3 | — | — |
| precip: wet | 15 | 13 | 15 | -1.8 [-6.8, +3.5] | -2.9 [-7.3, +2.1] |
| temp: cold | 18 | 16 | 18 | -2.2 [-6.7, +2.4] | -3.2 [-7.7, +1.2] |
| temp: mild | 80 | 76 | 77 | +1.0 [-0.4, +2.4] | +0.8 [-0.6, +2.1] |
| temp: warm | 33 | 31 | 28 | -0.2 [-3.3, +2.8] | +0.9 [-2.2, +4.1] |
| temp: hot | 5 (thin) | 5 | 5 | -7.1 [-12.6, -1.2] **\*** | -5.3 [-10.2, -0.3] **\*** |
| temp: warm_hot | 38 | 36 | 33 | -1.1 [-3.9, +1.6] | -0.1 [-2.8, +2.7] |

### Northwestern: Turnovers (LOWER = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 56 | 54 | 55 | -0.03 [-0.24, +0.18] | -0.03 [-0.23, +0.18] |
| wind: moderate | 46 | 44 | 42 | +0.20 [-0.05, +0.45] | +0.22 [-0.04, +0.49] |
| wind: windy | 34 | 30 | 31 | -0.21 [-0.53, +0.12] | -0.24 [-0.57, +0.10] |
| precip: none | 121 | 115 | 113 | +0.03 [-0.03, +0.08] | +0.03 [-0.02, +0.09] |
| precip: light | 12 | 10 | 12 | -0.14 [-0.66, +0.41] | -0.19 [-0.71, +0.37] |
| precip: steady | 3 (suppressed) | 3 | 3 | — | — |
| precip: wet | 15 | 13 | 15 | -0.21 [-0.65, +0.24] | -0.25 [-0.69, +0.19] |
| temp: cold | 18 | 16 | 18 | +0.08 [-0.45, +0.61] | +0.04 [-0.48, +0.56] |
| temp: mild | 80 | 76 | 77 | -0.10 [-0.26, +0.06] | -0.11 [-0.26, +0.04] |
| temp: warm | 33 | 31 | 28 | +0.16 [-0.17, +0.48] | +0.22 [-0.15, +0.58] |
| temp: hot | 5 (thin) | 5 | 5 | +0.32 [-1.02, +1.91] | +0.32 [-1.01, +1.90] |
| temp: warm_hot | 38 | 36 | 33 | +0.18 [-0.13, +0.49] | +0.23 [-0.10, +0.57] |

### Northwestern: Offensive PPA/play (higher = better)

| Bin | n | n ex-2020 | n adj | Raw Δ [90%] | Adj Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | 56 | 54 | 55 | -0.001 [-0.039, +0.033] | -0.013 [-0.044, +0.016] |
| wind: moderate | 46 | 44 | 42 | -0.019 [-0.064, +0.026] | -0.004 [-0.040, +0.033] |
| wind: windy | 34 | 30 | 31 | +0.028 [-0.015, +0.073] | +0.028 [-0.012, +0.068] |
| precip: none | 121 | 115 | 113 | +0.002 [-0.007, +0.012] | -0.002 [-0.011, +0.006] |
| precip: light | 12 | 10 | 12 | -0.002 [-0.079, +0.078] | +0.033 [-0.033, +0.101] |
| precip: steady | 3 (suppressed) | 3 | 3 | — | — |
| precip: wet | 15 | 13 | 15 | -0.018 [-0.100, +0.059] | +0.018 [-0.049, +0.085] |
| temp: cold | 18 | 16 | 18 | -0.018 [-0.088, +0.059] | +0.008 [-0.044, +0.065] |
| temp: mild | 80 | 76 | 77 | +0.001 [-0.025, +0.024] | +0.012 [-0.010, +0.033] |
| temp: warm | 33 | 31 | 28 | +0.016 [-0.038, +0.071] | -0.019 [-0.071, +0.033] |
| temp: hot | 5 (thin) | 5 | 5 | -0.050 [-0.249, +0.173] | -0.101 [-0.250, +0.061] |
| temp: warm_hot | 38 | 36 | 33 | +0.007 [-0.043, +0.056] | -0.032 [-0.077, +0.016] |

## Snow games

Snow is no longer split into delta rows (too few games). These are the actual games where an observation in the kickoff-to-+3.5h window reported a snow weather code. A code can mean flurries, so read the precipitation and temperature columns.

| Date | Game | Venue | Observed in window | Score |
|---|---|---|---|---|
| 2016-11-19 | Ohio State @ Michigan State | Spartan Stadium | 34°F, wind 22 mph (gust 35), precip 0.00 in, vis 4.0 mi | Ohio State 17, Michigan State 16 |
| 2017-11-18 | Minnesota @ Northwestern | Ryan Field | 36°F, wind 16 mph (gust 25), precip 0.10 in, vis 2.0 mi | Minnesota 0, Northwestern 39 |
| 2021-11-27 | Ohio State @ Michigan | Michigan Stadium | 28°F, wind 10 mph, precip 0.01 in, vis 0.8 mi | Ohio State 27, Michigan 42 |
| 2022-11-12 | Indiana @ Ohio State | Ohio Stadium | 36°F, wind 10 mph, precip 0.03 in, vis 1.5 mi | Indiana 14, Ohio State 56 |
| 2022-11-12 | Northwestern @ Minnesota | Huntington Bank Stadium | 28°F, wind 14 mph (gust 24), precip 0.00 in, vis 9.0 mi | Northwestern 3, Minnesota 31 |
| 2025-11-29 | Ohio State @ Michigan | Michigan Stadium | 28°F, wind 13 mph, precip 0.01 in, vis 0.8 mi | Ohio State 27, Michigan 9 |
| 2025-11-29 | Northwestern @ Illinois | Memorial Stadium (Champaign, IL) | 33°F, wind 28 mph (gust 44), precip 0.06 in, vis 0.5 mi | Northwestern 13, Illinois 20 |

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
