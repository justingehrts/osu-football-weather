"""Games, box scores and PPA for every tracked team, first_season to now -- on a call budget.

Two stages, because what we need to ask for depends on what the first stage returns:

  STAGE 1  one league-wide /games request per season (+1 for the postseason). Cheap, and
           it tells us every game any tracked team played, who played where, and the
           postseason weeks. We keep only games that involve a tracked team.
  STAGE 2  box scores (/games/teams) and play value (/ppa/games) for the games that still
           lack them. Past seasons: one request per TEAM (cheap when only a few teams are
           missing) or one per WEEK (returns the whole league, so it wins when many teams
           are missing) -- whichever costs fewer calls, with a slight preference for weeks
           (`week_vs_team_slack` in bins.yaml). The postseason always goes by week, since
           most teams don't play in it. Weeks/teams already cached on disk are skipped for free.

Data already in the database is never re-requested (`ingest_log` remembers finished
team-seasons), which is why the four teams loaded in earlier milestones cost nothing now.
"""
from collections import defaultdict

from .cfbd import CfbdClient, pick
from .common import connect, current_season, load_bins, load_yaml, tracked_teams


# --------------------------------------------------------------------------- parsing
def _stat(stats, *categories):
    by_cat = {s.get("category"): s.get("stat") for s in stats or []}
    for c in categories:
        if by_cat.get(c) not in (None, ""):
            return by_cat[c]
    return None


