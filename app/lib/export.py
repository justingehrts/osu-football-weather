"""PNG of the Gameday Card, sized for TV graphics (1920x1080, 16:9)."""
import io

from PIL import Image, ImageDraw, ImageFont

from . import colors, logic

W, H = 1920, 1080
BG, FG, MUTED, PANEL = (16, 24, 36), (255, 255, 255), (170, 182, 198), (28, 40, 58)
CHIP = {logic.CLEAR: ((11, 79, 138), (255, 255, 255)), logic.LEANS: ((242, 177, 52), (30, 30, 30)),
        logic.NONE: ((217, 221, 227), (30, 30, 30)), logic.FEW: ((240, 241, 243), (90, 90, 90)),
        logic.CONTEXT: ((230, 220, 242), (59, 42, 87))}


def _font(size, bold=False):
    for name in (("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), ("Arial Bold.ttf" if bold else "Arial.ttf")):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def _wrap(draw, text, font, width):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    return lines + ([cur] if cur else [])


def fit_lines(draw, text, width, sizes=(36, 32, 28, 24), max_lines=4):
    """Wrap text to the width, shrinking the font until it fits in max_lines. Never drops words: if even the
    smallest size needs more lines, they are all kept (the layout below then moves down)."""
    for size in sizes:
        lines = _wrap(draw, text, _font(size), width)
        if len(lines) <= max_lines:
            return size, lines
    return sizes[-1], lines


def render_card_png(view):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    x = 80
    f64 = _font(64, True)
    for part, is_team in ((view["away_team"], True), (view["joiner"].upper(), False), (view["home_team"], True)):
        w = d.textlength(part, font=f64)
        if is_team:
            c = colors.colors_for(part)
            d.rounded_rectangle((x, 38, x + w + 56, 126), radius=18, fill=colors.rgb(c["bg"]))
            d.text((x + 28, 46), part, font=f64, fill=colors.rgb(c["fg"]))
            x += w + 56 + 28
        else:
            d.text((x, 46), part, font=f64, fill=MUTED)
            x += w + 28
    sub = " · ".join(x for x in [view.get("venue")] if x)
    if sub:
        d.text((80, 140), sub, font=_font(32), fill=MUTED)
    x = 80
    for b in view.get("badges", []):
        w = d.textlength(b, font=_font(36, True)) + 44
        d.rounded_rectangle((x, 185, x + w, 245), radius=30, fill=(46, 64, 90))
        d.text((x + 22, 194), b, font=_font(36, True), fill=FG)
        x += w + 16
    size, lines = fit_lines(d, view["takeaway"], W - 160)
    y = 275
    for line in lines:
        d.text((80, y), line, font=_font(size), fill=FG)
        y += int(size * 1.33)
    sec = (view.get("sections") or [None])[0]
    if sec:
        y = max(y + 70, 520)                           # cards start below the text, with room for the heading
        panel_h = min(480, H - 90 - y)                 # never run into the footer line
        step = (panel_h - 100) // 2
        d.text((80, y - 48), f"{sec['title'].upper()}  ·  vs. all other games", font=_font(30, True), fill=MUTED)
        cols = [(view["focal"], 80), (view["opponent"], 700), (logic.POOLED, 1320)]
        for team, x0 in cols:
            name = f"All {view['pooled_n']} loaded teams" if team == logic.POOLED else team
            d.rounded_rectangle((x0, y, x0 + 520, y + panel_h), radius=24, fill=PANEL)
            if team == logic.POOLED:                      # the reference line stays neutral
                d.text((x0 + 30, y + 22), name, font=_font(38, True), fill=FG)
            else:
                c, f38 = colors.colors_for(team), _font(38, True)
                w = d.textlength(name, font=f38)
                d.rounded_rectangle((x0 + 22, y + 14, x0 + 22 + w + 36, y + 76), radius=12, fill=colors.rgb(c["bg"]))
                d.text((x0 + 40, y + 20), name, font=f38, fill=colors.rgb(c["fg"]))
            rows = [r for r in sec["rows"] if r.team == team and r.metric in ("pass_eff", "points")]
            yy = y + 100
            if rows and rows[0].status == "not_loaded":
                d.text((x0 + 30, yy), "data not loaded yet", font=_font(32), fill=MUTED)
            for r in rows:
                d.text((x0 + 30, yy), r.metric_name, font=_font(28), fill=MUTED)
                # the change in words ("1.72 fewer yds/pass"), shrunk to fit the panel; the signed number if no words
                big = r.extra.get("words_short") or r.text()
                size = next((s for s in (46, 40, 34, 30) if d.textlength(big, font=_font(s, True)) <= 460), 30)
                d.text((x0 + 30, yy + 36 + (46 - size) // 2), big, font=_font(size, True), fill=FG)
                bg, fg = CHIP.get(r.label, CHIP[logic.FEW])
                label = f"{r.label}  ·  n={r.n}"
                tw = d.textlength(label, font=_font(26, True)) + 28
                d.rounded_rectangle((x0 + 30, yy + 96, x0 + 30 + tw, yy + 136), radius=20, fill=bg)
                d.text((x0 + 44, yy + 100), label, font=_font(26, True), fill=fg)
                if r.extra.get("game_terms_short"):
                    d.text((x0 + 30, yy + 144), r.extra["game_terms_short"], font=_font(24), fill=MUTED)
                yy += step
    d.text((80, H - 60), "Exploratory history, not a prediction. Controlled for opponent strength, month and home/away.",
           font=_font(24), fill=MUTED)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()
