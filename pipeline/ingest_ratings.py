"""Opponent strength: CFBD SP+ ratings by season (one call per season, all teams).

Why SP+: for the opponent adjustment we need a strength number for EVERY opponent, but
we only have game data for the four tracked teams. SP+ is a season-level, tempo- and
opponent-adjusted team rating with separate offense and defense parts, available for all
FBS teams. Caveat: the rating is end-of-season, so it includes the game itself (a small
amount of leakage) -- fine for exploring, worth knowing about.
FCS opponents have no SP+ rating; those games are left out of adjusted numbers only.
"""
from .cfbd import CfbdClient, pick
from .common import connect, current_season, load_yaml


def parse_rating(rec):
    """-> (team, overall, offense, defense) or None. Tolerates the shapes CFBD has used."""
    team = rec.get("team")
    if not team or team == "nationalAverages":   # CFBD mixes a league-average row into the list
        return None
    off = (rec.get("offense") or {}).get("rating")
    de = (rec.get("defense") or {}).get("rating")
    return team, pick(rec, "rating"), off, de


def run(conn=None, client=None):
    conn = conn or connect()
    client = client or CfbdClient()
    first, now = load_yaml("teams.yaml")["first_season"], current_season()
    for season in range(first, now + 1):
        have = conn.execute("SELECT COUNT(*) FROM team_ratings WHERE season=?", (season,)).fetchone()[0]
        if have and season < now:        # finished seasons never change; current one refreshes
            continue
        recs = client.sp_ratings(season)
        rows = [(season, *r) for r in map(parse_rating, recs) if r]
        conn.executemany("INSERT OR REPLACE INTO team_ratings VALUES (?,?,?,?,?)", rows)
        conn.commit()
        print(f"SP+ ratings {season}: {len(rows)} teams")
        if recs and not rows:
            print("  WARNING: ratings came back in an unexpected shape:", sorted(recs[0]))


if __name__ == "__main__":
    run()
