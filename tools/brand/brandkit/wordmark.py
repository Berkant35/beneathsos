"""Wordmark outlined from the bundled Atkinson Hyperlegible Next, so SVGs never depend on installed fonts."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

from brandkit.symbol import symbol_elements

FONT_PATH = Path(__file__).resolve().parents[3] / "docs" / "brand" / "fonts" / "AtkinsonHyperlegibleNext[wght].ttf"


@dataclass(frozen=True)
class Run:
    text: str
    colour: str


def outline_runs(runs: list[Run], weight: int = 800, size: float = 100.0) -> tuple[str, float, float]:
    """SVG path elements (one per run), total width and line height, at `size` px, top-left origin."""
    static = instancer.instantiateVariableFont(TTFont(FONT_PATH), {"wght": weight})
    glyph_set = static.getGlyphSet()
    order = static.getGlyphOrder()
    upem = static["head"].unitsPerEm
    ascent, descent = static["hhea"].ascent, static["hhea"].descent
    scale = size / upem

    font = hb.Font(hb.Face(FONT_PATH.read_bytes()))
    font.set_variations({"wght": weight})
    buf = hb.Buffer()
    buf.add_str("".join(r.text for r in runs))
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})

    starts, cursor = [], 0
    for r in runs:
        starts.append(cursor)
        cursor += len(r.text)

    def run_index(cluster: int) -> int:
        return max(i for i, s in enumerate(starts) if s <= cluster)

    paths = [""] * len(runs)
    x = 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        pen = SVGPathPen(glyph_set)
        transform = (scale, 0, 0, -scale, (x + pos.x_offset) * scale, ascent * scale)
        glyph_set[order[info.codepoint]].draw(TransformPen(pen, transform))
        paths[run_index(info.cluster)] += pen.getCommands()
        x += pos.x_advance
    elements = "".join(f'<path d="{d}" fill="{r.colour}"/>' for d, r in zip(paths, runs) if d)
    return elements, x * scale, (ascent - descent) * scale


def wordmark_svg(primary: str, accent: str, size: float = 100.0) -> str:
    elements, width, height = outline_runs([Run("Beneath", primary), Run("SOS", accent)], size=size)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.1f}" height="{height:.1f}" '
        f'viewBox="0 0 {width:.3f} {height:.3f}">{elements}</svg>'
    )


def lockup_svg(line: str, accent: str, primary: str, height: int = 120) -> str:
    """Symbol left, wordmark right, both vertically centred; gap = ¼ symbol height (clear space)."""
    s = height / 48
    gap = height / 4
    elements, w_width, w_height = outline_runs([Run("Beneath", primary), Run("SOS", accent)], size=height * 0.5)
    total = height + gap + w_width
    y = (height - w_height) / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total:.1f}" height="{height}" '
        f'viewBox="0 0 {total:.3f} {height}">'
        f'<g transform="scale({s:.5f})">{symbol_elements(line, accent)}</g>'
        f'<g transform="translate({height + gap:.3f} {y:.3f})">{elements}</g></svg>'
    )
