# Milestone 3: scaled splits, controlled model, evidence tiers

_Generated 2026-10-28 01:08 UTC._

> **EXPLORATORY.** This report tests many team × bin × metric cells. At a 90% level roughly 1 in 10 intervals will exclude zero by luck alone, so a starred (\*) delta or a "leans" tier is a lead to check, not a finding.

> ⚠️ **PREVIEW.** Only 4 of the 13 tracked teams have data loaded (Northwestern, Ohio State, Oregon, USC). Missing: Ball State, Illinois, Indiana, Iowa, Kent State, Maryland, Michigan, Nebraska, Texas. The expansion is waiting on CFBD call budget.

## Plain-language summary

- **Wind (windy vs not)** -- pooled across 4 teams, controlled for opponent, month and home/away: Pass yds/att -0.69 yds/att [-1.02, -0.36] (interval excludes zero); Points scored -2.0 pts [-3.7, -0.1] (interval excludes zero); Offensive PPA/play -0.028 PPA [-0.057, +0.001] (interval spans zero). Clear evidence for: Ohio State. Leans: USC.
- **Wet (light + steady rain)** -- pooled across 4 teams, controlled for opponent, month and home/away: Pass yds/att -0.27 yds/att [-0.71, +0.19] (interval spans zero); Points scored +0.5 pts [-1.9, +3.0] (interval spans zero); Offensive PPA/play -0.032 PPA [-0.071, +0.006] (interval spans zero). No team clears the bar. Leans: Ohio State.
- **Warm/hot (70°F and up)** -- pooled across 4 teams, controlled for opponent, month and home/away: Pass yds/att +0.41 yds/att [+0.13, +0.69] (interval excludes zero); Points scored +1.4 pts [-0.1, +2.8] (interval spans zero); Offensive PPA/play +0.029 PPA [+0.005, +0.054] (interval excludes zero). No team clears the bar. Leans: Ohio State, Oregon.
- **Cold (39°F and below)** -- pooled across 4 teams, controlled for opponent, month and home/away: Pass yds/att +0.08 yds/att [-0.34, +0.51] (interval spans zero); Points scored +1.6 pts [-1.0, +4.3] (interval spans zero); Offensive PPA/play +0.029 PPA [-0.013, +0.068] (interval spans zero). No team clears the bar. 

Temperature: the controlled model finds no clear temperature effect for Northwestern, USC, so their temperature results are labelled context-only; it still shows one (kept as is) for Ohio State, Oregon.

_Exploratory: tiers and stars are leads to check, not findings._

## CFBD call budget

- This run: **2** CFBD calls.
- Month (2026-10) total so far: **439** of the 600-call cap (free-tier limit 1000). 561 calls remain before CFBD itself would stop us.
- 437 of those were spent before the call counter and raw cache existed (early un-cached runs).

Planned budget by endpoint (printed before spending):

| Endpoint | Calls | Basis |
|---|---|---|
| /games | 22 | exact |
| /games/teams | 147 | worst case |
| /ppa/games | 147 | worst case |
| /ratings/sp | 1 | exact |
| /venues | 1 | exact |
| /info | 1 | exact |
| **Total** | **319** | |

Calls logged by the counter this month, by endpoint: `/games` 1, `/info` 1

## 2026 Ohio State schedule

7 played, 5 remaining. Team list = Ohio State + every opponent below (13 teams, from `config/opponents.yaml`).

| Wk | Date | Opponent | Site | Venue | Status |
|---|---|---|---|---|---|
| 1 | Sep 05 | Ball State | home | Ohio Stadium | played: W 56-3 |
| 2 | Sep 12 | Texas | away | DKR-Texas Memorial Stadium | played: L 23-24 |
| 3 | Sep 19 | Kent State | home | Ohio Stadium | played: W 59-3 |
| 4 | Sep 26 | Illinois | home | Ohio Stadium | played: W 42-19 |
| 5 | Oct 03 | Iowa | away | Kinnick Stadium | played: W 31-14 |
| 6 | Oct 10 | Maryland | home | Ohio Stadium | played: W 45-16 |
| 7 | Oct 17 | Indiana | away | Memorial Stadium (Bloomington, IN) | played: W 19-15 |
| 9 | Oct 31 | USC | away | Los Angeles Memorial Coliseum | **remaining** |
| 10 | Nov 06 | Oregon | home | Ohio Stadium | **remaining** |
| 11 | Nov 13 | Northwestern | home | Ohio Stadium | **remaining** |
| 12 | Nov 20 | Nebraska | away | Memorial Stadium (Lincoln, NE) | **remaining** |
| 13 | Nov 28 | Michigan | home | Ohio Stadium | **remaining** |