def _int(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


def parse_team_stats(entry):
    """One team's side of a /games/teams record -> team_games columns."""
    stats = entry.get("stats")
    ca = _stat(stats, "completionAttempts")          # looks like "21-33"
    pass_att = _int(ca.split("-")[1]) if ca and "-" in str(ca) else None
    rush_att = _int(_stat(stats, "rushingAttempts"))
    return {
        "points": _int(entry.get("points")),
        "pass_att": pass_att,
        "pass_yds": _int(_stat(stats, "netPassingYards")),
        "rush_att": rush_att,
        "rush_yds": _int(_stat(stats, "rushingYards")),
        "turnovers": _int(_stat(stats, "turnovers")),
        # approximate: CFBD doesn't give total plays here, and sacks are inside rush attempts
        "plays": (pass_att + rush_att) if pass_att is not None and rush_att is not None else None,
    }


def store_games(conn, games, tset, season, season_type):
    """Keep only games that involve a tracked team (the response may cover the whole league)."""
    n = 0
    for g in games:
        home, away = pick(g, "homeTeam", "home_team"), pick(g, "awayTeam", "away_team")
        if home not in tset and away not in tset:
            continue
        conn.execute(
            """INSERT OR REPLACE INTO games(game_id,season,week,season_type,kickoff_utc,kickoff_tbd,
                  completed,home_team,away_team,home_class,away_class,venue_id,neutral_site,
                  home_points,away_points) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (g["id"], season, g.get("week"), season_type, pick(g, "startDate", "start_date"),
             int(bool(pick(g, "startTimeTBD", "start_time_tbd", default=False))),
             int(bool(g.get("completed"))), home, away,
             pick(g, "homeClassification", "home_classification"),
             pick(g, "awayClassification", "away_classification"),
             pick(g, "venueId", "venue_id"),
             int(bool(pick(g, "neutralSite", "neutral_site", default=False))),
             pick(g, "homePoints", "home_points"), pick(g, "awayPoints", "away_points")))
        n += 1
    return n


def store_box_scores(conn, records, tset, known_games):
    wrote = 0
    for rec in records:
        if rec["id"] not in known_games:
            continue
        sides = rec.get("teams") or []
        for side in sides:
            name = pick(side, "school", "team")
            if name not in tset:
                continue
            other = next((pick(o, "school", "team") for o in sides if o is not side), None)
            row = parse_team_stats(side)
            conn.execute(
                """INSERT INTO team_games(game_id,team,opponent,home_away,points,plays,pass_att,pass_yds,
                      rush_att,rush_yds,turnovers) VALUES(?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(game_id,team) DO UPDATE SET opponent=excluded.opponent,
                     home_away=excluded.home_away, points=excluded.points, plays=excluded.plays,
                     pass_att=excluded.pass_att, pass_yds=excluded.pass_yds, rush_att=excluded.rush_att,
                     rush_yds=excluded.rush_yds, turnovers=excluded.turnovers""",
                (rec["id"], name, other, pick(side, "homeAway", "home_away"), row["points"], row["plays"],
                 row["pass_att"], row["pass_yds"], row["rush_att"], row["rush_yds"], row["turnovers"]))
            wrote += 1
    return wrote


def store_ppa(conn, records, tset, request_team=None):
    wrote = 0
    for p in records:
        off = (p.get("offense") or {}).get("overall")
        gid = pick(p, "gameId", "game_id")
        team = pick(p, "team", "school") or request_team
        if off is not None and gid is not None and team in tset:
            wrote += conn.execute("UPDATE team_games SET ppa_off=? WHERE game_id=? AND team=?",
                                  (off, gid, team)).rowcount
    return wrote


# --------------------------------------------------------------------------- planning
def stage1_requests(first, cur, today=None):
    """[(season, season_type)] -- league-wide /games requests."""
    from datetime import date
    month = (today or date.today()).month
    out = []
    for season in range(first, cur + 1):
        out.append((season, "regular"))
        if season < cur or month in (12, 1, 2):     # current postseason only exists Dec-Jan
            out.append((season, "postseason"))
    return out


def games_ttl(season, cur, bins):
    return bins["cfbd"]["current_season_ttl_hours"] if season >= cur else None


def _missing_games(conn, team):
    return conn.execute(
        """SELECT g.game_id, g.season, g.week, g.season_type FROM games g
           WHERE g.completed = 1 AND (g.home_team = ? OR g.away_team = ?)
             AND NOT EXISTS (SELECT 1 FROM team_games t WHERE t.game_id = g.game_id AND t.team = ?)""",
        (team, team, team)).fetchall()


def _unlogged_team_seasons(conn, team, cur):
    """Past regular seasons this team has games in but that were never loaded in full."""
    done = {r[0] for r in conn.execute("SELECT season FROM ingest_log WHERE team=?", (team,))}
    rows = conn.execute("""SELECT DISTINCT season FROM games WHERE season_type='regular' AND completed=1
                           AND (home_team=? OR away_team=?)""", (team, team)).fetchall()
    return sorted(r[0] for r in rows if r[0] not in done)


def loadable_teams(conn, teams, bins):
    """Drop FCS teams' history when configured (CFBD rarely has their box scores/PPA)."""
    if bins["cfbd"]["load_history_for_non_fbs"]:
        return list(teams)
    res = load_yaml("opponents.yaml")
    non_fbs = set(res.get("non_fbs") or [])
    return [t for t in teams if t not in non_fbs]


def stats_requests(conn, teams, cur, bins):
    """The exact stage-2 request list, given the games currently in the database.

    Each item: dict(kind='team'|'week', season, season_type, team|week, endpoints=('box','ppa'),
                    covers=[(team, season), ...] for the ingest_log).
    """
    slack = bins["cfbd"]["week_vs_team_slack"]
    reqs = []
    by_season = defaultdict(lambda: defaultdict(set))       # season -> team -> {weeks missing}
    post_weeks = defaultdict(set)                            # season -> {postseason weeks missing}
    for team in teams:
        miss = _missing_games(conn, team)
        unlogged = set(_unlogged_team_seasons(conn, team, cur))
        for gid, season, week, stype in miss:
            if stype == "postseason":
                post_weeks[season].add(week)
            elif season >= cur or season in unlogged:
                by_season[season][team].add(week)
    for season, per_team in sorted(by_season.items()):
        weeks = sorted({w for ws in per_team.values() for w in ws})
        if len(weeks) <= slack * len(per_team):                  # by week: whole league per call
            for w in weeks:
                reqs.append(dict(kind="week", season=season, season_type="regular", week=w,
                                 covers=[(t, season) for t in per_team]))
        else:                                                    # by team
            for t in sorted(per_team):
                reqs.append(dict(kind="team", season=season, season_type="regular", team=t,
                                 covers=[(t, season)]))
    for season, weeks in sorted(post_weeks.items()):
        for w in sorted(w for w in weeks if w is not None) or [None]:
            reqs.append(dict(kind="week", season=season, season_type="postseason", week=w, covers=[]))
    return reqs


def request_is_cached(client, r, endpoint, cur, bins, last_week):
    ttl = None
    if r["season"] >= cur:
        # finished weeks never change; only the latest one (and by-team pulls) can still move
        ttl = None if (r["kind"] == "week" and r["week"] is not None and r["week"] < last_week) \
            else bins["cfbd"]["current_season_ttl_hours"]
    path = "/games/teams" if endpoint == "box" else "/ppa/games"
    params = dict(year=r["season"], seasonType=r["season_type"])
    if endpoint == "ppa":
        params["excludeGarbageTime"] = "false"
    if r.get("week") is not None:
        params["week"] = r["week"]
    if r.get("team"):
        params["team"] = r["team"]
    return client.is_cached(path, ttl, **params), ttl


# --------------------------------------------------------------------------- running
def run_stage1(conn, client, teams, first, cur, bins, today=None):
    tset = set(teams)
    for season, stype in stage1_requests(first, cur, today):
        data = client.games(season, stype, ttl_hours=games_ttl(season, cur, bins))
        n = store_games(conn, data, tset, season, stype)
        print(f"games {season} {stype}: {n} tracked-team games")
    conn.commit()


def run_stage2(conn, client, teams, cur, bins):
    tset = set(teams)
    known = {r[0] for r in conn.execute("SELECT game_id FROM games")}
    last_week = conn.execute("SELECT COALESCE(MAX(week),0) FROM games WHERE season=? AND completed=1 "
                             "AND season_type='regular'", (cur,)).fetchone()[0]
    probed = set()          # request shapes already test-driven with ONE request
    for r in stats_requests(conn, teams, cur, bins):
        for endpoint in ("box", "ppa"):
            _, ttl = request_is_cached(client, r, endpoint, cur, bins, last_week)
            kw = dict(season_type=r["season_type"], week=r.get("week"), team=r.get("team"), ttl_hours=ttl)
            if endpoint == "box":
                records = client.game_team_stats(r["season"], **kw)
                wrote = store_box_scores(conn, records, tset, known)
            else:
                records = client.ppa_games(r["season"], **kw)
                wrote = store_ppa(conn, records, tset, r.get("team"))
            # Budget rule: test every new kind of request once before looping. If a response
            # comes back with data but we could not store any of it, our reading of that endpoint
            # is wrong -- stop now rather than burn the rest of the budget on it.
            shape = (endpoint, r["kind"], r["season_type"])
            if shape not in probed:
                probed.add(shape)
                if records and not wrote:
                    conn.commit()
                    raise SystemExit(f"PROBE FAILED for {shape}: {len(records)} records came back but none "
                                     f"matched a tracked game. First record keys: {sorted(records[0])}. "
                                     "Stopping before spending more calls.")
        for team, season in r["covers"]:
            if season < cur:
                conn.execute("INSERT OR REPLACE INTO ingest_log VALUES (?,?,datetime('now'))", (team, season))
        conn.commit()
        print(f"stats {r['season']} {r['season_type']} {r.get('team') or 'week ' + str(r.get('week'))}: ok")
    # a team-season counts as loaded once none of its regular games are missing any more
    for team in teams:
        miss = {(s) for _, s, _, st in _missing_games(conn, team) if st == "regular"}
        for season in _unlogged_team_seasons(conn, team, cur):
            if season < cur and season not in miss:
                conn.execute("INSERT OR REPLACE INTO ingest_log VALUES (?,?,datetime('now'))", (team, season))
    conn.commit()


def run(conn=None, client=None, today=None):
    conn = conn or connect()
    client = client or CfbdClient()
    bins, cfg = load_bins(), load_yaml("teams.yaml")
    cur = current_season(today)
    teams = loadable_teams(conn, tracked_teams(), bins)
    run_stage1(conn, client, tracked_teams(), cfg["first_season"], cur, bins, today)
    run_stage2(conn, client, teams, cur, bins)


if __name__ == "__main__":
    run()
