"""Game times in the stadium's LOCAL time, with Eastern beside it when they differ ("4:30 PM PT (7:30 PM ET)").
No Streamlit import, so it is unit tested. A venue with no stored time zone falls back to ET (no parenthetical)."""
from zoneinfo import ZoneInfo

import pandas as pd

ET = "America/New_York"
# the everyday name for a zone is its STANDARD offset ("PT" all year, not PST/PDT); anything else uses its own abbreviation
GENERIC = {-5: "ET", -6: "CT", -7: "MT", -8: "PT", -9: "AKT", -10: "HT"}


def _local(ts, tz):
    t = pd.to_datetime(ts, utc=True)
    return t.tz_convert(ZoneInfo(tz if isinstance(tz, str) and tz else ET)), t.tz_convert(ZoneInfo(ET))   # (missing zone = ET)


def zone_name(local):
    standard = (local.utcoffset() - (local.dst() or pd.Timedelta(0))).total_seconds() / 3600
    return GENERIC.get(standard) or local.tzname()


def game_time(ts, tz, fmt="%a %b %d, %-I:%M %p", et_fmt="%-I:%M %p"):
    """'Sat Oct 31, 4:30 PM PT (7:30 PM ET)', or 'Sat Oct 31, 7:30 PM ET' when the game is on Eastern time.
    If the ET clock is on a different day (a late kickoff out west), the ET part names the day too."""
    local, et = _local(ts, tz)
    if local.utcoffset() == et.utcoffset():
        return f"{local.strftime(fmt)} ET"
    if et.date() != local.date():
        et_fmt = "%a " + et_fmt
    return f"{local.strftime(fmt)} {zone_name(local)} ({et.strftime(et_fmt)} ET)"


def local_day(ts, tz, fmt="%b %d"):
    """The date as it is at the stadium (a 10 PM PT kickoff is still that evening, though it is already tomorrow in ET)."""
    return _local(ts, tz)[0].strftime(fmt)


def hour_label(ts, tz):
    """Axis label for one hour: '4 PM PT|(7 PM ET)' (the '|' splits it onto two lines), or just '7 PM' on Eastern time."""
    local, et = _local(ts, tz)
    if local.utcoffset() == et.utcoffset():
        return local.strftime("%-I %p")
    return f"{local.strftime('%-I %p')} {zone_name(local)}|({et.strftime('%-I %p')} ET)"


def zone_title(tz, ts):
    """'ET' or 'PT (ET shown in brackets)' for an axis title."""
    local, et = _local(ts, tz)
    return "ET" if local.utcoffset() == et.utcoffset() else f"{zone_name(local)}, with ET in brackets"
