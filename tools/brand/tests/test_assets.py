import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops

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

    def ink_box(self, name, background=None):
        """Bounding box of the symbol: opaque pixels, or pixels that differ from the background."""
        img = self.img(name)
        if background is None:
            return img.getchannel("A").point(lambda a: 255 if a > 0 else 0).getbbox()
        bg = Image.new("RGB", img.size, background)
        diff = ImageChops.difference(img.convert("RGB"), bg).convert("L")
        return diff.point(lambda v: 255 if v > 8 else 0).getbbox()

    def test_android_icon_looks_as_large_as_ios(self):
        # Launchers show the central 72 of 108 dp; flutter_launcher_icons must add no inset
        # (adaptive_icon_foreground_inset: 0 in the app's flutter_launcher_icons.yaml).
        left, _, right, _ = self.ink_box("icon.png", background="#1B2A4E")
        ios_share = (right - left) / 1024
        left, _, right, _ = self.ink_box("android-foreground.png")
        android_share = (right - left) / (1024 * 72 / 108)
        self.assertAlmostEqual(android_share, ios_share, delta=0.02)

    def test_android_symbol_stays_inside_safe_zone(self):
        # Masks may crop to a 66 dp circle: every ink pixel must lie inside it.
        img = self.img("android-foreground.png")
        radius, centre = 1024 * 33 / 108, 512
        alpha = img.getchannel("A").load()
        for y in range(0, 1024, 2):
            for x in range(0, 1024, 2):
                if alpha[x, y] > 0:
                    self.assertLessEqual((x - centre) ** 2 + (y - centre) ** 2, radius ** 2, (x, y))

    def test_mono_symbol_has_one_ink_and_no_opacity(self):
        svg = (self.out / "svg" / "symbol-mono.svg").read_text()
        self.assertNotIn('opacity="0.', svg)

    def test_16px_master_uses_the_pixel_aligned_variant(self):
        img = Image.open(self.out / "png" / "symbol-16.png").convert("RGBA")
        self.assertEqual(img.getpixel((3, 10))[3], 255)

    def test_splash_has_no_text_layer(self):
        svg = (self.out / "svg" / "splash.svg").read_text()
        self.assertNotIn("Beneath", svg)
        self.assertNotIn("<text", svg)


if __name__ == "__main__":
    unittest.main()
