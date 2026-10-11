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
