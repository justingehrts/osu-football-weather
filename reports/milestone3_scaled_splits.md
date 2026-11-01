# Milestone 3: scaled splits, controlled model, evidence tiers

_Generated 2026-11-01 14:16 UTC._

> **EXPLORATORY.** This report tests many team × bin × metric cells. At a 90% level roughly 1 in 10 intervals will exclude zero by luck alone, so a starred (\*) delta or a "leans" tier is a lead to check, not a finding.

**Two yardsticks, always labelled.** *A. vs the team's overall average* compares a bin to all of the team's games, including the bin itself. *B. vs all other games* compares the bin to the games NOT in it ("windy vs not windy"); it is the A number divided by (1 − the bin's share of games). Evidence tiers use the controlled model, where the choice of yardstick does not change the verdict.

**Teams loaded (6):** Michigan, Nebraska, Northwestern, Ohio State, Oregon, USC. **Deferred by choice (7):** Ball State, Texas, Kent State, Illinois, Iowa, Maryland, Indiana -- not loaded (their 2026 games are already played, so they only matter for the Team Explorer); nothing here depends on them.

## Plain-language summary

- **Wind (windy vs not)** -- pooled across 6 teams, controlled for opponent, month and home/away: Pass yds/att -0.54 yds/att [-0.80, -0.27] (interval excludes zero); Points scored -2.2 pts [-3.6, -0.9] (interval excludes zero); Offensive PPA/play -0.032 PPA [-0.053, -0.010] (interval excludes zero). Clear evidence for: Ohio State. Leans: Michigan, Nebraska, USC.
- **Wet (light + steady rain)** -- pooled across 6 teams, controlled for opponent, month and home/away: Pass yds/att -0.35 yds/att [-0.76, +0.04] (interval spans zero); Points scored -0.1 pts [-1.9, +1.9] (interval spans zero); Offensive PPA/play -0.027 PPA [-0.059, +0.005] (interval spans zero). No team clears the bar. Leans: Ohio State.
- **Warm/hot (70°F and up)** -- pooled across 6 teams, controlled for opponent, month and home/away: Pass yds/att +0.34 yds/att [+0.11, +0.57] (interval excludes zero); Points scored +0.9 pts [-0.5, +2.2] (interval spans zero); Offensive PPA/play +0.013 PPA [-0.008, +0.035] (interval spans zero). No team clears the bar. Leans: Nebraska, Ohio State, Oregon.
- **Cold (39°F and below)** -- pooled across 6 teams, controlled for opponent, month and home/away: Pass yds/att -0.10 yds/att [-0.46, +0.23] (interval spans zero); Points scored -0.6 pts [-2.5, +1.2] (interval spans zero); Offensive PPA/play +0.013 PPA [-0.019, +0.043] (interval spans zero). No team clears the bar. 

Temperature: the controlled model finds no clear temperature effect for Michigan, Northwestern, USC, so their temperature results are labelled context-only; it still shows one (kept as is) for Nebraska, Ohio State, Oregon.

_Exploratory: tiers and stars are leads to check, not findings._

## CFBD call budget

- Month (2026-11) total so far: **4** of the 600-call cap (free-tier limit 1000); **996** calls remain before CFBD itself would stop us. CFBD's own `/info` count is the source of truth, and `/info` is not billed.
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
| wind: windy | Pass yds/att | 95 | -0.69 [-1.02, -0.36] \* | 171 | -0.54 [-0.80, -0.27] \* |
| wind: windy | Points scored | 95 | -2.0 [-3.7, -0.1] \* | 171 | -2.2 [-3.6, -0.9] \* |
| wind: windy | Points allowed (defense) | 95 | -3.0 [-4.6, -1.6] \* | 171 | -2.1 [-3.2, -1.0] \* |
| wind: windy | Offensive PPA/play | 95 | -0.028 [-0.057, +0.001] | 171 | -0.032 [-0.053, -0.010] \* |
| precip: wet | Pass yds/att | 58 | -0.27 [-0.71, +0.19] | 87 | -0.35 [-0.76, +0.04] |
| precip: wet | Points scored | 58 | +0.5 [-1.9, +3.0] | 87 | -0.1 [-1.9, +1.9] |
| precip: wet | Points allowed (defense) | 58 | -1.7 [-3.5, +0.5] | 87 | -2.3 [-3.9, -0.8] \* |
| precip: wet | Offensive PPA/play | 58 | -0.032 [-0.071, +0.006] | 87 | -0.027 [-0.059, +0.005] |
| precip: steady | Pass yds/att | 22 | -0.91 [-1.67, -0.11] \* | 28 | -0.74 [-1.41, -0.01] \* |
| precip: steady | Points scored | 22 | +0.4 [-4.1, +4.8] | 28 | +0.9 [-3.0, +5.2] |
| precip: steady | Points allowed (defense) | 22 | -2.0 [-5.6, +1.6] | 28 | -2.1 [-5.2, +1.0] |
| precip: steady | Offensive PPA/play | 22 | -0.073 [-0.147, -0.006] \* | 28 | -0.075 [-0.136, -0.015] \* |
| temp: cold | Pass yds/att | 50 | +0.08 [-0.34, +0.51] | 91 | -0.10 [-0.46, +0.23] |
| temp: cold | Points scored | 50 | +1.6 [-1.0, +4.3] | 91 | -0.6 [-2.5, +1.2] |
| temp: cold | Points allowed (defense) | 50 | -2.0 [-4.5, +0.6] | 91 | -2.2 [-4.1, -0.4] \* |
| temp: cold | Offensive PPA/play | 50 | +0.029 [-0.013, +0.068] | 91 | +0.013 [-0.019, +0.043] |
| temp: warm_hot | Pass yds/att | 163 | +0.41 [+0.13, +0.69] \* | 247 | +0.34 [+0.11, +0.57] \* |
| temp: warm_hot | Points scored | 163 | +1.4 [-0.1, +2.8] | 247 | +0.9 [-0.5, +2.2] |
| temp: warm_hot | Points allowed (defense) | 163 | -1.3 [-2.6, +0.0] | 247 | -0.8 [-1.8, +0.2] |
| temp: warm_hot | Offensive PPA/play | 163 | +0.029 [+0.005, +0.054] \* | 247 | +0.013 [-0.008, +0.035] |

## 2026 Ohio State schedule

8 played, 4 remaining. Team list = Ohio State + every opponent below (13 teams, from `config/opponents.yaml`).

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
| 10 | Nov 07 | Oregon | home | Ohio Stadium | **remaining** |
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
| Ohio State | **CLEAR** (62) | none (39) | **CLEAR** (31) | leans (109) | none (14) | leans (9) | leans (23) | none (21) | leans (71) | leans (34) | n/a (6) | leans (40) |
| USC | none (89) | none (34) | leans (9) | none (124) | n/a (3) | n/a (5) | n/a (8) | n/a (4) | context (75) | context (43) | n/a (9) | context (52) |
| Oregon | none (72) | leans (30) | none (20) | none (109) | n/a (8) | leans (5) | none (13) | n/a (7) | leans (90) | **CLEAR** (23) | n/a (2) | leans (25) |
| Northwestern | none (56) | none (42) | none (31) | none (114) | none (12) | n/a (3) | none (15) | context (18) | context (78) | context (28) | context (5) | context (33) |
| Nebraska | leans (53) | none (35) | none (44) | none (121) | none (11) | n/a (0) | none (11) | none (18) | leans (71) | leans (29) | none (14) | leans (43) |
| Michigan | leans (63) | none (38) | leans (29) | none (120) | none (10) | n/a (6) | none (16) | context (23) | context (71) | context (32) | n/a (4) | context (36) |
| Pooled (6 teams) | **CLEAR** (395) | none (218) | **CLEAR** (164) | leans (697) | none (58) | **CLEAR** (28) | leans (86) | context (91) | context (456) | context (189) | context (40) | context (229) |

### Scoring

| Team | wind:<br>calm | wind:<br>moderate | wind:<br>windy | precip:<br>none | precip:<br>light | precip:<br>steady | precip:<br>wet | temp:<br>cold | temp:<br>mild | temp:<br>warm | temp:<br>hot | temp:<br>warm_hot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ohio State | leans (62) | none (39) | **CLEAR** (31) | leans (109) | none (14) | n/a (9) | leans (23) | none (21) | leans (71) | **CLEAR** (34) | n/a (6) | leans (40) |
| USC | none (89) | none (34) | n/a (9) | none (124) | n/a (3) | n/a (5) | n/a (8) | n/a (4) | context (75) | context (43) | context (9) | context (52) |
| Oregon | none (72) | none (30) | none (20) | none (109) | n/a (8) | n/a (5) | none (13) | n/a (7) | none (90) | leans (23) | n/a (2) | none (25) |
| Northwestern | none (56) | none (42) | none (31) | none (114) | none (12) | n/a (3) | none (15) | context (18) | context (78) | context (28) | context (5) | context (33) |
| Nebraska | leans (53) | none (35) | leans (44) | none (121) | none (11) | n/a (0) | none (11) | none (18) | **CLEAR** (71) | leans (29) | none (14) | leans (43) |
| Michigan | leans (63) | none (38) | leans (29) | none (120) | none (10) | n/a (6) | none (16) | context (23) | context (71) | context (32) | n/a (4) | context (36) |
| Pooled (6 teams) | leans (395) | none (218) | **CLEAR** (164) | none (697) | none (58) | none (28) | none (86) | context (91) | context (456) | context (189) | context (40) | context (229) |

**Temperature:** a team's temperature tiers are kept as they are only if its controlled model has at least one CLEAR temperature cell; otherwise they are labelled context-only. Kept: Ohio State, Oregon, Nebraska. Context-only: Michigan, Northwestern, USC, Pooled (6 teams).

## Pooled reference line (all 6 loaded teams together)

Every team-game from the **6 teams** in the pool, each measured against its own team's baseline. Raw / Adjusted / Controlled as defined above; brackets are 90% intervals from a bootstrap over whole games. The same numbers are shown on two yardsticks; **steady** rain is kept as its own bin next to the merged **wet** bin.

### A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)

**wind** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | Pass yds/att | 403 | +0.16 [+0.03, +0.29] \* | +0.14 [+0.01, +0.26] \* | +0.16 [+0.03, +0.28] \* |
| wind: calm | Points scored | 403 | +0.7 [-0.0, +1.6] | +0.4 [-0.3, +1.0] | +0.5 [-0.1, +1.1] |
| wind: calm | Points allowed (defense) | 403 | +0.4 [-0.3, +1.1] | +0.1 [-0.6, +0.7] | +0.0 [-0.6, +0.6] |
| wind: calm | Offensive PPA/play | 403 | +0.017 [+0.005, +0.029] \* | +0.013 [+0.002, +0.024] \* | +0.017 [+0.006, +0.027] \* |
| wind: moderate | Pass yds/att | 230 | +0.15 [-0.05, +0.36] | +0.13 [-0.06, +0.34] | +0.13 [-0.08, +0.33] |
| wind: moderate | Points scored | 230 | +0.9 [-0.4, +2.2] | +1.1 [+0.0, +2.2] \* | +1.0 [+0.0, +2.1] \* |
| wind: moderate | Points allowed (defense) | 230 | +1.2 [-0.1, +2.4] | +1.3 [+0.3, +2.4] \* | +1.5 [+0.5, +2.5] \* |
| wind: moderate | Offensive PPA/play | 230 | -0.001 [-0.021, +0.019] | -0.001 [-0.018, +0.017] | -0.005 [-0.021, +0.015] |
| wind: windy | Pass yds/att | 171 | -0.56 [-0.82, -0.30] \* | -0.50 [-0.76, -0.24] \* | -0.54 [-0.80, -0.27] \* |
| wind: windy | Points scored | 171 | -2.6 [-4.1, -1.1] \* | -2.0 [-3.3, -0.8] \* | -2.2 [-3.6, -0.9] \* |
| wind: windy | Points allowed (defense) | 171 | -2.4 [-3.7, -1.1] \* | -1.9 [-3.0, -0.7] \* | -2.1 [-3.2, -1.0] \* |
| wind: windy | Offensive PPA/play | 171 | -0.036 [-0.061, -0.012] \* | -0.029 [-0.050, -0.008] \* | -0.032 [-0.053, -0.010] \* |

**precip** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| precip: none | Pass yds/att | 723 | +0.06 [+0.01, +0.11] \* | +0.04 [-0.00, +0.09] | +0.04 [-0.00, +0.09] |
| precip: none | Points scored | 723 | +0.1 [-0.1, +0.4] | +0.0 [-0.2, +0.2] | +0.0 [-0.2, +0.2] |
| precip: none | Points allowed (defense) | 723 | +0.2 [-0.0, +0.4] | +0.3 [+0.1, +0.4] \* | +0.3 [+0.1, +0.5] \* |
| precip: none | Offensive PPA/play | 723 | +0.005 [+0.001, +0.010] \* | +0.003 [-0.001, +0.007] | +0.003 [-0.001, +0.007] |
| precip: light | Pass yds/att | 59 | -0.34 [-0.84, +0.19] | -0.22 [-0.67, +0.26] | -0.16 [-0.63, +0.32] |
| precip: light | Points scored | 59 | -1.8 [-4.4, +1.1] | -0.8 [-2.8, +1.4] | -0.5 [-2.7, +1.6] |
| precip: light | Points allowed (defense) | 59 | -1.0 [-3.4, +1.4] | -1.8 [-3.6, -0.0] \* | -2.5 [-4.3, -0.4] \* |
| precip: light | Offensive PPA/play | 59 | -0.025 [-0.070, +0.021] | -0.007 [-0.047, +0.031] | -0.004 [-0.047, +0.035] |
| precip: steady | Pass yds/att | 28 | -0.79 [-1.50, -0.07] \* | -0.64 [-1.29, +0.08] | -0.74 [-1.41, -0.01] \* |
| precip: steady | Points scored | 28 | +0.1 [-5.0, +5.5] | +1.4 [-2.7, +5.6] | +0.9 [-3.0, +5.2] |
| precip: steady | Points allowed (defense) | 28 | -3.4 [-6.3, -0.4] \* | -2.6 [-5.6, +0.3] | -2.1 [-5.2, +1.0] |
| precip: steady | Offensive PPA/play | 28 | -0.083 [-0.149, -0.018] \* | -0.060 [-0.120, -0.003] \* | -0.075 [-0.136, -0.015] \* |
| precip: wet | Pass yds/att | 87 | -0.48 [-0.89, -0.07] \* | -0.36 [-0.74, +0.03] | -0.35 [-0.76, +0.04] |
| precip: wet | Points scored | 87 | -1.2 [-3.6, +1.3] | -0.1 [-1.9, +1.9] | -0.1 [-1.9, +1.9] |
| precip: wet | Points allowed (defense) | 87 | -1.8 [-3.6, +0.1] | -2.1 [-3.5, -0.7] \* | -2.3 [-3.9, -0.8] \* |
| precip: wet | Offensive PPA/play | 87 | -0.043 [-0.081, -0.006] \* | -0.024 [-0.057, +0.007] | -0.027 [-0.059, +0.005] |

**temp** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| temp: cold | Pass yds/att | 91 | -0.51 [-0.87, -0.17] \* | -0.21 [-0.56, +0.11] | -0.10 [-0.46, +0.23] |
| temp: cold | Points scored | 91 | -3.4 [-5.6, -1.3] \* | -0.7 [-2.4, +1.1] | -0.6 [-2.5, +1.2] |
| temp: cold | Points allowed (defense) | 91 | +0.2 [-1.9, +2.2] | -1.4 [-3.1, +0.2] | -2.2 [-4.1, -0.4] \* |
| temp: cold | Offensive PPA/play | 91 | -0.032 [-0.066, +0.002] | +0.003 [-0.026, +0.032] | +0.013 [-0.019, +0.043] |
| temp: mild | Pass yds/att | 465 | -0.20 [-0.31, -0.08] \* | -0.13 [-0.23, -0.02] \* | -0.10 [-0.22, +0.01] |
| temp: mild | Points scored | 465 | -0.8 [-1.5, -0.2] \* | -0.1 [-0.7, +0.4] | -0.0 [-0.6, +0.6] |
| temp: mild | Points allowed (defense) | 465 | +1.4 [+0.8, +2.0] \* | +0.9 [+0.4, +1.4] \* | +0.8 [+0.3, +1.3] \* |
| temp: mild | Offensive PPA/play | 465 | -0.018 [-0.028, -0.007] \* | -0.008 [-0.017, +0.001] | -0.006 [-0.016, +0.004] |
| temp: warm_hot | Pass yds/att | 247 | +0.57 [+0.36, +0.79] \* | +0.36 [+0.16, +0.56] \* | +0.34 [+0.11, +0.57] \* |
| temp: warm_hot | Points scored | 247 | +3.2 [+1.9, +4.5] \* | +0.9 [-0.1, +2.0] | +0.9 [-0.5, +2.2] |
| temp: warm_hot | Points allowed (defense) | 247 | -2.6 [-3.6, -1.6] \* | -1.1 [-2.0, -0.3] \* | -0.8 [-1.8, +0.2] |
| temp: warm_hot | Offensive PPA/play | 247 | +0.048 [+0.030, +0.066] \* | +0.017 [+0.000, +0.034] \* | +0.013 [-0.008, +0.035] |

### B. vs ALL OTHER GAMES (the complement: games not in the bin)

**wind** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| wind: calm | Pass yds/att | 403 | +0.31 [+0.05, +0.58] \* | +0.27 [+0.02, +0.52] \* | +0.32 [+0.06, +0.57] \* |
| wind: calm | Points scored | 403 | +1.5 [-0.0, +3.1] | +0.7 [-0.6, +2.0] | +1.0 [-0.3, +2.3] |
| wind: calm | Points allowed (defense) | 403 | +0.7 [-0.7, +2.2] | +0.1 [-1.1, +1.4] | +0.0 [-1.2, +1.3] |
| wind: calm | Offensive PPA/play | 403 | +0.034 [+0.010, +0.059] \* | +0.027 [+0.005, +0.048] \* | +0.035 [+0.011, +0.055] \* |
| wind: moderate | Pass yds/att | 230 | +0.21 [-0.07, +0.50] | +0.18 [-0.08, +0.46] | +0.17 [-0.10, +0.46] |
| wind: moderate | Points scored | 230 | +1.3 [-0.5, +3.0] | +1.5 [+0.1, +3.0] \* | +1.4 [+0.0, +2.8] \* |
| wind: moderate | Points allowed (defense) | 230 | +1.7 [-0.1, +3.4] | +1.8 [+0.4, +3.3] \* | +2.1 [+0.7, +3.5] \* |
| wind: moderate | Offensive PPA/play | 230 | -0.002 [-0.030, +0.026] | -0.002 [-0.025, +0.023] | -0.006 [-0.029, +0.020] |
| wind: windy | Pass yds/att | 171 | -0.71 [-1.04, -0.38] \* | -0.63 [-0.96, -0.30] \* | -0.68 [-1.01, -0.34] \* |
| wind: windy | Points scored | 171 | -3.3 [-5.2, -1.4] \* | -2.6 [-4.2, -1.0] \* | -2.8 [-4.5, -1.2] \* |
| wind: windy | Points allowed (defense) | 171 | -3.0 [-4.6, -1.4] \* | -2.4 [-3.8, -0.9] \* | -2.7 [-4.1, -1.3] \* |
| wind: windy | Offensive PPA/play | 171 | -0.045 [-0.076, -0.015] \* | -0.036 [-0.063, -0.010] \* | -0.041 [-0.066, -0.012] \* |

**precip** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| precip: none | Pass yds/att | 723 | +0.54 [+0.08, +1.00] \* | +0.40 [-0.03, +0.84] | +0.39 [-0.04, +0.85] |
| precip: none | Points scored | 723 | +1.3 [-1.4, +4.0] | +0.1 [-2.1, +2.2] | +0.1 [-2.1, +2.2] |
| precip: none | Points allowed (defense) | 723 | +2.0 [-0.1, +4.0] | +2.3 [+0.7, +4.0] \* | +2.6 [+0.9, +4.4] \* |
| precip: none | Offensive PPA/play | 723 | +0.049 [+0.007, +0.091] \* | +0.027 [-0.008, +0.064] | +0.030 [-0.005, +0.066] |
| precip: light | Pass yds/att | 59 | -0.36 [-0.91, +0.20] | -0.24 [-0.73, +0.28] | -0.17 [-0.68, +0.34] |
| precip: light | Points scored | 59 | -1.9 [-4.8, +1.2] | -0.8 [-3.0, +1.5] | -0.6 [-2.9, +1.8] |
| precip: light | Points allowed (defense) | 59 | -1.1 [-3.7, +1.5] | -2.0 [-3.8, -0.0] \* | -2.7 [-4.7, -0.5] \* |
| precip: light | Offensive PPA/play | 59 | -0.026 [-0.076, +0.023] | -0.008 [-0.051, +0.033] | -0.004 [-0.050, +0.038] |
| precip: steady | Pass yds/att | 28 | -0.82 [-1.56, -0.07] \* | -0.66 [-1.35, +0.08] | -0.77 [-1.46, -0.01] \* |
| precip: steady | Points scored | 28 | +0.1 [-5.2, +5.7] | +1.4 [-2.8, +5.8] | +0.9 [-3.1, +5.3] |
| precip: steady | Points allowed (defense) | 28 | -3.5 [-6.6, -0.5] \* | -2.7 [-5.8, +0.4] | -2.1 [-5.3, +1.1] |
| precip: steady | Offensive PPA/play | 28 | -0.086 [-0.154, -0.019] \* | -0.063 [-0.124, -0.003] \* | -0.078 [-0.141, -0.016] \* |
| precip: wet | Pass yds/att | 87 | -0.54 [-1.00, -0.08] \* | -0.40 [-0.84, +0.03] | -0.39 [-0.85, +0.04] |
| precip: wet | Points scored | 87 | -1.3 [-4.0, +1.4] | -0.1 [-2.2, +2.1] | -0.1 [-2.2, +2.1] |
| precip: wet | Points allowed (defense) | 87 | -2.0 [-4.0, +0.1] | -2.3 [-4.0, -0.7] \* | -2.6 [-4.4, -0.9] \* |
| precip: wet | Offensive PPA/play | 87 | -0.049 [-0.091, -0.007] \* | -0.027 [-0.064, +0.008] | -0.030 [-0.066, +0.005] |

**temp** (pooled across 6 teams)

| Bin | Metric | n | Raw Δ [90%] | Adj Δ [90%] | Controlled Δ [90%] |
|---|---|---|---|---|---|
| temp: cold | Pass yds/att | 91 | -0.57 [-0.98, -0.19] \* | -0.24 [-0.63, +0.12] | -0.12 [-0.53, +0.27] |
| temp: cold | Points scored | 91 | -3.8 [-6.3, -1.5] \* | -0.8 [-2.7, +1.3] | -0.7 [-2.8, +1.4] |
| temp: cold | Points allowed (defense) | 91 | +0.2 [-2.1, +2.5] | -1.6 [-3.5, +0.2] | -2.5 [-4.6, -0.4] \* |
| temp: cold | Offensive PPA/play | 91 | -0.035 [-0.074, +0.002] | +0.004 [-0.030, +0.036] | +0.014 [-0.022, +0.049] |
| temp: mild | Pass yds/att | 465 | -0.46 [-0.73, -0.18] \* | -0.31 [-0.56, -0.04] \* | -0.25 [-0.51, +0.02] |
| temp: mild | Points scored | 465 | -2.0 [-3.5, -0.4] \* | -0.3 [-1.7, +1.0] | -0.0 [-1.5, +1.4] |
| temp: mild | Points allowed (defense) | 465 | +3.2 [+1.8, +4.6] \* | +2.1 [+1.0, +3.3] \* | +1.8 [+0.7, +3.1] \* |
| temp: mild | Offensive PPA/play | 465 | -0.042 [-0.066, -0.017] \* | -0.019 [-0.041, +0.003] | -0.014 [-0.038, +0.010] |
| temp: warm_hot | Pass yds/att | 247 | +0.83 [+0.53, +1.13] \* | +0.50 [+0.22, +0.79] \* | +0.48 [+0.16, +0.80] \* |
| temp: warm_hot | Points scored | 247 | +4.6 [+2.8, +6.5] \* | +1.3 [-0.2, +2.7] | +1.2 [-0.6, +3.0] |
| temp: warm_hot | Points allowed (defense) | 247 | -3.7 [-5.1, -2.2] \* | -1.6 [-2.9, -0.4] \* | -1.2 [-2.6, +0.3] |
| temp: warm_hot | Offensive PPA/play | 247 | +0.069 [+0.043, +0.095] \* | +0.024 [+0.000, +0.048] \* | +0.019 [-0.011, +0.049] |

## How much do the controls change things?

Solid cells, per-team (not pooled), all seasons. *Sign flips* = adjusted and controlled point opposite ways. *Excl. 0* = intervals excluding zero (about 1 in 10 expected by luck).

| Metric | Cells | Avg \|raw\| | Avg \|adj\| | Avg \|ctl\| | Adj→Ctl sign flips | Raw excl. 0 | Adj excl. 0 | Ctl excl. 0 |
|---|---|---|---|---|---|---|---|---|
| Pass yds/att | 55 | 0.39 | 0.32 | 0.32 | 5 | 15 | 13 | 5 |
| Rush yds/carry | 55 | 0.18 | 0.16 | 0.16 | 8 | 7 | 5 | 3 |
| Points scored | 55 | 1.9 | 1.4 | 1.3 | 3 | 15 | 6 | 5 |
| Points allowed (defense) | 55 | 1.9 | 1.4 | 1.4 | 9 | 15 | 12 | 10 |
| Turnovers | 55 | 0.14 | 0.14 | 0.14 | 5 | 9 | 7 | 4 |
| Offensive PPA/play | 55 | 0.030 | 0.024 | 0.025 | 3 | 12 | 10 | 11 |

## Opponent ratings: which games have no SP+?

SP+ covers FBS teams only. A game against an FCS opponent has no rating, so it is left out of the **Adjusted** and **Controlled** columns (it still counts in **Raw**). It is never guessed. *Raw shift* = how much the average |raw Δ| of the team's solid cells moves when the raw numbers are recomputed on rated games only -- a direct read on whether dropping those games matters.

| Team | Usable games | No SP+ rating | Opponents without a rating | Raw shift |
|---|---|---|---|---|
| Michigan | 136 | 0 | — | 0.000 |
| Nebraska | 138 | 6 | Bethune-Cookman, Fordham, Houston Christian, North Dakota, Northern Iowa | 0.248 |
| Northwestern | 137 | 8 | Eastern Illinois, Howard, Illinois State, Indiana State, South Dakota State, Southern Illinois … | 0.178 |
| Ohio State | 134 | 2 | Grambling, Youngstown State | 0.082 |
| Oregon | 133 | 11 | Eastern Washington, Idaho, Montana, Montana State, Portland State, Southern Utah … | 0.401 |
| USC | 132 | 0 | — | 0.000 |

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
| 2026 (in progress) | 8 | 8 | 8 | 8 | 8 | 9 |

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
| **all usable games** | 134 | 33% | 31% | 33% | 3% | 59% | 39% | 2% | +5.7 | +0.0 |
| wind: calm | 62 | 32% | 35% | 26% | 6% | 56% | 40% | 3% | +5.9 | +0.1 |
| wind: moderate | 41 | 37% | 22% | 41% | 0% | 56% | 44% | 0% | +8.9 | +3.2 |
| wind: windy | 31 | 29% | 35% | 35% | 0% | 68% | 29% | 3% | +1.5 | -4.2 |
| precip: none | 111 | 32% | 32% | 32% | 4% | 59% | 38% | 3% | +6.0 | +0.3 |
| precip: light | 14 | 21% | 36% | 43% | 0% | 36% | 64% | 0% | +6.8 | +1.0 |
| precip: steady | 9 (thin) | 56% | 22% | 22% | 0% | 89% | 11% | 0% | +0.5 | -5.2 |
| precip: wet | 23 | 35% | 30% | 35% | 0% | 57% | 43% | 0% | +4.3 | -1.4 |
| temp: cold | 21 | 0% | 24% | 67% | 10% | 43% | 57% | 0% | +10.1 | +4.4 |
| temp: mild | 72 | 21% | 35% | 42% | 3% | 56% | 40% | 4% | +6.5 | +0.7 |
| temp: warm | 35 | 66% | 34% | 0% | 0% | 74% | 26% | 0% | +2.8 | -2.9 |
| temp: hot | 6 (thin) | 100% | 0% | 0% | 0% | 67% | 33% | 0% | -1.8 | -7.5 |
| temp: warm_hot | 41 | 71% | 29% | 0% | 0% | 73% | 27% | 0% | +2.1 | -3.6 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 62 | +0.52\* / +0.57\* / +0.51\* | +1.1 / +1.3 / +1.1 | -0.8 / -1.0 / -1.1 | +0.051\* / +0.055\* / +0.054\* |
| wind: moderate | 41 | +0.07 / +0.09 / +0.23 | +0.4 / +1.5 / +2.0 | +2.0 / +1.1 / +1.2 | -0.027 / -0.024 / -0.019 |
| wind: windy | 31 | -1.13\* / -1.25\* / -1.29\* | -2.6 / -4.3\* / -4.8\* | -1.1 / +0.5 / +0.7 | -0.066\* / -0.080\* / -0.083\* |
| precip: none | 111 | +0.06 / +0.09 / +0.08 | +0.0 / +0.3 / +0.2 | -0.1 / +0.0 / -0.0 | +0.013 / +0.015\* / +0.015\* |
| precip: light | 14 | +0.00 / +0.02 / +0.19 | -3.4 / -3.6 / -2.4 | +2.8 / +1.4 / +0.7 | -0.049 / -0.049 / -0.037 |
| precip: steady | 9 (thin) | -0.80 / -1.07 / -1.24 | +5.3 / +1.8 / +0.8 | -3.3 / -2.4 / -1.0 | -0.080 / -0.112 / -0.128 |
| precip: wet | 23 | -0.31 / -0.41 / -0.36 | -0.0 / -1.5 / -1.1 | +0.4 / -0.1 / +0.0 | -0.061 / -0.073\* / -0.071\* |
| temp: cold | 21 | -0.58 / -0.24 / +0.02 | -2.1 / +1.4 / +1.9 | +3.0 / +2.2 / +0.6 | -0.018 / +0.019 / +0.036 |
| temp: mild | 72 | -0.23 / -0.21 / -0.16 | -1.8 / -1.6 / -1.7 | +0.8 / +0.4 / -0.0 | -0.037\* / -0.035\* / -0.034\* |
| temp: warm | 35 | +0.87\* / +0.71\* / +0.58 | +4.9\* / +3.4\* / +4.0\* | -3.1\* / -2.5\* / -1.1 | +0.083\* / +0.064\* / +0.068\* |
| temp: hot | 6 (thin) | -0.28 / -0.64 / -0.86 | -0.4 / -4.8 / -4.7 | -1.5 / +0.9 / +3.7 | +0.022 / -0.019 / -0.031 |
| temp: warm_hot | 41 | +0.70\* / +0.50\* / +0.39 | +4.2\* / +2.2 / +3.0 | -2.9\* / -2.0\* / -0.3 | +0.074\* / +0.052\* / +0.062\* |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 62 | +0.97\* / +1.07\* / +0.97\* | +2.0 / +2.4 / +2.2 | -1.4 / -1.9 / -2.1 | +0.094\* / +0.104\* / +0.102\* |
| wind: moderate | 41 | +0.10 / +0.13 / +0.33 | +0.5 / +2.1 / +2.9 | +2.8 / +1.6 / +1.7 | -0.038 / -0.034 / -0.027 |
| wind: windy | 31 | -1.47\* / -1.63\* / -1.69\* | -3.4 / -5.7\* / -6.2\* | -1.4 / +0.7 / +0.9 | -0.086\* / -0.105\* / -0.109\* |
| precip: none | 111 | +0.37 / +0.49 / +0.43 | +0.0 / +1.8 / +1.4 | -0.5 / +0.1 / -0.1 | +0.074 / +0.089\* / +0.085\* |
| precip: light | 14 | +0.01 / +0.02 / +0.21 | -3.8 / -4.1 / -2.7 | +3.2 / +1.6 / +0.8 | -0.055 / -0.054 / -0.041 |
| precip: steady | 9 (thin) | -0.85 / -1.15 / -1.33 | +5.7 / +2.0 / +0.9 | -3.5 / -2.6 / -1.1 | -0.086 / -0.120 / -0.138 |
| precip: wet | 23 | -0.37 / -0.49 / -0.43 | -0.0 / -1.8 / -1.4 | +0.5 / -0.1 / +0.1 | -0.074 / -0.089\* / -0.085\* |
| temp: cold | 21 | -0.69 / -0.29 / +0.02 | -2.4 / +1.7 / +2.2 | +3.6 / +2.6 / +0.7 | -0.022 / +0.023 / +0.042 |
| temp: mild | 72 | -0.49 / -0.46 / -0.34 | -3.8 / -3.5 / -3.7 | +1.6 / +1.0 / -0.1 | -0.080\* / -0.075\* / -0.073\* |
| temp: warm | 35 | +1.18\* / +0.95\* / +0.78 | +6.7\* / +4.5\* / +5.4\* | -4.2\* / -3.3\* / -1.5 | +0.113\* / +0.086\* / +0.092\* |
| temp: hot | 6 (thin) | -0.30 / -0.67 / -0.90 | -0.4 / -5.0 / -5.0 | -1.6 / +1.0 / +3.9 | +0.023 / -0.020 / -0.032 |
| temp: warm_hot | 41 | +1.01\* / +0.72\* / +0.56 | +6.0\* / +3.1 / +4.3 | -4.1\* / -2.8\* / -0.4 | +0.107\* / +0.074\* / +0.088\* |

### USC

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 132 | 36% | 30% | 28% | 6% | 57% | 39% | 4% | +5.9 | +0.0 |
| wind: calm | 89 | 33% | 29% | 29% | 9% | 58% | 36% | 6% | +5.5 | -0.4 |
| wind: moderate | 34 | 44% | 32% | 24% | 0% | 59% | 41% | 0% | +6.4 | +0.5 |
| wind: windy | 9 (thin) | 33% | 33% | 33% | 0% | 33% | 67% | 0% | +8.5 | +2.5 |
| precip: none | 124 | 35% | 31% | 27% | 6% | 58% | 38% | 4% | +5.5 | -0.4 |
| precip: light | 3 (suppressed) | 0% | 67% | 33% | 0% | 33% | 67% | 0% | +18.7 | +12.8 |
| precip: steady | 5 (thin) | 60% | 0% | 40% | 0% | 40% | 60% | 0% | +9.4 | +3.5 |
| precip: wet | 8 (thin) | 38% | 25% | 38% | 0% | 38% | 62% | 0% | +12.9 | +7.0 |
| temp: cold | 4 (suppressed) | 0% | 50% | 50% | 0% | 0% | 100% | 0% | +14.5 | +8.6 |
| temp: mild | 75 | 17% | 32% | 40% | 11% | 52% | 41% | 7% | +7.9 | +2.0 |
| temp: warm | 43 | 63% | 26% | 12% | 0% | 72% | 28% | 0% | +3.3 | -2.6 |
| temp: hot | 9 (thin) | 67% | 33% | 0% | 0% | 56% | 44% | 0% | -2.7 | -8.7 |
| temp: warm_hot | 52 | 63% | 27% | 10% | 0% | 69% | 31% | 0% | +2.3 | -3.7 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 89 | +0.09 / +0.05 / +0.05 | +0.7 / +0.3 / +0.4 | -0.6 / -0.5 / -0.6 | +0.014 / +0.009 / +0.009 |
| wind: moderate | 34 | +0.15 / +0.15 / +0.13 | +0.3 / +0.4 / -0.1 | +1.8 / +1.4 / +1.8 | -0.015 / -0.015 / -0.021 |
| wind: windy | 9 (thin) | -1.49\* / -1.09\* / -0.96\* | -8.5\* / -4.5 / -3.4 | -1.4 / -0.2 / -1.0 | -0.083 / -0.029 / -0.011 |
| precip: none | 124 | +0.00 / -0.03 / -0.04 | +0.2 / -0.1 / -0.2 | +0.2 / +0.3\* / +0.3\* | +0.006\* / +0.001 / +0.000 |
| precip: light | 3 (suppressed) | — | — | — | — |
| precip: steady | 5 (thin) | +0.26 / +0.48 / +0.55 | +1.2 / +3.3 / +3.9 | -4.5 / -4.8\* / -4.8 | -0.025 / +0.004 / +0.018 |
| precip: wet | 8 (thin) | -0.05 / +0.45 / +0.60 | -2.7 / +2.1 / +3.1 | -3.0 / -4.4\* / -4.9\* | -0.087\* / -0.021 / -0.007 |
| temp: cold | 4 (suppressed) | — | — | — | — |
| temp: mild | 75 | -0.38\* / -0.25\* / -0.21 | -2.5\* / -1.3\* / -0.7 | +2.9\* / +2.3\* / +2.3\* | -0.025 / -0.008 / +0.002 |
| temp: warm | 43 | +0.59\* / +0.41\* / +0.27 | +4.1\* / +2.4\* / +0.9 | -3.7\* / -3.0\* / -2.4\* | +0.039 / +0.015 / -0.008 |
| temp: hot | 9 (thin) | +0.88\* / +0.48 / +0.39 | +8.6\* / +4.8\* / +4.5 | -5.2\* / -1.8 / -1.3 | +0.110\* / +0.057 / +0.052 |
| temp: warm_hot | 52 | +0.64\* / +0.42\* / +0.34 | +4.9\* / +2.8\* / +1.9 | -3.9\* / -2.8\* / -2.5\* | +0.051\* / +0.023 / +0.005 |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 89 | +0.29 / +0.16 / +0.14 | +2.3 / +1.0 / +1.1 | -1.7 / -1.6 / -1.8 | +0.044 / +0.026 / +0.028 |
| wind: moderate | 34 | +0.20 / +0.21 / +0.18 | +0.4 / +0.5 / -0.1 | +2.5 / +1.9 / +2.4 | -0.020 / -0.020 / -0.028 |
| wind: windy | 9 (thin) | -1.60\* / -1.17\* / -1.03\* | -9.1\* / -4.8 / -3.6 | -1.5 / -0.2 / -1.1 | -0.090 / -0.032 / -0.012 |
| precip: none | 124 | +0.05 / -0.48 / -0.64 | +2.8 / -2.3 / -3.3 | +3.2 / +4.7\* / +5.2\* | +0.092\* / +0.022 / +0.007 |
| precip: light | 3 (suppressed) | — | — | — | — |
| precip: steady | 5 (thin) | +0.27 / +0.50 / +0.58 | +1.2 / +3.4 / +4.0 | -4.7 / -5.0\* / -5.0 | -0.026 / +0.004 / +0.019 |
| precip: wet | 8 (thin) | -0.05 / +0.48 / +0.64 | -2.8 / +2.3 / +3.3 | -3.2 / -4.7\* / -5.2\* | -0.092\* / -0.022 / -0.007 |
| temp: cold | 4 (suppressed) | — | — | — | — |
| temp: mild | 75 | -0.88\* / -0.58\* / -0.48 | -5.8\* / -3.0\* / -1.6 | +6.6\* / +5.3\* / +5.2\* | -0.057 / -0.019 / +0.005 |
| temp: warm | 43 | +0.87\* / +0.61\* / +0.40 | +6.1\* / +3.6\* / +1.3 | -5.4\* / -4.4\* / -3.6\* | +0.057 / +0.023 / -0.012 |
| temp: hot | 9 (thin) | +0.94\* / +0.51 / +0.42 | +9.3\* / +5.1\* / +4.9 | -5.6\* / -1.9 / -1.4 | +0.118\* / +0.061 / +0.056 |
| temp: warm_hot | 52 | +1.05\* / +0.70\* / +0.56 | +8.1\* / +4.7\* / +3.1 | -6.5\* / -4.5\* / -4.1\* | +0.084\* / +0.037 / +0.008 |

### Oregon

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 133 | 34% | 29% | 31% | 7% | 56% | 39% | 5% | +5.3 | +0.0 |
| wind: calm | 79 | 25% | 30% | 37% | 8% | 57% | 39% | 4% | +7.0 | +1.6 |
| wind: moderate | 33 | 55% | 30% | 15% | 0% | 67% | 33% | 0% | +2.8 | -2.5 |
| wind: windy | 21 | 33% | 19% | 33% | 14% | 38% | 48% | 14% | +3.3 | -2.1 |
| precip: none | 119 | 36% | 28% | 29% | 8% | 57% | 38% | 5% | +5.4 | +0.1 |
| precip: light | 9 (thin) | 22% | 44% | 33% | 0% | 56% | 44% | 0% | +5.4 | +0.1 |
| precip: steady | 5 (thin) | 0% | 20% | 80% | 0% | 40% | 60% | 0% | +3.7 | -1.6 |
| precip: wet | 14 | 14% | 36% | 50% | 0% | 50% | 50% | 0% | +4.7 | -0.6 |
| temp: cold | 7 (thin) | 0% | 0% | 100% | 0% | 71% | 29% | 0% | +5.9 | +0.6 |
| temp: mild | 94 | 19% | 36% | 35% | 10% | 54% | 39% | 6% | +6.2 | +0.9 |
| temp: warm | 29 | 83% | 14% | 3% | 0% | 62% | 38% | 0% | +1.5 | -3.8 |
| temp: hot | 3 (suppressed) | 100% | 0% | 0% | 0% | 33% | 67% | 0% | +9.2 | +3.9 |
| temp: warm_hot | 32 | 84% | 12% | 3% | 0% | 59% | 41% | 0% | +2.1 | -3.2 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 79 | -0.02 / -0.07 / -0.03 | +0.3 / -0.6 / -0.2 | +2.0\* / +0.9 / +1.3 | -0.004 / -0.013 / -0.010 |
| wind: moderate | 33 | +0.40 / +0.51 / +0.42 | +1.2 / +2.7 / +1.5 | -1.6 / +0.8 / -0.1 | +0.033 / +0.048 / +0.038 |
| wind: windy | 21 | -0.55 / -0.52 / -0.49 | -2.9 / -1.8 / -1.3 | -5.0\* / -4.6\* / -4.4\* | -0.037 / -0.027 / -0.018 |
| precip: none | 119 | +0.11\* / +0.11\* / +0.11 | +0.1 / +0.1 / -0.1 | +0.1 / +0.1 / +0.1 | +0.002 / +0.001 / +0.001 |
| precip: light | 9 (thin) | -0.25 / -0.34 / -0.16 | +0.4 / +0.0 / +1.1 | -2.4 / -2.5 / -3.1 | +0.016 / +0.019 / +0.023 |
| precip: steady | 5 (thin) | -2.07\* / -1.92\* / -2.02\* | -4.0 / -1.5 / -0.2 | +1.9 / +2.4 / +3.4 | -0.074 / -0.046 / -0.060 |
| precip: wet | 14 | -0.90\* / -0.95\* / -0.88 | -1.2 / -0.5 / +0.6 | -0.8 / -0.7 / -0.6 | -0.016 / -0.006 / -0.008 |
| temp: cold | 7 (thin) | +0.32 / +0.23 / -0.12 | -1.7 / -1.4 / -1.9 | -2.2 / -5.6 / -4.5 | +0.033 / +0.032 / +0.010 |
| temp: mild | 94 | -0.31\* / -0.23\* / -0.18 | -2.1\* / -0.7 / -0.0 | +0.7 / +0.1 / +0.6 | -0.037\* / -0.021\* / -0.016 |
| temp: warm | 29 | +1.05\* / +0.91\* / +0.94\* | +7.8\* / +3.0 / +1.0 | -2.1 / +0.7 / -1.4 | +0.129\* / +0.085\* / +0.085\* |
| temp: hot | 3 (suppressed) | — | — | — | — |
| temp: warm_hot | 32 | +0.85\* / +0.76\* / +0.81\* | +6.4\* / +2.7 / +0.8 | -1.6 / +1.3 / -0.8 | +0.103\* / +0.068\* / +0.067 |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 79 | -0.05 / -0.16 / -0.07 | +0.7 / -1.5 / -0.6 | +4.9\* / +2.3 / +3.3 | -0.009 / -0.031 / -0.024 |
| wind: moderate | 33 | +0.53 / +0.67 / +0.56 | +1.6 / +3.6 / +2.0 | -2.1 / +1.0 / -0.2 | +0.043 / +0.064 / +0.050 |
| wind: windy | 21 | -0.66 / -0.62 / -0.58 | -3.5 / -2.2 / -1.6 | -5.9\* / -5.5\* / -5.3\* | -0.044 / -0.032 / -0.022 |
| precip: none | 119 | +1.00\* / +1.06\* / +0.99 | +1.3 / +0.6 / -0.7 | +0.9 / +0.7 / +0.7 | +0.018 / +0.007 / +0.009 |
| precip: light | 9 (thin) | -0.27 / -0.36 / -0.18 | +0.4 / +0.0 / +1.2 | -2.6 / -2.7 / -3.3 | +0.017 / +0.021 / +0.025 |
| precip: steady | 5 (thin) | -2.15\* / -2.00\* / -2.11\* | -4.2 / -1.5 / -0.2 | +2.0 / +2.5 / +3.6 | -0.077 / -0.048 / -0.062 |
| precip: wet | 14 | -1.00\* / -1.06\* / -0.99 | -1.3 / -0.6 / +0.7 | -0.9 / -0.7 / -0.7 | -0.018 / -0.007 / -0.009 |
| temp: cold | 7 (thin) | +0.33 / +0.24 / -0.13 | -1.8 / -1.4 / -2.0 | -2.3 / -5.9 / -4.8 | +0.034 / +0.034 / +0.010 |
| temp: mild | 94 | -1.06\* / -0.87\* / -0.67 | -7.0\* / -2.5 / -0.1 | +2.4 / +0.3 / +2.2 | -0.127\* / -0.082\* / -0.062 |
| temp: warm | 29 | +1.34\* / +1.12\* / +1.16\* | +9.9\* / +3.6 / +1.2 | -2.7 / +0.8 / -1.7 | +0.165\* / +0.104\* / +0.105\* |
| temp: hot | 3 (suppressed) | — | — | — | — |
| temp: warm_hot | 32 | +1.12\* / +0.95\* / +1.02\* | +8.4\* / +3.4 / +1.0 | -2.1 / +1.6 / -1.0 | +0.135\* / +0.086\* / +0.084 |

### Northwestern

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 137 | 30% | 33% | 33% | 4% | 48% | 39% | 12% | +6.4 | +0.0 |
| wind: calm | 57 | 39% | 37% | 21% | 4% | 47% | 46% | 7% | +4.7 | -1.7 |
| wind: moderate | 46 | 33% | 24% | 37% | 7% | 48% | 39% | 13% | +8.5 | +2.1 |
| wind: windy | 34 | 12% | 38% | 47% | 3% | 50% | 29% | 21% | +6.6 | +0.2 |
| precip: none | 122 | 32% | 33% | 32% | 3% | 48% | 39% | 13% | +6.0 | -0.4 |
| precip: light | 12 | 8% | 33% | 42% | 17% | 42% | 50% | 8% | +11.4 | +5.0 |
| precip: steady | 3 (suppressed) | 33% | 33% | 33% | 0% | 100% | 0% | 0% | +1.5 | -4.9 |
| precip: wet | 15 | 13% | 33% | 40% | 13% | 53% | 40% | 7% | +9.4 | +3.0 |
| temp: cold | 18 | 0% | 6% | 78% | 17% | 28% | 50% | 22% | +8.3 | +1.9 |
| temp: mild | 81 | 19% | 43% | 37% | 1% | 47% | 43% | 10% | +7.4 | +1.0 |
| temp: warm | 33 | 67% | 24% | 3% | 6% | 64% | 21% | 15% | +4.0 | -2.4 |
| temp: hot | 5 (thin) | 80% | 20% | 0% | 0% | 40% | 60% | 0% | -3.4 | -9.8 |
| temp: warm_hot | 38 | 68% | 24% | 3% | 5% | 61% | 26% | 13% | +2.9 | -3.5 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 57 | +0.01 / -0.07 / -0.08 | +0.3 / -0.5 / -0.3 | +0.4 / +0.2 / -0.0 | +0.001 / -0.009 / -0.007 |
| wind: moderate | 46 | +0.12 / +0.20 / +0.24 | -0.9 / +0.1 / +0.3 | +2.3 / +3.4\* / +3.6\* | -0.020 / -0.007 / -0.001 |
| wind: windy | 34 | -0.18 / -0.15 / -0.19 | +0.7 / +0.8 / +0.2 | -3.7\* / -5.0\* / -5.1\* | +0.026 / +0.026 / +0.013 |
| precip: none | 122 | +0.02 / -0.01 / -0.00 | +0.0 / -0.3 / -0.2 | +0.2 / +0.4 / +0.3 | +0.002 / -0.002 / -0.001 |
| precip: light | 12 | +0.01 / +0.23 / +0.22 | +1.0 / +2.9 / +2.4 | +0.3 / -2.0 / -1.5 | -0.004 / +0.030 / +0.022 |
| precip: steady | 3 (suppressed) | — | — | — | — |
| precip: wet | 15 | -0.13 / +0.10 / +0.04 | -0.1 / +1.9 / +1.4 | -1.9 / -3.0 / -2.1 | -0.020 / +0.015 / +0.005 |
| temp: cold | 18 | -0.27 / -0.11 / +0.01 | +0.2 / +1.5 / +1.7 | -2.2 / -3.3 / -3.7 | -0.019 / +0.005 / +0.013 |
| temp: mild | 81 | -0.02 / +0.01 / -0.02 | +0.2 / +0.6 / +0.3 | +1.1 / +0.8 / +0.9 | +0.002 / +0.013 / +0.004 |
| temp: warm | 33 | +0.35 / +0.28 / +0.33 | +0.1 / -1.2 / -0.6 | -0.3 / +0.8 / +1.3 | +0.014 / -0.022 / -0.007 |
| temp: hot | 5 (thin) | -0.96 / -1.31\* / -1.28\* | -4.5 / -8.1 / -6.8 | -7.1\* / -5.4\* / -7.5\* | -0.051 / -0.102 / -0.069 |
| temp: warm_hot | 38 | +0.18 / +0.04 / +0.06 | -0.5 / -2.3 / -1.9 | -1.2 / -0.1 / -0.2 | +0.005 / -0.034 / -0.020 |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 57 | +0.01 / -0.12 / -0.14 | +0.6 / -0.8 / -0.6 | +0.6 / +0.3 / -0.0 | +0.002 / -0.016 / -0.011 |
| wind: moderate | 46 | +0.18 / +0.30 / +0.36 | -1.4 / +0.1 / +0.4 | +3.5 / +5.1\* / +5.3\* | -0.031 / -0.010 / -0.001 |
| wind: windy | 34 | -0.24 / -0.20 / -0.25 | +0.9 / +1.0 / +0.3 | -4.9\* / -6.6\* / -6.7\* | +0.034 / +0.034 / +0.017 |
| precip: none | 122 | +0.15 / -0.11 / -0.04 | +0.1 / -2.2 / -1.6 | +2.1 / +3.4 / +2.3 | +0.023 / -0.017 / -0.006 |
| precip: light | 12 | +0.01 / +0.26 / +0.24 | +1.1 / +3.2 / +2.6 | +0.3 / -2.2 / -1.6 | -0.004 / +0.033 / +0.025 |
| precip: steady | 3 (suppressed) | — | — | — | — |
| precip: wet | 15 | -0.15 / +0.11 / +0.04 | -0.1 / +2.2 / +1.6 | -2.1 / -3.4 / -2.3 | -0.023 / +0.017 / +0.006 |
| temp: cold | 18 | -0.31 / -0.13 / +0.01 | +0.2 / +1.8 / +2.0 | -2.6 / -3.8 / -4.3 | -0.022 / +0.006 / +0.015 |
| temp: mild | 81 | -0.06 / +0.02 / -0.05 | +0.5 / +1.5 / +0.8 | +2.6 / +2.1 / +2.2 | +0.004 / +0.033 / +0.011 |
| temp: warm | 33 | +0.46 / +0.36 / +0.42 | +0.1 / -1.6 / -0.8 | -0.4 / +1.0 / +1.7 | +0.018 / -0.028 / -0.009 |
| temp: hot | 5 (thin) | -0.99 / -1.37\* / -1.33\* | -4.7 / -8.4 / -7.1 | -7.4\* / -5.6\* / -7.8\* | -0.053 / -0.106 / -0.072 |
| temp: warm_hot | 38 | +0.25 / +0.06 / +0.08 | -0.8 / -3.1 / -2.6 | -1.7 / -0.2 / -0.3 | +0.007 / -0.045 / -0.027 |

### Nebraska

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 138 | 35% | 30% | 30% | 4% | 57% | 40% | 3% | +6.0 | +0.0 |
| wind: calm | 53 | 28% | 30% | 32% | 9% | 38% | 55% | 8% | +6.4 | +0.3 |
| wind: moderate | 38 | 47% | 24% | 29% | 0% | 63% | 37% | 0% | +4.1 | -1.9 |
| wind: windy | 47 | 32% | 36% | 30% | 2% | 74% | 26% | 0% | +7.2 | +1.1 |
| precip: none | 127 | 36% | 31% | 29% | 4% | 59% | 39% | 2% | +6.3 | +0.2 |
| precip: light | 11 | 18% | 27% | 45% | 9% | 36% | 55% | 9% | +3.5 | -2.5 |
| precip: wet | 11 | 18% | 27% | 45% | 9% | 36% | 55% | 9% | +3.5 | -2.5 |
| temp: cold | 18 | 0% | 17% | 72% | 11% | 56% | 44% | 0% | +10.8 | +4.7 |
| temp: mild | 72 | 18% | 38% | 39% | 6% | 46% | 50% | 4% | +7.5 | +1.4 |
| temp: warm | 33 | 70% | 27% | 3% | 0% | 76% | 21% | 3% | +0.6 | -5.5 |
| temp: hot | 15 | 80% | 20% | 0% | 0% | 73% | 27% | 0% | +4.2 | -1.9 |
| temp: warm_hot | 48 | 73% | 25% | 2% | 0% | 75% | 23% | 2% | +1.7 | -4.3 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 53 | +0.20 / +0.32 / +0.37 | +0.2 / +1.1 / +1.9 | +2.2 / +1.2 / +1.0 | +0.005 / +0.019 / +0.028 |
| wind: moderate | 38 | -0.02 / -0.30 / -0.31 | +3.4\* / +1.2 / +1.1 | -1.5 / -0.5 / -0.6 | +0.020 / -0.007 / -0.013 |
| wind: windy | 47 | -0.21 / -0.15 / -0.19 | -2.9\* / -2.3\* / -3.2\* | -1.3 / -1.0 / -0.7 | -0.021 / -0.018 / -0.022 |
| precip: none | 127 | +0.08 / +0.08 / +0.07 | +0.2 / +0.1 / +0.0 | +0.6\* / +0.5\* / +0.6\* | +0.001 / -0.001 / -0.002 |
| precip: light | 11 | -0.98 / -0.85 / -0.81 | -2.0 / -1.0 / -0.4 | -7.3\* / -5.8\* / -6.7\* | -0.006 / +0.008 / +0.018 |
| precip: wet | 11 | -0.98 / -0.85 / -0.81 | -2.0 / -1.0 / -0.4 | -7.3\* / -5.8\* / -6.7\* | -0.006 / +0.008 / +0.018 |
| temp: cold | 18 | -1.26\* / -0.77\* / -0.65 | -6.8\* / -2.7 / -3.1 | +0.5 / -1.2 / -1.9 | -0.066 / -0.019 / -0.015 |
| temp: mild | 72 | -0.05 / +0.18 / +0.20 | -0.4 / +1.2 / +1.7\* | +2.2\* / +1.2 / +0.9 | -0.005 / +0.016 / +0.027\* |
| temp: warm | 33 | +0.34 / -0.23 / -0.41 | +3.7\* / -0.5 / -1.3 | -3.7\* / -0.9 / -0.1 | +0.021 / -0.039 / -0.064\* |
| temp: hot | 15 | +0.99 / +0.56 / +0.56 | +1.9 / -1.7 / -2.3 | -3.1 / -2.7 / -2.0 | +0.056 / +0.023 / +0.005 |
| temp: warm_hot | 48 | +0.55\* / +0.03 / -0.10 | +3.2\* / -0.9 / -2.1 | -3.5\* / -1.5 / -1.0 | +0.032 / -0.019 / -0.054\* |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 53 | +0.32 / +0.54 / +0.62 | +0.3 / +1.9 / +3.2 | +3.6 / +2.0 / +1.7 | +0.007 / +0.033 / +0.047 |
| wind: moderate | 38 | -0.02 / -0.41 / -0.42 | +4.7\* / +1.6 / +1.5 | -2.0 / -0.7 / -0.8 | +0.028 / -0.010 / -0.018 |
| wind: windy | 47 | -0.32 / -0.22 / -0.28 | -4.4\* / -3.4\* / -4.8\* | -2.0 / -1.5 / -1.1 | -0.032 / -0.027 / -0.034 |
| precip: none | 127 | +1.06 / +0.93 / +0.88 | +2.1 / +1.1 / +0.4 | +8.0\* / +6.4\* / +7.3\* | +0.007 / -0.009 / -0.020 |
| precip: light | 11 | -1.06 / -0.93 / -0.88 | -2.1 / -1.1 / -0.4 | -8.0\* / -6.4\* / -7.3\* | -0.007 / +0.009 / +0.020 |
| precip: wet | 11 | -1.06 / -0.93 / -0.88 | -2.1 / -1.1 / -0.4 | -8.0\* / -6.4\* / -7.3\* | -0.007 / +0.009 / +0.020 |
| temp: cold | 18 | -1.45\* / -0.89\* / -0.75 | -7.9\* / -3.1 / -3.5 | +0.6 / -1.4 / -2.1 | -0.076 / -0.022 / -0.017 |
| temp: mild | 72 | -0.10 / +0.39 / +0.44 | -0.8 / +2.6 / +3.6\* | +4.6\* / +2.6 / +1.9 | -0.010 / +0.036 / +0.058\* |
| temp: warm | 33 | +0.45 / -0.29 / -0.53 | +4.9\* / -0.7 / -1.6 | -4.8\* / -1.2 / -0.1 | +0.027 / -0.051 / -0.082\* |
| temp: hot | 15 | +1.11 / +0.62 / +0.63 | +2.2 / -1.9 / -2.5 | -3.5 / -3.0 / -2.2 | +0.063 / +0.026 / +0.005 |
| temp: warm_hot | 48 | +0.84\* / +0.04 / -0.15 | +4.8\* / -1.3 / -3.2 | -5.3\* / -2.2 / -1.4 | +0.049 / -0.028 / -0.080\* |

### Michigan

| Bin | n | Aug–Sep | Oct | Nov | Dec–Jan | Home | Away | Neutral | Opp SP+ | vs all games |
|---|---|---|---|---|---|---|---|---|---|---|
| **all usable games** | 136 | 32% | 30% | 32% | 5% | 57% | 38% | 6% | +6.3 | +0.0 |
| wind: calm | 63 | 33% | 30% | 33% | 3% | 48% | 49% | 3% | +4.4 | -1.9 |
| wind: moderate | 38 | 32% | 21% | 39% | 8% | 71% | 21% | 8% | +8.6 | +2.3 |
| wind: windy | 29 | 24% | 41% | 28% | 7% | 48% | 41% | 10% | +7.6 | +1.3 |
| precip: none | 120 | 34% | 30% | 32% | 4% | 54% | 41% | 5% | +5.9 | -0.4 |
| precip: light | 10 | 10% | 20% | 60% | 10% | 80% | 10% | 10% | +7.4 | +1.1 |
| precip: steady | 6 (thin) | 33% | 50% | 0% | 17% | 67% | 17% | 17% | +12.7 | +6.4 |
| precip: wet | 16 | 19% | 31% | 38% | 12% | 75% | 12% | 12% | +9.4 | +3.1 |
| temp: cold | 23 | 0% | 17% | 83% | 0% | 65% | 35% | 0% | +11.3 | +5.0 |
| temp: mild | 71 | 25% | 35% | 34% | 6% | 51% | 42% | 7% | +5.6 | -0.7 |
| temp: warm | 32 | 59% | 28% | 3% | 9% | 59% | 31% | 9% | +4.9 | -1.4 |
| temp: hot | 4 (suppressed) | 75% | 25% | 0% | 0% | 25% | 75% | 0% | +3.2 | -3.1 |
| temp: warm_hot | 36 | 61% | 28% | 3% | 8% | 56% | 36% | 8% | +4.7 | -1.6 |

Each cell: **Raw / Adjusted / Controlled** delta (\* = 90% interval excludes zero). Two yardsticks are shown; intervals are in `milestone3_detail.md`.

**A. vs the team's OVERALL AVERAGE (the average includes the bin's own games)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 63 | +0.21 / +0.08 / +0.11 | +1.9 / +0.8 / +0.9 | -0.7 / -0.2 / -0.7 | +0.039\* / +0.023 / +0.028 |
| wind: moderate | 38 | +0.22 / +0.19 / +0.17 | +1.5 / +1.2 / +1.1 | +3.6\* / +1.2 / +2.0 | +0.010 / +0.006 / +0.002 |
| wind: windy | 29 | -0.67\* / -0.39 / -0.36 | -3.9\* / -1.5 / -1.4 | -2.4 / -1.2 / -1.5 | -0.084\* / -0.049 / -0.048 |
| precip: none | 120 | +0.08 / +0.04 / +0.04 | +0.4 / +0.0 / +0.0 | +0.2 / +0.2 / +0.1 | +0.009 / +0.004 / +0.005 |
| precip: light | 10 | -0.56 / -0.50 / -0.61 | -2.4 / -1.9 / -2.9 | +0.3 / -0.6 / -0.1 | -0.022 / -0.015 / -0.026 |
| precip: steady | 6 (thin) | -0.64 / +0.05 / +0.18 | -3.0 / +3.1 / +4.1 | -3.7 / -3.1 / -2.1 | -0.144\* / -0.056 / -0.057 |
| precip: wet | 16 | -0.59 / -0.29 / -0.32 | -2.6 / -0.1 / -0.2 | -1.2 / -1.5 / -0.9 | -0.068 / -0.030 / -0.038 |
| temp: cold | 23 | -0.26 / +0.04 / -0.19 | -4.4\* / -1.7 / -4.0\* | +0.1 / -1.8 / -3.1 | -0.031 / +0.007 / -0.013 |
| temp: mild | 71 | -0.16 / -0.25 / -0.22 | +1.8 / +1.0 / +1.1 | +0.9 / +0.6 / +0.4 | -0.001 / -0.012 / -0.009 |
| temp: warm | 32 | +0.52 / +0.42 / +0.58 | +1.5 / +0.5 / +1.4 | -0.8 / -0.2 / +0.4 | +0.037 / +0.024 / +0.036 |
| temp: hot | 4 (suppressed) | — | — | — | — |
| temp: warm_hot | 36 | +0.55 / +0.50 / +0.71\* | +0.9 / +0.5 / +1.5 | -1.3 / -0.1 / +0.3 | +0.033 / +0.026 / +0.042 |

