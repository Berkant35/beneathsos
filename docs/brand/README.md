# BeneathSOS brand

Logo, app icon, colours and typeface of BeneathSOS. Decisions and reasons:
[ADR 0017](../adr/0017-visual-identity.md). Design guidance: [`docs/design/`](../design/principles.md).

## Files

Every file in `svg/` and `png/` is **generated** — never edit them by hand.

| File | Use |
|---|---|
| `svg/symbol.svg` | Symbol on light backgrounds |
| `svg/symbol-dark.svg` | Symbol on dark backgrounds |
| `svg/symbol-mono.svg` | One-colour symbol (print, stamps, embossing) |
| `svg/wordmark.svg`, `svg/wordmark-dark.svg` | "BeneathSOS" wordmark, outlined (no font needed) |
| `svg/lockup.svg`, `svg/lockup-dark.svg` | Symbol + wordmark side by side — the default logo |
| `svg/app-icon.svg` | App icon master (1024 px canvas) |
| `svg/splash.svg` | Launch-screen artwork (symbol only, no text) |
| `png/app-icon-1024.png` | App icon master as PNG |
| `png/symbol-16.png` … `png/symbol-512.png` | Symbol at 16, 24, 32, 48 and 512 px |
| `fonts/AtkinsonHyperlegibleNext[wght].ttf`, `fonts/OFL.txt` | Typeface and its licence |

## Regenerate

```bash
# first time only
/usr/bin/python3 -m venv tools/brand/.venv
tools/brand/.venv/bin/pip install -r tools/brand/requirements.txt

# brand files in this folder
tools/brand/.venv/bin/python tools/brand/build.py
# plus the app's icon and launch-screen sources
tools/brand/.venv/bin/python tools/brand/build.py --app-dir apps/beneathsos_app/assets/branding

# tests (contrast table, geometry, 16 px legibility, icon layers)
cd tools/brand && .venv/bin/python -m unittest discover -s tests
```

Requires `rsvg-convert` (`brew install librsvg`); the committed PNGs are byte-identical with
librsvg 2.60.0. Colours live in `tools/brand/brandkit/palette.py`; geometry in
`tools/brand/brandkit/symbol.py`.

### Updating the app icon and launch screen

After `--app-dir` has refreshed `apps/beneathsos_app/assets/branding/`, regenerate the native
resources in the app repository:

```bash
cd apps/beneathsos_app
fvm dart run flutter_launcher_icons
fvm dart run flutter_native_splash:create
git checkout ios/Runner.xcodeproj/project.pbxproj   # see below
```

`flutter_launcher_icons` (0.14.4) rewrites the boolean Xcode setting
`ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS` from `YES` to `AppIcon`; restore it.
Keep `adaptive_icon_foreground_inset: 0` in `flutter_launcher_icons.yaml`: the foreground is already
sized for the visible area (`ADAPTIVE_SCALE` in `brandkit/assets.py`). Then build both platforms and
upload to TestFlight (app README).

## Symbol: "signal exit"

| Element | Meaning |
|---|---|
| Straight line | The surface of the rubble |
| Dot below the line | The phone under the rubble |
| Three arcs rising, fading outwards | The signal leaving the rubble and weakening — **not** a position |

Geometry on a 48 × 48 grid, round caps, one stroke width (3.6):

- Line `M6 30 H42` in the primary colour.
- Dot at (24, 38), radius 3.4, in the accent colour.
- Arcs in the accent colour, opacity 1 / 0.75 / 0.5 from inner to outer:
  `M18.5 24.5 A7.5 7.5 0 0 1 29.5 24.5`, `M13.5 19.5 A14.5 14.5 0 0 1 34.5 19.5`,
  `M8.5 14.5 A21.5 21.5 0 0 1 39.5 14.5`.

## Clear space and minimum size

- Keep empty space around the symbol of at least **¼ of its height** on every side.
- Minimum size **16 px**. Below that, the arcs merge.

## Colours

| Role | Light | Dark | Use |
|---|---|---|---|
| Primary (calm body) | `#1B2A4E` | `#9DB2E0` | Titles, secondary buttons, navigation, the logo's rubble line |
| Accent (action / attention) | `#FF7900` | `#FF8C2E` | The primary button, identity-rotation warning, the logo's signal |
| On accent | `#1A0D00` | `#1A0D00` | Text and icons on accent |
| Error (blocked) | `#B3261E` | `#FFB4AB` | Bluetooth off, permission missing |
| Background / text | `#F5F6F9` / `#121A2B` | `#0C111D` / `#E8ECF5` | |
| Secondary surface (dark) | — | `#22324F` | Secondary buttons in dark theme |

**White text on orange is forbidden** (contrast 2.6, below the 4.5 minimum). **Orange text or icons
on the light background are forbidden** too (2.4, below the 3:1 icon minimum): in light theme orange
is a fill behind dark content only.

## Do not

- Recolour the logo outside this palette.
- Add a cross, a crescent or any medical or Red Cross / Red Crescent emblem — these are protected by law.
- Add a pin, a target or crosshair: BeneathSOS never claims a location.
- Stretch, rotate, outline or add shadows to the logo.
- Place the logo on busy photos without a solid background.
- Put white text on orange, or orange text or icons on a light background.
- Use the wordmark without the orange "SOS".

## Typeface

[Atkinson Hyperlegible Next](https://github.com/googlefonts/atkinson-hyperlegible-next) by the
Braille Institute — designed so that easily confused characters (I/l/1, O/0, 5/S) stay distinct.
Licensed under the SIL Open Font License 1.1 (`fonts/OFL.txt`): free to embed and redistribute with
the licence; the font may not be sold on its own.

## Not an official app

Use this statement in onboarding, the About screen and store listings:

> **EN:** BeneathSOS is an independent open-source project and is not affiliated with AFAD or any
> government agency.
>
> **TR:** BeneathSOS bağımsız bir açık kaynak projedir; AFAD veya herhangi bir kamu kurumuyla
> bağlantısı yoktur.
