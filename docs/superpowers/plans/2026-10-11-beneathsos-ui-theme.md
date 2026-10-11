# beneathsos_ui 1.2a — Tokens, Theme and Branded Home Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the `beneathsos_ui` package (brand tokens, light/dark theme, Atkinson font, logo, primary and secondary buttons) and make it visible in the app: a branded home screen whose two actions open "being prepared" screens.

**Architecture:** Material 3 `ThemeData` built from a hand-written `ColorScheme` with the exact brand colours, plus a `BeneathTokens` `ThemeExtension` for accent, numeric text and motion. The package depends only on Flutter. The app depends on it through a git tag and a local `pubspec_overrides.yaml`; routes stay typed `go_router` routes in the app.

**Tech Stack:** Flutter 3.47.5 / Dart 3.13 (FVM), flutter_test (widget and golden tests), go_router + go_router_builder, Riverpod 3 (app only), gen-l10n ARB (en, tr), Python 3.9 + fontTools (hub brand tool).

**Spec:** `docs/superpowers/specs/2026-10-11-beneathsos-ui-theme-design.md`

## Global Constraints

- Every repo: `fvm dart format --set-exit-if-changed .`, `fvm flutter analyze --fatal-infos`, `fvm flutter test` pass before a task is done (CLAUDE.md §3).
- `beneathsos_ui` may depend on Flutter only — never Riverpod, go_router, `ble_scanner`, `rubble_core`, `locator_engine`, `rubble_canvas`.
- Colours are exactly: primary `#1B2A4E` / `#9DB2E0`, accent `#FF7900` / `#FF8C2E`, on-accent `#1A0D00`, error `#B3261E` / `#FFB4AB`, on-error dark `#690005`, background/text light `#F5F6F9` / `#121A2B`, dark `#0C111D` / `#E8ECF5`, secondary surface dark `#22324F`, outline `#6B7590` / `#8C9AB8`.
- Material `secondary` and `tertiary` are navy, never orange. Orange is reachable only through `BeneathTokens.accent` and `PrimaryButton`.
- Typeface Atkinson Hyperlegible Next for every text role; body text ≥ 17; fine print 15 only for the legal note and "Powered by".
- Touch targets ≥ 56; primary button 64 tall; at most one `PrimaryButton` per screen, in the bottom half.
- Zero hard-coded user-facing strings in the app: every key in `app_en.arb` and `app_tr.arb` in the same change. "Socrepho" and the wordmark "BeneathSOS" are names and are not translated.
- Never "location"/"victim is here" wording; the victim screen always tells the user to call 112.
- Public members in `beneathsos_ui` carry doc comments (`public_member_api_docs`).
- Commits: Conventional Commits, English, ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Never force-push; never commit secrets.
- Creating the public GitHub repository, pushing and TestFlight happen only in Task 12, after the maintainer confirms.

## Review Focus

- **200 % system text on a small phone (375 × 667):** the home screen scrolls, nothing overflows, both actions stay reachable — pinned by the small-phone test in Task 11.
- **Turkish labels at 200 %:** longer strings wrap inside the buttons instead of clipping — pinned by the Turkish small-phone test in Task 11.
- **Dark mode:** the logo and buttons switch to the dark tokens (no navy on navy) — pinned by the dark goldens in Tasks 5 and 6 and the dark home test in Task 11.
- **Gloved double tap on "Start a search":** one screen opens and Back returns home — pinned by the double-tap test in Task 11 (routes use `go`, not `push`).
- **Screen readers:** the logo is read as "BeneathSOS" and both actions as buttons — pinned by the semantics tests in Tasks 5, 6 and 11.

---

## Paths

- Hub: `/Users/berkantcalikusu/IdeaProjects/beneathsos` (written `HUB` below)
- Package: `HUB/packages/beneathsos_ui` (new, own git repository)
- App: `HUB/apps/beneathsos_app`

## File structure

| File | Responsibility |
|---|---|
| `HUB/tools/brand/brandkit/fonts.py` | Static Atkinson instances (400/600/700/800) + OFL for Flutter |
| `beneathsos_ui/lib/beneathsos_ui.dart` | Single export |
| `beneathsos_ui/lib/src/tokens/colors.dart` | `BeneathColors` palette constants |
| `beneathsos_ui/lib/src/tokens/contrast.dart` | `contrastRatio(Color, Color)` |
| `beneathsos_ui/lib/src/tokens/typography.dart` | `BeneathTypography.textTheme()`, `.numeric()`, font constants |
| `beneathsos_ui/lib/src/tokens/spacing.dart` | `BeneathSpacing` |
| `beneathsos_ui/lib/src/tokens/sizes.dart` | `BeneathSizes` |
| `beneathsos_ui/lib/src/tokens/motion.dart` | `BeneathMotion` (standard / reduced) |
| `beneathsos_ui/lib/src/theme/beneath_tokens.dart` | `BeneathTokens` `ThemeExtension`, `of`, `motionOf` |
| `beneathsos_ui/lib/src/theme/beneath_theme.dart` | `BeneathTheme.light()` / `.dark()` |
| `beneathsos_ui/lib/src/widgets/signal_exit_painter.dart` | Symbol painter (48-unit grid) |
| `beneathsos_ui/lib/src/widgets/beneath_logo.dart` | `BeneathLogo.symbol` / `.lockup` |
| `beneathsos_ui/lib/src/widgets/primary_button.dart` | Orange 64 px button |
| `beneathsos_ui/lib/src/widgets/secondary_button.dart` | 56 px secondary button |
| `beneathsos_ui/test/helpers/golden.dart` | Font loading + golden frame |
| app `lib/core/widgets/app_scaffold.dart` | Optional title; package spacing |
| app `lib/core/router/app_router.dart` | `HomeRoute` with child routes `NewSiteRoute`, `VictimRoute` |
| app `lib/features/home/presentation/screens/home_screen.dart` + `widgets/home_actions.dart`, `widgets/home_footer.dart` | Branded home |
| app `lib/features/sites/presentation/screens/new_site_screen.dart` | "Being prepared" (rescuer) |
| app `lib/features/victim/presentation/screens/victim_screen.dart` | "Being prepared" + 112 (trapped person) |

Route paths follow `docs/architecture.md` §6: `/sites/new` (rescuer flow starts by creating a site) and `/victim` (victim mode). The spec's §6 was amended to these paths before this plan.

---

### Task 1: Static Atkinson fonts from the brand tool (hub)

**Files:**
- Create: `HUB/tools/brand/brandkit/fonts.py`
- Create: `HUB/tools/brand/tests/test_fonts.py`
- Modify: `HUB/tools/brand/build.py`
- Modify: `HUB/docs/brand/README.md` ("Regenerate" section)

**Interfaces:**
- Produces: `export_static_fonts(out_dir: Path) -> list[Path]` writing `AtkinsonHyperlegibleNext-{Regular,SemiBold,Bold,ExtraBold}.ttf` and `OFL.txt`; CLI flag `build.py --fonts-dir DIR`.

- [ ] **Step 1: Write the failing test** — `tools/brand/tests/test_fonts.py`

```python
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
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd HUB/tools/brand && .venv/bin/python -m unittest tests.test_fonts`
Expected: ERROR — `ModuleNotFoundError: No module named 'brandkit.fonts'`

- [ ] **Step 3: Implement** — `tools/brand/brandkit/fonts.py`

```python
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
```

Modify `tools/brand/build.py` — add the flag and the call:

```python
from brandkit.fonts import export_static_fonts  # noqa: E402
...
    parser.add_argument("--fonts-dir", type=Path, default=None,
                        help="also export static Atkinson fonts, e.g. packages/beneathsos_ui/fonts")
    args = parser.parse_args()
    made = build_all(args.out, args.app_dir)
    if args.fonts_dir is not None:
        made += export_static_fonts(args.fonts_dir)
    for path in made:
        print(path.relative_to(HUB) if HUB in path.parents else path)
```

- [ ] **Step 4: Run tests**

Run: `cd HUB/tools/brand && .venv/bin/python -m unittest discover -s tests`
Expected: OK (25 tests: 22 existing + 3 new)

- [ ] **Step 5: Document** — in `docs/brand/README.md` under "Regenerate", after the `--app-dir` line add:

```bash
# plus the static fonts bundled by the beneathsos_ui package
tools/brand/.venv/bin/python tools/brand/build.py --fonts-dir packages/beneathsos_ui/fonts
```

- [ ] **Step 6: Commit (hub)**

```bash
cd HUB && git add tools/brand docs/brand/README.md
git commit -m "feat(brand): export static Atkinson weights for Flutter"
```

---

### Task 2: Package skeleton, colours and contrast table

**Files:**
- Create: `HUB/packages/beneathsos_ui/` (via `flutter create`), then replace generated files
- Create: `lib/beneathsos_ui.dart`, `lib/src/tokens/colors.dart`, `lib/src/tokens/contrast.dart`
- Create: `pubspec.yaml`, `analysis_options.yaml`, `dart_test.yaml`, `README.md`, `CHANGELOG.md`, `.gitignore`
- Create: `fonts/` (from Task 1)
- Test: `test/tokens/contrast_test.dart`

**Interfaces:**
- Consumes: `build.py --fonts-dir` (Task 1).
- Produces: `abstract final class BeneathColors` with `static const Color` fields `primaryLight, primaryDark, accentLight, accentDark, onAccent, errorLight, errorDark, onErrorDark, backgroundLight, textLight, backgroundDark, textDark, surface2Dark, outlineLight, outlineDark, white`; `double contrastRatio(Color a, Color b)`.

- [ ] **Step 1: Create the package and its git repository**

```bash
cd HUB/packages
fvm flutter create --template=package --project-name beneathsos_ui beneathsos_ui
cd beneathsos_ui
rm -f lib/beneathsos_ui.dart test/beneathsos_ui_test.dart
git init -b main
cp HUB/.fvmrc .
HUB/tools/brand/.venv/bin/python HUB/tools/brand/build.py --fonts-dir fonts > /dev/null
HUB/tools/sync_governance.sh
```

Expected: `fonts/` holds 4 `.ttf` files and `OFL.txt`; `synced beneathsos_ui` printed (it also re-syncs the other repos; their files are unchanged — check `git -C HUB/apps/beneathsos_app status --short` and `git -C HUB/packages/ble_scanner status --short` are empty).

- [ ] **Step 2: Write `pubspec.yaml`**

```yaml
name: beneathsos_ui
description: BeneathSOS design system — brand tokens, light and dark theme, logo and core components.
version: 0.1.0
repository: https://github.com/Berkant35/beneathsos_ui
issue_tracker: https://github.com/Berkant35/beneathsos_ui/issues

environment:
  sdk: ^3.13.4
  flutter: '>=3.47.0'

dependencies:
  flutter:
    sdk: flutter

dev_dependencies:
  flutter_lints: ^6.0.0
  flutter_test:
    sdk: flutter

flutter:
  fonts:
    - family: AtkinsonHyperlegibleNext
      fonts:
        - asset: fonts/AtkinsonHyperlegibleNext-Regular.ttf
          weight: 400
        - asset: fonts/AtkinsonHyperlegibleNext-SemiBold.ttf
          weight: 600
        - asset: fonts/AtkinsonHyperlegibleNext-Bold.ttf
          weight: 700
        - asset: fonts/AtkinsonHyperlegibleNext-ExtraBold.ttf
          weight: 800
```

- [ ] **Step 3: Write `analysis_options.yaml`, `dart_test.yaml`, `.gitignore`**

`analysis_options.yaml`:

```yaml
include: package:flutter_lints/flutter.yaml

analyzer:
  language:
    strict-casts: true
    strict-inference: true
    strict-raw-types: true
  exclude:
    - build/**

linter:
  rules:
    always_declare_return_types: true
    always_use_package_imports: true
    avoid_catches_without_on_clauses: true
    avoid_dynamic_calls: true
    avoid_positional_boolean_parameters: true
    avoid_redundant_argument_values: true
    directives_ordering: true
    discarded_futures: true
    exhaustive_cases: true
    only_throw_errors: true
    prefer_const_constructors: true
    prefer_const_declarations: true
    prefer_final_locals: true
    prefer_single_quotes: true
    public_member_api_docs: true
    sort_constructors_first: true
    type_annotate_public_apis: true
    unawaited_futures: true
    unnecessary_lambdas: true
    use_named_constants: true
    use_super_parameters: true
```