## Evidence tiers (controlled model)

Computed in the pipeline from the **controlled** intervals (opponent strength + month + home/away held fixed). Metric groups: **passing** = pass yds/att + offensive PPA; **scoring** = points scored + offensive PPA.

- **CLEAR**: n ≥ 10 and the controlled interval excludes zero (same direction) on both metrics in the group.
- **leans**: both metrics point the same way and the effect is at least 1 standard error(s) in size, but not clear (an interval spans zero, or n is 5-9).
- **none** (no_clear_effect): n ≥ 10 and nothing there.   **n/a** (insufficient): n < 5, or n 5-9 with no lean.
- **context**: temperature results for a team whose controlled model finds no temperature effect in any bin -- kept for context, not as evidence.

### Passing

| Team | wind:<br>calm | wind:<br>moderate | wind:<br>windy | precip:<br>none | precip:<br>light | precip:<br>steady | precip:<br>wet | temp:<br>cold | temp:<br>mild | temp:<br>warm | temp:<br>hot | temp:<br>warm_hot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ohio State | **CLEAR** (61) | none (39) | **CLEAR** (31) | leans (109) | none (13) | leans (9) | leans (22) | none (21) | leans (70) | leans (34) | n/a (6) | leans (40) |
| USC | none (88) | none (34) | leans (9) | none (124) | n/a (2) | n/a (5) | n/a (7) | n/a (4) | context (74) | context (43) | n/a (9) | context (52) |
| Oregon | none (71) | leans (30) | none (20) | none (108) | n/a (8) | leans (5) | none (13) | n/a (7) | leans (89) | **CLEAR** (23) | n/a (2) | leans (25) |
| Northwestern | none (55) | none (42) | none (31) | none (113) | none (12) | n/a (3) | none (15) | context (18) | context (77) | context (28) | context (5) | context (33) |
| Pooled (4 teams) | leans (275) | none (145) | leans (91) | leans (454) | none (35) | **CLEAR** (22) | leans (57) | none (50) | **CLEAR** (310) | **CLEAR** (128) | none (22) | **CLEAR** (150) |

### Scoring

| Team | wind:<br>calm | wind:<br>moderate | wind:<br>windy | precip:<br>none | precip:<br>light | precip:<br>steady | precip:<br>wet | temp:<br>cold | temp:<br>mild | temp:<br>warm | temp:<br>hot | temp:<br>warm_hot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ohio State | leans (61) | none (39) | **CLEAR** (31) | none (109) | none (13) | n/a (9) | none (22) | none (21) | leans (70) | **CLEAR** (34) | n/a (6) | leans (40) |
| USC | none (88) | none (34) | n/a (9) | none (124) | n/a (2) | n/a (5) | n/a (7) | n/a (4) | context (74) | context (43) | context (9) | context (52) |
| Oregon | none (71) | none (30) | none (20) | none (108) | n/a (8) | n/a (5) | none (13) | n/a (7) | none (89) | leans (23) | n/a (2) | none (25) |
| Northwestern | none (55) | none (42) | none (31) | none (113) | none (12) | n/a (3) | none (15) | context (18) | context (77) | context (28) | context (5) | context (33) |
| Pooled (4 teams) | none (275) | none (145) | leans (91) | none (454) | none (35) | none (22) | none (57) | leans (50) | leans (310) | **CLEAR** (128) | none (22) | leans (150) |

**Temperature:** a team's temperature tiers are kept as they are only if its controlled model has at least one CLEAR temperature cell; otherwise they are labelled context-only. Kept: Ohio State, Oregon, Pooled (4 teams). Context-only: Northwestern, USC.

## Pooled reference line (all 4 loaded teams together)

Every team-game from the **4 teams** in the pool, each measured against its own team's baseline. Raw / Adjusted / Controlled as defined above; brackets are 90% intervals from a bootstrap over whole games.

