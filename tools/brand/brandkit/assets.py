"""Builds every brand file from the spec: SVG/PNG masters in docs/brand and the app's icon/splash sources."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from brandkit import palette as p
from brandkit.render import render_png
from brandkit.symbol import icon_svg, symbol_svg
from brandkit.wordmark import lockup_svg, wordmark_svg

ICON_SCALE = 0.62        # symbol share of the iOS icon canvas
# Android adaptive foreground (no inset): launchers show the central 72 of 108 dp, so 0.62 x 72/108
# gives the symbol the same visual share as on iOS and keeps it inside the 66 dp safe circle.
ADAPTIVE_SCALE = 0.41
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