`dart_test.yaml` (goldens are rendered on macOS; Linux CI skips them, the macOS job in Task 7 runs them):

```yaml
tags:
  golden:
    on_platform:
      linux:
        skip: "Golden images are rendered on macOS; the goldens workflow runs them."
```

`.gitignore`: keep the generated one and append `pubspec_overrides.yaml` and `test/**/failures/`.

- [ ] **Step 4: Write the failing test** — `test/tokens/contrast_test.dart`

```dart
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/painting.dart';
import 'package:flutter_test/flutter_test.dart';

double _rounded(Color a, Color b) => (contrastRatio(a, b) * 10).round() / 10;

void main() {
  group('text pairs keep their WCAG ratio (spec §4)', () {
    final cases = <(String, Color, Color, double)>[
      ('white on primary', BeneathColors.white, BeneathColors.primaryLight, 14.1),
      ('text on background', BeneathColors.textLight, BeneathColors.backgroundLight, 16.1),
      ('on-accent on accent, light', BeneathColors.onAccent, BeneathColors.accentLight, 7.3),
      ('on-accent on accent, dark', BeneathColors.onAccent, BeneathColors.accentDark, 8.2),
      ('white on error', BeneathColors.white, BeneathColors.errorLight, 6.5),
      ('on-error on error, dark', BeneathColors.onErrorDark, BeneathColors.errorDark, 7.7),
      ('on-primary on primary, dark', BeneathColors.backgroundDark, BeneathColors.primaryDark, 8.9),
      ('text on background, dark', BeneathColors.textDark, BeneathColors.backgroundDark, 15.9),
      ('text on secondary surface, dark', BeneathColors.textDark, BeneathColors.surface2Dark, 10.8),
      ('accent on background, dark', BeneathColors.accentDark, BeneathColors.backgroundDark, 8.1),
    ];
    for (final (name, fg, bg, expected) in cases) {
      test(name, () => expect(_rounded(fg, bg), expected));
    }
  });

  test('outlines reach 3:1 on every surface they sit on', () {
    expect(contrastRatio(BeneathColors.outlineLight, BeneathColors.backgroundLight), greaterThanOrEqualTo(3));
    expect(contrastRatio(BeneathColors.outlineLight, BeneathColors.white), greaterThanOrEqualTo(3));
    expect(contrastRatio(BeneathColors.outlineDark, BeneathColors.backgroundDark), greaterThanOrEqualTo(3));
    expect(contrastRatio(BeneathColors.outlineDark, BeneathColors.surface2Dark), greaterThanOrEqualTo(3));
  });

  test('orange stays forbidden for text and icons on light backgrounds', () {
    expect(contrastRatio(BeneathColors.accentLight, BeneathColors.backgroundLight), lessThan(3));
    expect(contrastRatio(BeneathColors.white, BeneathColors.accentLight), lessThan(4.5));
  });

  test('argument order does not matter', () {
    expect(
      contrastRatio(BeneathColors.white, BeneathColors.primaryLight),
      contrastRatio(BeneathColors.primaryLight, BeneathColors.white),
    );
  });
}
```

- [ ] **Step 5: Run it to verify it fails**

Run: `cd HUB/packages/beneathsos_ui && fvm flutter pub get && fvm flutter test test/tokens/contrast_test.dart`
Expected: FAIL — compilation error, `package:beneathsos_ui/beneathsos_ui.dart` not found.

- [ ] **Step 6: Implement**

`lib/src/tokens/colors.dart`:

```dart
import 'dart:ui';

/// The BeneathSOS palette (`docs/brand/README.md` in the hub). Widgets read colours from the theme;
/// use these constants only to build themes and in tests.
abstract final class BeneathColors {
  /// Ink navy — primary in the light theme.
  static const Color primaryLight = Color(0xFF1B2A4E);

  /// Light navy — primary in the dark theme.
  static const Color primaryDark = Color(0xFF9DB2E0);

  /// Safety orange — accent fill in the light theme. Never text or icons on light backgrounds.
  static const Color accentLight = Color(0xFFFF7900);

  /// Accent in the dark theme.
  static const Color accentDark = Color(0xFFFF8C2E);

  /// Text and icons on the accent, both themes. White on orange is forbidden.
  static const Color onAccent = Color(0xFF1A0D00);

  /// Error (blocked state) in the light theme.
  static const Color errorLight = Color(0xFFB3261E);

  /// Error in the dark theme.
  static const Color errorDark = Color(0xFFFFB4AB);

  /// Text and icons on the dark-theme error colour.
  static const Color onErrorDark = Color(0xFF690005);

  /// Background in the light theme.
  static const Color backgroundLight = Color(0xFFF5F6F9);

  /// Text in the light theme.
  static const Color textLight = Color(0xFF121A2B);

  /// Background in the dark theme.
  static const Color backgroundDark = Color(0xFF0C111D);

  /// Text in the dark theme.
  static const Color textDark = Color(0xFFE8ECF5);

  /// Secondary surface in the dark theme (cards, secondary buttons).
  static const Color surface2Dark = Color(0xFF22324F);

  /// Borders in the light theme (≥ 3:1 on its surfaces).
  static const Color outlineLight = Color(0xFF6B7590);

  /// Borders in the dark theme (≥ 3:1 on its surfaces).
  static const Color outlineDark = Color(0xFF8C9AB8);

  /// White.
  static const Color white = Color(0xFFFFFFFF);
}
```

`lib/src/tokens/contrast.dart`:

```dart
import 'dart:math' as math;
import 'dart:ui';

/// WCAG 2.2 contrast ratio of two opaque colours, from 1 to 21. Argument order does not matter.
double contrastRatio(Color a, Color b) {
  final la = a.computeLuminance();
  final lb = b.computeLuminance();
  return (math.max(la, lb) + 0.05) / (math.min(la, lb) + 0.05);
}
```

`lib/beneathsos_ui.dart`:

```dart
/// BeneathSOS design system: brand tokens, light and dark theme, logo and core components.
library;

export 'src/tokens/colors.dart';
export 'src/tokens/contrast.dart';
```

- [ ] **Step 7: Run tests**

Run: `fvm flutter test && fvm flutter analyze --fatal-infos && fvm dart format --set-exit-if-changed .`
Expected: All tests passed (13); No issues found; formatting clean.

- [ ] **Step 8: README and CHANGELOG**

`README.md`:

```markdown
# beneathsos_ui

[![CI](https://github.com/Berkant35/beneathsos_ui/actions/workflows/ci.yml/badge.svg)](https://github.com/Berkant35/beneathsos_ui/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

Design system of [BeneathSOS](https://github.com/Berkant35/beneathsos): brand tokens, a light and a
dark Material 3 theme, the bundled Atkinson Hyperlegible Next typeface, the logo and core components.
Built for people at a collapsed building in an emergency — high contrast, large targets, calm.

```dart
MaterialApp(theme: BeneathTheme.light(), darkTheme: BeneathTheme.dark(), ...);
```

## Rules
- Colours come from the theme. Orange (`BeneathTokens.accent`) is a fill behind dark content only;
  never orange text or icons on a light background.
- At most one `PrimaryButton` per screen, in the bottom half.
- Design guidance: [`docs/design/`](https://github.com/Berkant35/beneathsos/tree/main/docs/design)
  and [ADR 0018](https://github.com/Berkant35/beneathsos/blob/main/docs/adr/0018-design-system-material-theme.md).

## Development
- Fonts are generated in the hub: `tools/brand/build.py --fonts-dir packages/beneathsos_ui/fonts`.
- Golden tests (tag `golden`) run on macOS: `fvm flutter test --tags golden`;
  update with `--update-goldens`. Linux skips them (`dart_test.yaml`).

Licence: Apache-2.0. Atkinson Hyperlegible Next: SIL Open Font License 1.1 (`fonts/OFL.txt`).
```

`CHANGELOG.md`:

```markdown
## 0.1.0
- Initial release: brand colours and contrast table, light and dark theme, Atkinson Hyperlegible Next
  (400/600/700/800), `BeneathTokens` (accent, numeric text, motion), `BeneathLogo`, `PrimaryButton`,
  `SecondaryButton`.
```

- [ ] **Step 9: Commit (package)**

```bash
cd HUB/packages/beneathsos_ui && git add -A
git commit -m "feat(tokens): package skeleton, brand colours and contrast table"
```

---

### Task 3: Typography, spacing, sizes, motion and `BeneathTokens`

**Files:**
- Create: `lib/src/tokens/typography.dart`, `spacing.dart`, `sizes.dart`, `motion.dart`, `lib/src/theme/beneath_tokens.dart`
- Modify: `lib/beneathsos_ui.dart` (exports)
- Test: `test/tokens/typography_test.dart`, `test/tokens/spacing_test.dart`, `test/theme/beneath_tokens_test.dart`

**Interfaces:**
- Consumes: `BeneathColors` (Task 2).
- Produces:
  - `const String beneathFontFamily = 'AtkinsonHyperlegibleNext'`, `const String beneathFontPackage = 'beneathsos_ui'`
  - `BeneathTypography.textTheme() -> TextTheme`, `BeneathTypography.numeric() -> TextStyle`
  - `BeneathSpacing.{xs=4, s=8, sm=12, m=16, l=24, xl=32, xxl=48}`, `BeneathSpacing.pageFor(double width) -> EdgeInsets`
  - `BeneathSizes.{minTouchTarget=56, primaryButtonHeight=64, radius=16, radiusSmall=8, wideBreakpoint=600}`
  - `BeneathMotion({short, medium, long, curve})`, `BeneathMotion.standard`, `BeneathMotion.reduced`
  - `BeneathTokens({accent, onAccent, numeric})`, `BeneathTokens.light()`, `BeneathTokens.dark()`, `BeneathTokens.of(BuildContext)`, `BeneathTokens.motionOf(BuildContext)`

- [ ] **Step 1: Write the failing tests**

`test/tokens/typography_test.dart`:

```dart
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  final theme = BeneathTypography.textTheme();

  test('every role uses the bundled Atkinson font', () {
    final styles = [
      theme.displaySmall, theme.headlineSmall, theme.titleLarge, theme.bodyLarge,
      theme.bodyMedium, theme.bodySmall, theme.labelLarge, BeneathTypography.numeric(),
    ];
    for (final style in styles) {
      expect(style!.fontFamily, 'packages/beneathsos_ui/AtkinsonHyperlegibleNext');
    }
  });

  test('body text is never below 17', () {
    expect(theme.bodyLarge!.fontSize, 19);
    expect(theme.bodyMedium!.fontSize, 17);
  });

  test('spec sizes and weights', () {
    expect((theme.displaySmall!.fontSize, theme.displaySmall!.fontWeight), (32, FontWeight.w800));
    expect((theme.headlineSmall!.fontSize, theme.headlineSmall!.fontWeight), (24, FontWeight.w700));
    expect((theme.titleLarge!.fontSize, theme.titleLarge!.fontWeight), (20, FontWeight.w700));
    expect((theme.labelLarge!.fontSize, theme.labelLarge!.fontWeight), (19, FontWeight.w700));
    expect((theme.bodySmall!.fontSize, theme.bodySmall!.fontWeight), (15, FontWeight.w400));
    expect(theme.bodyLarge!.height! * theme.bodyLarge!.fontSize!, closeTo(28, 0.001));
  });

  test('numbers use bold tabular figures so changing values do not jump', () {
    final numeric = BeneathTypography.numeric();
    expect(numeric.fontFeatures, contains(const FontFeature.tabularFigures()));
    expect((numeric.fontSize, numeric.fontWeight), (28, FontWeight.w800));
  });
}
```

`test/tokens/spacing_test.dart`:

