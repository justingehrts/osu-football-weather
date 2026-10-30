"""Charts (Altair; no Streamlit import, so the specs are unit tested).

condition_chart: for each headline stat, one row of dots per team. The dot is the adjusted change ("vs. all other
games"); the bar is the 90% range. The axis is flipped where lower is better, so RIGHT IS ALWAYS BETTER and the
dashed line is "no difference". Interval NUMBERS are deliberately left out of the tooltip (the rule is that
interval numbers live in expanders); the bar shows the uncertainty visually.
"""
import altair as alt
import pandas as pd

from .logic import CLEAR, LEANS, NONE

LABEL_COLORS = {CLEAR: "#0b4f8a", LEANS: "#d99a14", NONE: "#9aa3ad"}


def condition_chart(df):
    """One small chart per stat (a list, in card order), each stretching to the page width so it also fits a phone.
    The legend is drawn once by the page (same colors as the evidence chips), not inside every chart."""
    if df is None or df.empty:
        return []
    out = []
    for metric, part in df.sort_values(["metric_order", "who_order"]).groupby("metric_order", sort=True):
        part = part.copy()
        domain = [l for l in (CLEAR, LEANS, NONE) if l in set(df.label)]
        color = alt.Color("label:N", scale=alt.Scale(domain=domain, range=[LABEL_COLORS[l] for l in domain]), legend=None)
        y = alt.Y("who:N", title=None, sort=alt.EncodingSortField("who_order"), axis=alt.Axis(labelLimit=130))
        x = alt.X("lo:Q", title=part["axis"].iloc[0] if "axis" in part else "◄ worse  ·  better ►", scale=alt.Scale(zero=True, nice=True), axis=alt.Axis(tickCount=4))
        base = alt.Chart(part)
        zero = base.mark_rule(strokeDash=[4, 3], color="#6b7480").encode(x="zero:Q")
        rng = base.mark_rule(strokeWidth=4, opacity=0.45).encode(x=x, x2="hi:Q", y=y, color=color)
        dot = base.mark_point(filled=True, size=140, opacity=1).encode(
            x="better:Q", y=y, color=color,
            tooltip=[alt.Tooltip("who:N", title="Team"), alt.Tooltip("metric:N", title="Stat"),
                     alt.Tooltip("in_words:N", title="Change"), alt.Tooltip("n:Q", title="Games"),
                     alt.Tooltip("label:N", title="Evidence")])
        title = alt.TitleParams(part.metric.iloc[0], anchor="start", fontSize=13, fontWeight="bold")
        out.append(alt.layer(zero, rng, dot).properties(height=alt.Step(26), width="container", title=title)
                   .configure_view(stroke=None))
    return out


def hourly_chart(hours, bins):
    """Wind (bars), gusts (dots) and chance of rain (line, right axis) for each hour of the game window,
    with dashed lines where 'windy' starts."""
    if not hours:
        return None
    df = pd.DataFrame(hours)
    df["time"] = pd.to_datetime(df["time"], utc=True).dt.tz_convert("America/New_York").dt.strftime("%-I %p")
    order = list(df["time"])
    w = bins["wind"]["windy"]
    x = alt.X("time:N", sort=order, title="Hour (ET)", axis=alt.Axis(labelAngle=0))
    bars = alt.Chart(df).mark_bar(color="#5b7fa6", opacity=0.75).encode(
        x=x, y=alt.Y("wind:Q", title="Wind / gusts (mph)"),
        tooltip=[alt.Tooltip("time:N", title="Hour"), alt.Tooltip("wind:Q", title="Sustained (mph)"),
                 alt.Tooltip("gust:Q", title="Gusts (mph)"), alt.Tooltip("pop:Q", title="Chance of rain (%)"),
                 alt.Tooltip("rain_in:Q", title="Rain (in.)"), alt.Tooltip("temp_f:Q", title="Temp (°F)")])
    gusts = alt.Chart(df).mark_point(filled=True, color="#1d2733", size=70, shape="triangle-up").encode(x=x, y="gust:Q")
    lines = alt.Chart(pd.DataFrame({"y": [w["sustained_min"], w["or_gust_min"]],
                                    "what": [f"windy: sustained {w['sustained_min']}+", f"windy: gusts {w['or_gust_min']}+"]})
                      ).mark_rule(strokeDash=[5, 4], color="#b0413e").encode(y="y:Q", tooltip="what:N")
    left = alt.layer(bars, gusts, lines)
    rain = alt.Chart(df).mark_line(point=True, color="#2a9d8f").encode(
        x=x, y=alt.Y("pop:Q", title="Chance of rain (%)", scale=alt.Scale(domain=[0, 100])))
    return alt.layer(left, rain).resolve_scale(y="independent").properties(height=200)


def trend_chart(history):
    """How the forecast for this game has moved from pull to pull (one point per usable pull, oldest on the left)."""
    if history is None or len(history) < 2:
        return None
    df = history.sort_values("snapshot_utc").copy()
    df["pulled"] = pd.to_datetime(df["snapshot_utc"], utc=True).dt.tz_convert("America/New_York").dt.strftime("%a %-I %p")
    order = list(dict.fromkeys(df["pulled"]))
    long = df.melt(id_vars=["pulled"], value_vars=["wind_sust", "wind_gust", "precip_prob"], var_name="what", value_name="value")
    long["what"] = long["what"].map({"wind_sust": "Wind (mph)", "wind_gust": "Gusts (mph)", "precip_prob": "Chance of rain (%)"})
    return alt.Chart(long).mark_line(point=True).encode(
        x=alt.X("pulled:N", sort=order, title="Forecast pulled (ET)", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("value:Q", title=None),
        color=alt.Color("what:N", title=None, legend=alt.Legend(orient="top"),
                        scale=alt.Scale(domain=["Wind (mph)", "Gusts (mph)", "Chance of rain (%)"],
                                        range=["#5b7fa6", "#1d2733", "#2a9d8f"])),
        tooltip=[alt.Tooltip("what:N", title="What"), alt.Tooltip("value:Q", format=".0f", title="Value"),
                 alt.Tooltip("pulled:N", title="Pulled")]).properties(height=320)   # Streamlit counts legend + axes in this