**wind** (pooled across 4 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | Pass yds/att | 283 | +0.14 [-0.00, +0.29] | +0.11 [-0.03, +0.25] | +0.11 [-0.03, +0.26] |
| wind: calm | Points scored | 283 | +0.7 [-0.2, +1.6] | +0.1 [-0.6, +0.9] | +0.1 [-0.7, +0.9] |
| wind: calm | Points allowed (defense) | 283 | +0.2 [-0.6, +1.1] | -0.1 [-0.9, +0.6] | +0.0 [-0.7, +0.8] |
| wind: calm | Offensive PPA/play | 283 | +0.015 [+0.001, +0.029] \* | +0.009 [-0.003, +0.022] | +0.010 [-0.002, +0.024] |
| wind: moderate | Pass yds/att | 154 | +0.18 [-0.08, +0.41] | +0.23 [+0.00, +0.46] \* | +0.23 [-0.01, +0.46] |
| wind: moderate | Points scored | 154 | +0.1 [-1.5, +1.7] | +1.1 [-0.3, +2.4] | +1.0 [-0.4, +2.4] |
| wind: moderate | Points allowed (defense) | 154 | +1.3 [-0.1, +2.8] | +1.8 [+0.5, +3.2] \* | +1.9 [+0.5, +3.3] \* |
| wind: moderate | Offensive PPA/play | 154 | -0.009 [-0.033, +0.014] | -0.001 [-0.022, +0.020] | -0.002 [-0.025, +0.019] |
| wind: windy | Pass yds/att | 95 | -0.70 [-1.03, -0.35] \* | -0.69 [-1.02, -0.36] \* | -0.69 [-1.02, -0.36] \* |
| wind: windy | Points scored | 95 | -2.1 [-4.2, +0.1] | -2.1 [-3.9, -0.2] \* | -2.0 [-3.7, -0.1] \* |
| wind: windy | Points allowed (defense) | 95 | -2.8 [-4.5, -1.1] \* | -2.5 [-4.0, -1.0] \* | -3.0 [-4.6, -1.6] \* |
| wind: windy | Offensive PPA/play | 95 | -0.028 [-0.059, +0.003] | -0.027 [-0.056, +0.001] | -0.028 [-0.057, +0.001] |

**precip** (pooled across 4 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| precip: none | Pass yds/att | 474 | +0.04 [-0.01, +0.10] | +0.04 [-0.02, +0.10] | +0.03 [-0.02, +0.09] |
| precip: none | Points scored | 474 | +0.0 [-0.3, +0.4] | -0.0 [-0.3, +0.3] | -0.1 [-0.4, +0.2] |
| precip: none | Points allowed (defense) | 474 | +0.1 [-0.2, +0.4] | +0.2 [-0.1, +0.4] | +0.2 [-0.1, +0.5] |
| precip: none | Offensive PPA/play | 474 | +0.005 [+0.000, +0.011] \* | +0.004 [-0.001, +0.009] | +0.004 [-0.001, +0.009] |
| precip: wet | Pass yds/att | 58 | -0.36 [-0.83, +0.12] | -0.30 [-0.75, +0.17] | -0.27 [-0.71, +0.19] |
| precip: wet | Points scored | 58 | -0.3 [-3.2, +2.7] | +0.3 [-2.1, +2.7] | +0.5 [-1.9, +3.0] |
| precip: wet | Points allowed (defense) | 58 | -1.0 [-3.3, +1.4] | -1.4 [-3.4, +0.6] | -1.7 [-3.5, +0.5] |
| precip: wet | Offensive PPA/play | 58 | -0.042 [-0.082, -0.000] \* | -0.030 [-0.067, +0.009] | -0.032 [-0.071, +0.006] |

**temp** (pooled across 4 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| temp: cold | Pass yds/att | 50 | -0.35 [-0.78, +0.05] | -0.12 [-0.54, +0.27] | +0.08 [-0.34, +0.51] |
| temp: cold | Points scored | 50 | -1.8 [-4.9, +1.3] | +0.5 [-2.1, +3.1] | +1.6 [-1.0, +4.3] |
| temp: cold | Points allowed (defense) | 50 | +0.2 [-2.5, +2.9] | -1.3 [-3.8, +1.1] | -2.0 [-4.5, +0.6] |
| temp: cold | Offensive PPA/play | 50 | -0.019 [-0.062, +0.023] | +0.010 [-0.029, +0.048] | +0.029 [-0.013, +0.068] |
| temp: mild | Pass yds/att | 318 | -0.24 [-0.37, -0.12] \* | -0.18 [-0.30, -0.06] \* | -0.16 [-0.30, -0.04] \* |
| temp: mild | Points scored | 318 | -1.5 [-2.3, -0.7] \* | -0.7 [-1.4, -0.0] \* | -0.7 [-1.4, +0.0] |
| temp: mild | Points allowed (defense) | 318 | +1.3 [+0.6, +2.0] \* | +0.9 [+0.3, +1.5] \* | +0.9 [+0.2, +1.5] \* |
| temp: mild | Offensive PPA/play | 318 | -0.025 [-0.037, -0.013] \* | -0.013 [-0.024, -0.003] \* | -0.015 [-0.027, -0.004] \* |
| temp: warm_hot | Pass yds/att | 163 | +0.59 [+0.36, +0.83] \* | +0.42 [+0.19, +0.66] \* | +0.41 [+0.13, +0.69] \* |
| temp: warm_hot | Points scored | 163 | +3.7 [+2.2, +5.2] \* | +1.5 [+0.3, +2.8] \* | +1.4 [-0.1, +2.8] |
| temp: warm_hot | Points allowed (defense) | 163 | -2.5 [-3.8, -1.2] \* | -1.3 [-2.5, -0.2] \* | -1.3 [-2.6, +0.0] |
| temp: warm_hot | Offensive PPA/play | 163 | +0.056 [+0.034, +0.078] \* | +0.026 [+0.006, +0.047] \* | +0.029 [+0.005, +0.054] \* |

## How much do the controls change things?

Solid cells, per-team (not pooled), all seasons. *Sign flips* = adjusted and controlled point opposite ways. *Excl. 0* = intervals excluding zero (about 1 in 10 expected by luck).

| Metric | Cells | Avg \|raw\| | Avg \|adj\| | Avg \|ctl\| | Adj→Ctl sign flips | Raw excl. 0 | Adj excl. 0 | Ctl excl. 0 |
|---|---|---|---|---|---|---|---|---|
| Pass yds/att | 34 | 0.35 | 0.32 | 0.30 | 2 | 12 | 12 | 5 |
| Rush yds/carry | 34 | 0.19 | 0.17 | 0.14 | 5 | 6 | 5 | 2 |
| Points scored | 34 | 1.7 | 1.5 | 1.2 | 3 | 8 | 4 | 3 |
| Points allowed (defense) | 34 | 1.6 | 1.5 | 1.3 | 5 | 8 | 8 | 6 |
| Turnovers | 34 | 0.11 | 0.12 | 0.11 | 1 | 4 | 2 | 0 |
| Offensive PPA/play | 34 | 0.032 | 0.028 | 0.025 | 3 | 10 | 10 | 6 |

## Opponent ratings: which games have no SP+?

SP+ covers FBS teams only. A game against an FCS opponent has no rating, so it is left out of the **Adjusted** and **Controlled** columns (it still counts in **Raw**). It is never guessed. *Raw shift* = how much the average |raw Δ| of the team's solid cells moves when the raw numbers are recomputed on rated games only -- a direct read on whether dropping those games matters.

| Team | Usable games | No SP+ rating | Opponents without a rating | Raw shift |
|---|---|---|---|---|
| Northwestern | 136 | 8 | Eastern Illinois, Howard, Illinois State, Indiana State, South Dakota State, Southern Illinois … | 0.179 |
| Ohio State | 133 | 2 | Grambling, Youngstown State | 0.082 |
| Oregon | 132 | 11 | Eastern Washington, Idaho, Montana, Montana State, Portland State, Southern Utah … | 0.402 |
| USC | 131 | 0 | — | 0.000 |

## Venues: domes, far stations, neutral sites, non-US

59 venues in the table; 0 are NEW since 2026-10-28 (marked **NEW**). Far = nearest ASOS more than 25 mi away.

**Domes (excluded from weather splits):** Caesars Superdome; Alamodome; AT&T Stadium; Ford Field; Lucas Oil Stadium; State Farm Stadium; Mercedes-Benz Stadium; Allegiant Stadium

**Far stations (> 25 mi):** Lane Stadium (25.3 mi to ROA)

**Neutral-site venues:** Rose Bowl (5 game(s)); Caesars Superdome (1 game(s)); Aviva Stadium (1 game(s)); Alamodome (3 game(s)); AT&T Stadium (8 game(s)); Ford Field (1 game(s)); Nissan Stadium (1 game(s)); Lucas Oil Stadium (6 game(s)); Raymond James Stadium (1 game(s)); Sam Boyd Stadium (1 game(s)); Qualcomm Stadium (3 game(s)); Soldier Field (1 game(s)); Hard Rock Stadium (2 game(s)); State Farm Stadium (5 game(s)); Camping World Stadium (1 game(s)); Yankee Stadium (1 game(s)); Petco Park (2 game(s)); Wrigley Field (6 game(s)); Levi's Stadium (4 game(s)); Mercedes-Benz Stadium (4 game(s)); Lanny and Sharon Martin Stadium (5 game(s)); Allegiant Stadium (6 game(s))

**Non-US venues (no US station used; those games are excluded):** Aviva Stadium

## Per team

Month/home/opponent mix of each bin first (what the bin is secretly measuring), then the effects.

### Ohio State

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

Each cell: **Raw / Adjusted / Controlled** delta vs the team's own average (\* = 90% interval excludes zero). Intervals are in `milestone3_detail.md`.

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 61 | +0.55\* / +0.60\* / +0.54\* | +1.3 / +1.5 / +1.3 | -0.9 / -1.1 / -1.2 | +0.053\* / +0.057\* / +0.056\* |
| wind: moderate | 41 | +0.05 / +0.07 / +0.22 | +0.2 / +1.3 / +1.9 | +2.1 / +1.2 / +1.2 | -0.028 / -0.025 / -0.020 |
| wind: windy | 31 | -1.15\* / -1.27\* / -1.31\* | -2.8 / -4.5\* / -4.9\* | -0.9 / +0.6 / +0.7 | -0.067\* / -0.081\* / -0.085\* |
| precip: none | 111 | +0.05 / +0.07 / +0.06 | -0.2 / +0.1 / +0.1 | +0.0 / +0.1 / +0.0 | +0.011 / +0.014\* / +0.014 |
| precip: light | 13 | +0.15 / +0.16 / +0.35 | -2.1 / -2.4 / -1.3 | +2.1 / +1.1 / +0.4 | -0.042 / -0.042 / -0.030 |
| precip: steady | 9 (thin) | -0.81 / -1.08 / -1.24 | +5.1 / +1.7 / +0.8 | -3.2 / -2.4 / -1.0 | -0.081 / -0.113 / -0.128\* |
| precip: wet | 22 | -0.24 / -0.35 / -0.29 | +0.8 / -0.7 / -0.4 | -0.1 / -0.3 / -0.2 | -0.058 / -0.071\* / -0.068 |
| temp: cold | 21 | -0.60 / -0.26 / -0.00 | -2.2 / +1.2 / +1.7 | +3.1 / +2.3 / +0.6 | -0.020 / +0.018 / +0.035 |
| temp: mild | 71 | -0.22 / -0.20 / -0.15 | -1.6 / -1.5 / -1.6 | +0.7 / +0.4 / -0.1 | -0.036\* / -0.034\* / -0.033\* |
| temp: warm | 35 | +0.85\* / +0.69\* / +0.56 | +4.8\* / +3.2 / +3.8\* | -3.0\* / -2.4\* / -1.0 | +0.082\* / +0.063\* / +0.067\* |
| temp: hot | 6 (thin) | -0.30 / -0.65 / -0.87 | -0.6 / -4.9 / -4.8 | -1.4 / +0.9 / +3.7 | +0.021 / -0.020 / -0.031 |
| temp: warm_hot | 41 | +0.68\* / +0.49\* / +0.37 | +4.0\* / +2.0 / +2.8 | -2.8\* / -1.9\* / -0.3 | +0.073\* / +0.050\* / +0.060\* |

### USC

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

Each cell: **Raw / Adjusted / Controlled** delta vs the team's own average (\* = 90% interval excludes zero). Intervals are in `milestone3_detail.md`.

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 88 | +0.09 / +0.04 / +0.03 | +0.8 / +0.3 / +0.3 | -0.5 / -0.5 / -0.5 | +0.015 / +0.008 / +0.009 |
| wind: moderate | 34 | +0.16 / +0.18 / +0.16 | +0.3 / +0.4 / -0.0 | +1.8 / +1.3 / +1.7 | -0.015 / -0.013 / -0.020 |
| wind: windy | 9 (thin) | -1.48\* / -1.04\* / -0.93\* | -8.5\* / -4.3 / -3.3 | -1.5 / -0.2 / -1.0 | -0.084 / -0.027 / -0.010 |
| precip: none | 124 | +0.01 / -0.01 / -0.02 | +0.1 / -0.1 / -0.1 | +0.1 / +0.2 / +0.2 | +0.005\* / +0.003 / +0.001 |
| precip: light | 2 (suppressed) | — | — | — | — |
| precip: steady | 5 (thin) | +0.27 / +0.51 / +0.56 | +1.1 / +3.4 / +3.9 | -4.6 / -4.9\* / -4.8 | -0.025 / +0.006 / +0.018 |
| precip: wet | 7 (thin) | -0.23 / +0.14 / +0.32 | -2.5 / +1.0 / +2.6 | -2.3 / -3.1 / -3.6 | -0.094\* / -0.046 / -0.023 |
| temp: cold | 4 (suppressed) | — | — | — | — |
| temp: mild | 74 | -0.39\* / -0.27\* / -0.23 | -2.5\* / -1.3\* / -0.8 | +2.9\* / +2.4\* / +2.4\* | -0.025 / -0.009 / +0.002 |
| temp: warm | 43 | +0.60\* / +0.42\* / +0.30 | +4.1\* / +2.5\* / +1.0 | -3.7\* / -3.1\* / -2.6\* | +0.038 / +0.016 / -0.007 |
| temp: hot | 9 (thin) | +0.89\* / +0.48 / +0.40 | +8.6\* / +4.8\* / +4.6 | -5.2\* / -1.8 / -1.3 | +0.110\* / +0.057 / +0.052 |
| temp: warm_hot | 52 | +0.65\* / +0.43\* / +0.37\* | +4.9\* / +2.9\* / +2.0\* | -4.0\* / -2.8\* / -2.7\* | +0.051\* / +0.023 / +0.006 |

### Oregon

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

Each cell: **Raw / Adjusted / Controlled** delta vs the team's own average (\* = 90% interval excludes zero). Intervals are in `milestone3_detail.md`.

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 78 | -0.03 / -0.08 / -0.05 | +0.3 / -0.7 / -0.3 | +2.0\* / +1.0 / +1.4 | -0.004 / -0.013 / -0.010 |
| wind: moderate | 33 | +0.42 / +0.53 / +0.46 | +1.2 / +2.8 / +1.6 | -1.6 / +0.8 / -0.1 | +0.032 / +0.049 / +0.038 |
| wind: windy | 21 | -0.54 / -0.50 / -0.48 | -2.9 / -1.8 / -1.3 | -5.0\* / -4.6\* / -4.4\* | -0.037 / -0.026 / -0.018 |
| precip: none | 118 | +0.10\* / +0.11\* / +0.10 | +0.1 / +0.1 / -0.1 | +0.1 / +0.1 / +0.1 | +0.002 / +0.001 / +0.001 |
| precip: light | 9 (thin) | -0.23 / -0.32 / -0.13 | +0.4 / +0.1 / +1.2 | -2.4 / -2.6 / -3.1 | +0.016 / +0.020 / +0.024 |
| precip: steady | 5 (thin) | -2.05\* / -1.90\* / -2.01\* | -4.0 / -1.4 / -0.2 | +2.0 / +2.4 / +3.4 | -0.074 / -0.046 / -0.059 |
| precip: wet | 14 | -0.88\* / -0.92\* / -0.85 | -1.2 / -0.5 / +0.7 | -0.8 / -0.7 / -0.6 | -0.016 / -0.005 / -0.008 |
| temp: cold | 7 (thin) | +0.33 / +0.25 / -0.11 | -1.7 / -1.3 / -1.9 | -2.2 / -5.6 / -4.5 | +0.032 / +0.032 / +0.010 |
| temp: mild | 93 | -0.32\* / -0.24\* / -0.18 | -2.1\* / -0.7 / -0.0 | +0.7 / +0.1 / +0.6 | -0.038\* / -0.022\* / -0.016 |
| temp: warm | 29 | +1.07\* / +0.93\* / +0.96\* | +7.7\* / +3.0 / +1.0 | -2.1 / +0.7 / -1.4 | +0.129\* / +0.085\* / +0.086\* |
| temp: hot | 3 (suppressed) | — | — | — | — |
| temp: warm_hot | 32 | +0.87\* / +0.78\* / +0.83\* | +6.4\* / +2.8 / +0.8 | -1.6 / +1.3 / -0.8 | +0.102\* / +0.069\* / +0.067 |

### Northwestern

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

Each cell: **Raw / Adjusted / Controlled** delta vs the team's own average (\* = 90% interval excludes zero). Intervals are in `milestone3_detail.md`.

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 56 | -0.00 / -0.09 / -0.10 | +0.3 / -0.6 / -0.4 | +0.2 / +0.1 / -0.1 | -0.001 / -0.013 / -0.010 |
| wind: moderate | 46 | +0.13 / +0.22 / +0.25 | -0.9 / +0.1 / +0.3 | +2.4 / +3.5\* / +3.6\* | -0.019 / -0.004 / +0.001 |
| wind: windy | 34 | -0.17 / -0.14 / -0.18 | +0.7 / +0.8 / +0.3 | -3.6\* / -4.9\* / -5.1\* | +0.028 / +0.028 / +0.016 |
| precip: none | 121 | +0.02 / -0.02 / -0.01 | +0.0 / -0.3 / -0.2 | +0.2 / +0.4 / +0.3 | +0.002 / -0.002 / -0.001 |
| precip: light | 12 | +0.02 / +0.25 / +0.24 | +1.1 / +3.0 / +2.4 | +0.3 / -1.9 / -1.4 | -0.002 / +0.033 / +0.025 |
| precip: steady | 3 (suppressed) | — | — | — | — |
| precip: wet | 15 | -0.12 / +0.12 / +0.05 | -0.0 / +2.0 / +1.5 | -1.8 / -2.9 / -2.0 | -0.018 / +0.018 / +0.007 |
| temp: cold | 18 | -0.26 / -0.10 / +0.01 | +0.2 / +1.6 / +1.7 | -2.2 / -3.2 / -3.7 | -0.018 / +0.008 / +0.014 |
| temp: mild | 80 | -0.03 / +0.00 / -0.03 | +0.2 / +0.6 / +0.3 | +1.0 / +0.8 / +0.8 | +0.001 / +0.012 / +0.003 |
| temp: warm | 33 | +0.36 / +0.30 / +0.34 | +0.1 / -1.2 / -0.6 | -0.2 / +0.9 / +1.3 | +0.016 / -0.019 / -0.005 |
| temp: hot | 5 (thin) | -0.95 / -1.31\* / -1.27\* | -4.5 / -8.0 / -6.8 | -7.1\* / -5.3\* / -7.5\* | -0.050 / -0.101 / -0.067 |
| temp: warm_hot | 38 | +0.19 / +0.05 / +0.07 | -0.5 / -2.2 / -1.9 | -1.1 / -0.1 / -0.2 | +0.007 / -0.032 / -0.018 |

## Snow games

Snow is not split into delta rows (too few games). These are the games where an observation in the kickoff-to-+3.5h window reported a snow weather code. A code can mean flurries, so read the precipitation and temperature columns.

| Date | Game | Venue | Observed in window | Score |
|---|---|---|---|---|
| 2016-11-19 | Ohio State @ Michigan State | Spartan Stadium | 34°F, wind 22 mph (gust 35), precip 0.00 in, vis 4.0 mi | Ohio State 17, Michigan State 16 |
| 2017-11-18 | Minnesota @ Northwestern | Ryan Field | 36°F, wind 16 mph (gust 25), precip 0.10 in, vis 2.0 mi | Minnesota 0, Northwestern 39 |
| 2021-11-27 | Ohio State @ Michigan | Michigan Stadium | 28°F, wind 10 mph, precip 0.01 in, vis 0.8 mi | Ohio State 27, Michigan 42 |
| 2022-11-12 | Indiana @ Ohio State | Ohio Stadium | 36°F, wind 10 mph, precip 0.03 in, vis 1.5 mi | Indiana 14, Ohio State 56 |
| 2022-11-12 | Northwestern @ Minnesota | Huntington Bank Stadium | 28°F, wind 14 mph (gust 24), precip 0.00 in, vis 9.0 mi | Northwestern 3, Minnesota 31 |
| 2025-11-29 | Ohio State @ Michigan | Michigan Stadium | 28°F, wind 13 mph, precip 0.01 in, vis 0.8 mi | Ohio State 27, Michigan 9 |
| 2025-11-29 | Northwestern @ Illinois | Memorial Stadium (Champaign, IL) | 33°F, wind 28 mph (gust 44), precip 0.06 in, vis 0.5 mi | Northwestern 13, Illinois 20 |

