# Pipeline (milestone 1)

Run order (`python -m pipeline.run_all` does all of it, incrementally):

1. `resolve_opponents` – one-time: freezes OSU's next 3 opponents into `config/opponents.yaml`.
2. `ingest_games` – games + team box scores from CFBD (needs `CFBD_API_KEY`).
3. `build_venues` – venue coordinates, dome flag, nearest ASOS station + distance.
4. `ingest_obs` – IEM observations for kickoff → +3.5 h, summarized into `weather_obs`.
5. `compute_splits` – baseline-relative splits into `team_splits`.
6. `report` – writes `reports/milestone1_sample_sizes.md`.

Edit `config/bins.yaml` and re-run: bin labels are recomputed from stored observations
without re-downloading anything.

Tests: `python -m pytest` (offline, synthetic data — they check the math, not real results).
