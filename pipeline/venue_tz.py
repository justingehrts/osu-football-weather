"""Venue time zones, so the app can show a game's times in the stadium's local time (with ET beside it).

Computed from each venue's coordinates with the `timezonefinder` package (offline: no web calls) and stored in
venues.tz. Only venues with no zone yet are filled, so this is cheap to run every time and never changes a stored value.
Run by build_venues; also runnable alone:  python -m pipeline.venue_tz
"""
from .common import connect


def fill_missing(conn):
    """Set venues.tz where it is empty. Returns how many were filled. Skips quietly (the app falls back to ET) if
    the package isn't installed or a venue has no coordinates."""
    try:
        from timezonefinder import TimezoneFinder
    except ImportError:
        print("timezonefinder is not installed; venue time zones left empty (the app shows ET).")
        return 0
    tf = TimezoneFinder()
    todo = conn.execute("SELECT venue_id, lat, lon FROM venues WHERE tz IS NULL AND lat IS NOT NULL AND lon IS NOT NULL").fetchall()
    filled = 0
    for vid, lat, lon in todo:
        zone = tf.timezone_at(lat=lat, lng=lon)
        if zone:
            conn.execute("UPDATE venues SET tz = ? WHERE venue_id = ?", (zone, vid))
            filled += 1
    conn.commit()
    return filled


if __name__ == "__main__":
    c = connect()
    print(f"filled {fill_missing(c)} venue time zones")
