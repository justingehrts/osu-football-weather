"""IEM ASOS station catalog + nearest-station lookup."""
import json
import re

from .common import CACHE_DIR, haversine_mi, http_session

IEM = "https://mesonet.agron.iastate.edu"
CATALOG = CACHE_DIR / "asos_stations.json"
US_STATE_NET = re.compile(r"^[A-Z]{2}_ASOS$")  # e.g. OH_ASOS (skips foreign networks)


def load_catalog(refresh=False):
    """All US ASOS stations, cached on disk (the list barely changes)."""
    if CATALOG.exists() and not refresh:
        return json.loads(CATALOG.read_text())
    s = http_session()
    nets = s.get(f"{IEM}/geojson/networks.geojson", timeout=60).json()["features"]
    out = []
    for net in (n["id"] for n in nets if US_STATE_NET.match(n["id"])):
        feats = s.get(f"{IEM}/geojson/network/{net}.geojson", timeout=60).json()["features"]
        for f in feats:
            p, (lon, lat) = f["properties"], f["geometry"]["coordinates"]
            out.append({
                "id": p["sid"], "name": p.get("sname"), "network": net,
                "lat": lat, "lon": lon,
                "begin": p.get("archive_begin"), "end": p.get("archive_end"),
                # IEM lists small AWOS sites inside the *_ASOS networks too. AWOS precip
                # is much less reliable, so we skip them.
                "is_awos": (p.get("attributes") or {}).get("IS_AWOS") == "1",
            })
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(json.dumps(out))
    return out


def nearest_station(lat, lon, catalog, need_since):
    """Closest true-ASOS station that has been reporting since `need_since` (YYYY-MM-DD)
    and is still reporting. Requiring a long record keeps the same station for every
    season instead of a nearer one that only started last year."""
    best = None
    for st in catalog:
        if st["is_awos"] or st["end"] is not None:
            continue
        if not st["begin"] or st["begin"] > need_since:
            continue
        d = haversine_mi(lat, lon, st["lat"], st["lon"])
        if best is None or d < best[1]:
            best = (st["id"], d)
    return best  # (station_id, miles) or None
