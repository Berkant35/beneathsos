# Brand and Design Principles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the approved phase 1.1 decisions into written design guidance, reproducible brand assets, and the app's real icon and launch screen.

**Architecture:** A small Python tool in the hub (`tools/brand/`) is the single generator for every brand asset: it builds the logo SVGs from the spec geometry, outlines the wordmark from the bundled Atkinson font (no dependency on installed fonts), renders PNGs with `rsvg-convert`, and exports the app's icon/splash sources. The app consumes those PNGs through `flutter_launcher_icons` and `flutter_native_splash`. Design guidance lives as Markdown in `docs/design/` plus ADR 0017.

**Tech Stack:** Python 3.9 (macOS system interpreter) with fontTools, uharfbuzz, Pillow, `unittest`; librsvg `rsvg-convert`; Flutter 3.47.5 (FVM); flutter_launcher_icons 0.14.4; flutter_native_splash 2.4.8.

**Spec:** `docs/superpowers/specs/2026-10-11-brand-and-design-principles-design.md`

## Global Constraints

- Colours (spec §4): primary `#1B2A4E` / dark `#9DB2E0`; accent `#FF7900` / dark `#FF8C2E`; on-accent `#1A0D00`; error `#B3261E` / dark `#FFB4AB`; background/text light `#F5F6F9` / `#121A2B`; dark `#0C111D` / `#E8ECF5`; dark secondary surface `#22324F`; logo line on navy `#E8ECF5`.
- White text on orange is forbidden (contrast 2.6).
- Logo geometry (spec §6): 48 × 48 grid, round caps, stroke 3.6; line `M6 30 H42`; dot (24, 38) r 3.4; arcs `M18.5 24.5 A7.5 7.5 0 0 1 29.5 24.5`, `M13.5 19.5 A14.5 14.5 0 0 1 34.5 19.5`, `M8.5 14.5 A21.5 21.5 0 0 1 39.5 14.5` at opacity 1 / 0.75 / 0.5.
- Wordmark: "Beneath" in primary + "SOS" in accent, Atkinson Hyperlegible Next weight 800, outlined.
- Typeface file ships with `OFL.txt`.
- Launch screen has no text. Never use the Red Cross / Red Crescent emblems.
- Non-affiliation statement, exact text — EN: "BeneathSOS is an independent open-source project and is not affiliated with AFAD or any government agency." TR: "BeneathSOS bağımsız bir açık kaynak projedir; AFAD veya herhangi bir kamu kurumuyla bağlantısı yoktur."
- Docs in English. Maintainer approves each task before the next; commits per repository; push and TestFlight upload after app changes (CLAUDE.md §9).
- Heredocs containing Markdown or code use `<<'EOF'` (tasks/lessons.md).

## Review Focus

- iOS "tinted" home-screen appearance: the tinted icon must be pure grayscale, or iOS tints it unevenly — pinned by the grayscale test in Task 4.
- Android 13+ themed icons: the monochrome layer must be one colour with alpha only — pinned by the monochrome test in Task 4.
- Very small renderings (16–24 px, e.g. Settings, notifications): the orange signal must still be visible — pinned by the 16 px accent-pixel test in Task 2.
- Dark mode on Android 12+ launch: the night splash must use `#0C111D`, not the light colour — pinned by the generated-resources check in Task 7.
- A later palette change silently breaking contrast — pinned by the contrast table test in Task 1.

---

### Task 1: Brand tool skeleton, palette and contrast check (hub)

**Files:**
- Create: `tools/brand/requirements.txt`, `tools/brand/brandkit/__init__.py`, `tools/brand/brandkit/palette.py`, `tools/brand/brandkit/contrast.py`, `tools/brand/tests/__init__.py`, `tools/brand/tests/test_contrast.py`
- Modify: `.gitignore` (add `tools/brand/.venv/`)

**Interfaces:**
- Produces: `brandkit.palette` constants (names below); `brandkit.contrast.contrast_ratio(a: str, b: str) -> float`.

- [ ] **Step 1: Create the virtual environment and dependencies**

```bash
cd /Users/berkantcalikusu/IdeaProjects/beneathsos
/usr/bin/python3 -m venv tools/brand/.venv      # Homebrew's python 3.14 venv is broken on this machine
tools/brand/.venv/bin/pip install -q --upgrade pip
tools/brand/.venv/bin/pip install -q fonttools uharfbuzz Pillow
tools/brand/.venv/bin/pip freeze | grep -iE '^(fonttools|uharfbuzz|pillow)==' > tools/brand/requirements.txt
printf '\n# Brand tool virtualenv\ntools/brand/.venv/\n' >> .gitignore
cat tools/brand/requirements.txt
```
Expected: three pinned lines (`fonttools==…`, `pillow==…`, `uharfbuzz==…`).

- [ ] **Step 2: Write the failing test** — `tools/brand/tests/test_contrast.py`

