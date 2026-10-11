"""The "signal exit" symbol — spec §6 geometry on a 48 × 48 grid."""
from __future__ import annotations

STROKE = 3.6
LINE = "M6 30 H42"
DOT = (24, 38, 3.4)
ARCS = (
    ("M18.5 24.5 A7.5 7.5 0 0 1 29.5 24.5", "1"),
    ("M13.5 19.5 A14.5 14.5 0 0 1 34.5 19.5", "0.75"),
    ("M8.5 14.5 A21.5 21.5 0 0 1 39.5 14.5", "0.5"),
)


def symbol_elements(line: str, accent: str) -> str:
    cx, cy, r = DOT
    parts = [
        f'<path d="{LINE}" stroke="{line}" stroke-width="{STROKE}" stroke-linecap="round" fill="none"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{accent}"/>',
    ]
    for d, opacity in ARCS:
        parts.append(
            f'<path d="{d}" stroke="{accent}" stroke-width="{STROKE}" stroke-linecap="round" '
            f'fill="none" opacity="{opacity}"/>'
        )
    return "".join(parts)


def symbol_svg(line: str, accent: str, size: int = 48) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 48 48">'
        f"{symbol_elements(line, accent)}</svg>"
    )


def icon_svg(canvas: int, scale: float, line: str, accent: str, background: str | None = None) -> str:
    """Symbol centred on a square canvas; `scale` is the symbol's share of the canvas width."""
    s = canvas * scale / 48
    offset = (canvas - 48 * s) / 2
    bg = f'<rect width="{canvas}" height="{canvas}" fill="{background}"/>' if background else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas}" height="{canvas}" '
        f'viewBox="0 0 {canvas} {canvas}">{bg}'
        f'<g transform="translate({offset:.3f} {offset:.3f}) scale({s:.5f})">'
        f"{symbol_elements(line, accent)}</g></svg>"
    )
