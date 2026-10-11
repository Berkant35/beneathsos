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