```python
import unittest

from brandkit import palette as p
from brandkit.contrast import contrast_ratio


class ContrastTableTest(unittest.TestCase):
    """Pins spec §4. Changing a colour must keep these ratios (rounded to 1 decimal)."""

    CASES = [
        ("#FFFFFF", p.PRIMARY_LIGHT, 14.1),
        (p.TEXT_LIGHT, p.BACKGROUND_LIGHT, 16.1),
        (p.ON_ACCENT, p.ACCENT_LIGHT, 7.3),
        (p.ON_ACCENT, p.ACCENT_DARK, 8.2),
        (p.ERROR_LIGHT, "#FFFFFF", 6.5),
        (p.PRIMARY_DARK, p.BACKGROUND_DARK, 8.9),
        (p.TEXT_DARK, p.BACKGROUND_DARK, 15.9),
        (p.TEXT_DARK, p.SURFACE2_DARK, 10.8),
    ]

    def test_spec_table(self):
        for fg, bg, expected in self.CASES:
            with self.subTest(fg=fg, bg=bg):
                self.assertEqual(round(contrast_ratio(fg, bg), 1), expected)

    def test_white_on_orange_stays_forbidden(self):
        self.assertLess(contrast_ratio("#FFFFFF", p.ACCENT_LIGHT), 4.5)

    def test_order_does_not_matter(self):
        self.assertEqual(contrast_ratio("#000000", "#FFFFFF"), contrast_ratio("#FFFFFF", "#000000"))
        self.assertEqual(round(contrast_ratio("#000000", "#FFFFFF"), 1), 21.0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run it to verify it fails**

Run: `cd tools/brand && .venv/bin/python -m unittest tests.test_contrast -v`
Expected: FAIL / ERROR — `ModuleNotFoundError: No module named 'brandkit'`.

- [ ] **Step 4: Implement** — `tools/brand/brandkit/__init__.py` (empty file), `tools/brand/tests/__init__.py` (empty file), and:

`tools/brand/brandkit/palette.py`
```python
"""Brand colours — spec §4. The single source for every generated asset."""

PRIMARY_LIGHT = "#1B2A4E"
PRIMARY_DARK = "#9DB2E0"
ACCENT_LIGHT = "#FF7900"
ACCENT_DARK = "#FF8C2E"
ON_ACCENT = "#1A0D00"
ERROR_LIGHT = "#B3261E"
ERROR_DARK = "#FFB4AB"
BACKGROUND_LIGHT = "#F5F6F9"
TEXT_LIGHT = "#121A2B"
BACKGROUND_DARK = "#0C111D"
TEXT_DARK = "#E8ECF5"
SURFACE2_DARK = "#22324F"
LINE_ON_NAVY = "#E8ECF5"
```

`tools/brand/brandkit/contrast.py`
```python
"""WCAG 2.x relative luminance and contrast ratio."""


def _channel(value: float) -> float:
    return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(a: str, b: str) -> float:
    light, dark = sorted((relative_luminance(a), relative_luminance(b)), reverse=True)
    return (light + 0.05) / (dark + 0.05)
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `cd tools/brand && .venv/bin/python -m unittest tests.test_contrast -v`
Expected: 3 tests OK.

- [ ] **Step 6: Commit (hub)**

```bash
git add .gitignore tools/brand
git commit -m "feat(brand): palette and WCAG contrast check"
```

---

### Task 2: Logo symbol SVGs

**Files:**
- Create: `tools/brand/brandkit/symbol.py`, `tools/brand/brandkit/render.py`, `tools/brand/tests/test_symbol.py`

**Interfaces:**
- Consumes: `brandkit.palette`.
- Produces: `symbol_elements(line: str, accent: str) -> str` (SVG elements in 48-unit space); `symbol_svg(line: str, accent: str, size: int = 48) -> str`; `icon_svg(canvas: int, scale: float, line: str, accent: str, background: str | None = None) -> str`; `render.render_png(svg_text: str, out: Path, width: int, height: int) -> Path`.

- [ ] **Step 1: Write the failing test** — `tools/brand/tests/test_symbol.py`

