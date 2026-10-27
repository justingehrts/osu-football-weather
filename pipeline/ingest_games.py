"""Step 2: games + team-level box score stats for every tracked team, first_season to now.

Incremental: finished past seasons already in the database are skipped; the
current season is always re-pulled (new results, corrected stats).
"""
from .cfbd import CfbdClient, pick
from .common import connect, current_season, load_yaml, tracked_teams

SEASON_TYPES = ("regular", "postseason")


def _stat(stats, *categories):
    """CFBD box score = list of {category, stat}. Return the first matching category as text."""
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


def run(conn=None, client=None, seasons=None, full=False):
    conn = conn or connect()
    client = client or CfbdClient()
    teams = tracked_teams()
    first = load_yaml("teams.yaml")["first_season"]
    now = current_season()
    seasons = seasons or range(first, now + 1)
    tset = set(teams)

    for team in teams:
        for season in seasons:
            if not full and season < now and conn.execute(
                    """SELECT COUNT(*) FROM team_games tg JOIN games g USING(game_id)
                       WHERE tg.team=? AND g.season=? AND g.completed=1""",
                    (team, season)).fetchone()[0] >= 1:
                continue
            for st in SEASON_TYPES:
                for g in client.games(season, team, st):
                    gid = g["id"]
                    start = pick(g, "startDate", "start_date")
                    conn.execute(
                        """INSERT OR REPLACE INTO games(game_id,season,week,season_type,kickoff_utc,
                              kickoff_tbd,completed,home_team,away_team,venue_id,neutral_site,
                              home_points,away_points) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (gid, season, g.get("week"), st, start,
                         int(bool(pick(g, "startTimeTBD", "start_time_tbd", default=False))),
                         int(bool(g.get("completed"))),
                         pick(g, "homeTeam", "home_team"), pick(g, "awayTeam", "away_team"),
                         pick(g, "venueId", "venue_id"),
                         int(bool(pick(g, "neutralSite", "neutral_site", default=False))),
                         pick(g, "homePoints", "home_points"), pick(g, "awayPoints", "away_points")))
                for rec in client.game_team_stats(season, team, st):
                    sides = rec.get("teams") or []
                    for side in sides:
                        name = pick(side, "school", "team")
                        if name not in tset:
                            continue
                        other = next((pick(o, "school", "team") for o in sides if o is not side), None)
                        row = parse_team_stats(side)
                        conn.execute(
                            """INSERT INTO team_games(game_id,team,opponent,home_away,points,plays,
                                  pass_att,pass_yds,rush_att,rush_yds,turnovers)
                               VALUES(?,?,?,?,?,?,?,?,?,?,?)
                               ON CONFLICT(game_id,team) DO UPDATE SET opponent=excluded.opponent,
                                 home_away=excluded.home_away, points=excluded.points,
                                 plays=excluded.plays, pass_att=excluded.pass_att,
                                 pass_yds=excluded.pass_yds, rush_att=excluded.rush_att,
                                 rush_yds=excluded.rush_yds, turnovers=excluded.turnovers""",
                            (rec["id"], name, other, pick(side, "homeAway", "home_away"),
                             row["points"], row["plays"], row["pass_att"], row["pass_yds"],
                             row["rush_att"], row["rush_yds"], row["turnovers"]))
            # Expected points added per play (offense). Optional: skip quietly if the call fails.
            try:
                for p in client.ppa_games(season, team):
                    off = (p.get("offense") or {}).get("overall")
                    gid = pick(p, "gameId", "game_id")
                    if off is not None and gid is not None:
                        conn.execute("UPDATE team_games SET ppa_off=? WHERE game_id=? AND team=?",
                                     (off, gid, team))
            except Exception as e:  # noqa: BLE001 - PPA is a nice-to-have, never block ingest
                print(f"  (PPA skipped for {team} {season}: {e})")
            conn.commit()
            print(f"{team} {season}: ok")


if __name__ == "__main__":
    run()
