"""Step 1: venue table + nearest ASOS station.

For every venue used by a tracked team since first_season we (a) check what the
CFBD venue record actually contains, (b) apply hand overrides, (c) find the
nearest ASOS station and (d) flag domes, bad coordinates and far stations.
"""
from datetime import date

from .cfbd import CfbdClient, pick
from .common import connect, haversine_mi, load_bins, load_yaml
from .stations import load_catalog, nearest_station

US_BOX = (24.0, 50.0, -125.0, -66.0)  # lat_min, lat_max, lon_min, lon_max (lower 48)


def read_coords(v):
    """CFBD has shipped coordinates both as latitude/longitude and as location{x,y}.
    Returns (lat, lon, source) or (None, None, None)."""
    lat, lon = pick(v, "latitude", "lat"), pick(v, "longitude", "lon", "lng")
    if lat is not None and lon is not None:
        return float(lat), float(lon), "cfbd:latitude/longitude"
    loc = v.get("location")
    if isinstance(loc, dict) and loc.get("x") is not None and loc.get("y") is not None:
        return float(loc["y"]), float(loc["x"]), "cfbd:location{x=lon,y=lat}"
    return None, None, None


def prune_unusable_weather(conn):
    """Drop stored weather for games whose venue is (now) a dome or has no station, so a
    corrected venue record also corrects past results."""
    conn.execute("""DELETE FROM weather_obs WHERE game_id IN (
        SELECT g.game_id FROM games g JOIN venues v ON v.venue_id = g.venue_id
        WHERE v.dome = 1 OR v.nearest_station IS NULL)""")


def run(conn=None, client=None):
    conn = conn or connect()
    bins, overrides = load_bins(), load_yaml("venue_overrides.yaml")
    far_mi = bins["quality"]["far_station_miles"]
    since = f'{load_yaml("teams.yaml")["first_season"]}-01-01'

    ids = [r[0] for r in conn.execute(
        "SELECT DISTINCT venue_id FROM games WHERE venue_id IS NOT NULL")]
    if not ids:
        print("No venues referenced by games yet -- run ingest_games first.")
        return
    client = client or CfbdClient()
    cfbd_venues = {v["id"]: v for v in client.venues()}
    if any(v not in cfbd_venues for v in ids) and client.is_cached("/venues"):
        # a venue we need isn't in the saved list (new stadium?) -> refresh the list once
        client.cache_path("/venues", {}).unlink()
        cfbd_venues = {v["id"]: v for v in client.venues()}
    sample = next(iter(cfbd_venues.values()), {})
    print("CFBD venue fields seen:", sorted(sample))  # so a field rename is obvious in logs
    catalog = load_catalog()

    for vid in ids:
        v = cfbd_venues.get(vid, {})
        o = overrides.get(vid) or overrides.get(str(vid)) or {}
        notes, abroad = [], False
        lat, lon, src = read_coords(v)
        if not v:
            notes.append("venue id not in CFBD /venues")
        if "lat" in o and "lon" in o:
            lat, lon, src = o["lat"], o["lon"], "override"
        if lat is None:
            notes.append("NO COORDINATES")
        elif (lat, lon) == (0, 0) or not (US_BOX[0] <= lat <= US_BOX[1] and US_BOX[2] <= lon <= US_BOX[3]):
            notes.append(f"outside lower 48 ({lat}, {lon}) -- no US station used, no weather splits")
            abroad = True
        dome_raw = pick(v, "dome", default=None)
        if dome_raw is None and "dome" not in o:
            notes.append("CFBD gave no dome value (treated as outdoor)")
        dome = int(bool(o["dome"] if "dome" in o else dome_raw))
        if o.get("note"):
            notes.append(o["note"])

        station = dist = far = None
        # A US station for a venue overseas (e.g. Dublin) would be someone else's weather.
        if not dome and lat is not None and not abroad:
            if o.get("station"):
                st = next((s for s in catalog if s["id"] == o["station"]), None)
                station = o["station"]
                dist = haversine_mi(lat, lon, st["lat"], st["lon"]) if st else None
            else:
                hit = nearest_station(lat, lon, catalog, since)
                station, dist = hit if hit else (None, None)
            if station is None:
                notes.append("no ASOS station found")
            elif dist is not None and dist > far_mi:
                far = 1
                notes.append(f"FAR STATION: {dist:.1f} mi (> {far_mi})")
        conn.execute(
            """INSERT INTO venues(venue_id,name,lat,lon,dome,nearest_station,station_dist_mi,
                                  station_far,coord_source,notes,first_seen)
               VALUES(?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(venue_id) DO UPDATE SET name=excluded.name, lat=excluded.lat,
                 lon=excluded.lon, dome=excluded.dome, nearest_station=excluded.nearest_station,
                 station_dist_mi=excluded.station_dist_mi, station_far=excluded.station_far,
                 coord_source=excluded.coord_source, notes=excluded.notes,
                 first_seen=COALESCE(venues.first_seen, excluded.first_seen)""",
            (vid, v.get("name"), lat, lon, dome, station,
             round(dist, 1) if dist is not None else None, far or 0, src, "; ".join(notes),
             date.today().isoformat()))
    prune_unusable_weather(conn)
    conn.commit()
    flagged = conn.execute("SELECT COUNT(*) FROM venues WHERE notes != ''").fetchone()[0]
    print(f"{len(ids)} venues processed, {flagged} with flags (see venues.notes).")


if __name__ == "__main__":
    run()