```python
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from brandkit import palette as p
from brandkit.render import render_png
from brandkit.symbol import icon_svg, symbol_svg


def _is_orange(px):
    r, g, b, a = px
    return a > 200 and r > 200 and 80 < g < 170 and b < 80


class SymbolTest(unittest.TestCase):
    def test_spec_geometry(self):
        svg = symbol_svg(p.PRIMARY_LIGHT, p.ACCENT_LIGHT)
        for fragment in (
            'viewBox="0 0 48 48"',
            'd="M6 30 H42"',
            'cx="24" cy="38" r="3.4"',
            "A7.5 7.5 0 0 1 29.5 24.5",
            "A14.5 14.5 0 0 1 34.5 19.5",
            "A21.5 21.5 0 0 1 39.5 14.5",
            'stroke-width="3.6"',
            'stroke-linecap="round"',
            'opacity="0.75"',
            'opacity="0.5"',
        ):
            self.assertIn(fragment, svg)

    def test_signal_is_visible_at_16px(self):
        with tempfile.TemporaryDirectory() as tmp:
            png = render_png(symbol_svg(p.PRIMARY_LIGHT, p.ACCENT_LIGHT), Path(tmp) / "s16.png", 16, 16)
            img = Image.open(png).convert("RGBA")
            self.assertEqual(img.size, (16, 16))
            self.assertTrue(any(_is_orange(img.getpixel((x, y))) for x in range(16) for y in range(16)))

    def test_icon_has_opaque_background_when_given(self):
        with tempfile.TemporaryDirectory() as tmp:
            svg = icon_svg(1024, 0.62, p.LINE_ON_NAVY, p.ACCENT_LIGHT, background=p.PRIMARY_LIGHT)
            img = Image.open(render_png(svg, Path(tmp) / "icon.png", 1024, 1024)).convert("RGBA")
            self.assertEqual(img.getpixel((4, 4)), (0x1B, 0x2A, 0x4E, 255))
            self.assertTrue(_is_orange(img.getpixel((512, 512 + int(14 * 1024 * 0.62 / 48)))))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd tools/brand && .venv/bin/python -m unittest tests.test_symbol -v`
Expected: ERROR — `No module named 'brandkit.symbol'`.

- [ ] **Step 3: Implement**

`tools/brand/brandkit/symbol.py`
```python
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
```

`tools/brand/brandkit/render.py`
```python
"""SVG → PNG with librsvg (`brew install librsvg`)."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


def render_png(svg_text: str, out: Path, width: int, height: int) -> Path:
    exe = shutil.which("rsvg-convert")
    if exe is None:
        raise RuntimeError("rsvg-convert not found — install librsvg (brew install librsvg)")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as f:
        f.write(svg_text)
        src = f.name
    subprocess.run([exe, "-w", str(width), "-h", str(height), "-o", str(out), src], check=True)
    Path(src).unlink()
    return out
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd tools/brand && .venv/bin/python -m unittest tests.test_symbol -v`
Expected: 3 tests OK.

- [ ] **Step 5: Commit (hub)**

```bash
git add tools/brand
git commit -m "feat(brand): signal-exit symbol SVG and PNG rendering"
```

---

### Task 3: Bundled font, outlined wordmark and lock-up

**Files:**
- Create: `docs/brand/fonts/AtkinsonHyperlegibleNext[wght].ttf`, `docs/brand/fonts/OFL.txt`, `tools/brand/brandkit/wordmark.py`, `tools/brand/tests/test_wordmark.py`

**Interfaces:**
- Consumes: `symbol_elements`, `render_png`, palette.
- Produces: `FONT_PATH: Path`; `Run(text: str, colour: str)`; `outline_runs(runs: list[Run], weight: int = 800, size: float = 100.0) -> tuple[str, float, float]` (elements, width, height); `wordmark_svg(primary: str, accent: str, size: float = 100.0) -> str`; `lockup_svg(line: str, accent: str, primary: str, height: int = 120) -> str`.

- [ ] **Step 1: Download the font and its licence**

```bash
cd /Users/berkantcalikusu/IdeaProjects/beneathsos
mkdir -p docs/brand/fonts
B=https://raw.githubusercontent.com/google/fonts/main/ofl/atkinsonhyperlegiblenext
curl -sL -o "docs/brand/fonts/AtkinsonHyperlegibleNext[wght].ttf" "$B/AtkinsonHyperlegibleNext%5Bwght%5D.ttf"
curl -sL -o docs/brand/fonts/OFL.txt "$B/OFL.txt"
ls -l docs/brand/fonts && head -3 docs/brand/fonts/OFL.txt
```
Expected: ~115 KB `.ttf`; OFL header "licensed under the SIL Open Font License, Version 1.1".

- [ ] **Step 2: Write the failing test** — `tools/brand/tests/test_wordmark.py`