```dart
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('page padding is 16 on phones and 24 from 600 px', () {
    expect(BeneathSpacing.pageFor(375), const EdgeInsets.all(16));
    expect(BeneathSpacing.pageFor(599), const EdgeInsets.all(16));
    expect(BeneathSpacing.pageFor(600), const EdgeInsets.all(24));
  });

  test('field-ergonomics sizes', () {
    expect(BeneathSizes.minTouchTarget, 56);
    expect(BeneathSizes.primaryButtonHeight, 64);
  });
}
```

`test/theme/beneath_tokens_test.dart`:

```dart
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

BeneathMotion _motion(WidgetTester tester) =>
    BeneathTokens.motionOf(tester.element(find.byType(SizedBox)));

void main() {
  test('light and dark tokens carry the theme accent', () {
    expect(BeneathTokens.light().accent, BeneathColors.accentLight);
    expect(BeneathTokens.dark().accent, BeneathColors.accentDark);
    expect(BeneathTokens.light().onAccent, BeneathColors.onAccent);
  });

  test('lerp ends on the target tokens', () {
    final lerped = BeneathTokens.light().lerp(BeneathTokens.dark(), 1);
    expect(lerped.accent, BeneathColors.accentDark);
  });

  testWidgets('reduce motion turns every duration to zero', (tester) async {
    await tester.pumpWidget(
      const MediaQuery(data: MediaQueryData(disableAnimations: true), child: SizedBox()),
    );
    final motion = _motion(tester);
    expect([motion.short, motion.medium, motion.long], everyElement(Duration.zero));
  });

  testWidgets('standard motion is 150 / 250 / 400 ms', (tester) async {
    await tester.pumpWidget(const MediaQuery(data: MediaQueryData(), child: SizedBox()));
    final motion = _motion(tester);
    expect(
      [motion.short, motion.medium, motion.long],
      const [Duration(milliseconds: 150), Duration(milliseconds: 250), Duration(milliseconds: 400)],
    );
  });

  testWidgets('of() explains a missing theme extension', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: SizedBox()));
    expect(
      () => BeneathTokens.of(tester.element(find.byType(SizedBox))),
      throwsA(isA<StateError>()),
    );
  });
}
```

- [ ] **Step 2: Run them to verify they fail**

Run: `fvm flutter test test/tokens test/theme`
Expected: FAIL — compilation errors (`BeneathTypography`, `BeneathSpacing`, `BeneathTokens` undefined).

- [ ] **Step 3: Implement**

`lib/src/tokens/typography.dart`:

```dart
import 'package:flutter/material.dart';

/// Font family declared in this package's `pubspec.yaml`.
const String beneathFontFamily = 'AtkinsonHyperlegibleNext';

/// Package that bundles the font; `TextStyle.package` resolves it from any app.
const String beneathFontPackage = 'beneathsos_ui';

/// Text roles (spec §4). Colours come from the theme; sizes scale with the system text size.
abstract final class BeneathTypography {
  static TextStyle _style(double size, double lineHeight, FontWeight weight) => TextStyle(
    fontFamily: beneathFontFamily,
    package: beneathFontPackage,
    fontSize: size,
    height: lineHeight / size,
    fontWeight: weight,
  );

  /// Every Material text slot. Body text never goes below 17; 15 is fine print only.
  static TextTheme textTheme() => TextTheme(
    displayLarge: _style(40, 48, FontWeight.w800),
    displayMedium: _style(36, 44, FontWeight.w800),
    displaySmall: _style(32, 40, FontWeight.w800),
    headlineLarge: _style(28, 36, FontWeight.w700),
    headlineMedium: _style(26, 34, FontWeight.w700),
    headlineSmall: _style(24, 32, FontWeight.w700),
    titleLarge: _style(20, 28, FontWeight.w700),
    titleMedium: _style(19, 26, FontWeight.w600),
    titleSmall: _style(17, 24, FontWeight.w600),
    bodyLarge: _style(19, 28, FontWeight.w400),
    bodyMedium: _style(17, 24, FontWeight.w400),
    bodySmall: _style(15, 20, FontWeight.w400),
    labelLarge: _style(19, 24, FontWeight.w700),
    labelMedium: _style(17, 22, FontWeight.w600),
    labelSmall: _style(15, 20, FontWeight.w600),
  );

  /// dBm, countdowns, metres: bold tabular figures, so changing numbers do not jump.
  static TextStyle numeric() => _style(28, 32, FontWeight.w800).copyWith(
    fontFeatures: const [FontFeature.tabularFigures()],
  );
}
```

`lib/src/tokens/spacing.dart`:

```dart
import 'package:beneathsos_ui/src/tokens/sizes.dart';
import 'package:flutter/widgets.dart';

/// Spacing scale in logical pixels.
abstract final class BeneathSpacing {
  /// 4.
  static const double xs = 4;

  /// 8.
  static const double s = 8;

  /// 12.
  static const double sm = 12;

  /// 16.
  static const double m = 16;

  /// 24.
  static const double l = 24;

  /// 32.
  static const double xl = 32;

  /// 48.
  static const double xxl = 48;

  /// Page padding: 16 on phones, 24 from [BeneathSizes.wideBreakpoint].
  static EdgeInsets pageFor(double width) =>
      EdgeInsets.all(width >= BeneathSizes.wideBreakpoint ? l : m);
}
```

`lib/src/tokens/sizes.dart`:

```dart
/// Field-ergonomics sizes (`docs/design/accessibility.md` in the hub).
abstract final class BeneathSizes {
  /// Smallest touch target — gloves, one hand, stress.
  static const double minTouchTarget = 56;

  /// Height of the primary action.
  static const double primaryButtonHeight = 64;

  /// Corner radius of buttons and cards.
  static const double radius = 16;

  /// Corner radius of small elements.
  static const double radiusSmall = 8;

  /// Width from which layouts use the wide page padding.
  static const double wideBreakpoint = 600;
}
```

`lib/src/tokens/motion.dart`:

```dart
import 'package:flutter/animation.dart';
import 'package:flutter/foundation.dart';

/// Animation durations and curve. Motion only explains time or state; never decoration.
@immutable
final class BeneathMotion {
  /// Creates a motion set.
  const BeneathMotion({
    required this.short,
    required this.medium,
    required this.long,
    required this.curve,
  });

  /// Default motion: 150 / 250 / 400 ms, ease-out.
  static const BeneathMotion standard = BeneathMotion(
    short: Duration(milliseconds: 150),
    medium: Duration(milliseconds: 250),
    long: Duration(milliseconds: 400),
    curve: Curves.easeOutCubic,
  );

  /// Used when the system "reduce motion" setting is on: no animation.
  static const BeneathMotion reduced = BeneathMotion(
    short: Duration.zero,
    medium: Duration.zero,
    long: Duration.zero,
    curve: Curves.linear,
  );

  /// Small state changes (pressed, toggled).
  final Duration short;

  /// Elements entering or leaving.
  final Duration medium;

  /// Screen-level transitions.
  final Duration long;

  /// Easing curve.
  final Curve curve;
}
```

`lib/src/theme/beneath_tokens.dart`:

```dart
import 'package:beneathsos_ui/src/tokens/colors.dart';
import 'package:beneathsos_ui/src/tokens/motion.dart';
import 'package:beneathsos_ui/src/tokens/typography.dart';
import 'package:flutter/material.dart';

/// Brand tokens Material has no slot for. Read with [BeneathTokens.of].
@immutable
class BeneathTokens extends ThemeExtension<BeneathTokens> {
  /// Creates tokens.
  const BeneathTokens({required this.accent, required this.onAccent, required this.numeric});

  /// Light-theme tokens.
  factory BeneathTokens.light() => BeneathTokens(
    accent: BeneathColors.accentLight,
    onAccent: BeneathColors.onAccent,
    numeric: BeneathTypography.numeric(),
  );

  /// Dark-theme tokens.
  factory BeneathTokens.dark() => BeneathTokens(
    accent: BeneathColors.accentDark,
    onAccent: BeneathColors.onAccent,
    numeric: BeneathTypography.numeric(),
  );

  /// Action and attention fill. In the light theme never use it for text or icons.
  final Color accent;

  /// Text and icons on [accent].
  final Color onAccent;

  /// Style for changing numbers (dBm, countdowns, metres).
  final TextStyle numeric;

  /// The tokens of the nearest theme. Throws a [StateError] if the theme is not a BeneathSOS theme.
  static BeneathTokens of(BuildContext context) =>
      Theme.of(context).extension<BeneathTokens>() ??
      (throw StateError('No BeneathTokens: use BeneathTheme.light() or BeneathTheme.dark().'));

  /// Motion for this context: [BeneathMotion.reduced] when the system asks to reduce motion.
  static BeneathMotion motionOf(BuildContext context) => MediaQuery.disableAnimationsOf(context)
      ? BeneathMotion.reduced
      : BeneathMotion.standard;

  @override
  BeneathTokens copyWith({Color? accent, Color? onAccent, TextStyle? numeric}) => BeneathTokens(
    accent: accent ?? this.accent,
    onAccent: onAccent ?? this.onAccent,
    numeric: numeric ?? this.numeric,
  );

  @override
  BeneathTokens lerp(covariant BeneathTokens? other, double t) {
    if (other == null) return this;
    return BeneathTokens(
      accent: Color.lerp(accent, other.accent, t)!,
      onAccent: Color.lerp(onAccent, other.onAccent, t)!,
      numeric: TextStyle.lerp(numeric, other.numeric, t)!,
    );
  }
}
```

`lib/beneathsos_ui.dart` exports (alphabetical):

```dart
export 'src/theme/beneath_tokens.dart';
export 'src/tokens/colors.dart';
export 'src/tokens/contrast.dart';
export 'src/tokens/motion.dart';
export 'src/tokens/sizes.dart';
export 'src/tokens/spacing.dart';
export 'src/tokens/typography.dart';
```

- [ ] **Step 4: Run tests**

Run: `fvm flutter test && fvm flutter analyze --fatal-infos && fvm dart format --set-exit-if-changed .`
Expected: All tests passed; No issues found.

- [ ] **Step 5: Commit (package)**

```bash
git add -A && git commit -m "feat(tokens): typography, spacing, sizes, motion and BeneathTokens"
```

---

### Task 4: `BeneathTheme` light and dark

**Files:**
- Create: `lib/src/theme/beneath_theme.dart`
- Modify: `lib/beneathsos_ui.dart`
- Test: `test/theme/beneath_theme_test.dart`

**Interfaces:**
- Consumes: Tasks 2–3.
- Produces: `BeneathTheme.light() -> ThemeData`, `BeneathTheme.dark() -> ThemeData` (with `BeneathTokens` extension).

- [ ] **Step 1: Write the failing test** — `test/theme/beneath_theme_test.dart`

