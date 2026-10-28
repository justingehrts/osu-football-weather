# OSU Football Weather: the app

Read-only Streamlit app. It never writes to the databases; all statistics are precomputed by the pipeline.

```
pip install -r app/requirements.txt
streamlit run app/streamlit_app.py
```

* **Gameday Card** (landing page): the next Ohio State game, the forecast as badges, a one-sentence takeaway,
  Ohio State vs. the opponent, What-If controls, copy-as-text / CSV / PNG exports.
* **Team Explorer**: any loaded team and condition. Deferred teams say "data not loaded yet".
* **Evidence**: the games behind any number, plus the snow games.
* **Methodology**: bins, the two yardsticks, opponent adjustment, evidence labels, limits.

Paths can be overridden with `OSU_DB_PATH`, `OSU_FORECAST_DB_PATH` and `OSU_CONFIG_DIR`.
Views are shareable: your game, What-If choices and team are kept in the page address.
Do not deploy from a branch: the live app runs from `main` after review.
