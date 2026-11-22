# Milestone 3: scaled splits, controlled model, evidence tiers

_Generated 2026-11-22 15:16 UTC._

> **EXPLORATORY.** This report tests many team × bin × metric cells. At a 90% level roughly 1 in 10 intervals will exclude zero by luck alone, so a starred (\*) delta or a "leans" tier is a lead to check, not a finding.

**Two yardsticks, always labelled.** *A. vs the team's overall average* compares a bin to all of the team's games, including the bin itself. *B. vs all other games* compares the bin to the games NOT in it ("windy vs not windy"); it is the A number divided by (1 − the bin's share of games). Evidence tiers use the controlled model, where the choice of yardstick does not change the verdict.

**Teams loaded (6):** Michigan, Nebraska, Northwestern, Ohio State, Oregon, USC. **Deferred by choice (7):** Ball State, Texas, Kent State, Illinois, Iowa, Maryland, Indiana -- not loaded (their 2026 games are already played, so they only matter for the Team Explorer); nothing here depends on them.

## Plain-language summary

- **Wind (windy vs not)** -- pooled across 6 teams, controlled for opponent, month and home/away: Pass yds/att -0.50 yds/att [-0.75, -0.25] (interval excludes zero); Points scored -2.2 pts [-3.4, -0.9] (interval excludes zero); Offensive PPA/play -0.030 PPA [-0.052, -0.009] (interval excludes zero). Clear evidence for: Ohio State. Leans: Michigan, Nebraska, USC.
- **Wet (light + steady rain)** -- pooled across 6 teams, controlled for opponent, month and home/away: Pass yds/att -0.32 yds/att [-0.70, +0.05] (interval spans zero); Points scored +0.1 pts [-1.8, +1.9] (interval spans zero); Offensive PPA/play -0.022 PPA [-0.054, +0.010] (interval spans zero). No team clears the bar. 
- **Warm/hot (70°F and up)** -- pooled across 6 teams, controlled for opponent, month and home/away: Pass yds/att +0.35 yds/att [+0.12, +0.57] (interval excludes zero); Points scored +0.9 pts [-0.3, +2.1] (interval spans zero); Offensive PPA/play +0.014 PPA [-0.007, +0.035] (interval spans zero). Clear evidence for: Ohio State. Leans: Nebraska, Ohio State, Oregon.
- **Cold (39°F and below)** -- pooled across 6 teams, controlled for opponent, month and home/away: Pass yds/att -0.13 yds/att [-0.47, +0.20] (interval spans zero); Points scored -0.9 pts [-2.7, +1.0] (interval spans zero); Offensive PPA/play +0.009 PPA [-0.025, +0.039] (interval spans zero). No team clears the bar. 

Temperature: the controlled model finds no clear temperature effect for Michigan, Northwestern, USC, so their temperature results are labelled context-only; it still shows one (kept as is) for Nebraska, Ohio State, Oregon.

_Exploratory: tiers and stars are leads to check, not findings._

## CFBD call budget

- Month (2026-11) total so far: **25** of the 600-call cap (free-tier limit 1000); **975** calls remain before CFBD itself would stop us. CFBD's own `/info` count is the source of truth, and `/info` is not billed.
- 437 of the month's calls were spent before the counter and raw cache existed (early un-cached runs).
- **This session's backfill (--skip-ratings): 91 calls** (planned worst case 115, threshold to ask first: 500). Counter went 438 → 529.

| Endpoint | Planned (worst case) | Planned (exact, after /games) | Actually used |
|---|---|---|---|
| /games | 22 | 0 | 22 |
| /games/teams | 46 | 34 | 34 |
| /ppa/games | 46 | 34 | 34 |
| /ratings/sp | 0 | 0 | 0 |
| /venues | 1 | 1 | 1 |
| **Total** | **115** | **91** | **91** |

## What changed in the pooled lines: 4 teams → 6 teams

Added: Michigan, Nebraska. Controlled Δ **vs the team's overall average** (same yardstick as the pooled tables above); n is the pooled game count; \* = 90% interval excludes zero.

| Bin | Metric | Before: n | Before | After: n | After |
|---|---|---|---|---|---|
| wind: windy | Pass yds/att | 95 | -0.69 [-1.02, -0.36] \* | 176 | -0.50 [-0.75, -0.25] \* |
| wind: windy | Points scored | 95 | -2.0 [-3.7, -0.1] \* | 176 | -2.2 [-3.4, -0.9] \* |
| wind: windy | Points allowed (defense) | 95 | -3.0 [-4.6, -1.6] \* | 176 | -2.1 [-3.3, -1.0] \* |
| wind: windy | Offensive PPA/play | 95 | -0.028 [-0.057, +0.001] | 176 | -0.030 [-0.052, -0.009] \* |
| precip: wet | Pass yds/att | 58 | -0.27 [-0.71, +0.19] | 89 | -0.32 [-0.70, +0.05] |
| precip: wet | Points scored | 58 | +0.5 [-1.9, +3.0] | 89 | +0.1 [-1.8, +1.9] |
| precip: wet | Points allowed (defense) | 58 | -1.7 [-3.5, +0.5] | 89 | -2.2 [-3.7, -0.8] \* |
| precip: wet | Offensive PPA/play | 58 | -0.032 [-0.071, +0.006] | 89 | -0.022 [-0.054, +0.010] |
| precip: steady | Pass yds/att | 22 | -0.91 [-1.67, -0.11] \* | 28 | -0.74 [-1.43, -0.08] \* |
| precip: steady | Points scored | 22 | +0.4 [-4.1, +4.8] | 28 | +0.9 [-3.0, +5.0] |
| precip: steady | Points allowed (defense) | 22 | -2.0 [-5.6, +1.6] | 28 | -2.1 [-5.2, +0.8] |
| precip: steady | Offensive PPA/play | 22 | -0.073 [-0.147, -0.006] \* | 28 | -0.074 [-0.136, -0.014] \* |
| temp: cold | Pass yds/att | 50 | +0.08 [-0.34, +0.51] | 93 | -0.13 [-0.47, +0.20] |
| temp: cold | Points scored | 50 | +1.6 [-1.0, +4.3] | 93 | -0.9 [-2.7, +1.0] |
| temp: cold | Points allowed (defense) | 50 | -2.0 [-4.5, +0.6] | 93 | -2.1 [-4.0, -0.4] \* |
| temp: cold | Offensive PPA/play | 50 | +0.029 [-0.013, +0.068] | 93 | +0.009 [-0.025, +0.039] |
| temp: warm_hot | Pass yds/att | 163 | +0.41 [+0.13, +0.69] \* | 247 | +0.35 [+0.12, +0.57] \* |
| temp: warm_hot | Points scored | 163 | +1.4 [-0.1, +2.8] | 247 | +0.9 [-0.3, +2.1] |
| temp: warm_hot | Points allowed (defense) | 163 | -1.3 [-2.6, +0.0] | 247 | -0.8 [-1.8, +0.2] |
| temp: warm_hot | Offensive PPA/play | 163 | +0.029 [+0.005, +0.054] \* | 247 | +0.014 [-0.007, +0.035] |

## 2026 Ohio State schedule

11 played, 1 remaining. Team list = Ohio State + every opponent below (13 teams, from `config/opponents.yaml`).

| Wk | Date | Opponent | Site | Venue | Status |
|---|---|---|---|---|---|
| 1 | Sep 05 | Ball State _(deferred)_ | home | Ohio Stadium | played: W 56-3 |
| 2 | Sep 12 | Texas _(deferred)_ | away | DKR-Texas Memorial Stadium | played: L 23-24 |
| 3 | Sep 19 | Kent State _(deferred)_ | home | Ohio Stadium | played: W 59-3 |
| 4 | Sep 26 | Illinois _(deferred)_ | home | Ohio Stadium | played: W 42-19 |
| 5 | Oct 03 | Iowa _(deferred)_ | away | Kinnick Stadium | played: W 31-14 |
| 6 | Oct 10 | Maryland _(deferred)_ | home | Ohio Stadium | played: W 45-16 |
| 7 | Oct 17 | Indiana _(deferred)_ | away | Memorial Stadium (Bloomington, IN) | played: W 19-15 |
| 9 | Oct 31 | USC | away | Los Angeles Memorial Coliseum | played: L 18-30 |
| 10 | Nov 07 | Oregon | home | Ohio Stadium | played: L 28-41 |
| 11 | Nov 14 | Northwestern | home | Ohio Stadium | played: W 28-19 |
| 12 | Nov 21 | Nebraska | away | Memorial Stadium (Lincoln, NE) | played: L 28-31 |
| 13 | Nov 28 | Michigan | home | Ohio Stadium | **remaining** |

## Evidence tiers (controlled model)

Computed in the pipeline from the **controlled** intervals (opponent strength + month + home/away held fixed). Metric groups: **passing** = pass yds/att + offensive PPA; **scoring** = points scored + offensive PPA.

- **CLEAR**: n ≥ 10 and the controlled interval excludes zero (same direction) on both metrics in the group.
- **leans**: both metrics point the same way and the effect is at least 1 standard error(s) in size, but not clear (an interval spans zero, or n is 5-9).
- **none** (no_clear_effect): n ≥ 10 and nothing there.   **n/a** (insufficient): n < 5, or n 5-9 with no lean.
- **context**: temperature results for a team whose controlled model finds no temperature effect in any bin -- kept for context, not as evidence.

### Passing

| Team | wind:<br>light | wind:<br>moderate | wind:<br>windy | precip:<br>none | precip:<br>light | precip:<br>steady | precip:<br>wet | temp:<br>cold | temp:<br>mild | temp:<br>warm | temp:<br>hot | temp:<br>warm_hot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ohio State | **CLEAR** (62) | none (41) | **CLEAR** (32) | none (111) | none (15) | leans (9) | none (24) | none (21) | leans (74) | leans (34) | n/a (6) | leans (40) |
| USC | none (91) | none (34) | leans (9) | none (126) | n/a (3) | n/a (5) | n/a (8) | n/a (4) | context (77) | context (43) | context (9) | context (52) |
| Oregon | none (73) | none (31) | none (21) | none (112) | n/a (8) | leans (5) | none (13) | n/a (7) | leans (93) | **CLEAR** (23) | n/a (2) | leans (25) |
| Northwestern | none (57) | none (44) | none (31) | none (117) | none (12) | n/a (3) | none (15) | context (18) | context (81) | context (28) | context (5) | context (33) |
| Nebraska | leans (54) | none (35) | none (46) | none (123) | none (12) | n/a (0) | none (12) | none (19) | leans (73) | leans (29) | none (14) | leans (43) |
| Michigan | none (65) | none (38) | leans (30) | none (123) | none (10) | n/a (6) | none (16) | context (24) | context (73) | context (32) | n/a (4) | context (36) |
| Pooled (6 teams) | **CLEAR** (402) | none (223) | **CLEAR** (169) | leans (712) | none (60) | **CLEAR** (28) | leans (88) | context (93) | context (471) | context (189) | context (40) | context (229) |

### Scoring

| Team | wind:<br>light | wind:<br>moderate | wind:<br>windy | precip:<br>none | precip:<br>light | precip:<br>steady | precip:<br>wet | temp:<br>cold | temp:<br>mild | temp:<br>warm | temp:<br>hot | temp:<br>warm_hot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ohio State | leans (62) | none (41) | **CLEAR** (32) | none (111) | none (15) | n/a (9) | none (24) | none (21) | **CLEAR** (74) | **CLEAR** (34) | n/a (6) | **CLEAR** (40) |
| USC | none (91) | none (34) | n/a (9) | none (126) | n/a (3) | n/a (5) | n/a (8) | n/a (4) | context (77) | context (43) | context (9) | context (52) |
| Oregon | none (73) | none (31) | none (21) | none (112) | n/a (8) | n/a (5) | none (13) | n/a (7) | none (93) | leans (23) | n/a (2) | none (25) |
| Northwestern | none (57) | none (44) | none (31) | none (117) | none (12) | n/a (3) | none (15) | context (18) | context (81) | context (28) | context (5) | context (33) |
| Nebraska | leans (54) | none (35) | leans (46) | none (123) | none (12) | n/a (0) | none (12) | none (19) | **CLEAR** (73) | leans (29) | none (14) | leans (43) |
| Michigan | none (65) | none (38) | leans (30) | none (123) | none (10) | n/a (6) | none (16) | context (24) | context (73) | context (32) | n/a (4) | context (36) |
| Pooled (6 teams) | leans (402) | none (223) | **CLEAR** (169) | none (712) | none (60) | none (28) | none (88) | context (93) | context (471) | context (189) | context (40) | context (229) |

**Temperature:** a team's temperature tiers are kept as they are only if its controlled model has at least one CLEAR temperature cell; otherwise they are labelled context-only. Kept: Ohio State, Oregon, Nebraska. Context-only: Michigan, Northwestern, USC, Pooled (6 teams).

## Pooled reference line (all 6 loaded teams together)

Every team-game from the **6 teams** in the pool, each measured against its own team's baseline. Raw / Adjusted / Controlled as defined above; brackets are 90% intervals from a bootstrap over whole games. The same numbers are shown on two yardsticks; **steady** rain is kept as its own bin next to the merged **wet** bin.

### A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)

**wind** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| wind: light | Pass yds/att | 410 | +0.15 [+0.02, +0.28] \* | +0.12 [+0.01, +0.24] \* | +0.15 [+0.02, +0.27] \* |
| wind: light | Points scored | 410 | +0.7 [-0.1, +1.5] | +0.3 [-0.3, +0.9] | +0.4 [-0.2, +1.1] |
| wind: light | Points allowed (defense) | 410 | +0.3 [-0.4, +1.0] | +0.0 [-0.6, +0.6] | +0.0 [-0.6, +0.6] |
| wind: light | Offensive PPA/play | 410 | +0.016 [+0.004, +0.028] \* | +0.012 [+0.001, +0.022] \* | +0.015 [+0.003, +0.026] \* |
| wind: moderate | Pass yds/att | 235 | +0.15 [-0.06, +0.35] | +0.13 [-0.07, +0.31] | +0.12 [-0.08, +0.31] |
| wind: moderate | Points scored | 235 | +0.9 [-0.2, +2.2] | +1.1 [+0.1, +2.1] \* | +1.1 [+0.1, +2.1] \* |
| wind: moderate | Points allowed (defense) | 235 | +1.3 [+0.1, +2.5] \* | +1.4 [+0.4, +2.4] \* | +1.5 [+0.5, +2.5] \* |
| wind: moderate | Offensive PPA/play | 235 | -0.000 [-0.020, +0.020] | -0.000 [-0.017, +0.017] | -0.003 [-0.021, +0.014] |
| wind: windy | Pass yds/att | 176 | -0.53 [-0.77, -0.26] \* | -0.46 [-0.70, -0.21] \* | -0.50 [-0.75, -0.25] \* |
| wind: windy | Points scored | 176 | -2.6 [-4.0, -1.1] \* | -2.0 [-3.2, -0.7] \* | -2.2 [-3.4, -0.9] \* |
| wind: windy | Points allowed (defense) | 176 | -2.4 [-3.7, -1.2] \* | -1.9 [-3.0, -0.8] \* | -2.1 [-3.3, -1.0] \* |
| wind: windy | Offensive PPA/play | 176 | -0.034 [-0.057, -0.012] \* | -0.027 [-0.049, -0.006] \* | -0.030 [-0.052, -0.009] \* |

**precip** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| precip: none | Pass yds/att | 738 | +0.05 [+0.00, +0.11] \* | +0.04 [-0.01, +0.09] | +0.04 [-0.01, +0.09] |
| precip: none | Points scored | 738 | +0.1 [-0.2, +0.4] | -0.0 [-0.2, +0.2] | -0.0 [-0.2, +0.2] |
| precip: none | Points allowed (defense) | 738 | +0.2 [-0.0, +0.4] | +0.3 [+0.1, +0.4] \* | +0.3 [+0.1, +0.5] \* |
| precip: none | Offensive PPA/play | 738 | +0.005 [+0.000, +0.009] \* | +0.003 [-0.001, +0.006] | +0.003 [-0.001, +0.007] |
| precip: light | Pass yds/att | 61 | -0.31 [-0.82, +0.20] | -0.18 [-0.66, +0.28] | -0.12 [-0.62, +0.33] |
| precip: light | Points scored | 61 | -1.7 [-4.2, +1.2] | -0.6 [-2.6, +1.5] | -0.3 [-2.5, +1.7] |
| precip: light | Points allowed (defense) | 61 | -0.7 [-3.1, +1.7] | -1.7 [-3.5, +0.0] | -2.3 [-4.1, -0.7] \* |
| precip: light | Offensive PPA/play | 61 | -0.019 [-0.066, +0.026] | -0.002 [-0.043, +0.038] | +0.003 [-0.039, +0.043] |
| precip: steady | Pass yds/att | 28 | -0.77 [-1.51, -0.03] \* | -0.63 [-1.32, +0.05] | -0.74 [-1.43, -0.08] \* |
| precip: steady | Points scored | 28 | +0.3 [-4.8, +5.6] | +1.4 [-2.6, +5.5] | +0.9 [-3.0, +5.0] |
| precip: steady | Points allowed (defense) | 28 | -3.5 [-6.3, -0.7] \* | -2.7 [-5.7, +0.2] | -2.1 [-5.2, +0.8] |
| precip: steady | Offensive PPA/play | 28 | -0.081 [-0.148, -0.015] \* | -0.060 [-0.121, -0.002] \* | -0.074 [-0.136, -0.014] \* |
| precip: wet | Pass yds/att | 89 | -0.45 [-0.87, -0.04] \* | -0.32 [-0.70, +0.05] | -0.32 [-0.70, +0.05] |
| precip: wet | Points scored | 89 | -1.1 [-3.3, +1.4] | +0.0 [-1.8, +1.9] | +0.1 [-1.8, +1.9] |
| precip: wet | Points allowed (defense) | 89 | -1.6 [-3.4, +0.2] | -2.0 [-3.5, -0.6] \* | -2.2 [-3.7, -0.8] \* |
| precip: wet | Offensive PPA/play | 89 | -0.038 [-0.074, -0.002] \* | -0.020 [-0.053, +0.011] | -0.022 [-0.054, +0.010] |

**temp** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| temp: cold | Pass yds/att | 93 | -0.51 [-0.85, -0.17] \* | -0.24 [-0.56, +0.09] | -0.13 [-0.47, +0.20] |
| temp: cold | Points scored | 93 | -3.5 [-5.6, -1.4] \* | -1.0 [-2.8, +0.7] | -0.9 [-2.7, +1.0] |
| temp: cold | Points allowed (defense) | 93 | +0.1 [-1.9, +2.1] | -1.4 [-3.0, +0.2] | -2.1 [-4.0, -0.4] \* |
| temp: cold | Offensive PPA/play | 93 | -0.032 [-0.065, -0.000] \* | -0.000 [-0.030, +0.027] | +0.009 [-0.025, +0.039] |
| temp: mild | Pass yds/att | 480 | -0.20 [-0.31, -0.09] \* | -0.13 [-0.23, -0.03] \* | -0.10 [-0.21, +0.01] |
| temp: mild | Points scored | 480 | -0.9 [-1.5, -0.2] \* | -0.1 [-0.7, +0.4] | +0.0 [-0.6, +0.6] |
| temp: mild | Points allowed (defense) | 480 | +1.3 [+0.8, +1.9] \* | +0.9 [+0.4, +1.4] \* | +0.7 [+0.2, +1.3] \* |
| temp: mild | Offensive PPA/play | 480 | -0.018 [-0.028, -0.008] \* | -0.008 [-0.017, +0.002] | -0.006 [-0.015, +0.005] |
| temp: warm_hot | Pass yds/att | 247 | +0.59 [+0.39, +0.80] \* | +0.37 [+0.18, +0.57] \* | +0.35 [+0.12, +0.57] \* |
| temp: warm_hot | Points scored | 247 | +3.4 [+2.2, +4.7] \* | +1.0 [-0.1, +2.1] | +0.9 [-0.3, +2.1] |
| temp: warm_hot | Points allowed (defense) | 247 | -2.6 [-3.6, -1.5] \* | -1.1 [-2.0, -0.2] \* | -0.8 [-1.8, +0.2] |
| temp: warm_hot | Offensive PPA/play | 247 | +0.050 [+0.031, +0.068] \* | +0.018 [+0.001, +0.034] \* | +0.014 [-0.007, +0.035] |

### B. vs ALL OTHER GAMES (the complement: games not in the bin)

**wind** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| wind: light | Pass yds/att | 410 | +0.29 [+0.04, +0.55] \* | +0.25 [+0.02, +0.49] \* | +0.29 [+0.05, +0.55] \* |
| wind: light | Points scored | 410 | +1.4 [-0.2, +3.0] | +0.6 [-0.6, +1.9] | +0.9 [-0.4, +2.1] |
| wind: light | Points allowed (defense) | 410 | +0.6 [-0.8, +2.1] | +0.1 [-1.1, +1.3] | +0.0 [-1.2, +1.2] |
| wind: light | Offensive PPA/play | 410 | +0.031 [+0.007, +0.055] \* | +0.024 [+0.002, +0.045] \* | +0.031 [+0.007, +0.052] \* |
| wind: moderate | Pass yds/att | 235 | +0.21 [-0.09, +0.49] | +0.18 [-0.10, +0.43] | +0.17 [-0.12, +0.44] |
| wind: moderate | Points scored | 235 | +1.3 [-0.3, +3.0] | +1.6 [+0.2, +3.0] \* | +1.5 [+0.1, +2.9] \* |
| wind: moderate | Points allowed (defense) | 235 | +1.8 [+0.1, +3.5] \* | +1.9 [+0.5, +3.3] \* | +2.1 [+0.8, +3.5] \* |
| wind: moderate | Offensive PPA/play | 235 | -0.001 [-0.027, +0.028] | -0.000 [-0.024, +0.023] | -0.004 [-0.029, +0.020] |
| wind: windy | Pass yds/att | 176 | -0.67 [-0.98, -0.33] \* | -0.59 [-0.88, -0.26] \* | -0.63 [-0.95, -0.31] \* |
| wind: windy | Points scored | 176 | -3.3 [-5.1, -1.4] \* | -2.5 [-4.1, -0.9] \* | -2.8 [-4.3, -1.1] \* |
| wind: windy | Points allowed (defense) | 176 | -3.0 [-4.6, -1.5] \* | -2.4 [-3.8, -1.0] \* | -2.7 [-4.2, -1.3] \* |
| wind: windy | Offensive PPA/play | 176 | -0.044 [-0.073, -0.016] \* | -0.034 [-0.062, -0.008] \* | -0.039 [-0.066, -0.012] \* |

**precip** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| precip: none | Pass yds/att | 738 | +0.51 [+0.05, +0.97] \* | +0.36 [-0.06, +0.79] | +0.36 [-0.05, +0.79] |
| precip: none | Points scored | 738 | +1.2 [-1.5, +3.8] | -0.0 [-2.1, +2.0] | -0.1 [-2.1, +2.0] |
| precip: none | Points allowed (defense) | 738 | +1.8 [-0.2, +3.8] | +2.3 [+0.6, +3.9] \* | +2.5 [+0.9, +4.1] \* |
| precip: none | Offensive PPA/play | 738 | +0.043 [+0.003, +0.083] \* | +0.023 [-0.012, +0.059] | +0.025 [-0.011, +0.060] |
| precip: light | Pass yds/att | 61 | -0.33 [-0.88, +0.22] | -0.20 [-0.71, +0.30] | -0.13 [-0.67, +0.35] |
| precip: light | Points scored | 61 | -1.8 [-4.6, +1.3] | -0.6 [-2.8, +1.6] | -0.4 [-2.6, +1.8] |
| precip: light | Points allowed (defense) | 61 | -0.7 [-3.4, +1.8] | -1.9 [-3.7, +0.0] | -2.5 [-4.4, -0.7] \* |
| precip: light | Offensive PPA/play | 61 | -0.020 [-0.071, +0.028] | -0.002 [-0.046, +0.041] | +0.003 [-0.042, +0.047] |
| precip: steady | Pass yds/att | 28 | -0.80 [-1.56, -0.03] \* | -0.65 [-1.36, +0.06] | -0.77 [-1.48, -0.09] \* |
| precip: steady | Points scored | 28 | +0.3 [-5.0, +5.8] | +1.4 [-2.7, +5.7] | +1.0 [-3.0, +5.2] |
| precip: steady | Points allowed (defense) | 28 | -3.6 [-6.5, -0.7] \* | -2.8 [-5.9, +0.2] | -2.2 [-5.4, +0.8] |
| precip: steady | Offensive PPA/play | 28 | -0.084 [-0.154, -0.016] \* | -0.062 [-0.126, -0.002] \* | -0.077 [-0.140, -0.015] \* |
| precip: wet | Pass yds/att | 89 | -0.51 [-0.97, -0.05] \* | -0.36 [-0.79, +0.06] | -0.36 [-0.79, +0.05] |
| precip: wet | Points scored | 89 | -1.2 [-3.8, +1.5] | +0.0 [-2.0, +2.1] | +0.1 [-2.0, +2.1] |
| precip: wet | Points allowed (defense) | 89 | -1.8 [-3.8, +0.2] | -2.3 [-3.9, -0.6] \* | -2.5 [-4.1, -0.9] \* |
| precip: wet | Offensive PPA/play | 89 | -0.043 [-0.083, -0.003] \* | -0.023 [-0.059, +0.012] | -0.025 [-0.060, +0.011] |

**temp** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| temp: cold | Pass yds/att | 93 | -0.57 [-0.95, -0.19] \* | -0.27 [-0.63, +0.10] | -0.14 [-0.53, +0.23] |
| temp: cold | Points scored | 93 | -4.0 [-6.3, -1.6] \* | -1.1 [-3.1, +0.8] | -1.0 [-3.1, +1.1] |
| temp: cold | Points allowed (defense) | 93 | +0.1 [-2.1, +2.4] | -1.6 [-3.4, +0.2] | -2.4 [-4.5, -0.4] \* |
| temp: cold | Offensive PPA/play | 93 | -0.036 [-0.073, -0.000] \* | -0.000 [-0.034, +0.031] | +0.010 [-0.028, +0.044] |
| temp: mild | Pass yds/att | 480 | -0.47 [-0.73, -0.20] \* | -0.31 [-0.55, -0.07] \* | -0.24 [-0.52, +0.02] |
| temp: mild | Points scored | 480 | -2.1 [-3.7, -0.4] \* | -0.3 [-1.7, +1.0] | +0.0 [-1.4, +1.4] |
| temp: mild | Points allowed (defense) | 480 | +3.2 [+1.9, +4.6] \* | +2.1 [+0.9, +3.3] \* | +1.8 [+0.6, +3.1] \* |
| temp: mild | Offensive PPA/play | 480 | -0.043 [-0.066, -0.017] \* | -0.019 [-0.041, +0.004] | -0.014 [-0.038, +0.012] |
| temp: warm_hot | Pass yds/att | 247 | +0.84 [+0.57, +1.13] \* | +0.52 [+0.26, +0.80] \* | +0.49 [+0.17, +0.80] \* |
| temp: warm_hot | Points scored | 247 | +4.8 [+3.1, +6.6] \* | +1.4 [-0.1, +2.9] | +1.3 [-0.5, +3.0] |
| temp: warm_hot | Points allowed (defense) | 247 | -3.6 [-5.1, -2.2] \* | -1.6 [-2.8, -0.3] \* | -1.2 [-2.5, +0.3] |
| temp: warm_hot | Offensive PPA/play | 247 | +0.071 [+0.044, +0.096] \* | +0.025 [+0.001, +0.048] \* | +0.020 [-0.010, +0.048] |

## How much do the controls change things?

Solid cells, per-team (not pooled), all seasons. *Sign flips* = adjusted and controlled point opposite ways. *Excl. 0* = intervals excluding zero (about 1 in 10 expected by luck).

| Metric | Cells | Avg \|raw\| | Avg \|adj\| | Avg \|ctl\| | Adj→Ctl sign flips | Raw excl. 0 | Adj excl. 0 | Ctl excl. 0 |
|---|---|---|---|---|---|---|---|---|
| Pass yds/att | 55 | 0.38 | 0.31 | 0.31 | 3 | 15 | 13 | 5 |
| Rush yds/carry | 55 | 0.18 | 0.16 | 0.16 | 7 | 6 | 4 | 3 |
| Points scored | 55 | 2.0 | 1.4 | 1.4 | 1 | 15 | 7 | 7 |
| Points allowed (defense) | 55 | 1.8 | 1.5 | 1.3 | 5 | 15 | 12 | 10 |
| Turnovers | 55 | 0.14 | 0.14 | 0.13 | 6 | 6 | 6 | 5 |
| Offensive PPA/play | 55 | 0.030 | 0.024 | 0.025 | 3 | 13 | 10 | 9 |

## Opponent ratings: which games have no SP+?

SP+ covers FBS teams only. A game against an FCS opponent has no rating, so it is left out of the **Adjusted** and **Controlled** columns (it still counts in **Raw**). It is never guessed. *Raw shift* = how much the average |raw Δ| of the team's solid cells moves when the raw numbers are recomputed on rated games only -- a direct read on whether dropping those games matters.

| Team | Usable games | No SP+ rating | Opponents without a rating | Raw shift |
|---|---|---|---|---|
| Michigan | 139 | 0 | — | 0.000 |
| Nebraska | 141 | 6 | Bethune-Cookman, Fordham, Houston Christian, North Dakota, Northern Iowa | 0.246 |
| Northwestern | 140 | 8 | Eastern Illinois, Howard, Illinois State, Indiana State, South Dakota State, Southern Illinois … | 0.175 |
| Ohio State | 137 | 2 | Grambling, Youngstown State | 0.081 |
| Oregon | 136 | 11 | Eastern Washington, Idaho, Montana, Montana State, Portland State, Southern Utah … | 0.402 |
| USC | 134 | 0 | — | 0.000 |

## Games by season (usable outdoor team-games)

Finished games from the in-progress season count exactly like any other season.

| Season | Michigan | Nebraska | Northwestern | Ohio State | Oregon | USC |
|---|---|---|---|---|---|---|
| 2015 | 12 | 13 | 12 | 12 | 11 | 14 |
| 2016 | 12 | 13 | 13 | 12 | 12 | 10 |
| 2017 | 12 | 12 | 13 | 11 | 11 | 13 |
| 2018 | 12 | 12 | 13 | 11 | 13 | 11 |
| 2019 | 12 | 12 | 11 | 12 | 12 | 13 |
| 2020 | 6 | 8 | 8 | 6 | 5 | 5 |
| 2021 | 13 | 12 | 12 | 12 | 11 | 12 |
| 2022 | 11 | 11 | 11 | 12 | 12 | 10 |
| 2023 | 12 | 12 | 12 | 12 | 12 | 13 |
| 2024 | 13 | 13 | 12 | 14 | 12 | 10 |
| 2025 | 13 | 12 | 12 | 12 | 14 | 12 |
| 2026 (in progress) | 11 | 11 | 11 | 11 | 11 | 11 |

## Venues: domes, far stations, neutral sites, non-US

77 venues in the table; 18 are NEW since 2026-10-28 (marked **NEW**). Far = nearest ASOS more than 25 mi away.

**Domes (excluded from weather splits):** Caesars Superdome; Alamodome; AT&T Stadium; Ford Field; Lucas Oil Stadium; NRG Stadium **NEW**; State Farm Stadium; Mercedes-Benz Stadium; Allegiant Stadium

**Far stations (> 25 mi):** Lane Stadium (25.3 mi to ROA); Peden Stadium **NEW** (35.3 mi to PKB)

**Neutral-site venues:** Cotton Bowl **NEW** (1 game(s)); Rose Bowl (6 game(s)); Caesars Superdome (1 game(s)); Aviva Stadium (1 game(s)); Alamodome (3 game(s)); GEHA Field at Arrowhead Stadium **NEW** (1 game(s)); AT&T Stadium (9 game(s)); Ford Field (1 game(s)); Nissan Stadium (2 game(s)); Lucas Oil Stadium (9 game(s)); Raymond James Stadium (3 game(s)); NRG Stadium **NEW** (1 game(s)); Sam Boyd Stadium (1 game(s)); Qualcomm Stadium (3 game(s)); Soldier Field (1 game(s)); Hard Rock Stadium (4 game(s)); State Farm Stadium (6 game(s)); Camping World Stadium (4 game(s)); Yankee Stadium (2 game(s)); Petco Park (2 game(s)); Wrigley Field (6 game(s)); Levi's Stadium (5 game(s)); Mercedes-Benz Stadium (5 game(s)); Lanny and Sharon Martin Stadium (5 game(s)); Allegiant Stadium (7 game(s))

**Non-US venues (no US station used; those games are excluded):** Aviva Stadium

## Per team

Month/home/opponent mix of each bin first (what the bin is secretly measuring), then the effects.

### Ohio State

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 137 | 32% | 31% | 34% | 3% | 59% | 39% | 2% | +6.0 | +0.0 |
| wind: light | 62 | 32% | 35% | 26% | 6% | 56% | 40% | 3% | +5.8 | -0.1 |
| wind: moderate | 43 | 35% | 21% | 44% | 0% | 58% | 42% | 0% | +9.3 | +3.3 |
| wind: windy | 32 | 28% | 34% | 38% | 0% | 66% | 31% | 3% | +2.0 | -4.0 |
| precip: none | 113 | 32% | 31% | 34% | 4% | 60% | 37% | 3% | +6.2 | +0.2 |
| precip: light | 15 | 20% | 33% | 47% | 0% | 33% | 67% | 0% | +7.5 | +1.5 |
| precip: steady | 9 (thin) | 56% | 22% | 22% | 0% | 89% | 11% | 0% | +0.4 | -5.6 |
| precip: wet | 24 | 33% | 29% | 38% | 0% | 54% | 46% | 0% | +4.9 | -1.1 |
| temp: cold | 21 | 0% | 24% | 67% | 10% | 43% | 57% | 0% | +10.1 | +4.2 |
| temp: mild | 75 | 20% | 33% | 44% | 3% | 56% | 40% | 4% | +6.8 | +0.8 |
| temp: warm | 35 | 66% | 34% | 0% | 0% | 74% | 26% | 0% | +2.9 | -3.1 |
| temp: hot | 6 (thin) | 100% | 0% | 0% | 0% | 67% | 33% | 0% | -1.4 | -7.4 |
| temp: warm_hot | 41 | 71% | 29% | 0% | 0% | 73% | 27% | 0% | +2.3 | -3.7 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: light | 62 | +0.55\* / +0.58\* / +0.52\* | +1.3 / +1.4 / +1.2 | -1.1 / -1.2 / -1.3 | +0.052\* / +0.055\* / +0.054\* |
| wind: moderate | 43 | -0.01 / +0.01 / +0.15 | +0.0 / +1.2 / +1.7 | +2.2 / +1.2 / +1.3 | -0.030 / -0.026 / -0.022 |
| wind: windy | 32 | -1.05\* / -1.14\* / -1.16\* | -2.7 / -4.2\* / -4.4\* | -0.9 / +0.8 / +0.8 | -0.061\* / -0.073\* / -0.075\* |
| precip: none | 113 | +0.05 / +0.07 / +0.05 | +0.1 / +0.3 / +0.2 | -0.2 / -0.1 / -0.1 | +0.012 / +0.014\* / +0.013 |
| precip: light | 15 | +0.07 / +0.14 / +0.33 | -3.8 / -3.4 / -2.1 | +3.3 / +2.0 / +1.2 | -0.043 / -0.036 / -0.024 |
| precip: steady | 9 (thin) | -0.77 / -1.05 / -1.22 | +5.6 / +1.8 / +0.9 | -3.6 / -2.6 / -1.2 | -0.078 / -0.112 / -0.128 |
| precip: wet | 24 | -0.24 / -0.31 / -0.24 | -0.3 / -1.4 / -0.9 | +0.7 / +0.2 / +0.3 | -0.056 / -0.065\* / -0.061 |
| temp: cold | 21 | -0.56 / -0.25 / +0.01 | -1.8 / +1.5 / +2.1 | +2.7 / +1.9 / +0.1 | -0.016 / +0.019 / +0.034 |
| temp: mild | 75 | -0.24 / -0.22 / -0.16 | -1.9 / -1.7\* / -1.8\* | +1.0 / +0.6 / +0.1 | -0.037\* / -0.034\* / -0.033\* |
| temp: warm | 35 | +0.90\* / +0.74\* / +0.60 | +5.2\* / +3.6\* / +4.1\* | -3.4\* / -2.7\* / -1.1 | +0.085\* / +0.065\* / +0.070\* |
| temp: hot | 6 (thin) | -0.25 / -0.58 / -0.84 | -0.1 / -4.4 / -4.5 | -1.8 / +0.8 / +3.7 | +0.024 / -0.016 / -0.028 |
| temp: warm_hot | 41 | +0.73\* / +0.54\* / +0.42 | +4.4\* / +2.4 / +3.2\* | -3.2\* / -2.2\* / -0.3 | +0.076\* / +0.053\* / +0.064\* |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: light | 62 | +1.00\* / +1.08\* / +0.96\* | +2.5 / +2.5 / +2.3 | -2.0 / -2.3 / -2.3 | +0.096\* / +0.102\* / +0.100\* |
| wind: moderate | 43 | -0.01 / +0.02 / +0.21 | +0.1 / +1.7 / +2.4 | +3.2 / +1.8 / +1.8 | -0.044 / -0.037 / -0.032 |
| wind: windy | 32 | -1.37\* / -1.50\* / -1.52\* | -3.5 / -5.5\* / -5.8\* | -1.1 / +1.0 / +1.1 | -0.080\* / -0.096\* / -0.098\* |
| precip: none | 113 | +0.29 / +0.37 / +0.30 | +0.3 / +1.7 / +1.1 | -0.9 / -0.3 / -0.3 | +0.068 / +0.079\* / +0.074 |
| precip: light | 15 | +0.08 / +0.16 / +0.37 | -4.2 / -3.8 / -2.3 | +3.7 / +2.2 / +1.3 | -0.048 / -0.041 / -0.027 |
| precip: steady | 9 (thin) | -0.82 / -1.12 / -1.30 | +5.9 / +2.0 / +1.0 | -3.9 / -2.8 / -1.3 | -0.084 / -0.120 / -0.137 |
| precip: wet | 24 | -0.29 / -0.37 / -0.30 | -0.3 / -1.7 / -1.1 | +0.9 / +0.3 / +0.3 | -0.068 / -0.079\* / -0.074 |
| temp: cold | 21 | -0.66 / -0.29 / +0.01 | -2.1 / +1.8 / +2.5 | +3.2 / +2.3 / +0.1 | -0.019 / +0.022 / +0.041 |
| temp: mild | 75 | -0.54 / -0.49 / -0.35 | -4.3 / -3.8\* / -3.9\* | +2.2 / +1.4 / +0.2 | -0.082\* / -0.075\* / -0.073\* |
| temp: warm | 35 | +1.20\* / +0.98\* / +0.80 | +7.0\* / +4.8\* / +5.5\* | -4.6\* / -3.6\* / -1.5 | +0.114\* / +0.087\* / +0.094\* |
| temp: hot | 6 (thin) | -0.27 / -0.61 / -0.88 | -0.1 / -4.6 / -4.7 | -1.9 / +0.8 / +3.9 | +0.025 / -0.017 / -0.030 |
| temp: warm_hot | 41 | +1.04\* / +0.76\* / +0.59 | +6.3\* / +3.4 / +4.5\* | -4.5\* / -3.1\* / -0.5 | +0.109\* / +0.076\* / +0.091\* |

### USC

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 134 | 35% | 30% | 29% | 6% | 57% | 40% | 4% | +6.0 | +0.0 |
| wind: light | 91 | 32% | 29% | 31% | 9% | 58% | 36% | 5% | +5.6 | -0.4 |
| wind: moderate | 34 | 44% | 32% | 24% | 0% | 59% | 41% | 0% | +6.4 | +0.4 |
| wind: windy | 9 (thin) | 33% | 33% | 33% | 0% | 33% | 67% | 0% | +8.5 | +2.5 |
| precip: none | 126 | 35% | 30% | 29% | 6% | 58% | 38% | 4% | +5.6 | -0.4 |
| precip: light | 3 (suppressed) | 0% | 67% | 33% | 0% | 33% | 67% | 0% | +17.2 | +11.2 |
| precip: steady | 5 (thin) | 60% | 0% | 40% | 0% | 40% | 60% | 0% | +9.4 | +3.4 |
| precip: wet | 8 (thin) | 38% | 25% | 38% | 0% | 38% | 62% | 0% | +12.3 | +6.3 |
| temp: cold | 4 (suppressed) | 0% | 50% | 50% | 0% | 0% | 100% | 0% | +14.5 | +8.5 |
| temp: mild | 77 | 17% | 31% | 42% | 10% | 52% | 42% | 6% | +7.9 | +1.9 |
| temp: warm | 43 | 63% | 26% | 12% | 0% | 72% | 28% | 0% | +3.5 | -2.5 |
| temp: hot | 9 (thin) | 67% | 33% | 0% | 0% | 56% | 44% | 0% | -2.8 | -8.8 |
| temp: warm_hot | 52 | 63% | 27% | 10% | 0% | 69% | 31% | 0% | +2.4 | -3.6 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: light | 91 | +0.08 / +0.04 / +0.04 | +0.6 / +0.3 / +0.3 | -0.6 / -0.5 / -0.6 | +0.013 / +0.008 / +0.009 |
| wind: moderate | 34 | +0.17 / +0.17 / +0.14 | +0.5 / +0.5 / +0.0 | +1.9 / +1.5 / +1.9 | -0.013 / -0.013 / -0.019 |
| wind: windy | 9 (thin) | -1.48\* / -1.08\* / -0.97\* | -8.3\* / -4.4 / -3.3 | -1.4 / -0.2 / -1.0 | -0.081 / -0.029 / -0.012 |
| precip: none | 126 | +0.00 / -0.03 / -0.03 | +0.2 / -0.1 / -0.2 | +0.2 / +0.3\* / +0.3\* | +0.005\* / +0.002 / +0.001 |
| precip: light | 3 (suppressed) | — | — | — | — |
| precip: steady | 5 (thin) | +0.27 / +0.48 / +0.54 | +1.3 / +3.4 / +3.9 | -4.5 / -4.8\* / -4.7 | -0.023 / +0.005 / +0.018 |
| precip: wet | 8 (thin) | -0.03 / +0.42 / +0.55 | -2.5 / +1.9 / +2.8 | -3.0 / -4.2\* / -4.6\* | -0.084\* / -0.025 / -0.012 |
| temp: cold | 4 (suppressed) | — | — | — | — |
| temp: mild | 77 | -0.38\* / -0.26\* / -0.21 | -2.6\* / -1.3\* / -0.7 | +2.8\* / +2.3\* / +2.2\* | -0.026\* / -0.009 / +0.001 |
| temp: warm | 43 | +0.60\* / +0.42\* / +0.28 | +4.3\* / +2.4\* / +0.9 | -3.6\* / -3.1\* / -2.6\* | +0.041 / +0.016 / -0.008 |
| temp: hot | 9 (thin) | +0.90\* / +0.52 / +0.42 | +8.8\* / +5.1\* / +4.8\* | -5.1\* / -1.6 / -1.1 | +0.112\* / +0.062 / +0.056 |
| temp: warm_hot | 52 | +0.65\* / +0.44\* / +0.36 | +5.0\* / +2.9\* / +2.0 | -3.9\* / -2.8\* / -2.6\* | +0.053\* / +0.024 / +0.006 |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: light | 91 | +0.26 / +0.14 / +0.14 | +2.0 / +0.8 / +1.0 | -1.8 / -1.7 / -1.9 | +0.040 / +0.024 / +0.027 |
| wind: moderate | 34 | +0.23 / +0.23 / +0.19 | +0.6 / +0.6 / +0.0 | +2.5 / +2.0 / +2.6 | -0.017 / -0.017 / -0.026 |
| wind: windy | 9 (thin) | -1.58\* / -1.16\* / -1.04\* | -8.9\* / -4.8 / -3.5 | -1.5 / -0.2 / -1.0 | -0.087 / -0.031 / -0.013 |
| precip: none | 126 | +0.03 / -0.44 / -0.58 | +2.7 / -2.0 / -3.0 | +3.2 / +4.5\* / +4.9\* | +0.090\* / +0.027 / +0.013 |
| precip: light | 3 (suppressed) | — | — | — | — |
| precip: steady | 5 (thin) | +0.28 / +0.50 / +0.56 | +1.4 / +3.5 / +4.1 | -4.6 / -4.9\* / -4.9 | -0.024 / +0.005 / +0.019 |
| precip: wet | 8 (thin) | -0.03 / +0.44 / +0.58 | -2.7 / +2.0 / +3.0 | -3.2 / -4.5\* / -4.9\* | -0.090\* / -0.027 / -0.013 |
| temp: cold | 4 (suppressed) | — | — | — | — |
| temp: mild | 77 | -0.90\* / -0.60\* / -0.50 | -6.0\* / -3.1\* / -1.7 | +6.5\* / +5.3\* / +5.3\* | -0.061\* / -0.021 / +0.003 |
| temp: warm | 43 | +0.89\* / +0.62\* / +0.41 | +6.3\* / +3.6\* / +1.4 | -5.3\* / -4.5\* / -3.8\* | +0.060 / +0.024 / -0.011 |
| temp: hot | 9 (thin) | +0.96\* / +0.56 / +0.45 | +9.4\* / +5.4\* / +5.1\* | -5.5\* / -1.7 / -1.2 | +0.120\* / +0.066 / +0.060 |
| temp: warm_hot | 52 | +1.07\* / +0.71\* / +0.59 | +8.2\* / +4.7\* / +3.2 | -6.4\* / -4.6\* / -4.2\* | +0.087\* / +0.040 / +0.010 |

### Oregon

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 136 | 33% | 28% | 32% | 7% | 56% | 40% | 4% | +5.5 | +0.0 |
| wind: light | 80 | 25% | 30% | 38% | 8% | 56% | 40% | 4% | +6.9 | +1.4 |
| wind: moderate | 34 | 53% | 29% | 18% | 0% | 65% | 35% | 0% | +3.5 | -2.0 |
| wind: windy | 22 | 32% | 18% | 36% | 14% | 41% | 45% | 14% | +3.5 | -2.0 |
| precip: none | 122 | 35% | 27% | 30% | 7% | 57% | 39% | 5% | +5.6 | +0.1 |
| precip: light | 9 (thin) | 22% | 44% | 33% | 0% | 56% | 44% | 0% | +5.4 | -0.1 |
| precip: steady | 5 (thin) | 0% | 20% | 80% | 0% | 40% | 60% | 0% | +3.7 | -1.8 |
| precip: wet | 14 | 14% | 36% | 50% | 0% | 50% | 50% | 0% | +4.8 | -0.7 |
| temp: cold | 7 (thin) | 0% | 0% | 100% | 0% | 71% | 29% | 0% | +5.9 | +0.4 |
| temp: mild | 97 | 19% | 35% | 37% | 9% | 54% | 40% | 6% | +6.4 | +0.9 |
| temp: warm | 29 | 83% | 14% | 3% | 0% | 62% | 38% | 0% | +1.5 | -4.0 |
| temp: hot | 3 (suppressed) | 100% | 0% | 0% | 0% | 33% | 67% | 0% | +9.4 | +3.9 |
| temp: warm_hot | 32 | 84% | 12% | 3% | 0% | 59% | 41% | 0% | +2.1 | -3.4 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: light | 80 | -0.04 / -0.11 / -0.07 | +0.3 / -0.7 / -0.3 | +2.0\* / +1.0 / +1.3 | -0.003 / -0.013 / -0.010 |
| wind: moderate | 34 | +0.34 / +0.45 / +0.37 | +1.2 / +2.8 / +1.9 | -1.2 / +0.8 / -0.2 | +0.029 / +0.045 / +0.035 |
| wind: windy | 22 | -0.37 / -0.29 / -0.26 | -3.1 / -1.7 / -1.4 | -5.3\* / -4.5\* / -4.3\* | -0.035 / -0.021 / -0.014 |
| precip: none | 122 | +0.10\* / +0.12\* / +0.11 | +0.1 / +0.1 / +0.0 | +0.1 / +0.1 / +0.1 | +0.002 / +0.001 / +0.002 |
| precip: light | 9 (thin) | -0.25 / -0.40 / -0.22 | +0.4 / -0.6 / +0.4 | -2.2 / -2.8 / -3.4 | +0.016 / +0.012 / +0.016 |
| precip: steady | 5 (thin) | -2.07\* / -1.96\* / -2.05\* | -4.0 / -1.8 / -1.0 | +2.2 / +2.6 / +3.7 | -0.073 / -0.050 / -0.065 |
| precip: wet | 14 | -0.90\* / -1.00\* / -0.93 | -1.2 / -1.0 / -0.1 | -0.6 / -0.7 / -0.7 | -0.016 / -0.012 / -0.015 |
| temp: cold | 7 (thin) | +0.31 / +0.20 / -0.20 | -1.7 / -1.6 / -2.6 | -2.0 / -5.5 / -4.1 | +0.033 / +0.029 / +0.003 |
| temp: mild | 97 | -0.30\* / -0.21\* / -0.17 | -2.0\* / -0.5 / +0.0 | +0.6 / +0.0 / +0.5 | -0.036\* / -0.020\* / -0.016 |
| temp: warm | 29 | +1.04\* / +0.90\* / +0.98\* | +7.7\* / +2.9 / +1.2 | -1.9 / +1.1 / -0.9 | +0.129\* / +0.084\* / +0.089\* |
| temp: hot | 3 (suppressed) | — | — | — | — |
| temp: warm_hot | 32 | +0.84\* / +0.74\* / +0.84\* | +6.4\* / +2.5 / +0.8 | -1.4 / +1.5 / -0.5 | +0.103\* / +0.066\* / +0.069 |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: light | 80 | -0.11 / -0.25 / -0.17 | +0.8 / -1.7 / -0.8 | +4.8\* / +2.3 / +3.2 | -0.006 / -0.031 / -0.024 |
| wind: moderate | 34 | +0.45 / +0.59 / +0.49 | +1.7 / +3.7 / +2.5 | -1.6 / +1.1 / -0.2 | +0.039 / +0.059 / +0.046 |
| wind: windy | 22 | -0.44 / -0.35 / -0.32 | -3.7 / -2.1 / -1.7 | -6.3\* / -5.5\* / -5.2\* | -0.042 / -0.025 / -0.017 |
| precip: none | 122 | +1.00\* / +1.11\* / +1.04 | +1.3 / +1.2 / +0.1 | +0.7 / +0.8 / +0.8 | +0.017 / +0.013 / +0.017 |
| precip: light | 9 (thin) | -0.27 / -0.43 / -0.23 | +0.4 / -0.6 / +0.4 | -2.3 / -3.0 / -3.6 | +0.018 / +0.013 / +0.017 |
| precip: steady | 5 (thin) | -2.15\* / -2.04\* / -2.14\* | -4.2 / -1.9 / -1.0 | +2.2 / +2.7 / +3.9 | -0.076 / -0.052 / -0.067 |
| precip: wet | 14 | -1.00\* / -1.11\* / -1.04 | -1.3 / -1.2 / -0.1 | -0.7 / -0.8 / -0.8 | -0.017 / -0.013 / -0.017 |
| temp: cold | 7 (thin) | +0.33 / +0.22 / -0.21 | -1.8 / -1.7 / -2.8 | -2.1 / -5.8 / -4.3 | +0.035 / +0.031 / +0.004 |
| temp: mild | 97 | -1.05\* / -0.83\* / -0.66 | -6.9\* / -2.1 / +0.2 | +2.1 / +0.0 / +1.8 | -0.127\* / -0.078\* / -0.061 |
| temp: warm | 29 | +1.33\* / +1.10\* / +1.20\* | +9.8\* / +3.5 / +1.5 | -2.4 / +1.3 / -1.1 | +0.164\* / +0.103\* / +0.109\* |
| temp: hot | 3 (suppressed) | — | — | — | — |
| temp: warm_hot | 32 | +1.10\* / +0.92\* / +1.05\* | +8.3\* / +3.1 / +1.1 | -1.8 / +1.9 / -0.6 | +0.135\* / +0.082\* / +0.086 |

### Northwestern

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 140 | 29% | 32% | 34% | 4% | 48% | 40% | 12% | +6.5 | +0.0 |
| wind: light | 58 | 38% | 36% | 22% | 3% | 48% | 45% | 7% | +5.0 | -1.5 |
| wind: moderate | 48 | 31% | 23% | 40% | 6% | 46% | 42% | 12% | +8.4 | +1.9 |
| wind: windy | 34 | 12% | 38% | 47% | 3% | 50% | 29% | 21% | +6.5 | +0.0 |
| precip: none | 125 | 31% | 32% | 34% | 3% | 47% | 40% | 13% | +6.1 | -0.4 |
| precip: light | 12 | 8% | 33% | 42% | 17% | 42% | 50% | 8% | +11.4 | +4.9 |
| precip: steady | 3 (suppressed) | 33% | 33% | 33% | 0% | 100% | 0% | 0% | +1.5 | -5.0 |
| precip: wet | 15 | 13% | 33% | 40% | 13% | 53% | 40% | 7% | +9.4 | +2.9 |
| temp: cold | 18 | 0% | 6% | 78% | 17% | 28% | 50% | 22% | +8.3 | +1.8 |
| temp: mild | 84 | 18% | 42% | 39% | 1% | 46% | 44% | 10% | +7.6 | +1.1 |
| temp: warm | 33 | 67% | 24% | 3% | 6% | 64% | 21% | 15% | +4.0 | -2.5 |
| temp: hot | 5 (thin) | 80% | 20% | 0% | 0% | 40% | 60% | 0% | -3.4 | -9.9 |
| temp: warm_hot | 38 | 68% | 24% | 3% | 5% | 61% | 26% | 13% | +2.9 | -3.6 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: light | 58 | -0.01 / -0.08 / -0.09 | +0.3 / -0.4 / -0.3 | +0.3 / +0.2 / +0.0 | -0.003 / -0.011 / -0.008 |
| wind: moderate | 48 | +0.15 / +0.22 / +0.27 | -0.9 / +0.0 / +0.3 | +2.2 / +3.3\* / +3.4\* | -0.015 / -0.001 / +0.005 |
| wind: windy | 34 | -0.19 / -0.18 / -0.23 | +0.8 / +0.8 / +0.2 | -3.7\* / -5.0\* / -5.1\* | +0.025 / +0.023 / +0.008 |
| precip: none | 125 | +0.02 / -0.01 / -0.00 | -0.0 / -0.2 / -0.2 | +0.2 / +0.4 / +0.3 | +0.002 / -0.001 / -0.000 |
| precip: light | 12 | +0.00 / +0.20 / +0.18 | +1.2 / +2.9 / +2.3 | +0.2 / -2.0 / -1.6 | -0.004 / +0.025 / +0.017 |
| precip: steady | 3 (suppressed) | — | — | — | — |
| precip: wet | 15 | -0.14 / +0.06 / +0.00 | +0.1 / +1.9 / +1.4 | -1.9 / -3.1 / -2.2 | -0.021 / +0.011 / +0.001 |
| temp: cold | 18 | -0.28 / -0.14 / -0.07 | +0.4 / +1.5 / +1.7 | -2.3 / -3.3 / -3.6 | -0.020 / +0.001 / +0.004 |
| temp: mild | 84 | -0.02 / +0.02 / -0.00 | +0.1 / +0.6 / +0.3 | +1.1 / +0.8 / +0.8 | +0.002 / +0.015 / +0.006 |
| temp: warm | 33 | +0.34 / +0.26 / +0.33 | +0.2 / -1.2 / -0.6 | -0.3 / +0.8 / +1.3 | +0.013 / -0.024 / -0.007 |
| temp: hot | 5 (thin) | -0.97 / -1.33\* / -1.28\* | -4.4 / -8.1 / -6.9 | -7.2\* / -5.4\* / -7.5\* | -0.052 / -0.104 / -0.070 |
| temp: warm_hot | 38 | +0.17 / +0.02 / +0.06 | -0.4 / -2.3 / -2.0 | -1.2 / -0.1 / -0.3 | +0.005 / -0.036 / -0.021 |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: light | 58 | -0.02 / -0.13 / -0.15 | +0.4 / -0.8 / -0.5 | +0.6 / +0.3 / +0.0 | -0.005 / -0.020 / -0.015 |
| wind: moderate | 48 | +0.23 / +0.34 / +0.40 | -1.4 / +0.0 / +0.4 | +3.4 / +5.0\* / +5.1\* | -0.022 / -0.002 / +0.007 |
| wind: windy | 34 | -0.25 / -0.23 / -0.30 | +1.1 / +1.0 / +0.3 | -4.9\* / -6.6\* / -6.7\* | +0.033 / +0.030 / +0.011 |
| precip: none | 125 | +0.16 / -0.07 / -0.00 | -0.1 / -2.1 / -1.5 | +2.1 / +3.5 / +2.4 | +0.023 / -0.012 / -0.001 |
| precip: light | 12 | +0.00 / +0.22 / +0.20 | +1.3 / +3.2 / +2.5 | +0.2 / -2.3 / -1.7 | -0.005 / +0.028 / +0.019 |
| precip: steady | 3 (suppressed) | — | — | — | — |
| precip: wet | 15 | -0.16 / +0.07 / +0.00 | +0.1 / +2.1 / +1.5 | -2.1 / -3.5 / -2.4 | -0.023 / +0.012 / +0.001 |
| temp: cold | 18 | -0.32 / -0.17 / -0.08 | +0.4 / +1.7 / +2.0 | -2.6 / -3.9 / -4.2 | -0.023 / +0.002 / +0.004 |
| temp: mild | 84 | -0.04 / +0.06 / -0.01 | +0.3 / +1.5 / +0.8 | +2.6 / +2.1 / +2.2 | +0.006 / +0.038 / +0.016 |
| temp: warm | 33 | +0.45 / +0.33 / +0.42 | +0.3 / -1.6 / -0.8 | -0.5 / +1.0 / +1.6 | +0.017 / -0.031 / -0.009 |
| temp: hot | 5 (thin) | -1.00 / -1.38\* / -1.33\* | -4.5 / -8.4 / -7.1 | -7.4\* / -5.6\* / -7.8\* | -0.054 / -0.108 / -0.073 |
| temp: warm_hot | 38 | +0.23 / +0.03 / +0.07 | -0.5 / -3.0 / -2.6 | -1.7 / -0.2 / -0.4 | +0.006 / -0.049 / -0.028 |

### Nebraska

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 141 | 34% | 30% | 32% | 4% | 57% | 40% | 3% | +6.1 | +0.0 |
| wind: light | 54 | 28% | 30% | 33% | 9% | 37% | 56% | 7% | +6.4 | +0.4 |
| wind: moderate | 38 | 47% | 24% | 29% | 0% | 63% | 37% | 0% | +4.1 | -1.9 |
| wind: windy | 49 | 31% | 35% | 33% | 2% | 73% | 27% | 0% | +7.1 | +1.0 |
| precip: none | 129 | 36% | 30% | 30% | 4% | 58% | 40% | 2% | +6.2 | +0.1 |
| precip: light | 12 | 17% | 25% | 50% | 8% | 42% | 50% | 8% | +5.2 | -0.9 |
| precip: wet | 12 | 17% | 25% | 50% | 8% | 42% | 50% | 8% | +5.2 | -0.9 |
| temp: cold | 19 | 0% | 16% | 74% | 11% | 53% | 47% | 0% | +10.6 | +4.5 |
| temp: mild | 74 | 18% | 36% | 41% | 5% | 46% | 50% | 4% | +7.5 | +1.4 |
| temp: warm | 33 | 70% | 27% | 3% | 0% | 76% | 21% | 3% | +0.6 | -5.5 |
| temp: hot | 15 | 80% | 20% | 0% | 0% | 73% | 27% | 0% | +4.0 | -2.0 |
| temp: warm_hot | 48 | 73% | 25% | 2% | 0% | 75% | 23% | 2% | +1.7 | -4.4 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: light | 54 | +0.18 / +0.31 / +0.37 | -0.1 / +0.9 / +1.8 | +2.3 / +1.3 / +1.3 | +0.003 / +0.018 / +0.027 |
| wind: moderate | 38 | -0.01 / -0.29 / -0.31 | +3.4\* / +1.2 / +1.2 | -1.3 / -0.3 / -0.4 | +0.018 / -0.009 / -0.015 |
| wind: windy | 49 | -0.20 / -0.15 / -0.18 | -2.6\* / -2.0\* / -3.0\* | -1.5 / -1.3 / -1.2 | -0.017 / -0.014 / -0.018 |
| precip: none | 129 | +0.09 / +0.07 / +0.06 | +0.1 / -0.0 / -0.1 | +0.6\* / +0.6\* / +0.6\* | -0.001 / -0.003 / -0.004 |
| precip: light | 12 | -0.91 / -0.71 / -0.63 | -1.4 / +0.2 / +0.8 | -6.3\* / -5.8\* / -6.3\* | +0.008 / +0.029 / +0.037 |
| precip: wet | 12 | -0.91 / -0.71 / -0.63 | -1.4 / +0.2 / +0.8 | -6.3\* / -5.8\* / -6.3\* | +0.008 / +0.029 / +0.037 |
| temp: cold | 19 | -1.24\* / -0.78\* / -0.65 | -7.2\* / -3.3 / -3.6 | +0.6 / -1.1 / -1.4 | -0.064 / -0.020 / -0.018 |
| temp: mild | 74 | -0.04 / +0.18 / +0.21 | -0.2 / +1.3 / +1.8\* | +2.0\* / +1.0 / +0.8 | -0.003 / +0.017 / +0.028\* |
| temp: warm | 33 | +0.35 / -0.21 / -0.42 | +3.8\* / -0.4 / -1.3 | -3.5\* / -0.7 / -0.1 | +0.019 / -0.040 / -0.065\* |
| temp: hot | 15 | +1.00 / +0.57 / +0.55 | +2.0 / -1.6 / -2.4 | -2.9 / -2.3 / -1.9 | +0.054 / +0.021 / +0.004 |
| temp: warm_hot | 48 | +0.55\* / +0.04 / -0.11 | +3.2\* / -0.8 / -2.2 | -3.3\* / -1.2 / -1.0 | +0.030 / -0.020 / -0.056\* |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: light | 54 | +0.30 / +0.52 / +0.62 | -0.1 / +1.6 / +3.0 | +3.8 / +2.2 / +2.1 | +0.004 / +0.029 / +0.044 |
| wind: moderate | 38 | -0.01 / -0.40 / -0.41 | +4.7\* / +1.7 / +1.6 | -1.8 / -0.4 / -0.5 | +0.024 / -0.012 / -0.021 |
| wind: windy | 49 | -0.30 / -0.22 / -0.28 | -4.0\* / -3.1\* / -4.6\* | -2.4 / -2.0 / -1.8 | -0.026 / -0.021 / -0.028 |
| precip: none | 129 | +1.00 / +0.78 / +0.70 | +1.5 / -0.2 / -0.9 | +6.9\* / +6.3\* / +6.9\* | -0.009 / -0.032 / -0.040 |
| precip: light | 12 | -1.00 / -0.78 / -0.70 | -1.5 / +0.2 / +0.9 | -6.9\* / -6.3\* / -6.9\* | +0.009 / +0.032 / +0.040 |
| precip: wet | 12 | -1.00 / -0.78 / -0.70 | -1.5 / +0.2 / +0.9 | -6.9\* / -6.3\* / -6.9\* | +0.009 / +0.032 / +0.040 |
| temp: cold | 19 | -1.43\* / -0.90\* / -0.75 | -8.3\* / -3.9 / -4.2 | +0.7 / -1.3 / -1.7 | -0.074 / -0.024 / -0.021 |
| temp: mild | 74 | -0.09 / +0.39 / +0.45 | -0.5 / +2.8 / +4.0\* | +4.2\* / +2.2 / +1.7 | -0.006 / +0.037 / +0.060\* |
| temp: warm | 33 | +0.46 / -0.27 / -0.53 | +4.9\* / -0.5 / -1.6 | -4.5\* / -0.9 / -0.2 | +0.024 / -0.051 / -0.083\* |
| temp: hot | 15 | +1.12 / +0.63 / +0.61 | +2.2 / -1.8 / -2.7 | -3.3 / -2.6 / -2.1 | +0.060 / +0.024 / +0.004 |
| temp: warm_hot | 48 | +0.84\* / +0.06 / -0.16 | +4.8\* / -1.1 / -3.3 | -5.0\* / -1.8 / -1.5 | +0.045 / -0.030 / -0.081\* |

### Michigan

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 139 | 32% | 29% | 34% | 5% | 57% | 37% | 6% | +6.4 | +0.0 |
| wind: light | 65 | 32% | 29% | 35% | 3% | 49% | 48% | 3% | +4.5 | -1.9 |
| wind: moderate | 38 | 32% | 21% | 39% | 8% | 71% | 21% | 8% | +8.6 | +2.2 |
| wind: windy | 30 | 23% | 40% | 30% | 7% | 47% | 43% | 10% | +7.8 | +1.4 |
| precip: none | 123 | 33% | 29% | 33% | 4% | 54% | 41% | 5% | +6.0 | -0.4 |
| precip: light | 10 | 10% | 20% | 60% | 10% | 80% | 10% | 10% | +7.4 | +1.0 |
| precip: steady | 6 (thin) | 33% | 50% | 0% | 17% | 67% | 17% | 17% | +12.7 | +6.3 |
| precip: wet | 16 | 19% | 31% | 38% | 12% | 75% | 12% | 12% | +9.4 | +3.0 |
| temp: cold | 24 | 0% | 17% | 83% | 0% | 67% | 33% | 0% | +10.7 | +4.3 |
| temp: mild | 73 | 25% | 34% | 36% | 5% | 51% | 42% | 7% | +5.9 | -0.5 |
| temp: warm | 32 | 59% | 28% | 3% | 9% | 59% | 31% | 9% | +4.9 | -1.5 |
| temp: hot | 4 (suppressed) | 75% | 25% | 0% | 0% | 25% | 75% | 0% | +3.2 | -3.2 |
| temp: warm_hot | 36 | 61% | 28% | 3% | 8% | 56% | 36% | 8% | +4.7 | -1.7 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: light | 65 | +0.20 / +0.07 / +0.09 | +1.7 / +0.6 / +0.6 | -0.9 / -0.3 / -0.7 | +0.035\* / +0.019 / +0.023 |
| wind: moderate | 38 | +0.29 / +0.24 / +0.23 | +1.9 / +1.5 / +1.5 | +3.5\* / +1.1 / +2.0 | +0.018 / +0.012 / +0.010 |
| wind: windy | 30 | -0.72\* / -0.45 / -0.42 | -4.2\* / -1.8 / -1.8 | -2.0 / -0.9 / -1.3 | -0.087\* / -0.053 / -0.052 |
| precip: none | 123 | +0.07 / +0.03 / +0.03 | +0.3 / -0.0 / -0.0 | +0.2 / +0.2 / +0.1 | +0.008 / +0.003 / +0.004 |
| precip: light | 10 | -0.49 / -0.45 / -0.51 | -2.0 / -1.6 / -2.1 | +0.2 / -0.6 / -0.1 | -0.014 / -0.009 / -0.012 |
| precip: steady | 6 (thin) | -0.58 / +0.10 / +0.17 | -2.5 / +3.4 / +4.1 | -3.7 / -3.2 / -2.2 | -0.136\* / -0.049 / -0.056 |
| precip: wet | 16 | -0.53 / -0.24 / -0.25 | -2.2 / +0.3 / +0.2 | -1.2 / -1.6 / -0.9 | -0.060 / -0.024 / -0.029 |
| temp: cold | 24 | -0.29 / -0.02 / -0.15 | -4.8\* / -2.4 / -4.1\* | -0.1 / -1.6 / -2.8 | -0.035 / -0.001 / -0.010 |
| temp: mild | 73 | -0.18 / -0.26 / -0.23 | +1.7 / +1.0 / +1.1 | +1.0 / +0.6 / +0.4 | -0.004 / -0.014 / -0.011 |
| temp: warm | 32 | +0.58 / +0.46 / +0.58 | +1.9 / +0.9 / +1.4 | -0.9 / -0.3 / +0.4 | +0.045 / +0.029 / +0.036 |
| temp: hot | 4 (suppressed) | — | — | — | — |
| temp: warm_hot | 36 | +0.61 / +0.55 / +0.72\* | +1.4 / +0.8 / +1.4 | -1.4 / -0.2 / +0.2 | +0.041 / +0.032 / +0.042 |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: light | 65 | +0.37 / +0.13 / +0.17 | +3.2 / +1.1 / +1.2 | -1.6 / -0.5 / -1.3 | +0.066\* / +0.035 / +0.043 |
| wind: moderate | 38 | +0.39 / +0.33 / +0.32 | +2.7 / +2.1 / +2.1 | +4.8\* / +1.5 / +2.7 | +0.024 / +0.016 / +0.014 |
| wind: windy | 30 | -0.92\* / -0.58 / -0.54 | -5.3\* / -2.3 / -2.3 | -2.5 / -1.1 / -1.7 | -0.111\* / -0.067 / -0.066 |
| precip: none | 123 | +0.60 / +0.28 / +0.28 | +2.5 / -0.3 / -0.3 | +1.4 / +1.8 / +1.1 | +0.068 / +0.027 / +0.032 |
| precip: light | 10 | -0.53 / -0.49 / -0.55 | -2.1 / -1.7 / -2.2 | +0.3 / -0.7 / -0.1 | -0.016 / -0.010 / -0.013 |
| precip: steady | 6 (thin) | -0.61 / +0.11 / +0.18 | -2.6 / +3.6 / +4.3 | -3.9 / -3.4 / -2.3 | -0.142\* / -0.051 / -0.059 |
| precip: wet | 16 | -0.60 / -0.28 / -0.28 | -2.5 / +0.3 / +0.3 | -1.4 / -1.8 / -1.1 | -0.068 / -0.027 / -0.032 |
| temp: cold | 24 | -0.35 / -0.02 / -0.18 | -5.8\* / -2.9 / -5.0\* | -0.1 / -2.0 / -3.4 | -0.043 / -0.001 / -0.012 |
| temp: mild | 73 | -0.38 / -0.55 / -0.49 | +3.6 / +2.1 / +2.3 | +2.0 / +1.3 / +0.9 | -0.007 / -0.030 / -0.022 |
| temp: warm | 32 | +0.76 / +0.60 / +0.75 | +2.5 / +1.1 / +1.8 | -1.1 / -0.4 / +0.5 | +0.058 / +0.038 / +0.047 |
| temp: hot | 4 (suppressed) | — | — | — | — |
| temp: warm_hot | 36 | +0.83 / +0.74 / +0.97\* | +1.9 / +1.1 / +1.9 | -1.8 / -0.3 / +0.3 | +0.055 / +0.043 / +0.057 |

## Snow games

Snow is not split into delta rows (too few games). These are the games where an observation in the kickoff-to-+3.5h window reported a snow weather code. A code can mean flurries, so read the precipitation and temperature columns.

| Date | Game | Venue | Observed in window | Score |
|---|---|---|---|---|
| 2016-11-19 | Ohio State @ Michigan State | Spartan Stadium | 34°F, wind 22 mph (gust 35), precip 0.00 in, vis 4.0 mi | Ohio State 17, Michigan State 16 |
| 2016-11-19 | Indiana @ Michigan | Michigan Stadium | 33°F, wind 24 mph (gust 29), precip 0.01 in, vis 1.0 mi | Indiana 10, Michigan 20 |
| 2017-11-18 | Minnesota @ Northwestern | Ryan Field | 36°F, wind 16 mph (gust 25), precip 0.10 in, vis 2.0 mi | Minnesota 0, Northwestern 39 |
| 2018-11-17 | Michigan State @ Nebraska | Memorial Stadium (Lincoln, NE) | 26°F, wind 26 mph (gust 36), precip 0.01 in, vis 1.8 mi | Michigan State 6, Nebraska 9 |
| 2019-10-12 | Nebraska @ Minnesota | Huntington Bank Stadium | 36°F, wind 17 mph (gust 35), precip 0.01 in, vis 9.0 mi | Nebraska 7, Minnesota 34 |
| 2021-11-27 | Ohio State @ Michigan | Michigan Stadium | 28°F, wind 10 mph, precip 0.01 in, vis 0.8 mi | Ohio State 27, Michigan 42 |
| 2022-11-12 | Indiana @ Ohio State | Ohio Stadium | 36°F, wind 10 mph, precip 0.03 in, vis 1.5 mi | Indiana 14, Ohio State 56 |
| 2022-11-12 | Northwestern @ Minnesota | Huntington Bank Stadium | 28°F, wind 14 mph (gust 24), precip 0.00 in, vis 9.0 mi | Northwestern 3, Minnesota 31 |
| 2022-11-12 | Nebraska @ Michigan | Michigan Stadium | 34°F, wind 7 mph, precip 0.02 in, vis 1.0 mi | Nebraska 3, Michigan 34 |
| 2025-11-29 | Ohio State @ Michigan | Michigan Stadium | 28°F, wind 13 mph, precip 0.01 in, vis 0.8 mi | Ohio State 27, Michigan 9 |
| 2025-11-29 | Northwestern @ Illinois | Memorial Stadium (Champaign, IL) | 33°F, wind 28 mph (gust 44), precip 0.06 in, vis 0.5 mi | Northwestern 13, Illinois 20 |