```python
import re
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from brandkit import palette as p
from brandkit.render import render_png
from brandkit.wordmark import FONT_PATH, Run, lockup_svg, outline_runs, wordmark_svg


class WordmarkTest(unittest.TestCase):
    def test_font_is_bundled_with_licence(self):
        self.assertTrue(FONT_PATH.exists())
        self.assertIn("SIL Open Font License", (FONT_PATH.parent / "OFL.txt").read_text())

    def test_runs_are_outlined_in_their_colours(self):
        elements, width, height = outline_runs([Run("Beneath", p.PRIMARY_LIGHT), Run("SOS", p.ACCENT_LIGHT)])
        fills = re.findall(r'fill="(#[0-9A-F]{6})"', elements)
        self.assertEqual(fills, [p.PRIMARY_LIGHT, p.ACCENT_LIGHT])
        self.assertNotIn("<text", elements)
        self.assertGreater(width, 4 * height)

    def test_wordmark_renders_both_colours(self):
        with tempfile.TemporaryDirectory() as tmp:
            img = Image.open(
                render_png(wordmark_svg(p.PRIMARY_LIGHT, p.ACCENT_LIGHT), Path(tmp) / "w.png", 600, 120)
            ).convert("RGBA")
            colours = {img.getpixel((x, y))[:3] for x in range(0, 600, 3) for y in range(0, 120, 3)
                       if img.getpixel((x, y))[3] == 255}
            self.assertIn((0x1B, 0x2A, 0x4E), colours)
            self.assertIn((0xFF, 0x79, 0x00), colours)

    def test_lockup_contains_symbol_and_wordmark(self):
        svg = lockup_svg(p.PRIMARY_LIGHT, p.ACCENT_LIGHT, p.PRIMARY_LIGHT)
        self.assertIn('d="M6 30 H42"', svg)
        self.assertEqual(len(re.findall(r'fill="#1B2A4E"', svg)), 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run it to verify it fails**

Run: `cd tools/brand && .venv/bin/python -m unittest tests.test_wordmark -v`
Expected: ERROR — `No module named 'brandkit.wordmark'`.

- [ ] **Step 4: Implement** — `tools/brand/brandkit/wordmark.py`

```python
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
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `cd tools/brand && .venv/bin/python -m unittest tests.test_wordmark -v`
Expected: 4 tests OK. If `test_wordmark_renders_both_colours` fails only on anti-aliasing, sample with `>= 250` alpha instead of `== 255`; do not change colours.

- [ ] **Step 6: Commit (hub)**

```bash
git add docs/brand/fonts tools/brand
git commit -m "feat(brand): bundled Atkinson font, outlined wordmark and lock-up"
```

---

### Task 4: Asset build (SVG/PNG masters + app exports)

**Files:**
- Create: `tools/brand/brandkit/assets.py`, `tools/brand/build.py`, `tools/brand/tests/test_assets.py`
- Generated (committed): `docs/brand/svg/*.svg`, `docs/brand/png/*.png`

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: `build_all(out_dir: Path, app_dir: Path | None = None) -> list[Path]`. App export file names (used by Task 7): `icon.png`, `icon-ios-dark.png`, `icon-ios-tinted.png`, `android-foreground.png`, `android-monochrome.png`, `splash.png`, `splash-dark.png`, `splash-android12.png`, `splash-android12-dark.png`.

- [ ] **Step 1: Write the failing test** — `tools/brand/tests/test_assets.py`

```python
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from brandkit.assets import APP_FILES, MASTER_FILES, build_all


class AssetBuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        cls.out, cls.app = root / "brand", root / "app"
        build_all(cls.out, cls.app)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def img(self, name):
        return Image.open(self.app / name).convert("RGBA")

    def test_all_files_exist(self):
        for name in MASTER_FILES:
            self.assertTrue((self.out / name).exists(), name)
        for name in APP_FILES:
            self.assertTrue((self.app / name).exists(), name)

    def test_main_icon_is_opaque_1024(self):
        icon = self.img("icon.png")
        self.assertEqual(icon.size, (1024, 1024))
        self.assertEqual(min(px[3] for px in icon.getdata()), 255)

    def test_ios_tinted_icon_is_grayscale(self):
        for r, g, b, _ in self.img("icon-ios-tinted.png").getdata():
            self.assertTrue(r == g == b, (r, g, b))

    def test_android_monochrome_is_single_colour(self):
        colours = {px[:3] for px in self.img("android-monochrome.png").getdata() if px[3] > 0}
        self.assertEqual(colours, {(255, 255, 255)})

    def test_transparent_layers_are_transparent_at_corners(self):
        for name in ("icon-ios-dark.png", "android-foreground.png", "splash.png", "splash-dark.png",
                     "splash-android12.png", "splash-android12-dark.png"):
            self.assertEqual(self.img(name).getpixel((0, 0))[3], 0, name)

    def test_splash_has_no_text_layer(self):
        svg = (self.out / "svg" / "splash.svg").read_text()
        self.assertNotIn("Beneath", svg)
        self.assertNotIn("<text", svg)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd tools/brand && .venv/bin/python -m unittest tests.test_assets -v`
Expected: ERROR — `No module named 'brandkit.assets'`.

- [ ] **Step 3: Implement** — `tools/brand/brandkit/assets.py`

