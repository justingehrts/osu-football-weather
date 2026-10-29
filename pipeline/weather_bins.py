"""Turn raw game-window weather into the bin labels defined in config/bins.yaml.

All thresholds come from the config. Values are rounded to whole mph / whole
degrees / hundredths of an inch first, so a 14.6 mph wind can't fall into the
gap between "moderate (max 14)" and "windy (min 15)".
"""


def classify_wind(sust_mph, gust_mph, cfg):
    if sust_mph is None:
        return None
    w = cfg["wind"]
    s = round(sust_mph)
    g = round(gust_mph) if gust_mph is not None else s  # no gust reported => no gusts
    if s >= w["windy"]["sustained_min"] or g >= w["windy"]["or_gust_min"]:
        return "windy"
    if s <= w["calm"]["sustained_max"] and g <= w["calm"]["gust_max"]:
        return "calm"
    return "moderate"  # everything between calm and windy


def classify_precip(total_in, cfg):
    if total_in is None:
        return None
    p = cfg["precip"]
    t = round(total_in, 2)  # trace amounts (0.0001) round to zero => "none"
    if t <= p["none"]["total_in_max"]:
        return "none"
    # bins.yaml has light "max 0.10" and steady "min 0.10": exactly 0.10 is ambiguous.
    # We call it steady (the heavier bin).
    if t >= p["steady"]["total_in_min"]:
        return "steady"
    return "light"


def classify_temp(temp_f, cfg):
    if temp_f is None:
        return None
    t = round(temp_f)
    for label, r in cfg["temperature"].items():
        if r.get("min", float("-inf")) <= t <= r.get("max", float("inf")):
            return label
    return None


def classify_all(row, cfg):
    return (classify_wind(row.get("wind_sust_max"), row.get("wind_gust_max"), cfg),
            classify_precip(row.get("precip_in_total"), cfg),
            classify_temp(row.get("temp_f_mean"), cfg))


def confidence(n, cfg):
    c = cfg["confidence"]
    if n < c["suppress_below_n"]:
        return "suppressed"
    if n < c["thin_below_n"]:
        return "thin"
    return "solid"
