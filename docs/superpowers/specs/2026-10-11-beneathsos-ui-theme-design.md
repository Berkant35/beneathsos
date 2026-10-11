# Roadmap 1.2a — `beneathsos_ui`: tokens, theme, logo, buttons and a branded home screen

- Date: 2026-10-11
- Status: approved in conversation, section by section (2026-10-11)
- Roadmap: phase 1, step 1.2 split into 1.2a (this spec), 1.2b (status banner, card), 1.2c
  (countdown ring, `AppScaffold` moved into the package)
- Builds on: [1.1 spec](2026-10-11-brand-and-design-principles-design.md),
  [`docs/design/`](../../design/principles.md), [`docs/brand/`](../../brand/README.md),
  [ADR 0017](../../adr/0017-visual-identity.md)

## 1. Purpose and success

> A very usable, readable interface for people at a collapsed building in an emergency.

1.1 defined the brand in documents and assets; the app's screens did not change, and the maintainer
saw "nothing done" on the phone. 1.2a puts the brand into code **and** makes it visible:

- A new package `beneathsos_ui` (own public repository `Berkant35/beneathsos_ui`) holds the design
  tokens, the light and dark theme, the bundled Atkinson font, the logo and the two button types.
- The app uses it, and its home screen becomes the real entry point: logo, one message, the primary
  action **"Start a search"**, the secondary action **"I am trapped"**, the independence statement
  and "Powered by Socrepho".

**Success = on the phone (TestFlight)** the home screen shows the logo, navy/orange colours and the
Atkinson typeface in both light and dark mode; both buttons open their "being prepared" screens.

Not in 1.2a: the real search flow (phase 4), status banners and cards (1.2b), the countdown ring
and moving `AppScaffold` (1.2c), Material Symbols (1.2b decides), Widgetbook (1.3).

## 2. Approach (decided)

**Material 3 theme + a brand `ThemeExtension`.** The `ColorScheme` is written by hand with the exact
brand colours (never `fromSeed`); tokens Material has no slot for (accent, spacing, motion, sizes,
numeric text) live in `BeneathTokens extends ThemeExtension`. Components wrap Material widgets, so
Flutter's built-in parts (dialogs, sheets, pickers, keyboard) follow the brand automatically.

Rejected: a fully custom design system (much more work; built-in widgets would not match); tokens
generated from one JSON for Python and Dart (adds a code-generation step — the same protection comes
from repeating the contrast table as a Dart test).

## 3. Package, repository and wiring

```
packages/beneathsos_ui/                 Berkant35/beneathsos_ui (public, Apache-2.0, tag v0.1.0)
  lib/beneathsos_ui.dart                single export
  lib/src/tokens/  colors.dart, typography.dart, spacing.dart, motion.dart, sizes.dart
  lib/src/theme/   beneath_theme.dart (BeneathTheme.light/dark), beneath_tokens.dart (ThemeExtension)
  lib/src/widgets/ beneath_logo.dart, signal_exit_painter.dart, primary_button.dart,
                   secondary_button.dart
  fonts/           AtkinsonHyperlegibleNext-{Regular,SemiBold,Bold,ExtraBold}.ttf + OFL.txt
  test/            contrast, theme, motion, widget and golden tests
```

- Governance files from the hub (`tools/sync_governance.sh`): licence, CONTRIBUTING, SECURITY, CODE
  OF CONDUCT, rulesets, PR template, shared CI. Package README and CHANGELOG.
- **Dependency rule** (added to `CLAUDE.md` §2 and `tools/check_deps` later):

  | Package | May depend on | Must NOT depend on |
  |---|---|---|
  | `beneathsos_ui` | Flutter | Riverpod, go_router, `ble_scanner`, `rubble_core`, `locator_engine`, `rubble_canvas` |

- **App:** git dependency `beneathsos_ui` (`ref: v0.1.0`); `tools/link_local.sh` links it locally.
  `lib/core/theme/app_theme.dart` is deleted; `app.dart` uses `BeneathTheme.light()/dark()` and
  follows the system setting; `AppSpacing` users move to the package tokens. `AppScaffold` stays in
  the app (moves in 1.2c) and gains a no-title variant for the home screen.
- **Font:** the hub's brand tool generates four static instances (400, 600, 700, 800) from the
  variable font — Flutter does not map `FontWeight` to a variable font's weight axis — and copies them
  with `OFL.txt` into the package. The font is declared in the package's `pubspec.yaml`, so every app
  using the package gets it.
- **Docs:** ADR 0018 (this approach), `docs/architecture.md` (design-system row, dependency rule),
  roadmap (1.2 split into 1.2a/b/c).

## 4. Tokens and theme

### Colours

Values are the 1.1 palette; every pair below is pinned by a Dart test.