```python
"""Builds every brand file from the spec: SVG/PNG masters in docs/brand and the app's icon/splash sources."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from brandkit import palette as p
from brandkit.render import render_png
from brandkit.symbol import icon_svg, symbol_svg
from brandkit.wordmark import lockup_svg, wordmark_svg

ICON_SCALE = 0.62        # symbol share of the iOS icon canvas
ADAPTIVE_SCALE = 0.50    # Android adaptive foreground: keeps the symbol inside the 66/108 safe zone
SPLASH_SCALE = 0.40
SPLASH12_SCALE = 0.42    # Android 12 splash: icon must sit inside the central 2/3 circle

MASTER_FILES = [
    "svg/symbol.svg", "svg/symbol-dark.svg", "svg/symbol-mono.svg",
    "svg/wordmark.svg", "svg/wordmark-dark.svg", "svg/lockup.svg", "svg/lockup-dark.svg",
    "svg/app-icon.svg", "svg/splash.svg",
    "png/app-icon-1024.png", "png/symbol-16.png", "png/symbol-24.png", "png/symbol-32.png",
    "png/symbol-48.png", "png/symbol-512.png",
]
APP_FILES = [
    "icon.png", "icon-ios-dark.png", "icon-ios-tinted.png", "android-foreground.png",
    "android-monochrome.png", "splash.png", "splash-dark.png", "splash-android12.png",
    "splash-android12-dark.png",
]


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def _to_grayscale(path: Path) -> None:
    img = Image.open(path).convert("RGBA")
    gray = img.convert("L")
    Image.merge("RGBA", (gray, gray, gray, img.getchannel("A"))).save(path)


def build_all(out_dir: Path, app_dir: Path | None = None) -> list[Path]:
    made: list[Path] = []
    svg, png = out_dir / "svg", out_dir / "png"

    made += [
        _write(svg / "symbol.svg", symbol_svg(p.PRIMARY_LIGHT, p.ACCENT_LIGHT)),
        _write(svg / "symbol-dark.svg", symbol_svg(p.PRIMARY_DARK, p.ACCENT_DARK)),
        _write(svg / "symbol-mono.svg", symbol_svg(p.TEXT_LIGHT, p.TEXT_LIGHT)),
        _write(svg / "wordmark.svg", wordmark_svg(p.PRIMARY_LIGHT, p.ACCENT_LIGHT)),
        _write(svg / "wordmark-dark.svg", wordmark_svg(p.PRIMARY_DARK, p.ACCENT_DARK)),
        _write(svg / "lockup.svg", lockup_svg(p.PRIMARY_LIGHT, p.ACCENT_LIGHT, p.PRIMARY_LIGHT)),
        _write(svg / "lockup-dark.svg", lockup_svg(p.PRIMARY_DARK, p.ACCENT_DARK, p.PRIMARY_DARK)),
        _write(svg / "app-icon.svg", icon_svg(1024, ICON_SCALE, p.LINE_ON_NAVY, p.ACCENT_LIGHT, p.PRIMARY_LIGHT)),
        _write(svg / "splash.svg", icon_svg(1024, SPLASH_SCALE, p.PRIMARY_LIGHT, p.ACCENT_LIGHT)),
    ]
    made.append(render_png((svg / "app-icon.svg").read_text(), png / "app-icon-1024.png", 1024, 1024))
    for size in (16, 24, 32, 48, 512):
        made.append(render_png((svg / "symbol.svg").read_text(), png / f"symbol-{size}.png", size, size))

    if app_dir is not None:
        exports = {
            "icon.png": icon_svg(1024, ICON_SCALE, p.LINE_ON_NAVY, p.ACCENT_LIGHT, p.PRIMARY_LIGHT),
            "icon-ios-dark.png": icon_svg(1024, ICON_SCALE, p.PRIMARY_DARK, p.ACCENT_DARK),
            "icon-ios-tinted.png": icon_svg(1024, ICON_SCALE, "#FFFFFF", "#FFFFFF", "#000000"),
            "android-foreground.png": icon_svg(1024, ADAPTIVE_SCALE, p.LINE_ON_NAVY, p.ACCENT_LIGHT),
            "android-monochrome.png": icon_svg(1024, ADAPTIVE_SCALE, "#FFFFFF", "#FFFFFF"),
            "splash.png": icon_svg(1024, SPLASH_SCALE, p.PRIMARY_LIGHT, p.ACCENT_LIGHT),
            "splash-dark.png": icon_svg(1024, SPLASH_SCALE, p.PRIMARY_DARK, p.ACCENT_DARK),
            "splash-android12.png": icon_svg(1152, SPLASH12_SCALE, p.PRIMARY_LIGHT, p.ACCENT_LIGHT),
            "splash-android12-dark.png": icon_svg(1152, SPLASH12_SCALE, p.PRIMARY_DARK, p.ACCENT_DARK),
        }
        for name, text in exports.items():
            size = 1152 if "android12" in name else 1024
            made.append(render_png(text, app_dir / name, size, size))
        _to_grayscale(app_dir / "icon-ios-tinted.png")
    return made
```

`tools/brand/build.py`
```python
"""Regenerate all brand assets: `tools/brand/.venv/bin/python tools/brand/build.py [--app-dir DIR]`."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from brandkit.assets import build_all  # noqa: E402

HUB = Path(__file__).resolve().parents[2]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HUB / "docs" / "brand")
    parser.add_argument("--app-dir", type=Path, default=None,
                        help="also export icon/splash sources, e.g. apps/beneathsos_app/assets/branding")
    args = parser.parse_args()
    for path in build_all(args.out, args.app_dir):
        print(path.relative_to(HUB) if HUB in path.parents else path)
```

