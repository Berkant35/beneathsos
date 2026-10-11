import tempfile
import unittest
from pathlib import Path

from fontTools.ttLib import TTFont

from brandkit.fonts import WEIGHTS, export_static_fonts
from brandkit.wordmark import FONT_PATH


class StaticFontTest(unittest.TestCase):
    def test_static_instances_have_their_weight_and_no_variation_axes(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = export_static_fonts(Path(tmp))
            self.assertEqual(len(paths), 5)
            for weight, style in WEIGHTS.items():
                font = TTFont(Path(tmp) / f"AtkinsonHyperlegibleNext-{style}.ttf")
                self.assertNotIn("fvar", font)
                self.assertEqual(font["OS/2"].usWeightClass, weight)

    def test_licence_travels_with_the_fonts(self):
        with tempfile.TemporaryDirectory() as tmp:
            export_static_fonts(Path(tmp))
            self.assertIn("SIL OPEN FONT LICENSE", (Path(tmp) / "OFL.txt").read_text().upper())

    def test_export_keeps_the_source_timestamp(self):
        # Reproducible bytes: fontTools must not stamp "now" into head.modified.
        with tempfile.TemporaryDirectory() as tmp:
            export_static_fonts(Path(tmp))
            source = TTFont(FONT_PATH)["head"].modified
            self.assertEqual(TTFont(Path(tmp) / "AtkinsonHyperlegibleNext-Bold.ttf")["head"].modified, source)


if __name__ == "__main__":
    unittest.main()