| Role | Light | Dark | Use |
|---|---|---|---|
| `primary` / `onPrimary` | `#1B2A4E` / `#FFFFFF` | `#9DB2E0` / `#0C111D` | Titles, secondary buttons, navigation |
| `secondary`, `tertiary` (+ `on…`) | = primary | = primary | Never orange (see below) |
| `surface` / `onSurface` | `#F5F6F9` / `#121A2B` | `#0C111D` / `#E8ECF5` | Background and text |
| `surfaceContainer` | `#FFFFFF` | `#22324F` | Cards, secondary button fill |
| `error` / `onError` | `#B3261E` / `#FFFFFF` | `#FFB4AB` / `#690005` | Blocked states |
| `outline` | `#6B7590` | `#8C9AB8` | Borders (≥ 3:1 on surfaces) |
| `accent` / `onAccent` (extension) | `#FF7900` / `#1A0D00` | `#FF8C2E` / `#1A0D00` | Primary button fill, attention fills |

**Material's `secondary` and `tertiary` are navy, not orange**, so no built-in widget can paint
orange text or icons on the light background (2.4 — forbidden by `docs/design/accessibility.md`).
Orange is reachable only through `BeneathTokens.accent` and `PrimaryButton`.

Pinned contrast pairs (WCAG ratio, rounded to 1 decimal):

| Pair | Ratio | Rule |
|---|---|---|
| `#FFFFFF` on `#1B2A4E` | 14.1 | text ≥ 4.5 |
| `#121A2B` on `#F5F6F9` | 16.1 | text ≥ 4.5 |
| `#1A0D00` on `#FF7900` | 7.3 | text ≥ 4.5 |
| `#1A0D00` on `#FF8C2E` | 8.2 | text ≥ 4.5 |
| `#FFFFFF` on `#B3261E` | 6.5 | text ≥ 4.5 |
| `#690005` on `#FFB4AB` | 7.7 | text ≥ 4.5 |
| `#0C111D` on `#9DB2E0` | 8.9 | text ≥ 4.5 |
| `#9DB2E0` on `#0C111D` | 8.9 | text ≥ 4.5 |
| `#E8ECF5` on `#0C111D` | 15.9 | text ≥ 4.5 |
| `#E8ECF5` on `#22324F` | 10.8 | text ≥ 4.5 |
| `#FF8C2E` on `#0C111D` | 8.1 | icons/text, dark theme |
| `#6B7590` on `#F5F6F9` / `#FFFFFF` | 4.3 / 4.6 | outline ≥ 3 |
| `#8C9AB8` on `#0C111D` / `#22324F` | 6.7 / 4.5 | outline ≥ 3 |
| `#FF7900` on `#F5F6F9` | 2.4 | **must stay < 3** (forbidden for text and icons) |

### Typography

Atkinson Hyperlegible Next for every role; sizes are logical pixels and scale with the system text
size.

| Role (Material slot) | Size / line height | Weight | Use |
|---|---|---|---|
| Hero (`displaySmall`) | 32 / 40 | 800 | A screen's main message |
| Title (`headlineSmall`) | 24 / 32 | 700 | Screen title |
| Subtitle (`titleLarge`) | 20 / 28 | 700 | Card title |
| Body (`bodyLarge`, `bodyMedium`) | 19 / 28, 17 / 24 | 400 | Text — never below 17 |
| Button (`labelLarge`) | 19 / 24 | 700 | Buttons |
| Fine print (`bodySmall`) | 15 / 20 | 400 | Legal note and "Powered by" only |
| Numeric (`BeneathTokens.numeric`) | 28 / 32 | 800, tabular figures | dBm, countdowns, metres |

### Spacing, sizes, motion

- Spacing: 4, 8, 12, 16, 24, 32, 48. Page padding 16 on phones, 24 from 600 px width.
- Minimum touch target 56; primary button height 64; corner radius 16 (buttons, cards), 8 (small).
- Motion: 150, 250, 400 ms with an ease-out curve. `BeneathTokens.motionOf(context)` returns zero
  durations when the system "reduce motion" setting (`MediaQuery.disableAnimations`) is on; every
  widget uses it.
- The theme sets button, app bar and card defaults from these tokens (e.g. every button ≥ 56 tall).

## 5. Components (package)

- **`BeneathLogo.symbol({double size})`** — the "signal exit" symbol drawn by `SignalExitPainter`
  from the 1.1 geometry (48-unit grid, stroke 3.6, line `M6 30 H42`, dot (24, 38) r 3.4, three arcs
  with opacity 1 / 0.75 / 0.5); line in `primary`, dot and arcs in `accent`.
- **`BeneathLogo.lockup({double height})`** — symbol + "Beneath" (primary) + "SOS" (accent), weight
  800. Screen readers read "BeneathSOS". Orange "SOS" on the light background is allowed: WCAG
  exempts logotypes and brand names from contrast minimums; the rule applies to text and icons.
