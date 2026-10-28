"""Thin CollegeFootballData client.

NOTE: written against the documented v1 REST shape but NOT yet run against the
live API (the build sandbox could not reach it). Field readers below accept the
alternate spellings CFBD has used, and ingest prints what it finds so a first
real run will show quickly if anything has moved.
"""
import os

from .common import http_session

BASE = os.environ.get("CFBD_BASE_URL", "https://api.collegefootballdata.com")


class CfbdClient:
    def __init__(self):
        key = os.environ.get("CFBD_API_KEY")
        if not key:
            raise SystemExit("CFBD_API_KEY is not set. Add it as an environment variable "
                             "(locally) or a repository secret (GitHub Actions).")
        self.s = http_session()
        self.s.headers["Authorization"] = f"Bearer {key}"

    def get(self, path, **params):
        r = self.s.get(f"{BASE}{path}", params=params, timeout=60)
        r.raise_for_status()
        return r.json()

    def games(self, year, team, season_type):
        return self.get("/games", year=year, team=team, seasonType=season_type)

    def game_team_stats(self, year, team, season_type):
        return self.get("/games/teams", year=year, team=team, seasonType=season_type)

    def ppa_games(self, year, team):
        return self.get("/ppa/games", year=year, team=team, excludeGarbageTime="false")

    def sp_ratings(self, year):
        return self.get("/ratings/sp", year=year)

    def venues(self):
        return self.get("/venues")


def pick(d, *names, default=None):
    """First present, non-None key among alternate spellings (camelCase / snake_case)."""
    for n in names:
        if d.get(n) is not None:
            return d[n]
    return default
