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
