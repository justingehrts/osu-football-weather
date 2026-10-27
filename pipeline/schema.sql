-- Tables follow the agreed schema; columns marked (+) are small additions.
CREATE TABLE IF NOT EXISTS venues (
  venue_id INTEGER PRIMARY KEY,
  name TEXT, lat REAL, lon REAL,
  dome INTEGER,                 -- 1 = indoor / excluded from weather splits
  nearest_station TEXT,
  station_dist_mi REAL,
  station_far INTEGER,          -- (+) 1 if farther than quality.far_station_miles
  coord_source TEXT,            -- (+) where the coordinates came from
  notes TEXT                    -- (+) data-quality flags, semicolon separated
);
CREATE TABLE IF NOT EXISTS games (
  game_id INTEGER PRIMARY KEY,
  season INTEGER, week INTEGER,
  season_type TEXT,             -- (+) regular / postseason
  kickoff_utc TEXT,
  kickoff_tbd INTEGER,          -- (+) 1 = CFBD has no real kickoff time yet
  completed INTEGER,            -- (+)
  home_team TEXT, away_team TEXT,
  venue_id INTEGER, neutral_site INTEGER,
  home_points INTEGER, away_points INTEGER
);
CREATE TABLE IF NOT EXISTS weather_obs (
  game_id INTEGER PRIMARY KEY,
  station TEXT, window_start TEXT, window_end TEXT,
  temp_f_mean REAL, wind_sust_max REAL, wind_gust_max REAL,
  precip_in_total REAL, snow_flag INTEGER, vis_min REAL, n_obs INTEGER,
  weather_ok INTEGER,           -- (+) 1 if n_obs >= quality.min_obs_in_window
  wind_bin TEXT, precip_bin TEXT, temp_bin TEXT   -- (+) labels from bins.yaml
);
CREATE TABLE IF NOT EXISTS team_games (
  game_id INTEGER, team TEXT, opponent TEXT, home_away TEXT,
  points INTEGER, plays INTEGER, pass_att INTEGER, pass_yds INTEGER,
  rush_att INTEGER, rush_yds INTEGER, turnovers INTEGER, ppa_off REAL,
  PRIMARY KEY (game_id, team)
);
-- Never overwritten: every forecast pull is a new row (used from milestone 2).
-- (+) Which team-seasons have been pulled in full. Needed because a team's rows can also be
-- created while pulling ANOTHER team's schedule (e.g. Oregon-vs-Ohio State), which must not
-- count as "Oregon's season is done".
CREATE TABLE IF NOT EXISTS ingest_log (
  team TEXT, season INTEGER, finished_utc TEXT, PRIMARY KEY (team, season)
);
CREATE TABLE IF NOT EXISTS forecast_snapshots (
  snapshot_utc TEXT, game_id INTEGER,
  wind_sust REAL, wind_gust REAL, precip_prob REAL, precip_amt REAL,
  temp_f REAL, source TEXT
);
CREATE TABLE IF NOT EXISTS team_splits (
  team TEXT, scope TEXT,        -- (+) 'all' or 'ex2020'
  bin_type TEXT, bin_value TEXT, metric TEXT,
  value REAL, baseline REAL, delta REAL, n INTEGER,
  confidence TEXT               -- (+) suppressed / thin / solid
);

DROP VIEW IF EXISTS team_game_weather;
CREATE VIEW team_game_weather AS
SELECT tg.*, g.season, g.week, g.season_type, g.kickoff_utc, g.venue_id, g.neutral_site,
       v.dome, v.station_far, v.station_dist_mi,
       w.station, w.temp_f_mean, w.wind_sust_max, w.wind_gust_max, w.precip_in_total,
       w.snow_flag, w.vis_min, w.n_obs, w.weather_ok,
       w.wind_bin, w.precip_bin, w.temp_bin
FROM team_games tg
JOIN games g ON g.game_id = tg.game_id
LEFT JOIN venues v ON v.venue_id = g.venue_id
LEFT JOIN weather_obs w ON w.game_id = tg.game_id;