```dart
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void _expectCommon(ThemeData theme, Color accent) {
  final s = theme.colorScheme;
  for (final role in [
    s.primary, s.secondary, s.tertiary, s.primaryContainer, s.secondaryContainer,
    s.tertiaryContainer, s.onSurface, s.onSurfaceVariant, s.outline,
  ]) {
    expect(role, isNot(accent), reason: 'no Material role may be orange');
  }
  expect(theme.extension<BeneathTokens>()!.accent, accent);
  expect(theme.textTheme.bodyMedium!.fontFamily, 'packages/beneathsos_ui/AtkinsonHyperlegibleNext');
  for (final style in [
    theme.filledButtonTheme.style, theme.outlinedButtonTheme.style,
    theme.textButtonTheme.style, theme.elevatedButtonTheme.style,
  ]) {
    expect(style!.minimumSize!.resolve(<WidgetState>{})!.height, greaterThanOrEqualTo(56));
  }
  expect(theme.scaffoldBackgroundColor, s.surface);
}

void main() {
  test('light theme uses the brand palette', () {
    final theme = BeneathTheme.light();
    final s = theme.colorScheme;
    expect(s.brightness, Brightness.light);
    expect((s.primary, s.onPrimary), (BeneathColors.primaryLight, BeneathColors.white));
    expect((s.secondary, s.tertiary), (BeneathColors.primaryLight, BeneathColors.primaryLight));
    expect((s.surface, s.onSurface), (BeneathColors.backgroundLight, BeneathColors.textLight));
    expect(s.surfaceContainer, BeneathColors.white);
    expect((s.error, s.onError), (BeneathColors.errorLight, BeneathColors.white));
    expect(s.outline, BeneathColors.outlineLight);
    _expectCommon(theme, BeneathColors.accentLight);
  });

  test('dark theme uses the brand palette', () {
    final theme = BeneathTheme.dark();
    final s = theme.colorScheme;
    expect(s.brightness, Brightness.dark);
    expect((s.primary, s.onPrimary), (BeneathColors.primaryDark, BeneathColors.backgroundDark));
    expect((s.secondary, s.tertiary), (BeneathColors.primaryDark, BeneathColors.primaryDark));
    expect((s.surface, s.onSurface), (BeneathColors.backgroundDark, BeneathColors.textDark));
    expect(s.surfaceContainer, BeneathColors.surface2Dark);
    expect((s.error, s.onError), (BeneathColors.errorDark, BeneathColors.onErrorDark));
    expect(s.outline, BeneathColors.outlineDark);
    _expectCommon(theme, BeneathColors.accentDark);
  });
}
```

- [ ] **Step 2: Run it to verify it fails**

Run: `fvm flutter test test/theme/beneath_theme_test.dart`
Expected: FAIL — `BeneathTheme` undefined.

- [ ] **Step 3: Implement** — `lib/src/theme/beneath_theme.dart`

```dart
import 'package:beneathsos_ui/src/theme/beneath_tokens.dart';
import 'package:beneathsos_ui/src/tokens/colors.dart';
import 'package:beneathsos_ui/src/tokens/sizes.dart';
import 'package:beneathsos_ui/src/tokens/typography.dart';
import 'package:flutter/material.dart';

/// The BeneathSOS light and dark themes. Apps pass both and follow the system setting.
abstract final class BeneathTheme {
  /// Light theme.
  static ThemeData light() => _build(_light, BeneathTokens.light());

  /// Dark theme.
  static ThemeData dark() => _build(_dark, BeneathTokens.dark());

  // secondary and tertiary are navy on purpose: no built-in widget may paint orange text or icons.
  static const ColorScheme _light = ColorScheme(
    brightness: Brightness.light,
    primary: BeneathColors.primaryLight,
    onPrimary: BeneathColors.white,
    secondary: BeneathColors.primaryLight,
    onSecondary: BeneathColors.white,
    tertiary: BeneathColors.primaryLight,
    onTertiary: BeneathColors.white,
    error: BeneathColors.errorLight,
    onError: BeneathColors.white,
    surface: BeneathColors.backgroundLight,
    onSurface: BeneathColors.textLight,
    surfaceContainerLowest: BeneathColors.white,
    surfaceContainerLow: BeneathColors.white,
    surfaceContainer: BeneathColors.white,
    surfaceContainerHigh: BeneathColors.white,
    surfaceContainerHighest: BeneathColors.white,
    outline: BeneathColors.outlineLight,
  );

  static const ColorScheme _dark = ColorScheme(
    brightness: Brightness.dark,
    primary: BeneathColors.primaryDark,
    onPrimary: BeneathColors.backgroundDark,
    secondary: BeneathColors.primaryDark,
    onSecondary: BeneathColors.backgroundDark,
    tertiary: BeneathColors.primaryDark,
    onTertiary: BeneathColors.backgroundDark,
    error: BeneathColors.errorDark,
    onError: BeneathColors.onErrorDark,
    surface: BeneathColors.backgroundDark,
    onSurface: BeneathColors.textDark,
    surfaceContainerLowest: BeneathColors.surface2Dark,
    surfaceContainerLow: BeneathColors.surface2Dark,
    surfaceContainer: BeneathColors.surface2Dark,
    surfaceContainerHigh: BeneathColors.surface2Dark,
    surfaceContainerHighest: BeneathColors.surface2Dark,
    outline: BeneathColors.outlineDark,
  );

  static ThemeData _build(ColorScheme scheme, BeneathTokens tokens) {
    final text = BeneathTypography.textTheme();
    final shape = RoundedRectangleBorder(borderRadius: BorderRadius.circular(BeneathSizes.radius));
    const minimum = Size(BeneathSizes.minTouchTarget, BeneathSizes.minTouchTarget);
    return ThemeData(
      colorScheme: scheme,
      scaffoldBackgroundColor: scheme.surface,
      textTheme: text,
      materialTapTargetSize: MaterialTapTargetSize.padded,
      extensions: [tokens],
      appBarTheme: AppBarTheme(
        backgroundColor: scheme.surface,
        foregroundColor: scheme.primary,
        elevation: 0,
        scrolledUnderElevation: 0,
        titleTextStyle: text.headlineSmall?.copyWith(color: scheme.primary),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(minimumSize: minimum, shape: shape, textStyle: text.labelLarge),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(minimumSize: minimum, shape: shape, textStyle: text.labelLarge),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(minimumSize: minimum, shape: shape, textStyle: text.labelLarge),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(minimumSize: minimum, shape: shape, textStyle: text.labelLarge),
      ),
      cardTheme: CardThemeData(color: scheme.surfaceContainer, shape: shape, elevation: 0),
      listTileTheme: const ListTileThemeData(minVerticalPadding: 10, minTileHeight: BeneathSizes.minTouchTarget),
    );
  }
}
```

Add `export 'src/theme/beneath_theme.dart';` to `lib/beneathsos_ui.dart` (before `beneath_tokens.dart`).

- [ ] **Step 4: Run tests**

Run: `fvm flutter test && fvm flutter analyze --fatal-infos && fvm dart format --set-exit-if-changed .`
Expected: All tests passed; No issues found.

- [ ] **Step 5: Commit (package)**

```bash
git add -A && git commit -m "feat(theme): BeneathTheme light and dark from the brand palette"
```

---

### Task 5: `BeneathLogo` (symbol painter and lock-up) with goldens

**Files:**
- Create: `lib/src/widgets/signal_exit_painter.dart`, `lib/src/widgets/beneath_logo.dart`
- Create: `test/helpers/golden.dart`
- Test: `test/widgets/beneath_logo_test.dart`, `test/widgets/logo_golden_test.dart`, `test/widgets/goldens/*.png`

**Interfaces:**
- Consumes: `BeneathTheme`, `BeneathTokens.of`, `beneathFontFamily`, `beneathFontPackage`.
- Produces: `SignalExitPainter({required Color line, required Color accent})`; `BeneathLogo.symbol({double size = 48, required String semanticLabel})`; `BeneathLogo.lockup({double height = 48, required String semanticLabel})`; test helpers `loadBeneathFont()`, `goldenFrame(Widget, {required Brightness brightness})`, `goldenKey`.

- [ ] **Step 1: Write the test helper** — `test/helpers/golden.dart`

```dart
import 'dart:io';
import 'dart:typed_data';

import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Key of the RepaintBoundary that golden tests capture.
const goldenKey = ValueKey('golden');

/// Loads the bundled Atkinson weights under the family name the theme uses (call in setUpAll).
Future<void> loadBeneathFont() async {
  final loader = FontLoader('packages/$beneathFontPackage/$beneathFontFamily');
  for (final style in const ['Regular', 'SemiBold', 'Bold', 'ExtraBold']) {
    final bytes = File('fonts/AtkinsonHyperlegibleNext-$style.ttf').readAsBytesSync();
    loader.addFont(Future.value(ByteData.sublistView(bytes)));
  }
  await loader.load();
}

/// [child] on the theme background, padded, inside a RepaintBoundary keyed [goldenKey].
Widget goldenFrame(Widget child, {required Brightness brightness}) => MaterialApp(
  debugShowCheckedModeBanner: false,
  theme: brightness == Brightness.light ? BeneathTheme.light() : BeneathTheme.dark(),
  home: Scaffold(
    body: Center(
      child: RepaintBoundary(
        key: goldenKey,
        child: Builder(
          builder: (context) => ColoredBox(
            color: Theme.of(context).colorScheme.surface,
            child: Padding(padding: const EdgeInsets.all(16), child: child),
          ),
        ),
      ),
    ),
  ),
);
```

- [ ] **Step 2: Write the failing tests**

`test/widgets/beneath_logo_test.dart`:

```dart
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/golden.dart';

SignalExitPainter _painter(WidgetTester tester) => tester
    .widgetList<CustomPaint>(find.descendant(of: find.byType(BeneathLogo), matching: find.byType(CustomPaint)))
    .map((paint) => paint.painter)
    .whereType<SignalExitPainter>()
    .single;

void main() {
  testWidgets('screen readers read the logo by its label, once', (tester) async {
    final handle = tester.ensureSemantics();
    await tester.pumpWidget(goldenFrame(
      const BeneathLogo.lockup(semanticLabel: 'BeneathSOS'),
      brightness: Brightness.light,
    ));
    expect(find.bySemanticsLabel('BeneathSOS'), findsOneWidget);
    handle.dispose();
  });

  testWidgets('colours follow the light theme', (tester) async {
    await tester.pumpWidget(goldenFrame(
      const BeneathLogo.symbol(semanticLabel: 'BeneathSOS'),
      brightness: Brightness.light,
    ));
    expect((_painter(tester).line, _painter(tester).accent), (BeneathColors.primaryLight, BeneathColors.accentLight));
  });

  testWidgets('colours follow the dark theme', (tester) async {
    await tester.pumpWidget(goldenFrame(
      const BeneathLogo.symbol(semanticLabel: 'BeneathSOS'),
      brightness: Brightness.dark,
    ));
    expect((_painter(tester).line, _painter(tester).accent), (BeneathColors.primaryDark, BeneathColors.accentDark));
  });

  testWidgets('the lock-up spells Beneath + SOS and ignores system text scaling', (tester) async {
    await tester.pumpWidget(goldenFrame(
      const BeneathLogo.lockup(semanticLabel: 'BeneathSOS'),
      brightness: Brightness.light,
    ));
    final text = tester.widget<RichText>(find.descendant(of: find.byType(BeneathLogo), matching: find.byType(RichText)));
    expect(text.text.toPlainText(), 'BeneathSOS');
    expect(text.textScaler, TextScaler.noScaling);
  });

  test('repaints only when a colour changes', () {
    const a = SignalExitPainter(line: BeneathColors.primaryLight, accent: BeneathColors.accentLight);
    const b = SignalExitPainter(line: BeneathColors.primaryLight, accent: BeneathColors.accentLight);
    const c = SignalExitPainter(line: BeneathColors.primaryDark, accent: BeneathColors.accentLight);
    expect(a.shouldRepaint(b), isFalse);
    expect(a.shouldRepaint(c), isTrue);
  });
}
```

`test/widgets/logo_golden_test.dart`:

```dart
@Tags(['golden'])
library;

import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/golden.dart';

void main() {
  setUpAll(loadBeneathFont);

  for (final brightness in Brightness.values) {
    testWidgets('symbol, ${brightness.name}', (tester) async {
      await tester.pumpWidget(goldenFrame(
        const BeneathLogo.symbol(size: 96, semanticLabel: 'BeneathSOS'),
        brightness: brightness,
      ));
      await expectLater(find.byKey(goldenKey), matchesGoldenFile('goldens/logo_symbol_${brightness.name}.png'));
    });

    testWidgets('lock-up, ${brightness.name}', (tester) async {
      await tester.pumpWidget(goldenFrame(
        const BeneathLogo.lockup(semanticLabel: 'BeneathSOS'),
        brightness: brightness,
      ));
      await expectLater(find.byKey(goldenKey), matchesGoldenFile('goldens/logo_lockup_${brightness.name}.png'));
    });
  }
}
```

- [ ] **Step 3: Run them to verify they fail**

Run: `fvm flutter test test/widgets`
Expected: FAIL — `BeneathLogo` / `SignalExitPainter` undefined.

- [ ] **Step 4: Implement**

