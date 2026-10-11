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
