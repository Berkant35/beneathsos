"""Static Atkinson Hyperlegible Next instances for Flutter, which does not map FontWeight to a variable font's axis."""
from __future__ import annotations

from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

from brandkit.wordmark import FONT_PATH

WEIGHTS = {400: "Regular", 600: "SemiBold", 700: "Bold", 800: "ExtraBold"}


def export_static_fonts(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    made: list[Path] = []
    for weight, style in WEIGHTS.items():
        font = instancer.instantiateVariableFont(TTFont(FONT_PATH, recalcTimestamp=False), {"wght": weight})
        font["OS/2"].usWeightClass = weight
        path = out_dir / f"AtkinsonHyperlegibleNext-{style}.ttf"
        font.save(path)
        made.append(path)
    licence = out_dir / "OFL.txt"
    licence.write_bytes((FONT_PATH.parent / "OFL.txt").read_bytes())
    made.append(licence)
    return made