`lib/src/widgets/signal_exit_painter.dart`:

```dart
import 'package:flutter/rendering.dart';

/// Draws the "signal exit" symbol: rubble line, phone dot below it, three arcs rising and fading.
/// Geometry is the brand's 48-unit grid (`docs/brand/README.md` in the hub).
class SignalExitPainter extends CustomPainter {
  /// Creates the painter; [line] colours the rubble line, [accent] the dot and arcs.
  const SignalExitPainter({required this.line, required this.accent});

  /// Rubble-line colour.
  final Color line;

  /// Dot and arc colour.
  final Color accent;

  static const double _grid = 48;
  static const double _stroke = 3.6;
  // (start x, end x, y, radius, opacity) — SVG "M x1 y A r r 0 0 1 x2 y".
  static const _arcs = [
    (18.5, 29.5, 24.5, 7.5, 1.0),
    (13.5, 34.5, 19.5, 14.5, 0.75),
    (8.5, 39.5, 14.5, 21.5, 0.5),
  ];

  @override
  void paint(Canvas canvas, Size size) {
    final scale = size.shortestSide / _grid;
    canvas
      ..save()
      ..translate((size.width - _grid * scale) / 2, (size.height - _grid * scale) / 2)
      ..scale(scale);
    final stroke = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = _stroke
      ..strokeCap = StrokeCap.round;
    canvas
      ..drawLine(const Offset(6, 30), const Offset(42, 30), stroke..color = line)
      ..drawCircle(const Offset(24, 38), 3.4, Paint()..color = accent);
    for (final (x1, x2, y, radius, opacity) in _arcs) {
      final arc = Path()
        ..moveTo(x1, y)
        ..arcToPoint(Offset(x2, y), radius: Radius.circular(radius));
      canvas.drawPath(arc, stroke..color = accent.withValues(alpha: opacity));
    }
    canvas.restore();
  }

  @override
  bool shouldRepaint(SignalExitPainter oldDelegate) =>
      oldDelegate.line != line || oldDelegate.accent != accent;
}
```