**B. vs ALL OTHER GAMES (the complement: games not in the bin)**

| Bin | n | Pass yds/att | Points scored | Points allowed (defense) | Offensive PPA/play |
|---|---|---|---|---|---|
| wind: calm | 63 | +0.40 / +0.16 / +0.20 | +3.6 / +1.4 / +1.6 | -1.4 / -0.4 / -1.2 | +0.073\* / +0.042 / +0.052 |
| wind: moderate | 38 | +0.31 / +0.27 / +0.23 | +2.1 / +1.7 / +1.5 | +4.9\* / +1.6 / +2.7 | +0.014 / +0.008 / +0.003 |
| wind: windy | 29 | -0.85\* / -0.50 / -0.45 | -5.0\* / -1.9 / -1.8 | -3.1 / -1.5 / -1.9 | -0.107\* / -0.062 / -0.060 |
| precip: none | 120 | +0.67 / +0.33 / +0.36 | +3.0 / +0.1 / +0.3 | +1.3 / +1.7 / +1.0 | +0.077 / +0.034 / +0.043 |
| precip: light | 10 | -0.60 / -0.54 / -0.66 | -2.6 / -2.1 / -3.1 | +0.3 / -0.6 / -0.1 | -0.024 / -0.016 / -0.028 |
| precip: steady | 6 (thin) | -0.67 / +0.05 / +0.18 | -3.1 / +3.2 / +4.3 | -3.8 / -3.2 / -2.2 | -0.151\* / -0.058 / -0.059 |
| precip: wet | 16 | -0.67 / -0.33 / -0.36 | -3.0 / -0.1 / -0.3 | -1.3 / -1.7 / -1.0 | -0.077 / -0.034 / -0.043 |
| temp: cold | 23 | -0.32 / +0.05 / -0.23 | -5.2\* / -2.1 / -4.8\* | +0.1 / -2.2 / -3.7 | -0.038 / +0.008 / -0.015 |
| temp: mild | 71 | -0.33 / -0.52 / -0.46 | +3.8 / +2.2 / +2.3 | +1.9 / +1.3 / +0.9 | -0.002 / -0.026 / -0.019 |
| temp: warm | 32 | +0.68 / +0.55 / +0.75 | +1.9 / +0.7 / +1.9 | -1.1 / -0.2 / +0.6 | +0.049 / +0.031 / +0.048 |
| temp: hot | 4 (suppressed) | — | — | — | — |
| temp: warm_hot | 36 | +0.75 / +0.68 / +0.97\* | +1.2 / +0.6 / +2.0 | -1.8 / -0.2 / +0.4 | +0.045 / +0.036 / +0.058 |

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