- [ ] **Step 4: Run all brand tests**

Run: `cd tools/brand && .venv/bin/python -m unittest discover -s tests -v`
Expected: all tests in Tasks 1–4 OK.

- [ ] **Step 5: Generate the masters into the repo and look at them**

```bash
cd /Users/berkantcalikusu/IdeaProjects/beneathsos
tools/brand/.venv/bin/python tools/brand/build.py
ls docs/brand/svg docs/brand/png
```
Open `docs/brand/png/app-icon-1024.png`, `docs/brand/svg/lockup.svg` and `docs/brand/png/symbol-16.png` and compare against the approved mockup (straight line, three fading orange arcs, orange dot).

- [ ] **Step 6: Commit (hub)**

```bash
git add tools/brand docs/brand/svg docs/brand/png
git commit -m "feat(brand): asset build — SVG/PNG masters and app icon/splash exports"
```

---

### Task 5: Brand README and ADR 0017 (hub)

**Files:**
- Create: `docs/brand/README.md`, `docs/adr/0017-visual-identity.md`
- Modify: `docs/adr/README.md` (add row 0017)

- [ ] **Step 1: Write `docs/brand/README.md`** with these sections and content:
  - **Files** — table of every file in `svg/` and `png/` (from `MASTER_FILES`) with its use.
  - **Regenerate** — `tools/brand/.venv/bin/python tools/brand/build.py` and, for the app, `--app-dir apps/beneathsos_app/assets/branding`; first-time setup = Task 1 Step 1 commands; never edit generated files by hand.
  - **Symbol** — the geometry list from Global Constraints; meaning (line = rubble surface, dot = phone, arcs = signal leaving the rubble, fading = weakening signal, not a position).
  - **Clear space and minimum size** — clear space ¼ of the symbol height; minimum 16 px.
  - **Colours** — the colour-role table of spec §4 including "white on orange is forbidden".
  - **Do not** — recolour outside the palette; add a cross or crescent; add a pin or target marker; stretch; place on busy photos; put white text on orange; use the wordmark without the "SOS" accent.
  - **Typeface** — Atkinson Hyperlegible Next, SIL OFL 1.1, `fonts/OFL.txt`.
  - **Not an official app** — the EN and TR non-affiliation statements verbatim from Global Constraints, with "use in onboarding, About and store listings".

- [ ] **Step 2: Write `docs/adr/0017-visual-identity.md`** in the ADR format (Status Accepted, Date 2026-10-11) with:
  - **Context:** purpose sentence (spec §1); users under stress outdoors; brand must look trustworthy.
  - **Decision:** the decision table of spec §2 and the colour roles of spec §4.
  - **Alternatives:** palette A (deep teal + signal amber) and C (graphite + high-vis lime); logo A (wordmark only) and C (probability rings — reads as a target); serif-free system fonts and Inter.
  - **Consequences:** navy/orange resemble AFAD → mitigations (distinct tones, own logo, non-affiliation statement); white on orange forbidden; Red Cross / Red Crescent emblems legally protected and never used; ~115 KB font in the app; every asset reproducible from `tools/brand`.
  - **References:** the spec, `docs/brand/README.md`, `docs/design/`.

- [ ] **Step 3: Add the index row** in `docs/adr/README.md` after 0016:

```markdown
| [0017](0017-visual-identity.md) | Visual identity: palette, typeface, logo, voice, accessibility targets | Accepted |
```

- [ ] **Step 4: Verify links**

```bash
cd /Users/berkantcalikusu/IdeaProjects/beneathsos
for f in docs/brand/README.md docs/adr/0017-visual-identity.md; do
  for l in $(grep -o '](\([^)h#][^)]*\))' "$f" | sed 's/](\(.*\))/\1/'); do
    [ -e "$(dirname "$f")/$l" ] || echo "BROKEN in $f: $l"; done; done; echo checked
```
Expected: only `checked`.

- [ ] **Step 5: Commit (hub)**

```bash
git add docs/brand/README.md docs/adr
git commit -m "docs(brand): brand README and ADR 0017 visual identity"
```

---

### Task 6: Design guidance documents (hub)

**Files:**
- Create: `docs/design/principles.md`, `docs/design/voice-and-tone.md`, `docs/design/accessibility.md`
- Modify: `.github/pull_request_template.md` (add one checklist line), then `tools/sync_governance.sh`

- [ ] **Step 1: Write `docs/design/principles.md`**: the purpose sentence (spec §1) as a quote, the users paragraph, the seven principles of spec §3 verbatim, the colour-role table and contrast table of spec §4, typography and icon rules of spec §5, and a "Related" list linking `voice-and-tone.md`, `accessibility.md`, `../brand/README.md`, `../adr/0017-visual-identity.md`.