- **`PrimaryButton({label, onPressed, icon})`** — accent fill, `onAccent` label, 64 tall, full
  width, radius 16. Documented rule: at most one per screen, in the bottom half.
- **`SecondaryButton({label, onPressed, icon})`** — 56 tall, full width; light: white fill, navy
  label and outline; dark: `#22324F` fill, `#E8ECF5` label.

## 6. Screens (app)

### Home (`HomeRoute`, `/`)

Top to bottom: logo lockup; hero message; short explanation; in the thumb zone **PrimaryButton
"Start a search"** (search icon) and below it **SecondaryButton "I am trapped"**; at the bottom in
fine print the independence statement and "Powered by Socrepho". No app bar (`AppScaffold` without
title). At 200 % system text size the page scrolls and nothing is clipped.

### Being prepared

- "Start a search" → `NewSearchRoute` (`/search/new`, feature `features/search/`): title "New
  search"; text "This step is being prepared. Here you will draw the outline of the rubble site."
- "I am trapped" → `TrappedRoute` (`/trapped`, feature `features/trapped/`): text "This mode is not
  ready yet. In an emergency, call 112." — a trapped person who taps it must get the one useful
  instruction, never an empty screen (the app supports, never replaces, professional rescue).

Typed `go_router` routes in `core/router/`; the real phase-4 flows replace these screens on the same
routes.

### Strings (ARB, English and Turkish in the same change)

| Key | English | Türkçe |
|---|---|---|
| `homeHeadline` | Search for a phone under rubble | Enkaz altındaki bir telefonu arayın |
| `homeBody` | Measure the phone's Bluetooth signal at a few points; the app shows the most likely area. | Telefonun Bluetooth sinyalini birkaç noktadan ölçün; uygulama en olası bölgeyi gösterir. |
| `homeStartSearch` | Start a search | Aramayı başlat |
| `homeTrapped` | I am trapped | Enkaz altındayım |
| `homeIndependence` | BeneathSOS is an independent open-source project and is not affiliated with AFAD or any government agency. | BeneathSOS bağımsız bir açık kaynak projedir; AFAD veya herhangi bir kamu kurumuyla bağlantısı yoktur. |
| `poweredBy` | Powered by Socrepho | Powered by Socrepho |
| `newSearchTitle` | New search | Yeni arama |
| `newSearchPreparing` | This step is being prepared. Here you will draw the outline of the rubble site. | Bu adım hazırlanıyor. Burada enkaz alanının sınırlarını çizeceksiniz. |
| `trappedTitle` | I am trapped | Enkaz altındayım |
| `trappedPreparing` | This mode is not ready yet. In an emergency, call 112. | Bu mod henüz hazır değil. Acil durumda 112'yi arayın. |
| `logoLabel` | BeneathSOS | BeneathSOS |

The old keys `homeUnderConstructionTitle` and `homeUnderConstructionBody` are removed. "Socrepho"
is a name and is not translated.

## 7. Testing and verification

**Package**

- Contrast: every pair in §4 (same values as `tools/brand/tests/test_contrast.py`).
- Theme: colours equal the table; `secondary`/`tertiary` are not the accent; body text ≥ 17; button
  minimum height ≥ 56; light and dark both built.
- Motion: with `disableAnimations` every duration is zero.
- Widgets: `PrimaryButton` is 64 tall with the `onAccent` label colour and a semantics label;
  `SecondaryButton` is 56 tall; the logo's semantics label is "BeneathSOS".
- Golden tests (tag `golden`, real Atkinson font loaded): symbol, lock-up, both buttons, light and
  dark. Goldens render text slightly differently on macOS and Linux, so the shared Linux CI runs
  `--exclude-tags golden` and the package adds one macOS CI job that runs them.

**App**

- Home: both buttons and both fine-print lines present (English and Turkish); "Start a search" goes
  to `/search/new`, "I am trapped" to `/trapped`; at text scale 2.0 there is no overflow.
- The existing 52 tests still pass.

**Done when** format, `analyze --fatal-infos` and tests pass in both repositories; iOS simulator
screenshots of the three screens in light and dark are sent to the maintainer; the Android debug APK
builds; the package is tagged `v0.1.0` and the app depends on that tag; both repositories are pushed
(creating the public repository is confirmed with the maintainer first); TestFlight build uploaded and
`VALID`; roadmap shows 1.2a done; ADR 0018 and `architecture.md` updated.

**On the phone the maintainer sees:** the new home screen (logo, navy/orange, Atkinson, the two
buttons, independence note, "Powered by Socrepho") in light and dark mode, and the two "being
prepared" screens. Not yet: the real search flow, banners, cards, the countdown ring.
