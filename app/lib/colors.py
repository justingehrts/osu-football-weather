"""Team-name chips in school colors, for the 'header' places only (card headers and the PNG).

Colors come from config/team_colors.yaml (never hard-coded here); a test checks every pair is legible.
"""
from functools import lru_cache
from html import escape

import yaml

from . import config

NEUTRAL = {"fg": "#1D2733", "bg": "#E9ECEF"}          # unknown teams, and the pooled 'all N teams' reference


@lru_cache(maxsize=1)
def load_colors(mtime=0):
    f = config.CONFIG_DIR / "team_colors.yaml"
    return yaml.safe_load(f.read_text()) or {} if f.exists() else {}


def colors_for(team):
    c = load_colors().get(team) or NEUTRAL
    return {"fg": c["fg"], "bg": c["bg"]}


def _luminance(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4   # noqa: E731
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast_ratio(fg, bg):
    """WCAG contrast ratio between two hex colors (4.5 is the minimum for normal text)."""
    hi, lo = sorted((_luminance(fg), _luminance(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def chip_html(team, label=None):
    c = colors_for(team)
    return (f'<span class="team-chip" style="color:{c["fg"]};background:{c["bg"]}">{escape(label or team)}</span>')