(`arcToPoint` defaults to `clockwise: true`, which in Flutter's y-down canvas matches SVG sweep-flag 1: arcs bulge upwards.)

`lib/src/widgets/beneath_logo.dart`:

```dart
import 'package:beneathsos_ui/src/theme/beneath_tokens.dart';
import 'package:beneathsos_ui/src/tokens/typography.dart';
import 'package:beneathsos_ui/src/widgets/signal_exit_painter.dart';
import 'package:flutter/material.dart';

/// The BeneathSOS logo in theme colours. Logotypes are exempt from WCAG contrast minimums, so the
/// orange "SOS" may sit on the light background (text and icons may not).
class BeneathLogo extends StatelessWidget {
  /// The symbol alone, [size] × [size].
  const BeneathLogo.symbol({required this.semanticLabel, this.size = 48, super.key}) : _lockup = false;

  /// Symbol + "Beneath" + "SOS", [height] tall. The wordmark ignores system text scaling.
  const BeneathLogo.lockup({required this.semanticLabel, double height = 48, super.key})
    : size = height,
      _lockup = true;

  /// What screen readers say (localised by the app, e.g. "BeneathSOS").
  final String semanticLabel;

  /// Symbol size, or lock-up height.
  final double size;

  final bool _lockup;

  @override
  Widget build(BuildContext context) {
    final primary = Theme.of(context).colorScheme.primary;
    final accent = BeneathTokens.of(context).accent;
    final symbol = CustomPaint(
      size: Size.square(size),
      painter: SignalExitPainter(line: primary, accent: accent),
    );
    final Widget logo = _lockup
        ? Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              symbol,
              SizedBox(width: size * 0.2),
              Text.rich(
                TextSpan(
                  children: [
                    TextSpan(text: 'Beneath', style: TextStyle(color: primary)),
                    TextSpan(text: 'SOS', style: TextStyle(color: accent)),
                  ],
                ),
                textScaler: TextScaler.noScaling,
                style: TextStyle(
                  fontFamily: beneathFontFamily,
                  package: beneathFontPackage,
                  fontWeight: FontWeight.w800,
                  fontSize: size * 0.6,
                  height: 1,
                ),
              ),
            ],
          )
        : symbol;
    return Semantics(label: semanticLabel, image: true, excludeSemantics: true, child: logo);
  }
}
```

Add exports to `lib/beneathsos_ui.dart`: `src/widgets/beneath_logo.dart`, `src/widgets/signal_exit_painter.dart`.

- [ ] **Step 5: Run the non-golden tests**

Run: `fvm flutter test test/widgets/beneath_logo_test.dart`
Expected: All tests passed (5).

- [ ] **Step 6: Watch the goldens fail, then create and inspect them**

Run: `fvm flutter test --tags golden`
Expected: FAIL — golden files do not exist yet.

Run: `fvm flutter test --tags golden --update-goldens`
Expected: 4 PNGs in `test/widgets/goldens/`. Open each (Read tool) and check: navy line + orange arcs on `#F5F6F9` (light); light-navy line + orange on `#0C111D` (dark); arcs bulge upwards and fade outwards; "Beneath" in navy, "SOS" in orange, Atkinson ExtraBold (not the test font boxes).

Run: `fvm flutter test`
Expected: All tests passed (goldens included on macOS).

- [ ] **Step 7: Commit (package)**

```bash
fvm flutter analyze --fatal-infos && fvm dart format --set-exit-if-changed .
git add -A && git commit -m "feat(widgets): BeneathLogo symbol and lock-up with goldens"
```

---

### Task 6: `PrimaryButton` and `SecondaryButton` with goldens

**Files:**
- Create: `lib/src/widgets/primary_button.dart`, `lib/src/widgets/secondary_button.dart`
- Test: `test/widgets/buttons_test.dart`, `test/widgets/buttons_golden_test.dart`, goldens

**Interfaces:**
- Consumes: `BeneathTokens.of`, `BeneathSizes`, theme text.
- Produces: `PrimaryButton({required String label, required VoidCallback? onPressed, IconData? icon})`; `SecondaryButton({required String label, required VoidCallback? onPressed, IconData? icon})`.

- [ ] **Step 1: Write the failing tests**

`test/widgets/buttons_test.dart`:

```dart
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

Widget _frame(Widget child, {Brightness brightness = Brightness.light}) => MaterialApp(
  theme: brightness == Brightness.light ? BeneathTheme.light() : BeneathTheme.dark(),
  home: Scaffold(body: Padding(padding: const EdgeInsets.all(16), child: Column(children: [child]))),
);

ButtonStyle _style<T extends ButtonStyleButton>(WidgetTester tester) => tester.widget<T>(find.byType(T)).style!;

void main() {
  testWidgets('primary: 64 tall, full width, dark text on orange', (tester) async {
    await tester.pumpWidget(_frame(PrimaryButton(label: 'Start a search', onPressed: () {})));
    final size = tester.getSize(find.byType(PrimaryButton));
    expect(size.height, 64);
    expect(size.width, 800 - 32);
    final style = _style<FilledButton>(tester);
    expect(style.backgroundColor!.resolve(<WidgetState>{}), BeneathColors.accentLight);
    expect(style.foregroundColor!.resolve(<WidgetState>{}), BeneathColors.onAccent);
  });

  testWidgets('primary: dark theme uses the dark accent', (tester) async {
    await tester.pumpWidget(_frame(PrimaryButton(label: 'Start', onPressed: () {}), brightness: Brightness.dark));
    expect(_style<FilledButton>(tester).backgroundColor!.resolve(<WidgetState>{}), BeneathColors.accentDark);
  });

  testWidgets('primary: tap calls onPressed and the icon is shown', (tester) async {
    var taps = 0;
    await tester.pumpWidget(_frame(PrimaryButton(label: 'Start', icon: Icons.search_rounded, onPressed: () => taps++)));
    expect(find.byIcon(Icons.search_rounded), findsOneWidget);
    await tester.tap(find.text('Start'));
    expect(taps, 1);
  });

  testWidgets('primary: screen readers hear a button with its label', (tester) async {
    final handle = tester.ensureSemantics();
    await tester.pumpWidget(_frame(PrimaryButton(label: 'Start a search', onPressed: () {})));
    expect(
      tester.getSemantics(find.bySemanticsLabel('Start a search')),
      containsSemantics(label: 'Start a search', isButton: true, isEnabled: true),
    );
    handle.dispose();
  });

  testWidgets('secondary: 56 tall; light = white fill, navy label and border', (tester) async {
    await tester.pumpWidget(_frame(SecondaryButton(label: 'I am trapped', onPressed: () {})));
    expect(tester.getSize(find.byType(SecondaryButton)).height, 56);
    final style = _style<OutlinedButton>(tester);
    expect(style.backgroundColor!.resolve(<WidgetState>{}), BeneathColors.white);
    expect(style.foregroundColor!.resolve(<WidgetState>{}), BeneathColors.primaryLight);
    expect(style.side!.resolve(<WidgetState>{})!.color, BeneathColors.primaryLight);
  });

  testWidgets('secondary: dark = #22324F fill, light label', (tester) async {
    await tester.pumpWidget(_frame(SecondaryButton(label: 'I am trapped', onPressed: () {}), brightness: Brightness.dark));
    final style = _style<OutlinedButton>(tester);
    expect(style.backgroundColor!.resolve(<WidgetState>{}), BeneathColors.surface2Dark);
    expect(style.foregroundColor!.resolve(<WidgetState>{}), BeneathColors.textDark);
  });
}
```

`test/widgets/buttons_golden_test.dart`:

```dart
@Tags(['golden'])
library;

import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/golden.dart';

void main() {
  setUpAll(loadBeneathFont);

  for (final brightness in Brightness.values) {
    testWidgets('buttons, ${brightness.name}', (tester) async {
      await tester.pumpWidget(goldenFrame(
        SizedBox(
          width: 360,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              PrimaryButton(label: 'Start a search', icon: Icons.search_rounded, onPressed: () {}),
              const SizedBox(height: 16),
              SecondaryButton(label: 'I am trapped', onPressed: () {}),
            ],
          ),
        ),
        brightness: brightness,
      ));
      await expectLater(find.byKey(goldenKey), matchesGoldenFile('goldens/buttons_${brightness.name}.png'));
    });
  }
}
```

- [ ] **Step 2: Run them to verify they fail**

Run: `fvm flutter test test/widgets/buttons_test.dart`
Expected: FAIL — `PrimaryButton` / `SecondaryButton` undefined.

- [ ] **Step 3: Implement**

`lib/src/widgets/primary_button.dart`:

```dart
import 'package:beneathsos_ui/src/theme/beneath_tokens.dart';
import 'package:beneathsos_ui/src/tokens/sizes.dart';
import 'package:flutter/material.dart';

/// The screen's one primary action: orange fill, dark label, 64 tall, full width.
/// Use at most one per screen, in the bottom half (thumb zone).
class PrimaryButton extends StatelessWidget {
  /// Creates the primary action. A null [onPressed] disables it.
  const PrimaryButton({required this.label, required this.onPressed, this.icon, super.key});

  /// Label, already localised.
  final String label;

  /// Called on tap; null disables the button.
  final VoidCallback? onPressed;

  /// Optional leading icon.
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    final tokens = BeneathTokens.of(context);
    final style = FilledButton.styleFrom(
      backgroundColor: tokens.accent,
      foregroundColor: tokens.onAccent,
      minimumSize: const Size.fromHeight(BeneathSizes.primaryButtonHeight),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(BeneathSizes.radius)),
      textStyle: Theme.of(context).textTheme.labelLarge,
    );
    final iconData = icon;
    return iconData == null
        ? FilledButton(onPressed: onPressed, style: style, child: Text(label))
        : FilledButton.icon(onPressed: onPressed, style: style, icon: Icon(iconData), label: Text(label));
  }
}
```

`lib/src/widgets/secondary_button.dart`:

```dart
import 'package:beneathsos_ui/src/tokens/sizes.dart';
import 'package:flutter/material.dart';

/// A secondary action: 56 tall, full width. Light: white fill, navy label and border;
/// dark: secondary-surface fill, light label, outline border.
class SecondaryButton extends StatelessWidget {
  /// Creates a secondary action. A null [onPressed] disables it.
  const SecondaryButton({required this.label, required this.onPressed, this.icon, super.key});

  /// Label, already localised.
  final String label;

  /// Called on tap; null disables the button.
  final VoidCallback? onPressed;

  /// Optional leading icon.
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final light = scheme.brightness == Brightness.light;
    final style = OutlinedButton.styleFrom(
      backgroundColor: scheme.surfaceContainer,
      foregroundColor: light ? scheme.primary : scheme.onSurface,
      side: BorderSide(color: light ? scheme.primary : scheme.outline, width: 1.5),
      minimumSize: const Size.fromHeight(BeneathSizes.minTouchTarget),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(BeneathSizes.radius)),
      textStyle: Theme.of(context).textTheme.labelLarge,
    );
    final iconData = icon;
    return iconData == null
        ? OutlinedButton(onPressed: onPressed, style: style, child: Text(label))
        : OutlinedButton.icon(onPressed: onPressed, style: style, icon: Icon(iconData), label: Text(label));
  }
}
```

Add both exports to `lib/beneathsos_ui.dart`.

- [ ] **Step 4: Run tests, then goldens (watch fail → create → inspect)**

Run: `fvm flutter test test/widgets/buttons_test.dart`
Expected: All tests passed (6).

Run: `fvm flutter test --tags golden`
Expected: FAIL for the two new button goldens (missing files); logo goldens pass.

Run: `fvm flutter test --tags golden --update-goldens` and open `test/widgets/goldens/buttons_light.png` and `buttons_dark.png`. Check: orange button with dark label and search icon, 64 tall; secondary white with navy border (light) / `#22324F` with light label (dark); Atkinson Bold labels.

Run: `fvm flutter test && fvm flutter analyze --fatal-infos && fvm dart format --set-exit-if-changed .`
Expected: All tests passed; No issues found.

- [ ] **Step 5: Commit (package)**

```bash
git add -A && git commit -m "feat(widgets): PrimaryButton and SecondaryButton with goldens"
```

---

### Task 7: Package CI for goldens on macOS

**Files:**
- Create: `HUB/packages/beneathsos_ui/.github/workflows/goldens.yml`

**Interfaces:** none (CI only). `ci.yml` comes from the hub template (Task 2) and skips goldens on Linux through `dart_test.yaml`.

- [ ] **Step 1: Write the workflow**

```yaml
name: goldens
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
concurrency:
  group: goldens-${{ github.ref }}
  cancel-in-progress: true
jobs:
  goldens:
    runs-on: macos-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with: { persist-credentials: false }
      - uses: kuhnroyal/flutter-fvm-config-action/setup@c378498f1d1962d33039c3989411093ef8a17b2c # v3.3
      - run: flutter pub get
      - run: flutter test --tags golden
```

- [ ] **Step 2: Verify locally**

Run: `ruby -ryaml -e 'YAML.load_file(".github/workflows/goldens.yml"); puts "ok"'` → `ok`.
Run: `fvm flutter test --tags golden` → All tests passed (6 goldens).
The workflows run on GitHub after the push in Task 12; check both runs there.

- [ ] **Step 3: Commit (package)**

```bash
git add -A && git commit -m "ci: run golden tests on macOS"
```

---

### Task 8: Hub wiring and documentation

**Files:**
- Modify: `HUB/tools/link_local.sh`
- Modify: `HUB/CLAUDE.md` (§2 layout tree and dependency table)
- Modify: `HUB/docs/architecture.md` (§2 repositories table + diagram, §6 routes, implementation status)
- Create: `HUB/docs/adr/0018-design-system-material-theme.md`; Modify: `HUB/docs/adr/README.md`
- Modify: `HUB/docs/roadmap.md` (split 1.2)

**Interfaces:**
- Produces: `tools/link_local.sh` writes `beneathsos_ui: path: ../../packages/beneathsos_ui` into the app's `pubspec_overrides.yaml`.

- [ ] **Step 1: Failing check** — the app override does not yet know the package:

Run: `HUB/tools/link_local.sh && grep -c beneathsos_ui HUB/apps/beneathsos_app/pubspec_overrides.yaml`
Expected: `0`

- [ ] **Step 2: Edit `tools/link_local.sh`** — the app line becomes:

```bash
    apps/beneathsos_app)     echo "ble_scanner beneathsos_ui rubble_core locator_engine rubble_canvas" ;;
```

Run: `HUB/tools/link_local.sh && grep -A1 beneathsos_ui HUB/apps/beneathsos_app/pubspec_overrides.yaml`
Expected: `beneathsos_ui:` followed by `path: ../../packages/beneathsos_ui`.

- [ ] **Step 3: `CLAUDE.md`** — in the §2 tree add under `packages/`:

```
   ├─ beneathsos_ui/                Berkant35/beneathsos_ui   Flutter — design tokens, theme, core components
```

and in the dependency table add:

```
| `beneathsos_ui` | Flutter | Riverpod, go_router, any other BeneathSOS package |
```

- [ ] **Step 4: ADR 0018** — `docs/adr/0018-design-system-material-theme.md`:

```markdown
# 0018. Design system: Material 3 theme with a brand extension, in its own package

- Status: Accepted
- Date: 2026-10-11

## Context

ADR 0017 fixed the visual identity. The app needs it in code — colours, the Atkinson typeface,
spacing, motion, logo and buttons — reusable by later packages (`rubble_canvas`) and visible on the
phone after every step.

## Decision

- A package `beneathsos_ui` (own repository) that depends on Flutter only.
- Material 3 `ThemeData` with a hand-written `ColorScheme` (exact brand colours, never `fromSeed`)
  plus `BeneathTokens extends ThemeExtension` for what Material has no slot for: accent, on-accent,
  numeric text, motion (`motionOf` honours "reduce motion").
- Material `secondary` and `tertiary` are navy: no built-in widget can paint orange text or icons on
  the light background. Orange is reachable only through `BeneathTokens.accent` and `PrimaryButton`.
- Atkinson Hyperlegible Next bundled as four static weights (400/600/700/800) generated by
  `tools/brand` — Flutter does not map `FontWeight` to a variable font's weight axis.
- The contrast table is repeated as a Dart test; golden tests run on macOS only.

## Alternatives

- **Fully custom design system** (no Material theme): total control, much more code, and built-in
  dialogs, sheets and pickers would not match the brand.
- **Tokens generated from one JSON for Python and Dart:** no drift between the two, but a code
  generation step; the Dart contrast test catches drift with less machinery.

## Consequences

- Built-in Material widgets follow the brand automatically; components stay thin wrappers.
- A colour change must keep both contrast tests (Python and Dart) green.
- Goldens differ between macOS and Linux text rendering, so Linux CI skips them (`dart_test.yaml`)
  and a macOS workflow runs them.
```

Add a row to `docs/adr/README.md`:

```
| [0018](0018-design-system-material-theme.md) | Design system: Material 3 theme with a brand extension, own package | Accepted |
```

- [ ] **Step 5: `docs/architecture.md`**
  - Implementation status row: `| Design system (\`beneathsos_ui\`) | ✅ 1.2a: tokens, theme, logo, buttons | \`beneathsos_ui\` v0.1.0 |`
  - §2 table: add `| [\`beneathsos_ui\`](https://github.com/Berkant35/beneathsos_ui) | Flutter | Design tokens, light/dark theme, Atkinson font, logo, core components | ✅ v0.1.0 |`; in the diagram add `beneathsos_ui (standalone)` next to `ble_scanner`.
  - §5.1 Home: replace the paragraph with: `Logo, one message, **"Start a search"** (primary) → rescuer flow, **"I am trapped"** (secondary) → victim mode, independence note and "Powered by Socrepho". *Today: both open "being prepared" screens (\`/sites/new\`, \`/victim\`).*`
  - §6 routes: `/` → `✅`; `/victim` → `✅ being prepared`; `/sites/new` → `✅ being prepared`.
  - §13 decisions range: `(0001–0018)`.

- [ ] **Step 6: `docs/roadmap.md`** — replace the 1.2 row with three rows:

```
| 1.2a | Design tokens, light/dark theme, Atkinson font, logo, primary and secondary buttons in `beneathsos_ui`; branded home screen with "Start a search" and "I am trapped" |
| 1.2b | Status banners and cards |
| 1.2c | Countdown ring; `AppScaffold` moves into `beneathsos_ui` |
```

- [ ] **Step 7: Commit (hub)**

```bash
cd HUB && git add tools/link_local.sh CLAUDE.md docs
git commit -m "docs: beneathsos_ui in the architecture, ADR 0018, roadmap 1.2a/b/c"
```

---

### Task 9: App uses the BeneathSOS theme

**Files:**
- Modify: `apps/beneathsos_app/pubspec.yaml`
- Delete: `lib/core/theme/app_theme.dart`
- Modify: `lib/app.dart`, `lib/core/widgets/app_scaffold.dart`, `lib/features/home/presentation/screens/home_screen.dart`
- Test: `test/app_test.dart`, `test/core/widgets/app_scaffold_test.dart`, `test/helpers/pump_app.dart`

**Interfaces:**
- Consumes: `BeneathTheme`, `BeneathTokens`, `BeneathSpacing`, `BeneathColors` (package).
- Produces: `AppScaffold({String? title, required Widget body, ...})` — no `AppBar` when `title` is null; test helpers `pumpLocalized(tester, home, {locale})`, `pumpRouterApp(tester, {locale, textScale, theme})`.

- [ ] **Step 1: Add the dependency**

In `pubspec.yaml` `dependencies:` (alphabetical, after `ble_scanner`):

```yaml
  beneathsos_ui:
    git:
      url: https://github.com/Berkant35/beneathsos_ui.git
      ref: v0.1.0
```

Run: `cd apps/beneathsos_app && HUB/tools/link_local.sh && fvm flutter pub get`
Expected: `Got dependencies!` (resolved from `../../packages/beneathsos_ui` through the override; the tag is published in Task 12).

- [ ] **Step 2: Write the failing tests**

`test/helpers/pump_app.dart`:

```dart
import 'package:beneathsos_app/core/router/app_router.dart';
import 'package:beneathsos_app/l10n/generated/app_localizations.dart';
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

/// Pumps [home] with the BeneathSOS light theme and localisations.
Future<void> pumpLocalized(WidgetTester tester, Widget home, {Locale locale = const Locale('en')}) async {
  await tester.pumpWidget(MaterialApp(
    locale: locale,
    theme: BeneathTheme.light(),
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    home: home,
  ));
  await tester.pumpAndSettle();
}

/// Pumps the real routes at `/` with a given locale, text scale and theme.
Future<void> pumpRouterApp(
  WidgetTester tester, {
  Locale locale = const Locale('en'),
  double textScale = 1,
  ThemeData? theme,
}) async {
  final router = GoRouter(routes: $appRoutes);
  addTearDown(router.dispose);
  await tester.pumpWidget(MaterialApp.router(
    locale: locale,
    theme: theme ?? BeneathTheme.light(),
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    routerConfig: router,
    builder: (context, child) => MediaQuery(
      data: MediaQuery.of(context).copyWith(textScaler: TextScaler.linear(textScale)),
      child: child!,
    ),
  ));
  await tester.pumpAndSettle();
}
```

`test/app_test.dart`:

```dart
import 'package:beneathsos_app/app.dart';
import 'package:beneathsos_app/features/home/presentation/screens/home_screen.dart';
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('the app uses the BeneathSOS theme', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: BeneathSosApp()));
    await tester.pumpAndSettle();
    final theme = Theme.of(tester.element(find.byType(HomeScreen)));
    expect(theme.colorScheme.primary, BeneathColors.primaryLight);
    expect(theme.extension<BeneathTokens>(), isNotNull);
  });
}
```

`test/core/widgets/app_scaffold_test.dart`:

```dart
import 'package:beneathsos_app/core/widgets/app_scaffold.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../helpers/pump_app.dart';

void main() {
  testWidgets('without a title there is no app bar', (tester) async {
    await pumpLocalized(tester, const AppScaffold(body: Text('body')));
    expect(find.byType(AppBar), findsNothing);
    expect(find.text('body'), findsOneWidget);
  });

  testWidgets('with a title the app bar shows it', (tester) async {
    await pumpLocalized(tester, const AppScaffold(title: 'Title', body: Text('body')));
    expect(find.widgetWithText(AppBar, 'Title'), findsOneWidget);
  });
}
```

- [ ] **Step 3: Run them to verify they fail**

Run: `fvm flutter test test/app_test.dart test/core/widgets`
Expected: FAIL — primary is the seed colour, not `#1B2A4E`; `AppScaffold` requires `title`.

- [ ] **Step 4: Implement**

Delete `lib/core/theme/app_theme.dart`.

`lib/app.dart` — imports and theme lines:

```dart
import 'package:beneathsos_app/core/router/app_router.dart';
import 'package:beneathsos_app/l10n/generated/app_localizations.dart';
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
...
    theme: BeneathTheme.light(),
    darkTheme: BeneathTheme.dark(),
```

`lib/core/widgets/app_scaffold.dart`:

```dart
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';

/// Standard screen frame: optional app bar from [title], safe area, page padding, max width on
/// tablets. Use a raw `Scaffold` only for full-bleed screens and say why.
class AppScaffold extends StatelessWidget {
  /// Creates a screen frame; without [title] there is no app bar (e.g. the home screen).
  const AppScaffold({
    required this.body,
    this.title,
    this.actions = const [],
    this.bottom,
    this.padded = true,
    super.key,
  });

  /// App bar title; null hides the app bar.
  final String? title;

  /// Screen content.
  final Widget body;

  /// App bar actions.
  final List<Widget> actions;

  /// Optional app bar bottom (e.g. a TabBar).
  final PreferredSizeWidget? bottom;

  /// Whether page padding is applied.
  final bool padded;

  static const double _maxWidth = 720;

  @override
  Widget build(BuildContext context) {
    final title = this.title;
    return Scaffold(
      appBar: title == null ? null : AppBar(title: Text(title), actions: actions, bottom: bottom),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: _maxWidth),
            child: padded
                ? Padding(padding: BeneathSpacing.pageFor(MediaQuery.sizeOf(context).width), child: body)
                : body,
          ),
        ),
      ),
    );
  }
}
```

`lib/features/home/presentation/screens/home_screen.dart`: replace `import 'package:beneathsos_app/core/theme/app_theme.dart';` with `import 'package:beneathsos_ui/beneathsos_ui.dart';`, `AppSpacing.s` with `BeneathSpacing.s`, and `title: l10n.appTitle` stays (the screen is rewritten in Task 11).

- [ ] **Step 5: Run everything**

Run: `fvm flutter test && fvm flutter analyze --fatal-infos && fvm dart format --set-exit-if-changed .`
Expected: All tests passed (52 existing + 3 new); No issues found.

- [ ] **Step 6: Commit (app)**

```bash
git add -A && git commit -m "feat(theme): use the beneathsos_ui theme; AppScaffold without title"
```

---

### Task 10: "Being prepared" screens, routes and strings

**Files:**
- Modify: `lib/l10n/app_en.arb`, `lib/l10n/app_tr.arb`
- Modify: `lib/core/router/app_router.dart` (+ regenerate `app_router.g.dart`)
- Create: `lib/features/sites/presentation/screens/new_site_screen.dart`, `lib/features/victim/presentation/screens/victim_screen.dart`
- Test: `test/features/sites/new_site_screen_test.dart`, `test/features/victim/victim_screen_test.dart`

**Interfaces:**
- Consumes: `AppScaffold` (Task 9), `pumpLocalized` (Task 9).
- Produces: `NewSiteRoute` (`/sites/new`), `VictimRoute` (`/victim`) as children of `HomeRoute`; `NewSiteScreen`, `VictimScreen`; ARB keys `homeHeadline, homeBody, homeStartSearch, homeTrapped, homeIndependence, poweredBy, newSiteTitle, newSitePreparing, victimTitle, victimPreparing, logoLabel`.

- [ ] **Step 1: Strings** — add to `app_en.arb` (keep existing keys for now):

```json
  "logoLabel": "BeneathSOS",
  "homeHeadline": "Search for a phone under rubble",
  "homeBody": "Measure the phone's Bluetooth signal at a few points; the app shows the most likely area.",
  "homeStartSearch": "Start a search",
  "homeTrapped": "I am trapped",
  "homeIndependence": "BeneathSOS is an independent open-source project and is not affiliated with AFAD or any government agency.",
  "poweredBy": "Powered by Socrepho",
  "newSiteTitle": "New search",
  "newSitePreparing": "This step is being prepared. Here you will draw the outline of the rubble site.",
  "victimTitle": "I am trapped",
  "victimPreparing": "This mode is not ready yet. In an emergency, call 112."
```

and to `app_tr.arb`:

```json
  "logoLabel": "BeneathSOS",
  "homeHeadline": "Enkaz altındaki bir telefonu arayın",
  "homeBody": "Telefonun Bluetooth sinyalini birkaç noktadan ölçün; uygulama en olası bölgeyi gösterir.",
  "homeStartSearch": "Aramayı başlat",
  "homeTrapped": "Enkaz altındayım",
  "homeIndependence": "BeneathSOS bağımsız bir açık kaynak projedir; AFAD veya herhangi bir kamu kurumuyla bağlantısı yoktur.",
  "poweredBy": "Powered by Socrepho",
  "newSiteTitle": "Yeni arama",
  "newSitePreparing": "Bu adım hazırlanıyor. Burada enkaz alanının sınırlarını çizeceksiniz.",
  "victimTitle": "Enkaz altındayım",
  "victimPreparing": "Bu mod henüz hazır değil. Acil durumda 112'yi arayın."
```

Run: `fvm flutter gen-l10n` → no output errors.

- [ ] **Step 2: Write the failing tests**

`test/features/sites/new_site_screen_test.dart`:

```dart
import 'package:beneathsos_app/features/sites/presentation/screens/new_site_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../helpers/pump_app.dart';

void main() {
  testWidgets('English: title and what comes next', (tester) async {
    await pumpLocalized(tester, const NewSiteScreen());
    expect(find.text('New search'), findsOneWidget);
    expect(find.textContaining('draw the outline of the rubble site'), findsOneWidget);
  });

  testWidgets('Turkish', (tester) async {
    await pumpLocalized(tester, const NewSiteScreen(), locale: const Locale('tr'));
    expect(find.text('Yeni arama'), findsOneWidget);
    expect(find.textContaining('enkaz alanının sınırlarını'), findsOneWidget);
  });
}
```

`test/features/victim/victim_screen_test.dart`:

```dart
import 'package:beneathsos_app/features/victim/presentation/screens/victim_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../helpers/pump_app.dart';

void main() {
  testWidgets('English: never an empty screen — tells the user to call 112', (tester) async {
    await pumpLocalized(tester, const VictimScreen());
    expect(find.text('I am trapped'), findsOneWidget);
    expect(find.textContaining('call 112'), findsOneWidget);
  });

  testWidgets('Turkish', (tester) async {
    await pumpLocalized(tester, const VictimScreen(), locale: const Locale('tr'));
    expect(find.text('Enkaz altındayım'), findsOneWidget);
    expect(find.textContaining("112'yi arayın"), findsOneWidget);
  });
}
```

- [ ] **Step 3: Run them to verify they fail**

Run: `fvm flutter test test/features/sites test/features/victim`
Expected: FAIL — screens not found.

- [ ] **Step 4: Implement**

`lib/features/sites/presentation/screens/new_site_screen.dart`:

```dart
import 'package:beneathsos_app/core/l10n_extension.dart';
import 'package:beneathsos_app/core/widgets/app_scaffold.dart';
import 'package:flutter/material.dart';

/// Start of the rescuer flow. "Being prepared" until roadmap phase 4 replaces it on the same route.
class NewSiteScreen extends StatelessWidget {
  /// Creates the screen.
  const NewSiteScreen({super.key});

  @override
  Widget build(BuildContext context) => AppScaffold(
    title: context.l10n.newSiteTitle,
    body: Text(context.l10n.newSitePreparing, style: Theme.of(context).textTheme.bodyLarge),
  );
}
```

`lib/features/victim/presentation/screens/victim_screen.dart`:

```dart
import 'package:beneathsos_app/core/l10n_extension.dart';
import 'package:beneathsos_app/core/widgets/app_scaffold.dart';
import 'package:flutter/material.dart';

/// Victim mode. Until phase 10 it only tells a trapped person to call 112 — never an empty screen.
class VictimScreen extends StatelessWidget {
  /// Creates the screen.
  const VictimScreen({super.key});

  @override
  Widget build(BuildContext context) => AppScaffold(
    title: context.l10n.victimTitle,
    body: Text(context.l10n.victimPreparing, style: Theme.of(context).textTheme.headlineSmall),
  );
}
```

`lib/core/router/app_router.dart`:

```dart
import 'package:beneathsos_app/features/home/presentation/screens/home_screen.dart';
import 'package:beneathsos_app/features/sites/presentation/screens/new_site_screen.dart';
import 'package:beneathsos_app/features/victim/presentation/screens/victim_screen.dart';
import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'app_router.g.dart';

/// Home. Its actions `go` to child routes, so Back returns here and a double tap opens one screen.
@TypedGoRoute<HomeRoute>(
  path: '/',
  routes: [
    TypedGoRoute<NewSiteRoute>(path: 'sites/new'),
    TypedGoRoute<VictimRoute>(path: 'victim'),
  ],
)
class HomeRoute extends GoRouteData with $HomeRoute {
  /// Route to the home screen.
  const HomeRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) => const HomeScreen();
}

/// Rescuer flow start (`/sites/new`) — "being prepared" until roadmap phase 4.
class NewSiteRoute extends GoRouteData with $NewSiteRoute {
  /// Route to the new-site screen.
  const NewSiteRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) => const NewSiteScreen();
}

/// Victim mode (`/victim`) — "being prepared" until roadmap phase 10.
class VictimRoute extends GoRouteData with $VictimRoute {
  /// Route to the victim screen.
  const VictimRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) => const VictimScreen();
}

/// The app router. Only this file knows paths.
@Riverpod(keepAlive: true)
GoRouter appRouter(Ref ref) => GoRouter(routes: $appRoutes);
```

Run: `fvm dart run build_runner build`
Expected: `app_router.g.dart` regenerated with `$NewSiteRoute`, `$VictimRoute`.

- [ ] **Step 5: Run everything**

Run: `fvm flutter test && fvm flutter analyze --fatal-infos && fvm dart format --set-exit-if-changed .`
Expected: All tests passed; No issues found.

- [ ] **Step 6: Commit (app)**

```bash
git add -A && git commit -m "feat(home): routes and being-prepared screens for search and victim mode"
```

---

### Task 11: Branded home screen

**Files:**
- Modify: `lib/features/home/presentation/screens/home_screen.dart`
- Create: `lib/features/home/presentation/widgets/home_actions.dart`, `lib/features/home/presentation/widgets/home_footer.dart`
- Modify: `lib/l10n/app_en.arb`, `lib/l10n/app_tr.arb` (remove `homeUnderConstructionTitle`, `homeUnderConstructionBody`)
- Modify: `CHANGELOG.md` (Unreleased)
- Test: `test/features/home/home_screen_test.dart`

**Interfaces:**
- Consumes: `BeneathLogo.lockup`, `PrimaryButton`, `SecondaryButton`, `BeneathSpacing`, `NewSiteRoute`, `VictimRoute`, ARB keys (Task 10), `pumpRouterApp` (Task 9).
- Produces: `HomeScreen`, `HomeActions`, `HomeFooter`.

- [ ] **Step 1: Write the failing tests** — `test/features/home/home_screen_test.dart`

```dart
import 'package:beneathsos_app/features/home/presentation/screens/home_screen.dart';
import 'package:beneathsos_app/features/sites/presentation/screens/new_site_screen.dart';
import 'package:beneathsos_app/features/victim/presentation/screens/victim_screen.dart';
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../helpers/pump_app.dart';

void _smallPhone(WidgetTester tester) {
  tester.view
    ..physicalSize = const Size(750, 1334) // 375 × 667 at 2×
    ..devicePixelRatio = 2;
  addTearDown(tester.view.reset);
}

Future<void> _expectReachable(WidgetTester tester, String label) async {
  await tester.dragUntilVisible(find.text(label), find.byType(SingleChildScrollView), const Offset(0, -200));
  expect(find.text(label).hitTestable(), findsOneWidget);
}

void main() {
  testWidgets('English: logo, message, both actions and the fine print', (tester) async {
    await pumpRouterApp(tester);
    expect(find.bySemanticsLabel('BeneathSOS'), findsOneWidget);
    expect(find.text('Search for a phone under rubble'), findsOneWidget);
    expect(find.text('Start a search'), findsOneWidget);
    expect(find.text('I am trapped'), findsOneWidget);
    expect(find.textContaining('not affiliated with AFAD'), findsOneWidget);
    expect(find.text('Powered by Socrepho'), findsOneWidget);
  });

  testWidgets('Turkish', (tester) async {
    await pumpRouterApp(tester, locale: const Locale('tr'));
    expect(find.text('Enkaz altındaki bir telefonu arayın'), findsOneWidget);
    expect(find.text('Aramayı başlat'), findsOneWidget);
    expect(find.text('Enkaz altındayım'), findsOneWidget);
    expect(find.textContaining('AFAD veya herhangi bir kamu kurumuyla'), findsOneWidget);
    expect(find.text('Powered by Socrepho'), findsOneWidget);
  });

  testWidgets('Start a search opens the new-site screen; Back returns home', (tester) async {
    await pumpRouterApp(tester);
    await tester.tap(find.text('Start a search'));
    await tester.pumpAndSettle();
    expect(find.byType(NewSiteScreen), findsOneWidget);
    await tester.pageBack();
    await tester.pumpAndSettle();
    expect(find.byType(HomeScreen), findsOneWidget);
  });

  testWidgets('I am trapped opens the victim screen with the 112 note', (tester) async {
    await pumpRouterApp(tester);
    await tester.tap(find.text('I am trapped'));
    await tester.pumpAndSettle();
    expect(find.byType(VictimScreen), findsOneWidget);
    expect(find.textContaining('call 112'), findsOneWidget);
  });

  testWidgets('a gloved double tap opens one screen and Back still returns home', (tester) async {
    await pumpRouterApp(tester);
    await tester.tap(find.text('Start a search'));
    await tester.tap(find.text('Start a search'), warnIfMissed: false);
    await tester.pumpAndSettle();
    await tester.pageBack();
    await tester.pumpAndSettle();
    expect(find.byType(HomeScreen), findsOneWidget);
  });

  testWidgets('200 % text on a small phone: no overflow, both actions reachable', (tester) async {
    _smallPhone(tester);
    await pumpRouterApp(tester, textScale: 2);
    expect(tester.takeException(), isNull);
    await _expectReachable(tester, 'Start a search');
    await _expectReachable(tester, 'I am trapped');
  });

  testWidgets('Turkish at 200 % on a small phone: labels wrap, nothing clips', (tester) async {
    _smallPhone(tester);
    await pumpRouterApp(tester, locale: const Locale('tr'), textScale: 2);
    expect(tester.takeException(), isNull);
    await _expectReachable(tester, 'Aramayı başlat');
    await _expectReachable(tester, 'Enkaz altındayım');
  });

  testWidgets('dark mode draws the logo in dark-theme colours', (tester) async {
    await pumpRouterApp(tester, theme: BeneathTheme.dark());
    final painter = tester
        .widgetList<CustomPaint>(find.descendant(of: find.byType(BeneathLogo), matching: find.byType(CustomPaint)))
        .map((paint) => paint.painter)
        .whereType<SignalExitPainter>()
        .single;
    expect((painter.line, painter.accent), (BeneathColors.primaryDark, BeneathColors.accentDark));
  });

  testWidgets('screen readers hear both actions as buttons', (tester) async {
    final handle = tester.ensureSemantics();
    await pumpRouterApp(tester);
    for (final label in ['Start a search', 'I am trapped']) {
      expect(tester.getSemantics(find.bySemanticsLabel(label)), containsSemantics(label: label, isButton: true));
    }
    handle.dispose();
  });
}
```

- [ ] **Step 2: Run them to verify they fail**

Run: `fvm flutter test test/features/home`
Expected: FAIL — the old placeholder shows "Under construction"; no buttons.

- [ ] **Step 3: Implement**

`lib/features/home/presentation/widgets/home_actions.dart`:

```dart
import 'package:beneathsos_app/core/l10n_extension.dart';
import 'package:beneathsos_app/core/router/app_router.dart';
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';

/// The home screen's two actions, in the thumb zone. `go` (not `push`) makes a double tap harmless.
class HomeActions extends StatelessWidget {
  /// Creates the actions.
  const HomeActions({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        PrimaryButton(
          label: l10n.homeStartSearch,
          icon: Icons.search_rounded,
          onPressed: () => const NewSiteRoute().go(context),
        ),
        const SizedBox(height: BeneathSpacing.m),
        SecondaryButton(label: l10n.homeTrapped, onPressed: () => const VictimRoute().go(context)),
      ],
    );
  }
}
```

`lib/features/home/presentation/widgets/home_footer.dart`:

```dart
import 'package:beneathsos_app/core/l10n_extension.dart';
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';

/// Fine print: the independence statement and "Powered by Socrepho".
class HomeFooter extends StatelessWidget {
  /// Creates the footer.
  const HomeFooter({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final theme = Theme.of(context);
    final style = theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.onSurfaceVariant);
    return Column(
      children: [
        Text(l10n.homeIndependence, style: style, textAlign: TextAlign.center),
        const SizedBox(height: BeneathSpacing.s),
        Text(l10n.poweredBy, style: style, textAlign: TextAlign.center),
      ],
    );
  }
}
```

`lib/features/home/presentation/screens/home_screen.dart`:

```dart
import 'package:beneathsos_app/core/l10n_extension.dart';
import 'package:beneathsos_app/core/widgets/app_scaffold.dart';
import 'package:beneathsos_app/features/home/presentation/widgets/home_actions.dart';
import 'package:beneathsos_app/features/home/presentation/widgets/home_footer.dart';
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';

/// Entry point: logo, one message, "Start a search" and "I am trapped". Scrolls at large text.
class HomeScreen extends StatelessWidget {
  /// Creates the home screen.
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final text = Theme.of(context).textTheme;
    return AppScaffold(
      body: LayoutBuilder(
        builder: (context, constraints) => SingleChildScrollView(
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: IntrinsicHeight(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: BeneathSpacing.l),
                  Center(child: BeneathLogo.lockup(semanticLabel: l10n.logoLabel)),
                  const Spacer(),
                  Text(l10n.homeHeadline, style: text.displaySmall, textAlign: TextAlign.center),
                  const SizedBox(height: BeneathSpacing.m),
                  Text(l10n.homeBody, style: text.bodyLarge, textAlign: TextAlign.center),
                  const Spacer(),
                  const SizedBox(height: BeneathSpacing.xl),
                  const HomeActions(),
                  const SizedBox(height: BeneathSpacing.l),
                  const HomeFooter(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
```

Remove `homeUnderConstructionTitle` and `homeUnderConstructionBody` from both ARB files; run `fvm flutter gen-l10n`.

`CHANGELOG.md` under `## [Unreleased]` → `### Added`, add:

```markdown
- Branded home screen: logo, "Start a search" and "I am trapped" (both open "being prepared"
  screens; the victim screen says to call 112), independence note, "Powered by Socrepho".
- BeneathSOS theme from `beneathsos_ui` (light and dark, Atkinson Hyperlegible Next).
```

- [ ] **Step 4: Run everything**

Run: `fvm flutter test && fvm flutter analyze --fatal-infos && fvm dart format --set-exit-if-changed .`
Expected: All tests passed; No issues found. If the 200 % tests report an overflow, fix the layout (never the test).

- [ ] **Step 5: Commit (app)**

```bash
git add -A && git commit -m "feat(home): branded home screen with search and trapped actions"
```

---

### Task 12: Verification, publish and TestFlight

**Files:** `HUB/docs/roadmap.md`, `HUB/tasks/todo.md` (status); no code.

- [ ] **Step 1: All checks, every touched repo**

```bash
for r in packages/beneathsos_ui apps/beneathsos_app; do (cd HUB/$r && fvm dart format --set-exit-if-changed . && fvm flutter analyze --fatal-infos && fvm flutter test) || echo "FAIL $r"; done
cd HUB/tools/brand && .venv/bin/python -m unittest discover -s tests
```

Expected: no `FAIL`; brand tests OK.

- [ ] **Step 2: iOS simulator screenshots** (UDID `72AE56FC-52D0-4CE2-8811-B113CE30EA21`)

```bash
cd HUB/apps/beneathsos_app && fvm flutter build ios --simulator --debug
xcrun simctl install 72AE56FC-52D0-4CE2-8811-B113CE30EA21 build/ios/iphonesimulator/Runner.app
```

For `light` and `dark` (`xcrun simctl ui <UDID> appearance <mode>`): launch, screenshot home; tap "Start a search", screenshot; Back; tap "I am trapped", screenshot. Save in the scratchpad and send all six to the maintainer. Check: navy/orange, Atkinson, logo, buttons in the bottom half, footer readable.

- [ ] **Step 3: Android** — `fvm flutter build apk --debug > log 2>&1; echo exit=$?` → `exit=0`, `✓ Built`.

- [ ] **Step 4: STOP — ask the maintainer** to approve creating the public repository `Berkant35/beneathsos_ui`. Continue only after a clear yes.

- [ ] **Step 5: Publish the package**

```bash
cd HUB/packages/beneathsos_ui
gh repo create Berkant35/beneathsos_ui --public --description "BeneathSOS design system: brand tokens, light/dark theme, logo and core components" --source . --push
for f in .github/rulesets/*.json; do gh api -X POST repos/Berkant35/beneathsos_ui/rulesets --input "$f" > /dev/null; done
gh api -X PUT repos/Berkant35/beneathsos_ui/private-vulnerability-reporting
git tag -a v0.1.0 -m "beneathsos_ui 0.1.0" && git push origin v0.1.0
gh release create v0.1.0 --title "beneathsos_ui 0.1.0" --notes-file CHANGELOG.md
```

Check `ci` and `goldens` workflow runs on GitHub (`gh run list --repo Berkant35/beneathsos_ui --limit 4`) are green. If Linux CI fails on goldens, the `dart_test.yaml` skip did not apply — fix there and push.

- [ ] **Step 6: Prove the app resolves from the tag** (fresh clone, no overrides)

```bash
rm -rf SCRATCH/app-clone && git clone -q HUB/apps/beneathsos_app SCRATCH/app-clone
cd SCRATCH/app-clone && fvm flutter pub get
```

Expected: `Got dependencies!` with `beneathsos_ui` from `github.com/Berkant35/beneathsos_ui.git` at `v0.1.0`.

- [ ] **Step 7: Push app and hub; TestFlight**

```bash
cd HUB/apps/beneathsos_app && git push
ASC_KEY_ID=$ASC_KEY_ID ASC_ISSUER_ID=$ASC_ISSUER_ID tools/testflight.sh
```

Poll App Store Connect until the build is `VALID` and `IN_BETA_TESTING`; report the build number.

- [ ] **Step 8: Close the step (hub)** — `docs/roadmap.md`: `1.2a ✅`; `tasks/todo.md`: a "Done: Phase 1.2a" section with files, test counts and the build number, and the line "On the phone: …"; comment on issue #7 linking the commits (keep it open for 1.2b/c). Commit and push the hub.
