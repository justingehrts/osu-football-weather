"""PNG of the Gameday Card, sized for TV graphics (1920x1080, 16:9)."""
import io

from PIL import Image, ImageDraw, ImageFont

from . import logic

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


def render_card_png(view):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((80, 50), view["title"].upper(), font=_font(64, True), fill=FG)
    sub = " · ".join(x for x in [view.get("venue")] if x)
    if sub:
        d.text((80, 130), sub, font=_font(32), fill=MUTED)
    x = 80
    for b in view.get("badges", []):
        w = d.textlength(b, font=_font(36, True)) + 44
        d.rounded_rectangle((x, 185, x + w, 245), radius=30, fill=(46, 64, 90))
        d.text((x + 22, 194), b, font=_font(36, True), fill=FG)
        x += w + 16
    y = 275
    for line in _wrap(d, view["takeaway"], _font(36), W - 160)[:4]:
        d.text((80, y), line, font=_font(36), fill=FG)
        y += 48
    sec = (view.get("sections") or [None])[0]
    if sec:
        y = max(y + 20, 500)
        d.text((80, y - 50), f"{sec['title'].upper()}  ·  vs. all other games", font=_font(30, True), fill=MUTED)
        cols = [(view["focal"], 80), (view["opponent"], 700), (logic.POOLED, 1320)]
        for team, x0 in cols:
            name = f"All {view['pooled_n']} loaded teams" if team == logic.POOLED else team
            d.rounded_rectangle((x0, y, x0 + 520, y + 440), radius=24, fill=PANEL)
            d.text((x0 + 30, y + 22), name, font=_font(38, True), fill=FG)
            rows = [r for r in sec["rows"] if r.team == team and r.metric in ("pass_eff", "points")]
            yy = y + 100
            if rows and rows[0].status == "not_loaded":
                d.text((x0 + 30, yy), "data not loaded yet", font=_font(32), fill=MUTED)
            for r in rows:
                d.text((x0 + 30, yy), r.metric_name, font=_font(28), fill=MUTED)
                d.text((x0 + 30, yy + 36), r.text(), font=_font(48, True), fill=FG)
                bg, fg = CHIP.get(r.label, CHIP[logic.FEW])
                label = f"{r.label}  ·  n={r.n}"
                tw = d.textlength(label, font=_font(26, True)) + 28
                d.rounded_rectangle((x0 + 30, yy + 100, x0 + 30 + tw, yy + 140), radius=20, fill=bg)
                d.text((x0 + 44, yy + 104), label, font=_font(26, True), fill=fg)
                yy += 170
    d.text((80, H - 60), "Exploratory history, not a prediction. Controlled for opponent strength, month and home/away.",
           font=_font(24), fill=MUTED)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()