- [ ] **Step 2: Write `docs/design/voice-and-tone.md`**: the rules and the Do/Don't table of spec §7 verbatim, plus this glossary (exact terms; UI copy must use them):

```markdown
| English | Türkçe | Notes |
|---|---|---|
| probability region | olasılık bölgesi | Never "location" alone |
| most likely area | en olası bölge | The 50 % region |
| signal exit point | sinyal çıkış noktası | Where the signal leaves the rubble — not the person |
| measurement point | ölçüm noktası | |
| signal heard / no signal | sinyal var / sinyal yok | "No signal" is information, not failure |
| target | hedef | The device being searched for |
| identity rotation | kimlik değişimi | Phones change their Bluetooth identity ~ every 15 min |
| relink | yeniden bağla | Confirming the new identity of the target |
| ambient scan | ortam taraması | 30 s scan to blacklist surface devices |
| rubble site | enkaz alanı | |
| rescuer | kurtarıcı | |
| I am trapped (victim mode) | Enkaz altındayım | UI label; "victim mode" is internal only |
```

- [ ] **Step 3: Write `docs/design/accessibility.md`**: the target and five bullets of spec §8, then:

```markdown
## Pull request checklist (UI changes)

- [ ] Text contrast ≥ 4.5 (large text ≥ 3); no white text on orange
- [ ] Touch targets ≥ 56 px; the primary action is ≥ 64 px tall and in the bottom half
- [ ] Body text ≥ 17 pt; checked at 200 % system text size with no clipped or overlapping text
- [ ] No information by colour alone (icon or text too)
- [ ] Critical events also vibrate and sound
- [ ] Works with "reduce motion"; no decorative animation
- [ ] Every string from ARB in English and Turkish, using the glossary terms
- [ ] Screen readers: meaningful labels on icons and controls
- [ ] Checked in light and dark mode
```

- [ ] **Step 4: Link the checklist from the PR template** — in `.github/pull_request_template.md`, under "Rules checklist", add:

```markdown
- [ ] UI changes: [accessibility checklist](https://github.com/Berkant35/beneathsos/blob/main/docs/design/accessibility.md#pull-request-checklist-ui-changes) completed
```
Then run `tools/sync_governance.sh` (copies the template into the app and plugin repositories).

- [ ] **Step 5: Verify links and sync**

```bash
cd /Users/berkantcalikusu/IdeaProjects/beneathsos
for f in docs/design/*.md; do for l in $(grep -o '](\([^)h#][^)]*\))' "$f" | sed 's/](\(.*\))/\1/'); do
  [ -e "docs/design/$l" ] || echo "BROKEN in $f: $l"; done; done; echo checked
for r in apps/beneathsos_app packages/ble_scanner; do git -C $r status --short; done
```
Expected: `checked`; each sub-repo shows only `M .github/pull_request_template.md`.

- [ ] **Step 6: Commit (hub, app, plugin)**

```bash
git add docs/design .github/pull_request_template.md && git commit -m "docs(design): principles, voice and tone, accessibility checklist"
for r in apps/beneathsos_app packages/ble_scanner; do git -C $r add .github/pull_request_template.md && git -C $r commit -m "chore(github): link the accessibility checklist in the PR template"; done
```

---

### Task 7: App icon and launch screen (app)

**Files:**
- Create: `apps/beneathsos_app/assets/branding/*` (generated, 9 files), `apps/beneathsos_app/flutter_launcher_icons.yaml`, `apps/beneathsos_app/flutter_native_splash.yaml`
- Modify: `apps/beneathsos_app/pubspec.yaml` (dev dependencies), generated native files under `ios/` and `android/`, `apps/beneathsos_app/CHANGELOG.md`

- [ ] **Step 1: Export the sources into the app**

```bash
cd /Users/berkantcalikusu/IdeaProjects/beneathsos
tools/brand/.venv/bin/python tools/brand/build.py --app-dir apps/beneathsos_app/assets/branding
ls apps/beneathsos_app/assets/branding
```
Expected: the nine files listed in Task 4 `APP_FILES`.

- [ ] **Step 2: Add the generators as dev dependencies**

```bash
cd apps/beneathsos_app
fvm flutter pub add --dev flutter_launcher_icons:^0.14.4 flutter_native_splash:^2.4.8
```

- [ ] **Step 3: Configure** — `apps/beneathsos_app/flutter_launcher_icons.yaml`

```yaml
flutter_launcher_icons:
  android: "ic_launcher"
  ios: true
  image_path: "assets/branding/icon.png"
  remove_alpha_ios: true
  image_path_ios_dark_transparent: "assets/branding/icon-ios-dark.png"
  image_path_ios_tinted_grayscale: "assets/branding/icon-ios-tinted.png"
  adaptive_icon_background: "#1B2A4E"
  adaptive_icon_foreground: "assets/branding/android-foreground.png"
  adaptive_icon_monochrome: "assets/branding/android-monochrome.png"
  min_sdk_android: 24
```

