# Milestone 3: scaled splits, controlled model, evidence tiers

_Generated 2026-11-15 14:45 UTC._

> **EXPLORATORY.** This report tests many team × bin × metric cells. At a 90% level roughly 1 in 10 intervals will exclude zero by luck alone, so a starred (\*) delta or a "leans" tier is a lead to check, not a finding.

**Two yardsticks, always labelled.** *A. vs the team's overall average* compares a bin to all of the team's games, including the bin itself. *B. vs all other games* compares the bin to the games NOT in it ("windy vs not windy"); it is the A number divided by (1 − the bin's share of games). Evidence tiers use the controlled model, where the choice of yardstick does not change the verdict.

**Teams loaded (6):** Michigan, Nebraska, Northwestern, Ohio State, Oregon, USC. **Deferred by choice (7):** Ball State, Texas, Kent State, Illinois, Iowa, Maryland, Indiana -- not loaded (their 2026 games are already played, so they only matter for the Team Explorer); nothing here depends on them.

## Plain-language summary

- **Wind (windy vs not)** -- pooled across 6 teams, controlled for opponent, month and home/away: Pass yds/att -0.51 yds/att [-0.76, -0.26] (interval excludes zero); Points scored -2.2 pts [-3.5, -0.9] (interval excludes zero); Offensive PPA/play -0.032 PPA [-0.053, -0.011] (interval excludes zero). Clear evidence for: Ohio State. Leans: Michigan, Nebraska, USC.
- **Wet (light + steady rain)** -- pooled across 6 teams, controlled for opponent, month and home/away: Pass yds/att -0.35 yds/att [-0.70, +0.04] (interval spans zero); Points scored -0.0 pts [-1.8, +1.9] (interval spans zero); Offensive PPA/play -0.027 PPA [-0.057, +0.007] (interval spans zero). No team clears the bar. Leans: Ohio State.
- **Warm/hot (70°F and up)** -- pooled across 6 teams, controlled for opponent, month and home/away: Pass yds/att +0.35 yds/att [+0.12, +0.58] (interval excludes zero); Points scored +0.9 pts [-0.3, +2.2] (interval spans zero); Offensive PPA/play +0.014 PPA [-0.006, +0.035] (interval spans zero). No team clears the bar. Leans: Ohio State, Oregon.
- **Cold (39°F and below)** -- pooled across 6 teams, controlled for opponent, month and home/away: Pass yds/att -0.12 yds/att [-0.47, +0.24] (interval spans zero); Points scored -0.8 pts [-2.7, +1.1] (interval spans zero); Offensive PPA/play +0.011 PPA [-0.019, +0.043] (interval spans zero). No team clears the bar. 

Temperature: the controlled model finds no clear temperature effect for Michigan, Nebraska, Northwestern, USC, so their temperature results are labelled context-only; it still shows one (kept as is) for Ohio State, Oregon.

_Exploratory: tiers and stars are leads to check, not findings._

## CFBD call budget

- Month (2026-11) total so far: **18** of the 600-call cap (free-tier limit 1000); **982** calls remain before CFBD itself would stop us. CFBD's own `/info` count is the source of truth, and `/info` is not billed.
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
| wind: windy | Pass yds/att | 95 | -0.69 [-1.02, -0.36] \* | 174 | -0.51 [-0.76, -0.26] \* |
| wind: windy | Points scored | 95 | -2.0 [-3.7, -0.1] \* | 174 | -2.2 [-3.5, -0.9] \* |
| wind: windy | Points allowed (defense) | 95 | -3.0 [-4.6, -1.6] \* | 174 | -2.2 [-3.3, -1.1] \* |
| wind: windy | Offensive PPA/play | 95 | -0.028 [-0.057, +0.001] | 174 | -0.032 [-0.053, -0.011] \* |
| precip: wet | Pass yds/att | 58 | -0.27 [-0.71, +0.19] | 87 | -0.35 [-0.70, +0.04] |
| precip: wet | Points scored | 58 | +0.5 [-1.9, +3.0] | 87 | -0.0 [-1.8, +1.9] |
| precip: wet | Points allowed (defense) | 58 | -1.7 [-3.5, +0.5] | 87 | -2.4 [-3.8, -0.8] \* |
| precip: wet | Offensive PPA/play | 58 | -0.032 [-0.071, +0.006] | 87 | -0.027 [-0.057, +0.007] |
| precip: steady | Pass yds/att | 22 | -0.91 [-1.67, -0.11] \* | 28 | -0.74 [-1.44, -0.04] \* |
| precip: steady | Points scored | 22 | +0.4 [-4.1, +4.8] | 28 | +1.0 [-3.0, +5.0] |
| precip: steady | Points allowed (defense) | 22 | -2.0 [-5.6, +1.6] | 28 | -2.1 [-5.1, +0.9] |
| precip: steady | Offensive PPA/play | 22 | -0.073 [-0.147, -0.006] \* | 28 | -0.074 [-0.132, -0.015] \* |
| temp: cold | Pass yds/att | 50 | +0.08 [-0.34, +0.51] | 93 | -0.12 [-0.47, +0.24] |
| temp: cold | Points scored | 50 | +1.6 [-1.0, +4.3] | 93 | -0.8 [-2.7, +1.1] |
| temp: cold | Points allowed (defense) | 50 | -2.0 [-4.5, +0.6] | 93 | -2.2 [-4.0, -0.5] \* |
| temp: cold | Offensive PPA/play | 50 | +0.029 [-0.013, +0.068] | 93 | +0.011 [-0.019, +0.043] |
| temp: warm_hot | Pass yds/att | 163 | +0.41 [+0.13, +0.69] \* | 247 | +0.35 [+0.12, +0.58] \* |
| temp: warm_hot | Points scored | 163 | +1.4 [-0.1, +2.8] | 247 | +0.9 [-0.3, +2.2] |
| temp: warm_hot | Points allowed (defense) | 163 | -1.3 [-2.6, +0.0] | 247 | -0.9 [-1.9, +0.2] |
| temp: warm_hot | Offensive PPA/play | 163 | +0.029 [+0.005, +0.054] \* | 247 | +0.014 [-0.006, +0.035] |

## 2026 Ohio State schedule

10 played, 2 remaining. Team list = Ohio State + every opponent below (13 teams, from `config/opponents.yaml`).

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
| 12 | Nov 21 | Nebraska | away | Memorial Stadium (Lincoln, NE) | **remaining** |
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
| Ohio State | **CLEAR** (62) | none (41) | **CLEAR** (31) | leans (111) | none (14) | leans (9) | leans (23) | none (21) | leans (73) | leans (34) | n/a (6) | leans (40) |
| USC | none (90) | none (34) | leans (9) | none (125) | n/a (3) | n/a (5) | n/a (8) | n/a (4) | context (76) | context (43) | n/a (9) | context (52) |
| Oregon | none (72) | none (31) | none (21) | none (111) | n/a (8) | leans (5) | none (13) | n/a (7) | leans (92) | **CLEAR** (23) | n/a (2) | leans (25) |
| Northwestern | none (57) | none (43) | none (31) | none (116) | none (12) | n/a (3) | none (15) | context (18) | context (80) | context (28) | context (5) | context (33) |
| Nebraska | leans (54) | none (35) | none (45) | none (123) | none (11) | n/a (0) | none (11) | context (19) | context (72) | context (29) | context (14) | context (43) |
| Michigan | none (64) | none (38) | leans (30) | none (122) | none (10) | n/a (6) | none (16) | context (24) | context (72) | context (32) | n/a (4) | context (36) |
| Pooled (6 teams) | **CLEAR** (399) | none (222) | **CLEAR** (167) | leans (708) | none (58) | **CLEAR** (28) | leans (86) | context (93) | context (465) | context (189) | context (40) | context (229) |

### Scoring

| Team | wind:<br>calm | wind:<br>moderate | wind:<br>windy | precip:<br>none | precip:<br>light | precip:<br>steady | precip:<br>wet | temp:<br>cold | temp:<br>mild | temp:<br>warm | temp:<br>hot | temp:<br>warm_hot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ohio State | leans (62) | none (41) | **CLEAR** (31) | none (111) | none (14) | n/a (9) | none (23) | none (21) | leans (73) | **CLEAR** (34) | n/a (6) | leans (40) |
| USC | none (90) | none (34) | n/a (9) | none (125) | n/a (3) | n/a (5) | n/a (8) | n/a (4) | context (76) | context (43) | context (9) | context (52) |
| Oregon | none (72) | leans (31) | none (21) | none (111) | n/a (8) | n/a (5) | none (13) | n/a (7) | none (92) | leans (23) | n/a (2) | none (25) |
| Northwestern | none (57) | none (43) | none (31) | none (116) | none (12) | n/a (3) | none (15) | context (18) | context (80) | context (28) | context (5) | context (33) |
| Nebraska | leans (54) | none (35) | leans (45) | none (123) | none (11) | n/a (0) | none (11) | context (19) | context (72) | context (29) | context (14) | context (43) |
| Michigan | leans (64) | none (38) | leans (30) | none (122) | none (10) | n/a (6) | none (16) | context (24) | context (72) | context (32) | n/a (4) | context (36) |
| Pooled (6 teams) | leans (399) | none (222) | **CLEAR** (167) | none (708) | none (58) | none (28) | none (86) | context (93) | context (465) | context (189) | context (40) | context (229) |

**Temperature:** a team's temperature tiers are kept as they are only if its controlled model has at least one CLEAR temperature cell; otherwise they are labelled context-only. Kept: Ohio State, Oregon. Context-only: Michigan, Nebraska, Northwestern, USC, Pooled (6 teams).

## Pooled reference line (all 6 loaded teams together)

Every team-game from the **6 teams** in the pool, each measured against its own team's baseline. Raw / Adjusted / Controlled as defined above; brackets are 90% intervals from a bootstrap over whole games. The same numbers are shown on two yardsticks; **steady** rain is kept as its own bin next to the merged **wet** bin.

### A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)

**wind** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | Pass yds/att | 407 | +0.16 [+0.03, +0.29] \* | +0.13 [+0.01, +0.26] \* | +0.16 [+0.03, +0.28] \* |
| wind: calm | Points scored | 407 | +0.7 [-0.1, +1.5] | +0.3 [-0.4, +0.9] | +0.4 [-0.3, +1.1] |
| wind: calm | Points allowed (defense) | 407 | +0.4 [-0.3, +1.1] | +0.1 [-0.5, +0.7] | +0.0 [-0.6, +0.6] |
| wind: calm | Offensive PPA/play | 407 | +0.017 [+0.005, +0.029] \* | +0.013 [+0.002, +0.023] \* | +0.016 [+0.006, +0.027] \* |
| wind: moderate | Pass yds/att | 234 | +0.14 [-0.06, +0.35] | +0.13 [-0.06, +0.31] | +0.12 [-0.07, +0.32] |
| wind: moderate | Points scored | 234 | +0.9 [-0.3, +2.2] | +1.2 [+0.2, +2.2] \* | +1.1 [+0.0, +2.1] \* |
| wind: moderate | Points allowed (defense) | 234 | +1.3 [+0.1, +2.5] \* | +1.4 [+0.4, +2.3] \* | +1.5 [+0.5, +2.5] \* |
| wind: moderate | Offensive PPA/play | 234 | -0.001 [-0.020, +0.018] | -0.000 [-0.017, +0.016] | -0.004 [-0.021, +0.012] |
| wind: windy | Pass yds/att | 174 | -0.54 [-0.78, -0.29] \* | -0.48 [-0.73, -0.24] \* | -0.51 [-0.76, -0.26] \* |
| wind: windy | Points scored | 174 | -2.6 [-4.1, -1.0] \* | -2.0 [-3.2, -0.8] \* | -2.2 [-3.5, -0.9] \* |
| wind: windy | Points allowed (defense) | 174 | -2.5 [-3.7, -1.2] \* | -2.0 [-3.0, -0.9] \* | -2.2 [-3.3, -1.1] \* |
| wind: windy | Offensive PPA/play | 174 | -0.036 [-0.059, -0.013] \* | -0.029 [-0.049, -0.008] \* | -0.032 [-0.053, -0.011] \* |

**precip** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| precip: none | Pass yds/att | 734 | +0.06 [+0.01, +0.10] \* | +0.04 [-0.00, +0.09] | +0.04 [-0.00, +0.08] |
| precip: none | Points scored | 734 | +0.1 [-0.2, +0.4] | +0.0 [-0.2, +0.2] | +0.0 [-0.2, +0.2] |
| precip: none | Points allowed (defense) | 734 | +0.2 [+0.0, +0.4] \* | +0.3 [+0.1, +0.4] \* | +0.3 [+0.1, +0.5] \* |
| precip: none | Offensive PPA/play | 734 | +0.005 [+0.001, +0.009] \* | +0.003 [-0.001, +0.007] | +0.003 [-0.001, +0.007] |
| precip: light | Pass yds/att | 59 | -0.32 [-0.81, +0.19] | -0.22 [-0.68, +0.25] | -0.16 [-0.61, +0.29] |
| precip: light | Points scored | 59 | -1.6 [-4.2, +1.1] | -0.8 [-2.7, +1.3] | -0.5 [-2.6, +1.6] |
| precip: light | Points allowed (defense) | 59 | -1.0 [-3.3, +1.4] | -1.9 [-3.6, -0.2] \* | -2.5 [-4.2, -0.6] \* |
| precip: light | Offensive PPA/play | 59 | -0.023 [-0.067, +0.023] | -0.008 [-0.047, +0.032] | -0.004 [-0.043, +0.036] |
| precip: steady | Pass yds/att | 28 | -0.77 [-1.50, -0.06] \* | -0.63 [-1.30, +0.05] | -0.74 [-1.44, -0.04] \* |
| precip: steady | Points scored | 28 | +0.3 [-4.8, +5.5] | +1.4 [-2.5, +5.5] | +1.0 [-3.0, +5.0] |
| precip: steady | Points allowed (defense) | 28 | -3.5 [-6.3, -0.6] \* | -2.6 [-5.7, +0.3] | -2.1 [-5.1, +0.9] |
| precip: steady | Offensive PPA/play | 28 | -0.081 [-0.143, -0.017] \* | -0.059 [-0.116, -0.004] \* | -0.074 [-0.132, -0.015] \* |
| precip: wet | Pass yds/att | 87 | -0.47 [-0.86, -0.05] \* | -0.35 [-0.71, +0.02] | -0.35 [-0.70, +0.04] |
| precip: wet | Points scored | 87 | -1.0 [-3.4, +1.5] | -0.1 [-1.8, +1.8] | -0.0 [-1.8, +1.9] |
| precip: wet | Points allowed (defense) | 87 | -1.8 [-3.5, -0.0] \* | -2.1 [-3.5, -0.7] \* | -2.4 [-3.8, -0.8] \* |
| precip: wet | Offensive PPA/play | 87 | -0.042 [-0.077, -0.006] \* | -0.024 [-0.055, +0.008] | -0.027 [-0.057, +0.007] |

**temp** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| temp: cold | Pass yds/att | 93 | -0.51 [-0.86, -0.17] \* | -0.23 [-0.58, +0.10] | -0.12 [-0.47, +0.24] |
| temp: cold | Points scored | 93 | -3.6 [-5.8, -1.3] \* | -1.0 [-2.8, +0.9] | -0.8 [-2.7, +1.1] |
| temp: cold | Points allowed (defense) | 93 | +0.1 [-1.9, +2.2] | -1.4 [-3.1, +0.1] | -2.2 [-4.0, -0.5] \* |
| temp: cold | Offensive PPA/play | 93 | -0.032 [-0.065, +0.000] | +0.001 [-0.029, +0.030] | +0.011 [-0.019, +0.043] |
| temp: mild | Pass yds/att | 474 | -0.20 [-0.31, -0.08] \* | -0.13 [-0.23, -0.03] \* | -0.10 [-0.22, +0.01] |
| temp: mild | Points scored | 474 | -0.9 [-1.6, -0.2] \* | -0.1 [-0.7, +0.4] | +0.0 [-0.6, +0.6] |
| temp: mild | Points allowed (defense) | 474 | +1.4 [+0.8, +2.0] \* | +0.9 [+0.4, +1.4] \* | +0.8 [+0.3, +1.3] \* |
| temp: mild | Offensive PPA/play | 474 | -0.018 [-0.028, -0.008] \* | -0.008 [-0.017, +0.001] | -0.006 [-0.017, +0.004] |
| temp: warm_hot | Pass yds/att | 247 | +0.59 [+0.38, +0.80] \* | +0.37 [+0.18, +0.56] \* | +0.35 [+0.12, +0.58] \* |
| temp: warm_hot | Points scored | 247 | +3.4 [+2.1, +4.7] \* | +1.0 [-0.0, +2.1] | +0.9 [-0.3, +2.2] |
| temp: warm_hot | Points allowed (defense) | 247 | -2.6 [-3.6, -1.6] \* | -1.2 [-2.1, -0.3] \* | -0.9 [-1.9, +0.2] |
| temp: warm_hot | Offensive PPA/play | 247 | +0.050 [+0.031, +0.069] \* | +0.018 [+0.002, +0.035] \* | +0.014 [-0.006, +0.035] |

### B. vs ALL OTHER GAMES (the complement: games not in the bin)

**wind** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | Pass yds/att | 407 | +0.31 [+0.06, +0.57] \* | +0.26 [+0.03, +0.52] \* | +0.31 [+0.06, +0.57] \* |
| wind: calm | Points scored | 407 | +1.4 [-0.1, +3.0] | +0.6 [-0.7, +1.9] | +0.9 [-0.5, +2.2] |
| wind: calm | Points allowed (defense) | 407 | +0.7 [-0.6, +2.1] | +0.1 [-1.1, +1.3] | +0.1 [-1.1, +1.3] |
| wind: calm | Offensive PPA/play | 407 | +0.033 [+0.009, +0.058] \* | +0.025 [+0.004, +0.047] \* | +0.033 [+0.011, +0.055] \* |
| wind: moderate | Pass yds/att | 234 | +0.19 [-0.08, +0.48] | +0.18 [-0.09, +0.43] | +0.16 [-0.10, +0.44] |
| wind: moderate | Points scored | 234 | +1.3 [-0.4, +3.1] | +1.7 [+0.2, +3.1] \* | +1.5 [+0.1, +2.9] \* |
| wind: moderate | Points allowed (defense) | 234 | +1.8 [+0.2, +3.5] \* | +1.9 [+0.5, +3.2] \* | +2.1 [+0.7, +3.5] \* |
| wind: moderate | Offensive PPA/play | 234 | -0.002 [-0.029, +0.025] | -0.001 [-0.023, +0.022] | -0.005 [-0.029, +0.017] |
| wind: windy | Pass yds/att | 174 | -0.68 [-1.00, -0.36] \* | -0.61 [-0.92, -0.30] \* | -0.65 [-0.97, -0.33] \* |
| wind: windy | Points scored | 174 | -3.3 [-5.2, -1.3] \* | -2.6 [-4.0, -1.0] \* | -2.8 [-4.4, -1.2] \* |
| wind: windy | Points allowed (defense) | 174 | -3.2 [-4.7, -1.6] \* | -2.5 [-3.8, -1.1] \* | -2.8 [-4.2, -1.4] \* |
| wind: windy | Offensive PPA/play | 174 | -0.045 [-0.074, -0.017] \* | -0.036 [-0.063, -0.010] \* | -0.041 [-0.067, -0.013] \* |

**precip** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| precip: none | Pass yds/att | 734 | +0.52 [+0.06, +0.96] \* | +0.40 [-0.03, +0.80] | +0.39 [-0.04, +0.78] |
| precip: none | Points scored | 734 | +1.1 [-1.7, +3.8] | +0.1 [-2.1, +2.0] | +0.0 [-2.1, +2.0] |
| precip: none | Points allowed (defense) | 734 | +2.0 [+0.0, +4.0] \* | +2.4 [+0.7, +4.0] \* | +2.6 [+0.9, +4.2] \* |
| precip: none | Offensive PPA/play | 734 | +0.047 [+0.006, +0.086] \* | +0.027 [-0.009, +0.061] | +0.030 [-0.007, +0.064] |
| precip: light | Pass yds/att | 59 | -0.35 [-0.87, +0.20] | -0.24 [-0.73, +0.27] | -0.17 [-0.65, +0.31] |
| precip: light | Points scored | 59 | -1.8 [-4.5, +1.2] | -0.8 [-3.0, +1.4] | -0.5 [-2.8, +1.7] |
| precip: light | Points allowed (defense) | 59 | -1.1 [-3.5, +1.5] | -2.0 [-3.8, -0.2] \* | -2.7 [-4.5, -0.7] \* |
| precip: light | Offensive PPA/play | 59 | -0.025 [-0.072, +0.025] | -0.008 [-0.051, +0.034] | -0.004 [-0.046, +0.040] |
| precip: steady | Pass yds/att | 28 | -0.80 [-1.54, -0.06] \* | -0.65 [-1.35, +0.05] | -0.77 [-1.50, -0.04] \* |
| precip: steady | Points scored | 28 | +0.3 [-5.0, +5.7] | +1.5 [-2.6, +5.7] | +1.0 [-3.1, +5.1] |
| precip: steady | Points allowed (defense) | 28 | -3.6 [-6.4, -0.7] \* | -2.7 [-5.9, +0.3] | -2.2 [-5.3, +0.9] |
| precip: steady | Offensive PPA/play | 28 | -0.084 [-0.149, -0.018] \* | -0.062 [-0.120, -0.004] \* | -0.077 [-0.137, -0.015] \* |
| precip: wet | Pass yds/att | 87 | -0.52 [-0.96, -0.06] \* | -0.40 [-0.80, +0.03] | -0.39 [-0.78, +0.04] |
| precip: wet | Points scored | 87 | -1.1 [-3.8, +1.7] | -0.1 [-2.0, +2.1] | -0.0 [-2.0, +2.1] |
| precip: wet | Points allowed (defense) | 87 | -2.0 [-4.0, -0.0] \* | -2.4 [-4.0, -0.7] \* | -2.6 [-4.2, -0.9] \* |
| precip: wet | Offensive PPA/play | 87 | -0.047 [-0.086, -0.006] \* | -0.027 [-0.061, +0.009] | -0.030 [-0.064, +0.007] |

**temp** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| temp: cold | Pass yds/att | 93 | -0.58 [-0.97, -0.19] \* | -0.27 [-0.65, +0.11] | -0.14 [-0.53, +0.27] |
| temp: cold | Points scored | 93 | -4.0 [-6.5, -1.5] \* | -1.1 [-3.1, +1.0] | -1.0 [-3.1, +1.3] |
| temp: cold | Points allowed (defense) | 93 | +0.1 [-2.1, +2.4] | -1.6 [-3.5, +0.1] | -2.4 [-4.5, -0.5] \* |
| temp: cold | Offensive PPA/play | 93 | -0.036 [-0.073, +0.000] | +0.001 [-0.032, +0.034] | +0.012 [-0.022, +0.049] |
| temp: mild | Pass yds/att | 474 | -0.46 [-0.73, -0.20] \* | -0.31 [-0.56, -0.06] \* | -0.24 [-0.53, +0.01] |
| temp: mild | Points scored | 474 | -2.0 [-3.8, -0.4] \* | -0.3 [-1.7, +1.0] | +0.0 [-1.4, +1.4] |
| temp: mild | Points allowed (defense) | 474 | +3.2 [+1.8, +4.6] \* | +2.1 [+1.0, +3.3] \* | +1.8 [+0.7, +3.1] \* |
| temp: mild | Offensive PPA/play | 474 | -0.043 [-0.067, -0.018] \* | -0.020 [-0.042, +0.002] | -0.014 [-0.040, +0.009] |
| temp: warm_hot | Pass yds/att | 247 | +0.84 [+0.54, +1.13] \* | +0.52 [+0.25, +0.80] \* | +0.49 [+0.17, +0.81] \* |
| temp: warm_hot | Points scored | 247 | +4.8 [+3.0, +6.7] \* | +1.4 [-0.0, +2.9] | +1.3 [-0.4, +3.1] |
| temp: warm_hot | Points allowed (defense) | 247 | -3.7 [-5.1, -2.3] \* | -1.6 [-2.9, -0.4] \* | -1.2 [-2.7, +0.2] |
| temp: warm_hot | Offensive PPA/play | 247 | +0.071 [+0.044, +0.098] \* | +0.026 [+0.002, +0.050] \* | +0.020 [-0.009, +0.049] |

## How much do the controls change things?

Solid cells, per-team (not pooled), all seasons. *Sign flips* = adjusted and controlled point opposite ways. *Excl. 0* = intervals excluding zero (about 1 in 10 expected by luck).

| Metric | Cells | Avg \|raw\| | Avg \|adj\| | Avg \|ctl\| | Adj→Ctl sign flips | Raw excl. 0 | Adj excl. 0 | Ctl excl. 0 |
|---|---|---|---|---|---|---|---|---|
| Pass yds/att | 55 | 0.38 | 0.32 | 0.32 | 3 | 16 | 13 | 5 |
| Rush yds/carry | 55 | 0.18 | 0.16 | 0.16 | 8 | 6 | 4 | 2 |
| Points scored | 55 | 2.0 | 1.4 | 1.3 | 4 | 15 | 7 | 6 |
| Points allowed (defense) | 55 | 1.9 | 1.5 | 1.4 | 5 | 16 | 12 | 10 |
| Turnovers | 55 | 0.14 | 0.14 | 0.13 | 5 | 8 | 6 | 4 |
| Offensive PPA/play | 55 | 0.031 | 0.024 | 0.025 | 3 | 13 | 10 | 8 |

## Opponent ratings: which games have no SP+?

SP+ covers FBS teams only. A game against an FCS opponent has no rating, so it is left out of the **Adjusted** and **Controlled** columns (it still counts in **Raw**). It is never guessed. *Raw shift* = how much the average |raw Δ| of the team's solid cells moves when the raw numbers are recomputed on rated games only -- a direct read on whether dropping those games matters.

| Team | Usable games | No SP+ rating | Opponents without a rating | Raw shift |
|---|---|---|---|---|
| Michigan | 138 | 0 | — | 0.000 |
| Nebraska | 140 | 6 | Bethune-Cookman, Fordham, Houston Christian, North Dakota, Northern Iowa | 0.246 |
| Northwestern | 139 | 8 | Eastern Illinois, Howard, Illinois State, Indiana State, South Dakota State, Southern Illinois … | 0.177 |
| Ohio State | 136 | 2 | Grambling, Youngstown State | 0.081 |
| Oregon | 135 | 11 | Eastern Washington, Idaho, Montana, Montana State, Portland State, Southern Utah … | 0.402 |
| USC | 133 | 0 | — | 0.000 |

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
| 2026 (in progress) | 10 | 10 | 10 | 10 | 10 | 10 |

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
| **all usable games** | 136 | 32% | 31% | 34% | 3% | 60% | 38% | 2% | +5.9 | +0.0 |
| wind: calm | 62 | 32% | 35% | 26% | 6% | 56% | 40% | 3% | +5.9 | -0.1 |
| wind: moderate | 43 | 35% | 21% | 44% | 0% | 58% | 42% | 0% | +9.3 | +3.4 |
| wind: windy | 31 | 29% | 35% | 35% | 0% | 68% | 29% | 3% | +1.6 | -4.4 |
| precip: none | 113 | 32% | 31% | 34% | 4% | 60% | 37% | 3% | +6.3 | +0.3 |
| precip: light | 14 | 21% | 36% | 43% | 0% | 36% | 64% | 0% | +6.9 | +1.0 |
| precip: steady | 9 (thin) | 56% | 22% | 22% | 0% | 89% | 11% | 0% | +0.4 | -5.5 |
| precip: wet | 23 | 35% | 30% | 35% | 0% | 57% | 43% | 0% | +4.4 | -1.6 |
| temp: cold | 21 | 0% | 24% | 67% | 10% | 43% | 57% | 0% | +10.1 | +4.2 |
| temp: mild | 74 | 20% | 34% | 43% | 3% | 57% | 39% | 4% | +6.7 | +0.8 |
| temp: warm | 35 | 66% | 34% | 0% | 0% | 74% | 26% | 0% | +3.0 | -3.0 |
| temp: hot | 6 (thin) | 100% | 0% | 0% | 0% | 67% | 33% | 0% | -1.2 | -7.2 |
| temp: warm_hot | 41 | 71% | 29% | 0% | 0% | 73% | 27% | 0% | +2.3 | -3.6 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 62 | +0.55\* / +0.59\* / +0.53\* | +1.3 / +1.3 / +1.2 | -1.0 / -1.1 / -1.2 | +0.053\* / +0.056\* / +0.055\* |
| wind: moderate | 43 | -0.00 / +0.03 / +0.18 | -0.0 / +1.2 / +1.7 | +2.3 / +1.4 / +1.4 | -0.030 / -0.025 / -0.020 |
| wind: windy | 31 | -1.10\* / -1.22\* / -1.27\* | -2.4 / -4.2\* / -4.6\* | -1.3 / +0.5 / +0.6 | -0.064\* / -0.079\* / -0.082\* |
| precip: none | 113 | +0.06 / +0.08 / +0.07 | -0.0 / +0.3 / +0.2 | -0.0 / +0.0 / +0.0 | +0.012 / +0.015\* / +0.014 |
| precip: light | 14 | +0.04 / +0.05 / +0.21 | -3.3 / -3.5 / -2.3 | +2.6 / +1.2 / +0.6 | -0.047 / -0.047 / -0.036 |
| precip: steady | 9 (thin) | -0.76 / -1.04 / -1.21 | +5.5 / +1.9 / +1.0 | -3.5 / -2.4 / -1.1 | -0.078 / -0.111 / -0.127 |
| precip: wet | 23 | -0.28 / -0.38 / -0.34 | +0.2 / -1.4 / -1.0 | +0.2 / -0.2 / -0.1 | -0.059 / -0.072\* / -0.069 |
| temp: cold | 21 | -0.55 / -0.22 / +0.05 | -1.9 / +1.5 / +2.2 | +2.8 / +2.1 / +0.3 | -0.016 / +0.020 / +0.038 |
| temp: mild | 74 | -0.25 / -0.23 / -0.17 | -1.9 / -1.7\* / -1.8 | +0.9 / +0.6 / +0.1 | -0.038\* / -0.035\* / -0.034\* |
| temp: warm | 35 | +0.90\* / +0.74\* / +0.59 | +5.1\* / +3.6\* / +4.1\* | -3.3\* / -2.6\* / -1.1 | +0.085\* / +0.066\* / +0.069\* |
| temp: hot | 6 (thin) | -0.25 / -0.58 / -0.84 | -0.2 / -4.4 / -4.5 | -1.7 / +0.7 / +3.6 | +0.024 / -0.015 / -0.028 |
| temp: warm_hot | 41 | +0.73\* / +0.54\* / +0.41 | +4.3\* / +2.4 / +3.2 | -3.1\* / -2.1\* / -0.4 | +0.076\* / +0.054\* / +0.063\* |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 62 | +1.02\* / +1.10\* / +0.98\* | +2.3 / +2.5 / +2.3 | -1.8 / -2.1 / -2.2 | +0.097\* / +0.104\* / +0.102\* |
| wind: moderate | 43 | -0.01 / +0.04 / +0.26 | -0.1 / +1.7 / +2.5 | +3.4 / +2.0 / +2.0 | -0.044 / -0.036 / -0.029 |
| wind: windy | 31 | -1.43\* / -1.59\* / -1.65\* | -3.2 / -5.5\* / -6.0\* | -1.6 / +0.6 / +0.7 | -0.083\* / -0.103\* / -0.106\* |
| precip: none | 113 | +0.33 / +0.46 / +0.41 | -0.2 / +1.7 / +1.2 | -0.3 / +0.2 / +0.1 | +0.071 / +0.087\* / +0.084 |
| precip: light | 14 | +0.04 / +0.05 / +0.23 | -3.6 / -3.9 / -2.6 | +2.9 / +1.4 / +0.6 | -0.052 / -0.052 / -0.040 |
| precip: steady | 9 (thin) | -0.82 / -1.12 / -1.30 | +5.9 / +2.1 / +1.1 | -3.7 / -2.6 / -1.1 | -0.084 / -0.119 / -0.136 |
| precip: wet | 23 | -0.33 / -0.46 / -0.41 | +0.2 / -1.7 / -1.2 | +0.3 / -0.2 / -0.1 | -0.071 / -0.087\* / -0.084 |
| temp: cold | 21 | -0.65 / -0.27 / +0.06 | -2.2 / +1.8 / +2.6 | +3.3 / +2.5 / +0.4 | -0.019 / +0.024 / +0.045 |
| temp: mild | 74 | -0.55 / -0.51 / -0.37 | -4.1 / -3.8\* / -3.9 | +2.0 / +1.2 / +0.1 | -0.083\* / -0.078\* / -0.075\* |
| temp: warm | 35 | +1.21\* / +0.99\* / +0.79 | +6.9\* / +4.8\* / +5.5\* | -4.4\* / -3.5\* / -1.5 | +0.115\* / +0.089\* / +0.093\* |
| temp: hot | 6 (thin) | -0.26 / -0.61 / -0.88 | -0.2 / -4.6 / -4.7 | -1.8 / +0.8 / +3.8 | +0.025 / -0.016 / -0.029 |
| temp: warm_hot | 41 | +1.05\* / +0.77\* / +0.58 | +6.2\* / +3.4 / +4.5 | -4.4\* / -3.0\* / -0.5 | +0.109\* / +0.077\* / +0.090\* |

### USC

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 133 | 35% | 30% | 29% | 6% | 56% | 40% | 4% | +6.0 | +0.0 |
| wind: calm | 90 | 32% | 29% | 30% | 9% | 58% | 37% | 6% | +5.6 | -0.4 |
| wind: moderate | 34 | 44% | 32% | 24% | 0% | 59% | 41% | 0% | +6.4 | +0.4 |
| wind: windy | 9 (thin) | 33% | 33% | 33% | 0% | 33% | 67% | 0% | +8.5 | +2.4 |
| precip: none | 125 | 35% | 30% | 28% | 6% | 58% | 38% | 4% | +5.6 | -0.4 |
| precip: light | 3 (suppressed) | 0% | 67% | 33% | 0% | 33% | 67% | 0% | +17.2 | +11.1 |
| precip: steady | 5 (thin) | 60% | 0% | 40% | 0% | 40% | 60% | 0% | +9.4 | +3.4 |
| precip: wet | 8 (thin) | 38% | 25% | 38% | 0% | 38% | 62% | 0% | +12.3 | +6.3 |
| temp: cold | 4 (suppressed) | 0% | 50% | 50% | 0% | 0% | 100% | 0% | +14.5 | +8.5 |
| temp: mild | 76 | 17% | 32% | 41% | 11% | 51% | 42% | 7% | +8.0 | +2.0 |
| temp: warm | 43 | 63% | 26% | 12% | 0% | 72% | 28% | 0% | +3.4 | -2.6 |
| temp: hot | 9 (thin) | 67% | 33% | 0% | 0% | 56% | 44% | 0% | -2.7 | -8.8 |
| temp: warm_hot | 52 | 63% | 27% | 10% | 0% | 69% | 31% | 0% | +2.3 | -3.7 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 90 | +0.09 / +0.05 / +0.05 | +0.7 / +0.3 / +0.3 | -0.6 / -0.5 / -0.6 | +0.013 / +0.008 / +0.009 |
| wind: moderate | 34 | +0.16 / +0.15 / +0.13 | +0.5 / +0.4 / -0.0 | +1.8 / +1.4 / +1.8 | -0.013 / -0.014 / -0.020 |
| wind: windy | 9 (thin) | -1.49\* / -1.09\* / -0.98\* | -8.3\* / -4.4 / -3.3 | -1.4 / -0.2 / -1.0 | -0.082 / -0.028 / -0.011 |
| precip: none | 125 | +0.00 / -0.03 / -0.03 | +0.2 / -0.1 / -0.2 | +0.2 / +0.3\* / +0.3\* | +0.005\* / +0.002 / +0.001 |
| precip: light | 3 (suppressed) | — | — | — | — |
| precip: steady | 5 (thin) | +0.26 / +0.47 / +0.53 | +1.3 / +3.4 / +3.9 | -4.5 / -4.8\* / -4.8 | -0.023 / +0.005 / +0.018 |
| precip: wet | 8 (thin) | -0.04 / +0.40 / +0.53 | -2.5 / +1.8 / +2.8 | -3.0 / -4.2\* / -4.7\* | -0.085\* / -0.026 / -0.012 |
| temp: cold | 4 (suppressed) | — | — | — | — |
| temp: mild | 76 | -0.38\* / -0.25\* / -0.21 | -2.6\* / -1.3\* / -0.7 | +2.8\* / +2.3\* / +2.3\* | -0.026\* / -0.008 / +0.002 |
| temp: warm | 43 | +0.59\* / +0.41\* / +0.27 | +4.3\* / +2.4\* / +0.9 | -3.7\* / -3.0\* / -2.5\* | +0.040 / +0.016 / -0.008 |
| temp: hot | 9 (thin) | +0.89\* / +0.49 / +0.41 | +8.8\* / +4.9\* / +4.7 | -5.2\* / -1.7 / -1.2 | +0.112\* / +0.059 / +0.054 |
| temp: warm_hot | 52 | +0.64\* / +0.42\* / +0.35 | +5.1\* / +2.9\* / +2.0\* | -3.9\* / -2.8\* / -2.6\* | +0.053\* / +0.023 / +0.005 |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 90 | +0.28 / +0.16 / +0.15 | +2.0 / +0.8 / +1.0 | -1.7 / -1.6 / -1.9 | +0.041 / +0.025 / +0.028 |
| wind: moderate | 34 | +0.21 / +0.21 / +0.17 | +0.6 / +0.6 / -0.0 | +2.5 / +1.9 / +2.5 | -0.018 / -0.019 / -0.027 |
| wind: windy | 9 (thin) | -1.60\* / -1.17\* / -1.05\* | -8.9\* / -4.7 / -3.5 | -1.5 / -0.2 / -1.0 | -0.088 / -0.030 / -0.012 |
| precip: none | 125 | +0.04 / -0.42 / -0.57 | +2.7 / -2.0 / -3.0 | +3.2 / +4.5\* / +5.0\* | +0.090\* / +0.027 / +0.013 |
| precip: light | 3 (suppressed) | — | — | — | — |
| precip: steady | 5 (thin) | +0.27 / +0.49 / +0.55 | +1.4 / +3.5 / +4.1 | -4.7 / -5.0\* / -4.9 | -0.024 / +0.005 / +0.018 |
| precip: wet | 8 (thin) | -0.04 / +0.42 / +0.57 | -2.7 / +2.0 / +3.0 | -3.2 / -4.5\* / -5.0\* | -0.090\* / -0.027 / -0.013 |
| temp: cold | 4 (suppressed) | — | — | — | — |
| temp: mild | 76 | -0.88\* / -0.58\* / -0.49 | -6.1\* / -3.1\* / -1.7 | +6.6\* / +5.3\* / +5.3\* | -0.060\* / -0.020 / +0.004 |
| temp: warm | 43 | +0.88\* / +0.60\* / +0.40 | +6.3\* / +3.6\* / +1.4 | -5.4\* / -4.5\* / -3.7\* | +0.060 / +0.023 / -0.011 |
| temp: hot | 9 (thin) | +0.95\* / +0.53 / +0.44 | +9.4\* / +5.3\* / +5.0 | -5.6\* / -1.8 / -1.3 | +0.120\* / +0.063 / +0.058 |
| temp: warm_hot | 52 | +1.06\* / +0.69\* / +0.57 | +8.3\* / +4.7\* / +3.2\* | -6.5\* / -4.6\* / -4.2\* | +0.087\* / +0.038 / +0.009 |

### Oregon

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 135 | 33% | 28% | 32% | 7% | 56% | 39% | 4% | +5.6 | +0.0 |
| wind: calm | 79 | 25% | 30% | 37% | 8% | 57% | 39% | 4% | +7.1 | +1.5 |
| wind: moderate | 34 | 53% | 29% | 18% | 0% | 65% | 35% | 0% | +3.6 | -2.0 |
| wind: windy | 22 | 32% | 18% | 36% | 14% | 41% | 45% | 14% | +3.6 | -2.0 |
| precip: none | 121 | 36% | 27% | 30% | 7% | 57% | 38% | 5% | +5.7 | +0.1 |
| precip: light | 9 (thin) | 22% | 44% | 33% | 0% | 56% | 44% | 0% | +5.8 | +0.2 |
| precip: steady | 5 (thin) | 0% | 20% | 80% | 0% | 40% | 60% | 0% | +3.7 | -1.9 |
| precip: wet | 14 | 14% | 36% | 50% | 0% | 50% | 50% | 0% | +5.0 | -0.6 |
| temp: cold | 7 (thin) | 0% | 0% | 100% | 0% | 71% | 29% | 0% | +5.9 | +0.3 |
| temp: mild | 96 | 19% | 35% | 36% | 9% | 54% | 40% | 6% | +6.5 | +0.9 |
| temp: warm | 29 | 83% | 14% | 3% | 0% | 62% | 38% | 0% | +1.6 | -4.0 |
| temp: hot | 3 (suppressed) | 100% | 0% | 0% | 0% | 33% | 67% | 0% | +10.8 | +5.2 |
| temp: warm_hot | 32 | 84% | 12% | 3% | 0% | 59% | 41% | 0% | +2.4 | -3.3 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 79 | -0.04 / -0.10 / -0.07 | +0.3 / -0.8 / -0.4 | +2.1\* / +1.1 / +1.4 | -0.003 / -0.014 / -0.011 |
| wind: moderate | 34 | +0.33 / +0.44 / +0.36 | +1.3 / +2.9 / +1.9 | -1.3 / +0.7 / -0.2 | +0.029 / +0.046 / +0.035 |
| wind: windy | 22 | -0.38 / -0.30 / -0.27 | -3.1 / -1.6 / -1.2 | -5.4\* / -4.7\* / -4.4\* | -0.035 / -0.019 / -0.012 |
| precip: none | 121 | +0.11\* / +0.12\* / +0.11 | +0.1 / +0.1 / -0.0 | +0.1 / +0.1 / +0.1 | +0.002 / +0.001 / +0.001 |
| precip: light | 9 (thin) | -0.26 / -0.39 / -0.21 | +0.4 / -0.3 / +0.7 | -2.3 / -2.9 / -3.5\* | +0.017 / +0.015 / +0.019 |
| precip: steady | 5 (thin) | -2.08\* / -1.97\* / -2.09\* | -4.0 / -1.7 / -0.7 | +2.0 / +2.6 / +3.6 | -0.073 / -0.049 / -0.063 |
| precip: wet | 14 | -0.91\* / -1.00\* / -0.93 | -1.1 / -0.8 / +0.2 | -0.7 / -0.8 / -0.8 | -0.015 / -0.009 / -0.012 |
| temp: cold | 7 (thin) | +0.30 / +0.20 / -0.23 | -1.6 / -1.5 / -2.4 | -2.1 / -5.5 / -4.2 | +0.033 / +0.030 / +0.005 |
| temp: mild | 96 | -0.30\* / -0.21\* / -0.17 | -2.0\* / -0.6 / +0.0 | +0.7 / +0.1 / +0.5 | -0.037\* / -0.020\* / -0.016 |
| temp: warm | 29 | +1.03\* / +0.89\* / +0.96\* | +7.8\* / +2.9 / +1.1 | -2.0 / +0.9 / -1.1 | +0.130\* / +0.084\* / +0.088\* |
| temp: hot | 3 (suppressed) | — | — | — | — |
| temp: warm_hot | 32 | +0.83\* / +0.73\* / +0.83\* | +6.4\* / +2.6 / +0.9 | -1.5 / +1.3 / -0.7 | +0.103\* / +0.067\* / +0.069 |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 79 | -0.09 / -0.24 / -0.16 | +0.7 / -1.9 / -1.0 | +5.0\* / +2.5 / +3.4 | -0.007 / -0.034 / -0.026 |
| wind: moderate | 34 | +0.44 / +0.58 / +0.48 | +1.7 / +3.9 / +2.6 | -1.8 / +0.9 / -0.2 | +0.039 / +0.061 / +0.047 |
| wind: windy | 22 | -0.45 / -0.36 / -0.33 | -3.7 / -1.9 / -1.5 | -6.5\* / -5.6\* / -5.4\* | -0.042 / -0.023 / -0.015 |
| precip: none | 121 | +1.02\* / +1.11\* / +1.04 | +1.3 / +0.9 / -0.2 | +0.8 / +0.9 / +0.9 | +0.017 / +0.010 / +0.014 |
| precip: light | 9 (thin) | -0.28 / -0.41 / -0.22 | +0.5 / -0.3 / +0.8 | -2.5 / -3.1 / -3.7\* | +0.018 / +0.016 / +0.021 |
| precip: steady | 5 (thin) | -2.16\* / -2.05\* / -2.18\* | -4.1 / -1.8 / -0.8 | +2.1 / +2.7 / +3.7 | -0.076 / -0.051 / -0.065 |
| precip: wet | 14 | -1.02\* / -1.11\* / -1.04 | -1.3 / -0.9 / +0.2 | -0.8 / -0.9 / -0.9 | -0.017 / -0.010 / -0.014 |
| temp: cold | 7 (thin) | +0.32 / +0.21 / -0.24 | -1.7 / -1.6 / -2.5 | -2.2 / -5.8 / -4.4 | +0.035 / +0.032 / +0.005 |
| temp: mild | 96 | -1.04\* / -0.83\* / -0.64 | -7.0\* / -2.3 / +0.1 | +2.3 / +0.2 / +2.0 | -0.128\* / -0.079\* / -0.061 |
| temp: warm | 29 | +1.32\* / +1.09\* / +1.18\* | +9.9\* / +3.6 / +1.4 | -2.6 / +1.1 / -1.3 | +0.165\* / +0.103\* / +0.108\* |
| temp: hot | 3 (suppressed) | — | — | — | — |
| temp: warm_hot | 32 | +1.09\* / +0.92\* / +1.04\* | +8.4\* / +3.2 / +1.1 | -2.0 / +1.6 / -0.9 | +0.136\* / +0.084\* / +0.086 |

### Northwestern

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 139 | 29% | 32% | 34% | 4% | 48% | 40% | 12% | +6.5 | +0.0 |
| wind: calm | 58 | 38% | 36% | 22% | 3% | 48% | 45% | 7% | +4.9 | -1.7 |
| wind: moderate | 47 | 32% | 23% | 38% | 6% | 47% | 40% | 13% | +8.7 | +2.2 |
| wind: windy | 34 | 12% | 38% | 47% | 3% | 50% | 29% | 21% | +6.6 | +0.0 |
| precip: none | 124 | 31% | 32% | 33% | 3% | 48% | 40% | 13% | +6.2 | -0.4 |
| precip: light | 12 | 8% | 33% | 42% | 17% | 42% | 50% | 8% | +11.3 | +4.7 |
| precip: steady | 3 (suppressed) | 33% | 33% | 33% | 0% | 100% | 0% | 0% | +1.5 | -5.1 |
| precip: wet | 15 | 13% | 33% | 40% | 13% | 53% | 40% | 7% | +9.3 | +2.8 |
| temp: cold | 18 | 0% | 6% | 78% | 17% | 28% | 50% | 22% | +8.3 | +1.8 |
| temp: mild | 83 | 18% | 42% | 39% | 1% | 47% | 43% | 10% | +7.7 | +1.1 |
| temp: warm | 33 | 67% | 24% | 3% | 6% | 64% | 21% | 15% | +4.0 | -2.5 |
| temp: hot | 5 (thin) | 80% | 20% | 0% | 0% | 40% | 60% | 0% | -3.4 | -10.0 |
| temp: warm_hot | 38 | 68% | 24% | 3% | 5% | 61% | 26% | 13% | +2.9 | -3.6 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 58 | -0.01 / -0.07 / -0.08 | +0.2 / -0.5 / -0.4 | +0.3 / +0.2 / +0.1 | -0.001 / -0.010 / -0.007 |
| wind: moderate | 47 | +0.14 / +0.22 / +0.26 | -0.9 / +0.1 / +0.3 | +2.3\* / +3.4\* / +3.4\* | -0.018 / -0.005 / +0.001 |
| wind: windy | 34 | -0.18 / -0.17 / -0.21 | +0.8 / +0.8 / +0.2 | -3.8\* / -5.0\* / -5.1\* | +0.027 / +0.025 / +0.012 |
| precip: none | 124 | +0.02 / -0.01 / -0.00 | -0.0 / -0.2 / -0.2 | +0.2 / +0.4 / +0.3 | +0.002 / -0.002 / -0.001 |
| precip: light | 12 | +0.01 / +0.21 / +0.20 | +1.2 / +2.9 / +2.3 | +0.2 / -2.0 / -1.5 | -0.003 / +0.029 / +0.021 |
| precip: steady | 3 (suppressed) | — | — | — | — |
| precip: wet | 15 | -0.13 / +0.08 / +0.02 | +0.1 / +1.9 / +1.4 | -1.9 / -3.0 / -2.1 | -0.019 / +0.014 / +0.004 |
| temp: cold | 18 | -0.27 / -0.13 / -0.04 | +0.3 / +1.5 / +1.6 | -2.3 / -3.3 / -3.7 | -0.018 / +0.004 / +0.010 |
| temp: mild | 83 | -0.02 / +0.02 / -0.01 | +0.1 / +0.6 / +0.3 | +1.1 / +0.8 / +0.9 | +0.001 / +0.013 / +0.005 |
| temp: warm | 33 | +0.35 / +0.27 / +0.33 | +0.2 / -1.3 / -0.6 | -0.4 / +0.8 / +1.2 | +0.015 / -0.023 / -0.007 |
| temp: hot | 5 (thin) | -0.96 / -1.32\* / -1.28\* | -4.4 / -8.1 / -6.9 | -7.2\* / -5.4\* / -7.5\* | -0.050 / -0.102 / -0.070 |
| temp: warm_hot | 38 | +0.18 / +0.03 / +0.06 | -0.4 / -2.3 / -2.0 | -1.3 / -0.1 / -0.3 | +0.006 / -0.035 / -0.021 |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 58 | -0.01 / -0.12 / -0.15 | +0.4 / -0.9 / -0.6 | +0.6 / +0.4 / +0.1 | -0.002 / -0.018 / -0.013 |
| wind: moderate | 47 | +0.21 / +0.32 / +0.38 | -1.3 / +0.2 / +0.5 | +3.5\* / +5.0\* / +5.1\* | -0.027 / -0.007 / +0.002 |
| wind: windy | 34 | -0.24 / -0.22 / -0.28 | +1.1 / +1.0 / +0.2 | -5.0\* / -6.6\* / -6.7\* | +0.035 / +0.032 / +0.015 |
| precip: none | 124 | +0.15 / -0.09 / -0.02 | -0.1 / -2.2 / -1.6 | +2.2 / +3.4 / +2.4 | +0.021 / -0.015 / -0.005 |
| precip: light | 12 | +0.01 / +0.23 / +0.22 | +1.3 / +3.2 / +2.6 | +0.2 / -2.2 / -1.6 | -0.003 / +0.031 / +0.023 |
| precip: steady | 3 (suppressed) | — | — | — | — |
| precip: wet | 15 | -0.15 / +0.09 / +0.02 | +0.1 / +2.2 / +1.6 | -2.2 / -3.4 / -2.4 | -0.021 / +0.015 / +0.005 |
| temp: cold | 18 | -0.31 / -0.15 / -0.05 | +0.4 / +1.7 / +1.9 | -2.6 / -3.9 / -4.3 | -0.021 / +0.004 / +0.011 |
| temp: mild | 83 | -0.05 / +0.04 / -0.03 | +0.3 / +1.6 / +0.8 | +2.7 / +2.1 / +2.2 | +0.003 / +0.035 / +0.013 |
| temp: warm | 33 | +0.46 / +0.34 / +0.42 | +0.2 / -1.6 / -0.8 | -0.5 / +1.0 / +1.6 | +0.019 / -0.029 / -0.009 |
| temp: hot | 5 (thin) | -1.00 / -1.37\* / -1.33\* | -4.6 / -8.4 / -7.2 | -7.5\* / -5.6\* / -7.8\* | -0.052 / -0.107 / -0.072 |
| temp: warm_hot | 38 | +0.24 / +0.04 / +0.08 | -0.6 / -3.1 / -2.6 | -1.7 / -0.2 / -0.4 | +0.009 / -0.046 / -0.027 |

### Nebraska

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 140 | 34% | 30% | 31% | 4% | 56% | 41% | 3% | +5.9 | +0.0 |
| wind: calm | 54 | 28% | 30% | 33% | 9% | 37% | 56% | 7% | +6.4 | +0.4 |
| wind: moderate | 38 | 47% | 24% | 29% | 0% | 63% | 37% | 0% | +4.1 | -1.8 |
| wind: windy | 48 | 31% | 35% | 31% | 2% | 73% | 27% | 0% | +6.8 | +0.9 |
| precip: none | 129 | 36% | 30% | 30% | 4% | 58% | 40% | 2% | +6.2 | +0.2 |
| precip: light | 11 | 18% | 27% | 45% | 9% | 36% | 55% | 9% | +3.5 | -2.4 |
| precip: wet | 11 | 18% | 27% | 45% | 9% | 36% | 55% | 9% | +3.5 | -2.4 |
| temp: cold | 19 | 0% | 16% | 74% | 11% | 53% | 47% | 0% | +10.6 | +4.7 |
| temp: mild | 73 | 18% | 37% | 40% | 5% | 45% | 51% | 4% | +7.2 | +1.3 |
| temp: warm | 33 | 70% | 27% | 3% | 0% | 76% | 21% | 3% | +0.6 | -5.4 |
| temp: hot | 15 | 80% | 20% | 0% | 0% | 73% | 27% | 0% | +4.2 | -1.7 |
| temp: warm_hot | 48 | 73% | 25% | 2% | 0% | 75% | 23% | 2% | +1.7 | -4.2 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 54 | +0.18 / +0.32 / +0.37 | -0.0 / +1.0 / +1.8 | +2.3 / +1.3 / +1.3 | +0.004 / +0.020 / +0.028 |
| wind: moderate | 38 | -0.01 / -0.29 / -0.30 | +3.5\* / +1.3 / +1.3 | -1.3 / -0.3 / -0.4 | +0.019 / -0.007 / -0.014 |
| wind: windy | 48 | -0.20 / -0.16 / -0.20 | -2.7\* / -2.2\* / -3.2\* | -1.6 / -1.3 / -1.1 | -0.020 / -0.018 / -0.022 |
| precip: none | 129 | +0.08 / +0.07 / +0.07 | +0.2 / +0.1 / +0.0 | +0.6\* / +0.5\* / +0.6\* | +0.001 / -0.001 / -0.002 |
| precip: light | 11 | -0.97 / -0.84 / -0.79 | -1.9 / -0.9 / -0.2 | -7.2\* / -5.6\* / -6.2\* | -0.007 / +0.008 / +0.017 |
| precip: wet | 11 | -0.97 / -0.84 / -0.79 | -1.9 / -0.9 / -0.2 | -7.2\* / -5.6\* / -6.2\* | -0.007 / +0.008 / +0.017 |
| temp: cold | 19 | -1.24\* / -0.77\* / -0.63 | -7.1\* / -3.2 / -3.4 | +0.6 / -1.2 / -1.6 | -0.062 / -0.017 / -0.012 |
| temp: mild | 73 | -0.04 / +0.17 / +0.20 | -0.3 / +1.2 / +1.8\* | +2.0\* / +1.1 / +0.9 | -0.004 / +0.016 / +0.026 |
| temp: warm | 33 | +0.35 / -0.21 / -0.42 | +3.8\* / -0.3 / -1.3 | -3.5\* / -0.7 / -0.2 | +0.020 / -0.039 / -0.065\* |
| temp: hot | 15 | +0.99 / +0.58 / +0.56 | +2.0 / -1.4 / -2.3 | -2.9 / -2.4 / -2.0 | +0.055 / +0.024 / +0.005 |
| temp: warm_hot | 48 | +0.55\* / +0.05 / -0.10 | +3.2\* / -0.7 / -2.2 | -3.3\* / -1.3 / -1.1 | +0.031 / -0.019 / -0.054\* |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 54 | +0.30 / +0.53 / +0.62 | -0.0 / +1.7 / +3.1 | +3.8 / +2.2 / +2.1 | +0.007 / +0.033 / +0.047 |
| wind: moderate | 38 | -0.02 / -0.39 / -0.40 | +4.7\* / +1.8 / +1.7 | -1.8 / -0.5 / -0.5 | +0.026 / -0.010 / -0.018 |
| wind: windy | 48 | -0.30 / -0.23 / -0.29 | -4.1\* / -3.4\* / -4.8\* | -2.5 / -2.0 / -1.7 | -0.030 / -0.027 / -0.033 |
| precip: none | 129 | +1.05 / +0.91 / +0.86 | +2.1 / +1.0 / +0.2 | +7.8\* / +6.1\* / +6.8\* | +0.008 / -0.009 / -0.018 |
| precip: light | 11 | -1.05 / -0.91 / -0.86 | -2.1 / -1.0 / -0.2 | -7.8\* / -6.1\* / -6.8\* | -0.008 / +0.009 / +0.018 |
| precip: wet | 11 | -1.05 / -0.91 / -0.86 | -2.1 / -1.0 / -0.2 | -7.8\* / -6.1\* / -6.8\* | -0.008 / +0.009 / +0.018 |
| temp: cold | 19 | -1.43\* / -0.90\* / -0.73 | -8.2\* / -3.7 / -3.9 | +0.7 / -1.4 / -1.9 | -0.072 / -0.020 / -0.014 |
| temp: mild | 73 | -0.08 / +0.38 / +0.44 | -0.6 / +2.7 / +3.8\* | +4.2\* / +2.4 / +1.9 | -0.009 / +0.034 / +0.056 |
| temp: warm | 33 | +0.46 / -0.27 / -0.53 | +5.0\* / -0.4 / -1.6 | -4.5\* / -0.9 / -0.2 | +0.026 / -0.050 / -0.083\* |
| temp: hot | 15 | +1.11 / +0.65 / +0.63 | +2.2 / -1.6 / -2.5 | -3.2 / -2.7 / -2.3 | +0.062 / +0.026 / +0.006 |
| temp: warm_hot | 48 | +0.84\* / +0.07 / -0.15 | +4.9\* / -1.0 / -3.2 | -5.0\* / -1.9 / -1.6 | +0.047 / -0.028 / -0.080\* |

### Michigan

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 138 | 32% | 30% | 33% | 5% | 57% | 38% | 6% | +6.3 | +0.0 |
| wind: calm | 64 | 33% | 30% | 34% | 3% | 48% | 48% | 3% | +4.3 | -2.0 |
| wind: moderate | 38 | 32% | 21% | 39% | 8% | 71% | 21% | 8% | +8.6 | +2.3 |
| wind: windy | 30 | 23% | 40% | 30% | 7% | 47% | 43% | 10% | +7.8 | +1.6 |
| precip: none | 122 | 34% | 30% | 33% | 4% | 54% | 41% | 5% | +5.9 | -0.4 |
| precip: light | 10 | 10% | 20% | 60% | 10% | 80% | 10% | 10% | +7.4 | +1.1 |
| precip: steady | 6 (thin) | 33% | 50% | 0% | 17% | 67% | 17% | 17% | +12.7 | +6.4 |
| precip: wet | 16 | 19% | 31% | 38% | 12% | 75% | 12% | 12% | +9.4 | +3.1 |
| temp: cold | 24 | 0% | 17% | 83% | 0% | 67% | 33% | 0% | +10.7 | +4.4 |
| temp: mild | 72 | 25% | 35% | 35% | 6% | 50% | 43% | 7% | +5.7 | -0.6 |
| temp: warm | 32 | 59% | 28% | 3% | 9% | 59% | 31% | 9% | +4.9 | -1.4 |
| temp: hot | 4 (suppressed) | 75% | 25% | 0% | 0% | 25% | 75% | 0% | +3.2 | -3.1 |
| temp: warm_hot | 36 | 61% | 28% | 3% | 8% | 56% | 36% | 8% | +4.7 | -1.6 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 64 | +0.22 / +0.08 / +0.11 | +1.8 / +0.6 / +0.7 | -0.9 / -0.2 / -0.7 | +0.039\* / +0.021 / +0.027 |
| wind: moderate | 38 | +0.27 / +0.24 / +0.22 | +1.9 / +1.6 / +1.5 | +3.5\* / +1.1 / +1.9 | +0.015 / +0.011 / +0.008 |
| wind: windy | 30 | -0.74\* / -0.46 / -0.43 | -4.3\* / -1.9 / -1.8 | -2.0 / -1.0 / -1.4 | -0.089\* / -0.054 / -0.054 |
| precip: none | 122 | +0.07 / +0.03 / +0.04 | +0.3 / -0.0 / -0.0 | +0.2 / +0.2 / +0.1 | +0.008 / +0.003 / +0.004 |
| precip: light | 10 | -0.51 / -0.46 / -0.53 | -2.1 / -1.6 / -2.1 | +0.2 / -0.7 / -0.2 | -0.017 / -0.010 / -0.016 |
| precip: steady | 6 (thin) | -0.60 / +0.09 / +0.16 | -2.6 / +3.4 / +4.0 | -3.7 / -3.3 / -2.2 | -0.139\* / -0.051 / -0.058 |
| precip: wet | 16 | -0.54 / -0.25 / -0.27 | -2.3 / +0.3 / +0.2 | -1.3 / -1.7 / -1.0 | -0.063 / -0.026 / -0.032 |
| temp: cold | 24 | -0.30 / -0.03 / -0.19 | -4.9\* / -2.5 / -4.3\* | -0.1 / -1.7 / -3.0 | -0.038 / -0.003 / -0.017 |
| temp: mild | 72 | -0.17 / -0.26 / -0.22 | +1.8 / +1.0 / +1.2 | +1.0 / +0.7 / +0.4 | -0.001 / -0.013 / -0.008 |
| temp: warm | 32 | +0.57 / +0.46 / +0.58 | +1.8 / +0.9 / +1.4 | -0.9 / -0.3 / +0.4 | +0.042 / +0.029 / +0.037 |
| temp: hot | 4 (suppressed) | — | — | — | — |
| temp: warm_hot | 36 | +0.60\* / +0.54 / +0.72\* | +1.3 / +0.8 / +1.4 | -1.4 / -0.3 / +0.2 | +0.038 / +0.031 / +0.042 |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 64 | +0.41 / +0.15 / +0.20 | +3.4 / +1.2 / +1.3 | -1.6 / -0.4 / -1.2 | +0.073\* / +0.040 / +0.050 |
| wind: moderate | 38 | +0.37 / +0.32 / +0.30 | +2.6 / +2.1 / +2.1 | +4.8\* / +1.5 / +2.6 | +0.021 / +0.015 / +0.011 |
| wind: windy | 30 | -0.94\* / -0.59 / -0.55 | -5.4\* / -2.4 / -2.3 | -2.5 / -1.2 / -1.8 | -0.114\* / -0.070 / -0.068 |
| precip: none | 122 | +0.61 / +0.28 / +0.31 | +2.6 / -0.3 / -0.2 | +1.4 / +1.9 / +1.1 | +0.071 / +0.029 / +0.036 |
| precip: light | 10 | -0.55 / -0.49 / -0.57 | -2.2 / -1.7 / -2.3 | +0.2 / -0.7 / -0.3 | -0.018 / -0.011 / -0.017 |
| precip: steady | 6 (thin) | -0.63 / +0.10 / +0.17 | -2.8 / +3.6 / +4.2 | -3.9 / -3.4 / -2.3 | -0.145\* / -0.054 / -0.061 |
| precip: wet | 16 | -0.61 / -0.28 / -0.31 | -2.6 / +0.3 / +0.2 | -1.4 / -1.9 / -1.1 | -0.071 / -0.029 / -0.036 |
| temp: cold | 24 | -0.37 / -0.03 / -0.23 | -5.9\* / -3.0 / -5.2\* | -0.1 / -2.1 / -3.7 | -0.046 / -0.003 / -0.020 |
| temp: mild | 72 | -0.35 / -0.54 / -0.46 | +3.8 / +2.2 / +2.4 | +2.1 / +1.4 / +0.9 | -0.003 / -0.026 / -0.017 |
| temp: warm | 32 | +0.74 / +0.60 / +0.75 | +2.4 / +1.1 / +1.9 | -1.2 / -0.4 / +0.5 | +0.055 / +0.037 / +0.048 |
| temp: hot | 4 (suppressed) | — | — | — | — |
| temp: warm_hot | 36 | +0.81\* / +0.73 / +0.97\* | +1.7 / +1.1 / +2.0 | -1.9 / -0.4 / +0.3 | +0.052 / +0.042 / +0.057 |

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

