"""Opponent strength: CFBD SP+ ratings by season (ONE call per season returns every team).

Why SP+: for the opponent adjustment we need a strength number for EVERY opponent any
tracked team has played, not just the tracked teams. SP+ is a season-level, opponent-
adjusted rating with separate offense and defense parts for all FBS teams. Caveats: it is
end-of-season (includes the game itself -- a small leak), and FCS opponents have no rating.
Seasons already in the database cost nothing; only the current season is refreshed.
"""
from .cfbd import CfbdClient, pick
from .common import connect, current_season, load_bins, load_yaml


def parse_rating(rec):
    """-> (team, overall, offense, defense) or None."""
    team = rec.get("team")
    if not team or team == "nationalAverages":   # CFBD mixes a league-average row into the list
        return None
    return (team, pick(rec, "rating"), (rec.get("offense") or {}).get("rating"),
            (rec.get("defense") or {}).get("rating"))


def run(conn=None, client=None, skip_current=False):
    conn = conn or connect()
    client = client or CfbdClient()
    bins = load_bins()
    first, now = load_yaml("teams.yaml")["first_season"], current_season()
    for season in range(first, now + 1):
        have = conn.execute("SELECT COUNT(*) FROM team_ratings WHERE season=?", (season,)).fetchone()[0]
        if have and season < now:        # finished seasons never change
            continue
        if have and skip_current:        # in-progress ratings already on file; don't spend a call refreshing
            continue
        ttl = bins["cfbd"]["current_season_ttl_hours"] if season >= now else None
        recs = client.sp_ratings(season, ttl_hours=ttl)
        rows = [(season, *r) for r in map(parse_rating, recs) if r]
        conn.executemany("INSERT OR REPLACE INTO team_ratings VALUES (?,?,?,?,?)", rows)
        conn.commit()
        print(f"SP+ ratings {season}: {len(rows)} teams")
        if recs and not rows:
            print("  WARNING: ratings came back in an unexpected shape:", sorted(recs[0]))


if __name__ == "__main__":
    run()