`apps/beneathsos_app/flutter_native_splash.yaml`
```yaml
flutter_native_splash:
  color: "#F5F6F9"
  color_dark: "#0C111D"
  image: assets/branding/splash.png
  image_dark: assets/branding/splash-dark.png
  android_12:
    image: assets/branding/splash-android12.png
    image_dark: assets/branding/splash-android12-dark.png
    color: "#F5F6F9"
    color_dark: "#0C111D"
  android: true
  ios: true
  web: false
```

- [ ] **Step 4: Generate native resources**

```bash
fvm dart run flutter_launcher_icons
fvm dart run flutter_native_splash:create
git status --short
```
Expected: changes under `ios/Runner/Assets.xcassets/AppIcon.appiconset/`, `ios/Runner/Assets.xcassets/LaunchImage*.imageset/`, `ios/Runner/Base.lproj/LaunchScreen.storyboard`, `android/app/src/main/res/` (mipmaps, `mipmap-anydpi-v26/ic_launcher.xml`, `drawable*`, `values*/styles.xml`).

- [ ] **Step 5: Verify the generated configuration (Review Focus)**

```bash
grep -c '"luminosity"' ios/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json   # dark appearance present
grep -c '"tinted"' ios/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json        # tinted appearance present
grep -c '<monochrome' android/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml      # themed icon layer present
grep -ri '0C111D' android/app/src/main/res/values-night-v31/ | head -2                # dark Android 12 splash colour
grep -ri 'F5F6F9' android/app/src/main/res/values-v31/ | head -2                      # light Android 12 splash colour
```
Expected: each count ≥ 1 and both colour greps print a line. If the iOS counts are 0, the installed flutter_launcher_icons did not write the iOS 18 appearances — stop and report (do not hand-edit without approval).

- [ ] **Step 6: Analyze, test, and changelog**

```bash
fvm flutter analyze --fatal-infos && fvm flutter test
```
Expected: no issues; all tests pass. Then add under `## [Unreleased]` in `CHANGELOG.md`:

```markdown
### Added
- App icon (iOS light, dark and tinted; Android adaptive and themed) and launch screen in the BeneathSOS brand.
```

- [ ] **Step 7: Commit (app)**

```bash
git add -A && git commit -m "feat(brand): app icon and launch screen"
```

---

### Task 8: Visual verification, push and TestFlight

**Files:** none (verification and release)

- [ ] **Step 1: iOS simulator — light mode**

```bash
cd /Users/berkantcalikusu/IdeaProjects/beneathsos/apps/beneathsos_app
UDID=72AE56FC-52D0-4CE2-8811-B113CE30EA21
xcrun simctl boot $UDID 2>/dev/null; xcrun simctl ui $UDID appearance light
fvm flutter build ios --simulator --debug
xcrun simctl terminate $UDID org.beneathsos.app 2>/dev/null
xcrun simctl install $UDID build/ios/iphonesimulator/Runner.app
xcrun simctl launch $UDID org.beneathsos.app && xcrun simctl io $UDID screenshot /tmp/beneathsos-launch-light.png
sleep 3; xcrun simctl io $UDID screenshot /tmp/beneathsos-home-light.png
```
Check: launch screenshot shows the symbol on `#F5F6F9` without text; after pressing Home, the home-screen icon is navy with the orange signal.

- [ ] **Step 2: iOS simulator — dark mode**: repeat Step 1 with `appearance dark` and file names `*-dark.png`. Check: launch background `#0C111D`; dark icon variant.

- [ ] **Step 3: Android build**

```bash
fvm flutter build apk --debug
```
Expected: `✓ Built build/app/outputs/flutter-apk/app-debug.apk`.

- [ ] **Step 4: Push all three repositories**

```bash
cd /Users/berkantcalikusu/IdeaProjects/beneathsos
git push && git -C apps/beneathsos_app push && git -C packages/ble_scanner push
```
Expected: "Bypassed rule violations" notices only; remote heads equal local heads.

- [ ] **Step 5: TestFlight upload and processing**

```bash
cd apps/beneathsos_app
ASC_KEY_ID=BQK4J6Z42Q ASC_ISSUER_ID=7c7907b5-e5f2-42df-ba1d-a05dde857c7c tools/testflight.sh
```
Expected: `UPLOAD SUCCEEDED`. Poll App Store Connect until the build is `VALID` and `IN_BETA_TESTING`; report the build number. On the phone, the TestFlight update shows the new icon.

- [ ] **Step 6: Close the phase step (hub)**: in `docs/roadmap.md` mark step 1.1 done; in `tasks/todo.md` add the 1.1 review (files, test counts, build number); close GitHub issue #6 ("Design principles and brand") with a comment linking the commits. Commit and push the hub.
