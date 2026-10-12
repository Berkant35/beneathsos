# 1.2b — Status Banner, Card and Device Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `StatusBanner` and `BeneathCard` to `beneathsos_ui` 0.2.0 and show a live Bluetooth/permission readiness banner on the app's home screen, with the "being prepared" text inside cards.

**Architecture:** The package gets two Material-wrapping components plus the 1.2a polish items. The app gets a `CheckReadiness` use case that runs the existing scan preconditions without scanning, a thin `ReadinessController` (Riverpod) that re-checks on Bluetooth changes and on resume when blocked, and a `ReadinessBanner` whose mapping lives in a mixin.

**Tech Stack:** Flutter 3.47.5 / Dart 3.13 (FVM), flutter_test (widget + golden), Riverpod 3 + riverpod_generator, go_router, gen-l10n (en, tr).

**Spec:** `docs/superpowers/specs/2026-10-12-status-banner-and-card-design.md`

## Global Constraints

- Every repo: `fvm dart format --set-exit-if-changed .`, `fvm flutter analyze --fatal-infos`, `fvm flutter test` exit 0 before a commit — gate on the command's own exit code (`cmd > log 2>&1; echo $?`), never on a piped `tail`.
- `beneathsos_ui` depends on Flutter only. Public members documented.
- Banner kinds: `ready` = surface container fill + `onSurface` text + `outlineVariant` border; `attention` = accent fill + `#1A0D00` text; `blocked` = error fill + on-error text (light white on `#B3261E`, dark `#690005` on `#FFB4AB`). Every kind has its own icon.
- `outlineVariant`: light `#D5DAE5`, dark `#33456A`. Button icons 24 px. Lock-up: gap = height / 4, wordmark = height / 2.
- Tappable banner/card: ≥ 56 tall and a semantics button; banner is a live region; cross-fade uses `BeneathTokens.motionOf(context).medium`.
- Readiness never starts a scan. Permission is asked automatically **at most once per app session**; afterwards only when the user taps the banner.
- "Start a search" stays enabled in every readiness state.
- Every user-facing string in `app_en.arb` and `app_tr.arb` in the same change; messages say what happened, then what to do.
- Commits: Conventional Commits, English, ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Pushing, tagging and TestFlight happen in Task 8.

## Review Focus

- **Android permission loop:** the permission dialog closing fires "resumed"; a denied permission must not be asked again automatically — pinned by "asks at most once per session" in Task 5.
- **Rapid Bluetooth toggling:** overlapping re-checks must end on the latest state, not the slowest — pinned by "latest re-check wins" in Task 5.
- **200 % text on a small phone with the banner present:** both actions stay reachable — pinned by the home small-phone tests in Task 6 (they now render the banner).
- **Screen readers hear changes:** the banner is a live region and tappable banners are buttons — pinned by semantics tests in Tasks 2 and 6.
- **Dark mode:** banner and card colours switch (no navy on navy, readable red) — pinned by dark goldens and colour tests in Tasks 2 and 3.

---

## Paths

`HUB` = `/Users/berkantcalikusu/IdeaProjects/beneathsos`; package `HUB/packages/beneathsos_ui`; app `HUB/apps/beneathsos_app`; scratch logs in the session scratchpad (`S`).

## File structure

| File | Responsibility |
|---|---|
| pkg `lib/src/tokens/colors.dart` | + `outlineVariantLight`, `outlineVariantDark` |
| pkg `lib/src/theme/beneath_theme.dart` | `outlineVariant`, `primaryTextTheme`, cached themes |
| pkg `lib/src/theme/beneath_tokens.dart` | `==` / `hashCode` |
| pkg `lib/src/widgets/{primary,secondary}_button.dart` | icon size 24 |
| pkg `lib/src/widgets/beneath_logo.dart` | lock-up proportions |
| pkg `lib/src/widgets/status_banner.dart` | `StatusKind`, `StatusBanner` |
| pkg `lib/src/widgets/beneath_card.dart` | `BeneathCard` |
| pkg `test/helpers/golden.dart` | `materialIconsFont(root)` throws when missing |
| pkg `test/helpers/readable.dart` | `expectFullyReadable` |
| app `lib/core/scanning/domain/{start_scan_result,scan_preconditions}.dart` | `BluetoothUnavailable.unsupported`; `PermissionPrecondition.ask` |
| app `lib/core/readiness/domain/{device_readiness,check_readiness}.dart` | sealed readiness + use case |
| app `lib/core/readiness/presentation/providers/readiness_controller.dart` | `checkReadinessProvider`, `ReadinessController` |
| app `lib/features/home/presentation/{mixins/readiness_banner_mixin,widgets/readiness_banner}.dart` | mapping + widget |
| app `test/helpers/pump_app.dart` | ProviderScope with fake ports |

---

### Task 1: Package polish from 1.2a (outlineVariant, icons 24, equality, primaryTextTheme, lock-up, golden helper)

**Files:**
- Modify: `lib/src/tokens/colors.dart`, `lib/src/theme/beneath_theme.dart`, `lib/src/theme/beneath_tokens.dart`, `lib/src/widgets/primary_button.dart`, `lib/src/widgets/secondary_button.dart`, `lib/src/widgets/beneath_logo.dart`, `test/helpers/golden.dart`
- Test: `test/theme/beneath_theme_test.dart`, `test/theme/beneath_tokens_test.dart`, `test/widgets/buttons_test.dart`, `test/widgets/beneath_logo_test.dart`, `test/helpers/golden_helper_test.dart`, goldens `logo_lockup_*.png`

**Interfaces:**
- Produces: `BeneathColors.outlineVariantLight` (`0xFFD5DAE5`), `BeneathColors.outlineVariantDark` (`0xFF33456A`); `BeneathTheme.light()/dark()` return cached instances; `BeneathTokens ==`; `File materialIconsFont(String? flutterRoot)` in `test/helpers/golden.dart`.

- [ ] **Step 1: Failing tests**

Append to `_expectCommon` in `test/theme/beneath_theme_test.dart`:

```dart
  expect(theme.primaryTextTheme.bodyLarge!.fontFamily, 'packages/beneathsos_ui/AtkinsonHyperlegibleNext');
```

and add to `main()`:

```dart
  test('outlineVariant is the calm border colour', () {
    expect(BeneathTheme.light().colorScheme.outlineVariant, BeneathColors.outlineVariantLight);
    expect(BeneathTheme.dark().colorScheme.outlineVariant, BeneathColors.outlineVariantDark);
  });

  test('themes are stable between calls (no theme animation on rebuild)', () {
    expect(BeneathTheme.light(), BeneathTheme.light());
    expect(BeneathTheme.dark(), BeneathTheme.dark());
  });
```

Add to `test/theme/beneath_tokens_test.dart`:

```dart
  test('tokens with equal values are equal', () {
    expect(BeneathTokens.light(), BeneathTokens.light());
    expect(BeneathTokens.light().hashCode, BeneathTokens.light().hashCode);
    expect(BeneathTokens.light(), isNot(BeneathTokens.dark()));
  });
```

Add to `test/widgets/buttons_test.dart`:

```dart
  testWidgets('both buttons draw 24 px icons', (tester) async {
    await tester.pumpWidget(_frame(PrimaryButton(label: 'Start', onPressed: () {})));
    expect(_style<FilledButton>(tester).iconSize!.resolve(<WidgetState>{}), 24);
    await tester.pumpWidget(_frame(SecondaryButton(label: 'Trapped', onPressed: () {})));
    expect(_style<OutlinedButton>(tester).iconSize!.resolve(<WidgetState>{}), 24);
  });
```

Add to `test/widgets/beneath_logo_test.dart`:

```dart
  testWidgets('lock-up proportions follow the brand source', (tester) async {
    await tester.pumpWidget(goldenFrame(
      const BeneathLogo.lockup(height: 48, semanticLabel: 'BeneathSOS'),
      brightness: Brightness.light,
    ));
    final gap = tester.widget<SizedBox>(
      find.descendant(of: find.byType(BeneathLogo), matching: find.byType(SizedBox)).first,
    );
    expect(gap.width, 12); // height / 4
    final text = tester.widget<RichText>(find.descendant(of: find.byType(BeneathLogo), matching: find.byType(RichText)));
    expect(text.text.style!.fontSize, 24); // height / 2
  });
```

Create `test/helpers/golden_helper_test.dart`:

```dart
import 'package:flutter_test/flutter_test.dart';

import 'golden.dart';

void main() {
  test('a missing Material icon font is an error, not a silent skip', () {
    expect(() => materialIconsFont(null), throwsStateError);
    expect(() => materialIconsFont('/nonexistent'), throwsStateError);
  });
}
```

- [ ] **Step 2: Run — expect RED**

Run: `fvm flutter test test/theme test/widgets/buttons_test.dart test/widgets/beneath_logo_test.dart test/helpers > S/t1.log 2>&1; echo exit=$?`
Expected: `exit=1` — `outlineVariantLight` undefined / `materialIconsFont` undefined (compile errors).

- [ ] **Step 3: Implement**

`colors.dart` — add:

```dart
  /// Calm borders and dividers in the light theme (decorative; never carries information).
  static const Color outlineVariantLight = Color(0xFFD5DAE5);

  /// Calm borders and dividers in the dark theme (decorative; never carries information).
  static const Color outlineVariantDark = Color(0xFF33456A);
```

`beneath_theme.dart`:
- add `outlineVariant: BeneathColors.outlineVariantLight,` to `_light` and `outlineVariant: BeneathColors.outlineVariantDark,` to `_dark`;
- cache the themes:

```dart
  /// Light theme (one instance, so rebuilds never animate between equal themes).
  static ThemeData light() => _lightTheme;

  /// Dark theme (one instance).
  static ThemeData dark() => _darkTheme;

  static final ThemeData _lightTheme = _build(_light, BeneathTokens.light());
  static final ThemeData _darkTheme = _build(_dark, BeneathTokens.dark());
```

- in `_build`, add `primaryTextTheme: text,` next to `textTheme: text,`.

`beneath_tokens.dart` — add:

```dart
  @override
  bool operator ==(Object other) =>
      other is BeneathTokens &&
      other.accent == accent &&
      other.onAccent == onAccent &&
      other.numeric == numeric;

  @override
  int get hashCode => Object.hash(accent, onAccent, numeric);
```

`primary_button.dart` — in `FilledButton.styleFrom(...)` add `iconSize: 24,`. `secondary_button.dart` — in `OutlinedButton.styleFrom(...)` add `iconSize: 24,`.

`beneath_logo.dart` — `SizedBox(width: size * 0.25)` and `fontSize: size * 0.5`; doc comment: "proportions follow `tools/brand/brandkit/wordmark.py` (gap ¼, wordmark ½ of the height)".

`test/helpers/golden.dart` — replace `_loadMaterialIcons` with:

```dart
/// The Material icon font of the Flutter SDK at [flutterRoot]; throws if it is missing, so a golden
/// never silently renders icons as boxes.
File materialIconsFont(String? flutterRoot) {
  final font = File('$flutterRoot/bin/cache/artifacts/material_fonts/MaterialIcons-Regular.otf');
  if (flutterRoot == null || !font.existsSync()) {
    throw StateError('Material icon font not found under FLUTTER_ROOT=$flutterRoot');
  }
  return font;
}

Future<void> _loadMaterialIcons() async {
  final font = materialIconsFont(Platform.environment['FLUTTER_ROOT']);
  final loader = FontLoader('MaterialIcons')
    ..addFont(Future.value(ByteData.sublistView(font.readAsBytesSync())));
  await loader.load();
}
```

- [ ] **Step 4: GREEN + goldens**

Run: `fvm flutter test --exclude-tags golden > S/t1.log 2>&1; echo exit=$?` → `exit=0`.
Run: `fvm flutter test --tags golden > S/g1.log 2>&1; echo exit=$?` → `exit=1` (lock-up goldens differ: new proportions; buttons differ: 24 px icons). Then `fvm flutter test --tags golden --update-goldens`, open `logo_lockup_light.png` and `buttons_light.png`: gap ¼ of the height, wordmark half the height; larger search icon.

- [ ] **Step 5: Full checks and commit (package)**

```bash
fvm dart format . ; fvm dart format --set-exit-if-changed . > S/f.log 2>&1; F=$?
fvm flutter analyze --fatal-infos > S/a.log 2>&1; A=$?
fvm flutter test > S/t.log 2>&1; T=$?
echo "format=$F analyze=$A test=$T"   # all 0, then:
git add -A && git commit -m "feat(theme): outlineVariant, stable themes, 24 px icons, brand lock-up proportions"
```

---

### Task 2: `StatusBanner`

**Files:**
- Create: `lib/src/widgets/status_banner.dart`, `test/helpers/readable.dart`, `test/widgets/status_banner_test.dart`, `test/widgets/status_banner_golden_test.dart`
- Modify: `lib/beneathsos_ui.dart`, `test/tokens/contrast_test.dart`

**Interfaces:**
- Consumes: `BeneathTokens.of/motionOf`, `BeneathSizes`, theme colours.
- Produces: `enum StatusKind { ready, attention, blocked }`; `StatusBanner({required StatusKind kind, required String message, VoidCallback? onTap, IconData? icon})`.

- [ ] **Step 1: Failing tests**

`test/helpers/readable.dart`:

```dart
import 'package:flutter/rendering.dart';
import 'package:flutter_test/flutter_test.dart';

/// Fails if the paragraph found by [text] is laid out shorter than its text (clipped).
void expectNotClipped(WidgetTester tester, Finder text) {
  final paragraph = tester.renderObject<RenderParagraph>(text);
  expect(
    paragraph.size.height,
    greaterThanOrEqualTo(paragraph.getMaxIntrinsicHeight(paragraph.size.width) - 0.5),
    reason: 'the paragraph is clipped',
  );
}
```

Add to the contrast cases in `test/tokens/contrast_test.dart`:

```dart
      ('text on surface container (ready banner, card)', BeneathColors.textLight, BeneathColors.white, 17.4),
```

`test/widgets/status_banner_test.dart`:

```dart
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/readable.dart';

Widget _frame(Widget child, {Brightness brightness = Brightness.light, double textScale = 1, bool reduceMotion = false}) =>
    MaterialApp(
      theme: brightness == Brightness.light ? BeneathTheme.light() : BeneathTheme.dark(),
      home: Builder(
        builder: (context) => MediaQuery(
          data: MediaQuery.of(context).copyWith(
            textScaler: TextScaler.linear(textScale),
            disableAnimations: reduceMotion,
          ),
          child: Scaffold(body: Padding(padding: const EdgeInsets.all(16), child: Column(children: [child]))),
        ),
      ),
    );

Material _surface(WidgetTester tester) => tester.widget<Material>(
  find.descendant(of: find.byType(StatusBanner), matching: find.byType(Material)).first,
);

Color? _textColour(WidgetTester tester, String message) =>
    tester.widget<Text>(find.text(message)).style?.color;

void main() {
  testWidgets('ready, light: white fill, dark text, calm border, check icon', (tester) async {
    await tester.pumpWidget(_frame(const StatusBanner(kind: StatusKind.ready, message: 'Ready.')));
    final shape = _surface(tester).shape! as RoundedRectangleBorder;
    expect(_surface(tester).color, BeneathColors.white);
    expect(shape.side.color, BeneathColors.outlineVariantLight);
    expect(_textColour(tester, 'Ready.'), BeneathColors.textLight);
    expect(find.byIcon(Icons.check_circle_rounded), findsOneWidget);
  });

  testWidgets('ready, dark: secondary surface fill, light text', (tester) async {
    await tester.pumpWidget(_frame(const StatusBanner(kind: StatusKind.ready, message: 'Ready.'), brightness: Brightness.dark));
    expect(_surface(tester).color, BeneathColors.surface2Dark);
    expect(_textColour(tester, 'Ready.'), BeneathColors.textDark);
  });

  testWidgets('attention: orange fill, dark text, warning icon', (tester) async {
    await tester.pumpWidget(_frame(const StatusBanner(kind: StatusKind.attention, message: 'Look.')));
    expect(_surface(tester).color, BeneathColors.accentLight);
    expect(_textColour(tester, 'Look.'), BeneathColors.onAccent);
    expect(find.byIcon(Icons.warning_rounded), findsOneWidget);
  });

  testWidgets('blocked, light and dark: readable red, block icon', (tester) async {
    await tester.pumpWidget(_frame(const StatusBanner(kind: StatusKind.blocked, message: 'Off.')));
    expect(_surface(tester).color, BeneathColors.errorLight);
    expect(_textColour(tester, 'Off.'), BeneathColors.white);
    expect(find.byIcon(Icons.block_rounded), findsOneWidget);
    await tester.pumpWidget(_frame(const StatusBanner(kind: StatusKind.blocked, message: 'Off.'), brightness: Brightness.dark));
    await tester.pumpAndSettle();
    expect(_surface(tester).color, BeneathColors.errorDark);
    expect(_textColour(tester, 'Off.'), BeneathColors.onErrorDark);
  });

  testWidgets('a custom icon replaces the default', (tester) async {
    await tester.pumpWidget(_frame(const StatusBanner(kind: StatusKind.ready, message: 'Wait.', icon: Icons.hourglass_top_rounded)));
    expect(find.byIcon(Icons.hourglass_top_rounded), findsOneWidget);
    expect(find.byIcon(Icons.check_circle_rounded), findsNothing);
  });

  testWidgets('tappable: a 56 px button with a chevron that calls onTap', (tester) async {
    var taps = 0;
    final handle = tester.ensureSemantics();
    await tester.pumpWidget(_frame(StatusBanner(kind: StatusKind.blocked, message: 'Tap me.', onTap: () => taps++)));
    expect(tester.getSize(find.byType(StatusBanner)).height, greaterThanOrEqualTo(56));
    expect(find.byIcon(Icons.chevron_right_rounded), findsOneWidget);
    expect(
      tester.getSemantics(find.bySemanticsLabel('Tap me.')),
      isSemantics(label: 'Tap me.', isButton: true, isLiveRegion: true),
    );
    await tester.tap(find.byType(StatusBanner));
    expect(taps, 1);
    handle.dispose();
  });

  testWidgets('not tappable: no chevron, not a button, still a live region', (tester) async {
    final handle = tester.ensureSemantics();
    await tester.pumpWidget(_frame(const StatusBanner(kind: StatusKind.ready, message: 'Ready.')));
    expect(find.byIcon(Icons.chevron_right_rounded), findsNothing);
    expect(
      tester.getSemantics(find.bySemanticsLabel('Ready.')),
      isSemantics(label: 'Ready.', isButton: false, isLiveRegion: true),
    );
    handle.dispose();
  });

  testWidgets('200 % text: the message wraps and is not clipped', (tester) async {
    const message = 'Bluetooth permission is off. Tap to turn it on in Settings.';
    await tester.pumpWidget(_frame(StatusBanner(kind: StatusKind.blocked, message: message, onTap: () {}), textScale: 2));
    expect(tester.takeException(), isNull);
    expectNotClipped(tester, find.text(message));
  });

  testWidgets('reduce motion: the cross-fade takes no time', (tester) async {
    await tester.pumpWidget(_frame(const StatusBanner(kind: StatusKind.ready, message: 'Ready.'), reduceMotion: true));
    expect(tester.widget<AnimatedSwitcher>(find.byType(AnimatedSwitcher)).duration, Duration.zero);
  });
}
```

`test/widgets/status_banner_golden_test.dart`:

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
    testWidgets('status banners, ${brightness.name}', (tester) async {
      await tester.pumpWidget(goldenFrame(
        SizedBox(
          width: 360,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const StatusBanner(kind: StatusKind.ready, message: 'Bluetooth is on and ready.'),
              const SizedBox(height: 12),
              const StatusBanner(kind: StatusKind.attention, message: 'Identity is changing.'),
              const SizedBox(height: 12),
              StatusBanner(kind: StatusKind.blocked, message: 'Bluetooth is off. Turn it on in your phone\'s settings.', onTap: () {}),
            ],
          ),
        ),
        brightness: brightness,
      ));
      await tester.pumpAndSettle();
      await expectLater(find.byKey(goldenKey), matchesGoldenFile('goldens/status_banners_${brightness.name}.png'));
    });
  }
}
```

- [ ] **Step 2: Run — expect RED**

Run: `fvm flutter test test/widgets/status_banner_test.dart > S/t2.log 2>&1; echo exit=$?` → `exit=1` (`StatusBanner` undefined).

- [ ] **Step 3: Implement** — `lib/src/widgets/status_banner.dart`

```dart
import 'package:beneathsos_ui/src/theme/beneath_tokens.dart';
import 'package:beneathsos_ui/src/tokens/sizes.dart';
import 'package:beneathsos_ui/src/tokens/spacing.dart';
import 'package:flutter/material.dart';

/// What a [StatusBanner] reports. Each kind has its own colour **and** icon — never colour alone.
enum StatusKind {
  /// All good, or neutral progress.
  ready,

  /// Needs attention soon (e.g. the target's identity is changing).
  attention,

  /// Something blocks the task (Bluetooth off, permission missing). Red means blocked only.
  blocked,
}

/// One status line: what happened, then what to do. With [onTap] the whole banner is a button.
/// Changes are announced to screen readers (live region) and cross-fade unless motion is reduced.
class StatusBanner extends StatelessWidget {
  /// Creates a banner. [message] is localised by the app.
  const StatusBanner({required this.kind, required this.message, this.onTap, this.icon, super.key});

  /// What the banner reports.
  final StatusKind kind;

  /// What happened and what to do.
  final String message;

  /// Makes the banner a button (≥ 56 tall, trailing chevron).
  final VoidCallback? onTap;

  /// Replaces the kind's default icon.
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final tokens = BeneathTokens.of(context);
    final (background, foreground, border, defaultIcon) = switch (kind) {
      StatusKind.ready => (scheme.surfaceContainer, scheme.onSurface, scheme.outlineVariant, Icons.check_circle_rounded),
      StatusKind.attention => (tokens.accent, tokens.onAccent, Colors.transparent, Icons.warning_rounded),
      StatusKind.blocked => (scheme.error, scheme.onError, Colors.transparent, Icons.block_rounded),
    };
    final shape = RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(BeneathSizes.radius),
      side: BorderSide(color: border),
    );
    final style = Theme.of(context).textTheme.bodyLarge?.copyWith(color: foreground, fontWeight: FontWeight.w600);
    final tap = onTap;
    final banner = Material(
      key: ValueKey((kind, message)),
      color: background,
      shape: shape,
      child: InkWell(
        onTap: tap,
        customBorder: shape,
        child: ConstrainedBox(
          constraints: const BoxConstraints(minHeight: BeneathSizes.minTouchTarget),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: BeneathSpacing.m, vertical: BeneathSpacing.sm),
            child: Row(
              children: [
                Icon(icon ?? defaultIcon, color: foreground, size: 28),
                const SizedBox(width: BeneathSpacing.sm),
                Expanded(child: Text(message, style: style)),
                if (tap != null) Icon(Icons.chevron_right_rounded, color: foreground),
              ],
            ),
          ),
        ),
      ),
    );
    return MergeSemantics(
      child: Semantics(
        liveRegion: true,
        button: tap != null,
        child: AnimatedSwitcher(duration: BeneathTokens.motionOf(context).medium, child: banner),
      ),
    );
  }
}
```

Export `src/widgets/status_banner.dart` from `lib/beneathsos_ui.dart`.

- [ ] **Step 4: GREEN, goldens (fail → create → inspect), full checks, commit**

Run: `fvm flutter test test/widgets/status_banner_test.dart test/tokens > S/t2.log 2>&1; echo exit=$?` → `exit=0`.
Run: `fvm flutter test --tags golden` → fails on the 2 new goldens (missing); `--update-goldens`; open both: ready (calm), attention (orange), blocked (red with chevron), icons visible, Atkinson.
Full checks (format/analyze/test exit 0), then `git add -A && git commit -m "feat(widgets): StatusBanner (ready, attention, blocked) with goldens"`.

---

### Task 3: `BeneathCard`

**Files:**
- Create: `lib/src/widgets/beneath_card.dart`, `test/widgets/beneath_card_test.dart`, `test/widgets/beneath_card_golden_test.dart`
- Modify: `lib/beneathsos_ui.dart`

**Interfaces:**
- Produces: `BeneathCard({required Widget child, String? title, IconData? icon, VoidCallback? onTap})`.

- [ ] **Step 1: Failing tests** — `test/widgets/beneath_card_test.dart`

```dart
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

Widget _frame(Widget child, {Brightness brightness = Brightness.light}) => MaterialApp(
  theme: brightness == Brightness.light ? BeneathTheme.light() : BeneathTheme.dark(),
  home: Scaffold(body: Padding(padding: const EdgeInsets.all(16), child: child)),
);

Material _surface(WidgetTester tester) => tester.widget<Material>(
  find.descendant(of: find.byType(BeneathCard), matching: find.byType(Material)).first,
);

void main() {
  testWidgets('shows title, icon and content on the container colour with a calm border', (tester) async {
    await tester.pumpWidget(_frame(const BeneathCard(title: 'Being prepared', icon: Icons.construction_rounded, child: Text('Body'))));
    expect(find.text('Being prepared'), findsOneWidget);
    expect(find.byIcon(Icons.construction_rounded), findsOneWidget);
    expect(find.text('Body'), findsOneWidget);
    expect(_surface(tester).color, BeneathColors.white);
    expect((_surface(tester).shape! as RoundedRectangleBorder).side.color, BeneathColors.outlineVariantLight);
  });

  testWidgets('dark: secondary surface and dark border', (tester) async {
    await tester.pumpWidget(_frame(const BeneathCard(child: Text('Body')), brightness: Brightness.dark));
    expect(_surface(tester).color, BeneathColors.surface2Dark);
    expect((_surface(tester).shape! as RoundedRectangleBorder).side.color, BeneathColors.outlineVariantDark);
  });

  testWidgets('with onTap it is a button for screen readers and calls back', (tester) async {
    var taps = 0;
    final handle = tester.ensureSemantics();
    await tester.pumpWidget(_frame(BeneathCard(title: 'Open', onTap: () => taps++, child: const Text('Body'))));
    expect(tester.getSemantics(find.byType(BeneathCard)), isSemantics(isButton: true));
    await tester.tap(find.byType(BeneathCard));
    expect(taps, 1);
    handle.dispose();
  });

  testWidgets('without onTap it is not a button', (tester) async {
    final handle = tester.ensureSemantics();
    await tester.pumpWidget(_frame(const BeneathCard(title: 'Info', child: Text('Body'))));
    expect(tester.getSemantics(find.byType(BeneathCard)), isNot(isSemantics(isButton: true)));
    handle.dispose();
  });
}
```

Golden `test/widgets/beneath_card_golden_test.dart` (tag golden; light and dark): a 360-wide `BeneathCard(title: 'Being prepared', icon: Icons.construction_rounded, child: Text('This step is being prepared. Here you will draw the outline of the rubble site.'))`, file `goldens/card_${brightness.name}.png`, using `goldenFrame` and `loadBeneathFont` exactly as in `status_banner_golden_test.dart`.

- [ ] **Step 2: Run — expect RED** (`BeneathCard` undefined): `fvm flutter test test/widgets/beneath_card_test.dart > S/t3.log 2>&1; echo exit=$?` → `exit=1`.

- [ ] **Step 3: Implement** — `lib/src/widgets/beneath_card.dart`

```dart
import 'package:beneathsos_ui/src/tokens/sizes.dart';
import 'package:beneathsos_ui/src/tokens/spacing.dart';
import 'package:flutter/material.dart';

/// A content card: container fill, calm border, optional title with icon. With [onTap] it is a
/// button for screen readers.
class BeneathCard extends StatelessWidget {
  /// Creates a card.
  const BeneathCard({required this.child, this.title, this.icon, this.onTap, super.key});

  /// Card content.
  final Widget child;

  /// Optional title, already localised.
  final String? title;

  /// Optional icon before the title.
  final IconData? icon;

  /// Makes the card tappable.
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;
    final title = this.title;
    final icon = this.icon;
    final shape = RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(BeneathSizes.radius),
      side: BorderSide(color: scheme.outlineVariant),
    );
    final content = Padding(
      padding: const EdgeInsets.all(BeneathSpacing.m),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          if (title != null) ...[
            Row(
              children: [
                if (icon != null) ...[
                  Icon(icon, color: scheme.primary, size: 28),
                  const SizedBox(width: BeneathSpacing.sm),
                ],
                Expanded(child: Text(title, style: theme.textTheme.titleLarge?.copyWith(color: scheme.primary))),
              ],
            ),
            const SizedBox(height: BeneathSpacing.sm),
          ],
          child,
        ],
      ),
    );
    final tap = onTap;
    final card = Material(
      color: scheme.surfaceContainer,
      shape: shape,
      clipBehavior: Clip.antiAlias,
      child: tap == null ? content : InkWell(onTap: tap, child: content),
    );
    return tap == null ? card : Semantics(button: true, child: card);
  }
}
```

Export it from `lib/beneathsos_ui.dart`.

- [ ] **Step 4: GREEN, goldens (fail → create → inspect), full checks, commit**

`git add -A && git commit -m "feat(widgets): BeneathCard with goldens"`.

---

### Task 4: Domain — `CheckReadiness` reusing the scan preconditions (app)

**Files:**
- Modify: `lib/core/scanning/domain/start_scan_result.dart`, `lib/core/scanning/domain/scan_preconditions.dart`
- Create: `lib/core/readiness/domain/device_readiness.dart`, `lib/core/readiness/domain/check_readiness.dart`
- Test: `test/core/scanning/domain/scan_preconditions_test.dart`, `test/core/readiness/domain/check_readiness_test.dart`

**Interfaces:**
- Consumes: `ScannerPort`, `ScanPermissionPort`, `FakeScanner`, `FakePermissions` (`test/core/scanning/fakes.dart`).
- Produces: `BluetoothUnavailable({bool unsupported = false})`; `PermissionPrecondition(ScanPermissionPort, {bool ask = true})`; `sealed class DeviceReadiness` with `ReadinessChecking, ReadinessReady, ReadinessNeedsPermission, ReadinessPermissionInSettings, ReadinessBluetoothOff, ReadinessUnsupported` (all `const`); `CheckReadiness({required ScanPermissionPort permissions, required ScannerPort scanner})` with `Future<DeviceReadiness> call({required bool askForPermission})`.

- [ ] **Step 1: Failing tests**

In `scan_preconditions_test.dart`, replace the body of `'blocks when off or unsupported'` with:

```dart
      expect(
        await checkWith(BluetoothAvailability.off),
        isA<BluetoothUnavailable>().having((r) => r.unsupported, 'unsupported', false),
      );
      expect(
        await checkWith(BluetoothAvailability.unsupported),
        isA<BluetoothUnavailable>().having((r) => r.unsupported, 'unsupported', true),
      );
```

and add to the `PermissionPrecondition` group:

```dart
    test('with ask: false it only checks, never requests', () async {
      final permissions = FakePermissions(checkResult: ScanPermission.denied);
      final result = await PermissionPrecondition(permissions, ask: false).check();
      expect(result, isA<PermissionMissing>().having((r) => r.permanent, 'permanent', false));
      expect(permissions.calls, ['check']);
    });
```

`test/core/readiness/domain/check_readiness_test.dart`:

```dart
import 'package:beneathsos_app/core/readiness/domain/check_readiness.dart';
import 'package:beneathsos_app/core/readiness/domain/device_readiness.dart';
import 'package:beneathsos_app/core/scanning/domain/scan_types.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../scanning/fakes.dart';

void main() {
  late FakeScanner scanner;
  late FakePermissions permissions;

  setUp(() {
    scanner = FakeScanner();
    permissions = FakePermissions(checkResult: ScanPermission.granted);
  });
  tearDown(() => scanner.close());

  Future<DeviceReadiness> check({bool ask = false}) =>
      CheckReadiness(permissions: permissions, scanner: scanner)(askForPermission: ask);

  test('permission and Bluetooth fine → ready, and a scan is never started', () async {
    expect(await check(), isA<ReadinessReady>());
    expect(scanner.calls, isEmpty);
  });

  test('missing permission is asked when allowed; granted → ready', () async {
    permissions
      ..checkResult = ScanPermission.denied
      ..requestResult = ScanPermission.granted;
    expect(await check(ask: true), isA<ReadinessReady>());
    expect(permissions.calls, ['check', 'request']);
  });

  test('missing permission, asking not allowed → needs permission, no dialog', () async {
    permissions.checkResult = ScanPermission.denied;
    expect(await check(), isA<ReadinessNeedsPermission>());
    expect(permissions.calls, ['check']);
  });

  test('permanently denied → settings', () async {
    permissions.checkResult = ScanPermission.permanentlyDenied;
    expect(await check(ask: true), isA<ReadinessPermissionInSettings>());
  });

  test('iOS Bluetooth unauthorised → settings', () async {
    scanner.availability = BluetoothAvailability.unauthorized;
    expect(await check(), isA<ReadinessPermissionInSettings>());
  });

  test('Bluetooth off → off', () async {
    scanner.availability = BluetoothAvailability.off;
    expect(await check(), isA<ReadinessBluetoothOff>());
  });

  test('no Bluetooth LE → unsupported', () async {
    scanner.availability = BluetoothAvailability.unsupported;
    expect(await check(), isA<ReadinessUnsupported>());
  });

  test('permission and Bluetooth both missing → permission first (the app can fix it)', () async {
    permissions.checkResult = ScanPermission.denied;
    scanner.availability = BluetoothAvailability.off;
    expect(await check(), isA<ReadinessNeedsPermission>());
  });
}
```

- [ ] **Step 2: Run — expect RED** (`check_readiness.dart` missing, `unsupported`/`ask` undefined): `fvm flutter test test/core > S/t4.log 2>&1; echo exit=$?` → `exit=1`.

- [ ] **Step 3: Implement**

`start_scan_result.dart`:

```dart
/// Bluetooth is off ([unsupported] false) or the device has no Bluetooth LE ([unsupported] true).
final class BluetoothUnavailable extends StartScanResult {
  /// Creates the result.
  const BluetoothUnavailable({this.unsupported = false});

  /// Whether the device cannot do Bluetooth LE at all.
  final bool unsupported;
}
```

`scan_preconditions.dart`:
- `PermissionPrecondition`: constructor `const PermissionPrecondition(this._permissions, {this.ask = true});`, field doc `/// Whether a missing permission is requested (false: only checked).` `final bool ask;`, and `if (ask && permission == ScanPermission.denied) { permission = await _permissions.request(); }`. Class doc: "Scanning permissions must be granted; asks once when missing (unless [ask] is false)."
- `BluetoothPrecondition`: split the arm: `BluetoothAvailability.off => const BluetoothUnavailable(), BluetoothAvailability.unsupported => const BluetoothUnavailable(unsupported: true),`.

`lib/core/readiness/domain/device_readiness.dart`:

```dart
/// Can this phone search right now? Shown on the home screen; never starts a scan.
sealed class DeviceReadiness {
  const DeviceReadiness();
}

/// Not known yet.
final class ReadinessChecking extends DeviceReadiness {
  /// Creates the state.
  const ReadinessChecking();
}

/// Permission granted and Bluetooth on.
final class ReadinessReady extends DeviceReadiness {
  /// Creates the state.
  const ReadinessReady();
}

/// Permission missing; the app can ask.
final class ReadinessNeedsPermission extends DeviceReadiness {
  /// Creates the state.
  const ReadinessNeedsPermission();
}

/// Permission missing; only the system settings can grant it.
final class ReadinessPermissionInSettings extends DeviceReadiness {
  /// Creates the state.
  const ReadinessPermissionInSettings();
}

/// Bluetooth is off.
final class ReadinessBluetoothOff extends DeviceReadiness {
  /// Creates the state.
  const ReadinessBluetoothOff();
}

/// The phone has no Bluetooth LE.
final class ReadinessUnsupported extends DeviceReadiness {
  /// Creates the state.
  const ReadinessUnsupported();
}
```

`lib/core/readiness/domain/check_readiness.dart`:

```dart
import 'package:beneathsos_app/core/readiness/domain/device_readiness.dart';
import 'package:beneathsos_app/core/scanning/domain/scan_ports.dart';
import 'package:beneathsos_app/core/scanning/domain/scan_preconditions.dart';
import 'package:beneathsos_app/core/scanning/domain/start_scan_result.dart';

/// "Can this phone search right now?" — the same preconditions scanning uses (permission first,
/// then Bluetooth), without starting a scan.
final class CheckReadiness {
  /// Creates the use case.
  const CheckReadiness({required ScanPermissionPort permissions, required ScannerPort scanner})
    : _permissions = permissions,
      _scanner = scanner;

  final ScanPermissionPort _permissions;
  final ScannerPort _scanner;

  /// Checks; requests a missing permission only when [askForPermission] is true.
  Future<DeviceReadiness> call({required bool askForPermission}) async {
    final preconditions = [
      PermissionPrecondition(_permissions, ask: askForPermission),
      BluetoothPrecondition(_scanner),
    ];
    for (final precondition in preconditions) {
      final blocked = await precondition.check();
      if (blocked != null) return _readiness(blocked);
    }
    return const ReadinessReady();
  }

  static DeviceReadiness _readiness(StartScanResult blocked) => switch (blocked) {
    PermissionMissing(permanent: false) => const ReadinessNeedsPermission(),
    PermissionMissing(permanent: true) => const ReadinessPermissionInSettings(),
    BluetoothUnavailable(unsupported: true) => const ReadinessUnsupported(),
    BluetoothUnavailable() => const ReadinessBluetoothOff(),
    // Preconditions only block with the two results above.
    ScanStarted() || StartFailed() => const ReadinessReady(),
  };
}
```

- [ ] **Step 4: GREEN + full checks + commit (app)**

All app tests pass (the scan controller still maps `BluetoothUnavailable()` to `ScanBluetoothOff`). `git commit -m "feat(readiness): CheckReadiness reuses the scan preconditions without scanning"`.

---

### Task 5: `ReadinessController` (app)

**Files:**
- Create: `lib/core/readiness/presentation/providers/readiness_controller.dart` (+ generated `.g.dart`)
- Test: `test/core/readiness/presentation/readiness_controller_test.dart`

**Interfaces:**
- Consumes: `CheckReadiness`, `scannerPortProvider`, `scanPermissionPortProvider`, `appLifecycleProvider`.
- Produces: `checkReadinessProvider` (`CheckReadiness`), `readinessControllerProvider` (`DeviceReadiness`) with methods `Future<void> recheck()`, `Future<void> requestPermission()`, `Future<void> openSettings()`.

- [ ] **Step 1: Failing tests**

```dart
import 'dart:async';

import 'package:beneathsos_app/core/readiness/domain/device_readiness.dart';
import 'package:beneathsos_app/core/readiness/presentation/providers/readiness_controller.dart';
import 'package:beneathsos_app/core/scanning/domain/scan_types.dart';
import 'package:beneathsos_app/core/scanning/presentation/providers/scanning_providers.dart';
import 'package:beneathsos_app/core/services/app_lifecycle.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import '../../scanning/fakes.dart';

/// Scanner whose availability answers wait for the test (to model slow, overlapping checks).
class _SlowScanner extends FakeScanner {
  final pending = <Completer<BluetoothAvailability>>[];

  @override
  Future<BluetoothAvailability> settledAvailability() {
    final answer = Completer<BluetoothAvailability>();
    pending.add(answer);
    return answer.future;
  }
}

void main() {
  late FakeScanner scanner;
  late FakePermissions permissions;
  late StreamController<AppLifecycleState> lifecycle;
  late ProviderContainer container;

  void start(FakeScanner withScanner) {
    scanner = withScanner;
    container = ProviderContainer(
      overrides: [
        scannerPortProvider.overrideWithValue(scanner),
        scanPermissionPortProvider.overrideWithValue(permissions),
        appLifecycleProvider.overrideWith((ref) => lifecycle.stream),
      ],
    );
    // Riverpod 3 pauses unwatched providers; keep a listener like the home banner does.
    container.listen(readinessControllerProvider, (_, _) {});
  }

  setUp(() {
    permissions = FakePermissions(checkResult: ScanPermission.granted);
    lifecycle = StreamController<AppLifecycleState>();
  });

  tearDown(() async {
    container.dispose();
    await lifecycle.close();
    await scanner.close();
  });

  DeviceReadiness state() => container.read(readinessControllerProvider);

  test('starts as checking, then ready; never scans', () async {
    start(FakeScanner());
    expect(state(), isA<ReadinessChecking>());
    await pumpEventQueue();
    expect(state(), isA<ReadinessReady>());
    expect(scanner.calls, isEmpty);
  });

  test('Bluetooth switched off and on changes the state', () async {
    start(FakeScanner());
    await pumpEventQueue();
    scanner.emitAvailability(BluetoothAvailability.off);
    await pumpEventQueue();
    expect(state(), isA<ReadinessBluetoothOff>());
    scanner.emitAvailability(BluetoothAvailability.on);
    await pumpEventQueue();
    expect(state(), isA<ReadinessReady>());
  });

  test('asks at most once per session: resume after a denial does not ask again', () async {
    permissions
      ..checkResult = ScanPermission.denied
      ..requestResult = ScanPermission.denied;
    start(FakeScanner());
    await pumpEventQueue();
    expect(state(), isA<ReadinessNeedsPermission>());
    lifecycle.add(AppLifecycleState.resumed); // the dialog closing resumes the app on Android
    await pumpEventQueue();
    expect(permissions.calls.where((c) => c == 'request'), hasLength(1));
  });

  test('resume re-checks when blocked (back from Settings)', () async {
    start(FakeScanner()..availability = BluetoothAvailability.off);
    await pumpEventQueue();
    expect(state(), isA<ReadinessBluetoothOff>());
    scanner.availability = BluetoothAvailability.on; // turned on in Settings, no event seen
    lifecycle.add(AppLifecycleState.resumed);
    await pumpEventQueue();
    expect(state(), isA<ReadinessReady>());
  });

  test('resume does nothing when ready', () async {
    start(FakeScanner());
    await pumpEventQueue();
    final checks = permissions.calls.length;
    lifecycle.add(AppLifecycleState.resumed);
    await pumpEventQueue();
    expect(permissions.calls, hasLength(checks));
  });

  test('requestPermission asks, then re-checks', () async {
    permissions
      ..checkResult = ScanPermission.denied
      ..requestResult = ScanPermission.denied;
    start(FakeScanner());
    await pumpEventQueue();
    permissions
      ..requestResult = ScanPermission.granted
      ..checkResult = ScanPermission.granted;
    await container.read(readinessControllerProvider.notifier).requestPermission();
    expect(state(), isA<ReadinessReady>());
    expect(permissions.calls.where((c) => c == 'request'), hasLength(2));
  });

  test('openSettings opens the system settings', () async {
    start(FakeScanner());
    await pumpEventQueue();
    await container.read(readinessControllerProvider.notifier).openSettings();
    expect(permissions.calls, contains('openSettings'));
  });

  test('latest re-check wins when checks overlap (rapid toggling)', () async {
    final slow = _SlowScanner();
    start(slow);
    await pumpEventQueue();
    slow.pending.removeAt(0).complete(BluetoothAvailability.on); // initial check
    await pumpEventQueue();
    final notifier = container.read(readinessControllerProvider.notifier);
    unawaited(notifier.recheck()); // older: will answer "off" last
    unawaited(notifier.recheck()); // newer: answers "on" first
    await pumpEventQueue();
    slow.pending[1].complete(BluetoothAvailability.on);
    await pumpEventQueue();
    slow.pending[0].complete(BluetoothAvailability.off);
    await pumpEventQueue();
    expect(state(), isA<ReadinessReady>());
  });
}
```

- [ ] **Step 2: Run — expect RED** (`readiness_controller.dart` missing): `fvm flutter test test/core/readiness > S/t5.log 2>&1; echo exit=$?` → `exit=1`.

- [ ] **Step 3: Implement** — `lib/core/readiness/presentation/providers/readiness_controller.dart`

```dart
import 'dart:async';

import 'package:beneathsos_app/core/readiness/domain/check_readiness.dart';
import 'package:beneathsos_app/core/readiness/domain/device_readiness.dart';
import 'package:beneathsos_app/core/scanning/presentation/providers/scanning_providers.dart';
import 'package:beneathsos_app/core/services/app_lifecycle.dart';
import 'package:flutter/widgets.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'readiness_controller.g.dart';

/// The readiness use case, bound to the app's ports.
@Riverpod(keepAlive: true)
CheckReadiness checkReadiness(Ref ref) => CheckReadiness(
  permissions: ref.watch(scanPermissionPortProvider),
  scanner: ref.watch(scannerPortProvider),
);

/// Device readiness for the home banner. Thin: runs the use case, re-checks on Bluetooth changes
/// and on resume when blocked. Asks for permission automatically once per session; never scans.
@Riverpod(keepAlive: true)
class ReadinessController extends _$ReadinessController {
  int _generation = 0;

  @override
  DeviceReadiness build() {
    final changes = ref.watch(scannerPortProvider).availabilityChanges.listen((_) => unawaited(recheck()));
    ref.listen(appLifecycleProvider, (_, next) {
      if (next.value == AppLifecycleState.resumed && _blocked) unawaited(recheck());
    });
    ref.onDispose(() => unawaited(changes.cancel()));
    unawaited(_check(askForPermission: true));
    return const ReadinessChecking();
  }

  bool get _blocked => switch (state) {
    ReadinessChecking() || ReadinessReady() => false,
    _ => true,
  };

  /// Checks again without asking for permission.
  Future<void> recheck() => _check(askForPermission: false);

  /// Asks for the missing permission (user tapped the banner), then re-checks.
  Future<void> requestPermission() async {
    await ref.read(scanPermissionPortProvider).request();
    await recheck();
  }

  /// Opens the system settings, then re-checks (and again on resume).
  Future<void> openSettings() async {
    await ref.read(scanPermissionPortProvider).openSettings();
    await recheck();
  }

  Future<void> _check({required bool askForPermission}) async {
    final generation = ++_generation;
    final result = await ref.read(checkReadinessProvider)(askForPermission: askForPermission);
    if (!ref.mounted || generation != _generation) return; // a newer check is in flight
    state = result;
  }
}
```

Run: `fvm dart run build_runner build > S/br.log 2>&1; echo exit=$?` → `exit=0`.

- [ ] **Step 4: GREEN + full checks + commit (app)**

`git commit -m "feat(readiness): ReadinessController re-checks on Bluetooth and resume, asks once"`.

---

### Task 6: Readiness banner on the home screen (app)

**Files:**
- Modify: `lib/l10n/app_en.arb`, `lib/l10n/app_tr.arb`, `lib/features/home/presentation/screens/home_screen.dart`, `test/helpers/pump_app.dart`, `test/app_test.dart`, `test/features/home/home_screen_test.dart`
- Create: `lib/features/home/presentation/mixins/readiness_banner_mixin.dart`, `lib/features/home/presentation/widgets/readiness_banner.dart`

**Interfaces:**
- Consumes: `readinessControllerProvider`, `StatusBanner`, `StatusKind`, `FakeScanner`, `FakePermissions`.
- Produces: `ReadinessBanner` (ConsumerWidget); `ReadinessBannerMixin.bannerFor(AppLocalizations, DeviceReadiness, ReadinessController) -> BannerContent`; `typedef BannerContent = ({StatusKind kind, String message, IconData? icon, VoidCallback? onTap})`; `pumpRouterApp(tester, {locale, textScale, theme, FakeScanner? scanner, FakePermissions? permissions})`.

- [ ] **Step 1: Strings** — add to `app_en.arb` / `app_tr.arb` (spec §4 table): `readinessChecking`, `readinessReady`, `readinessNeedsPermission`, `readinessPermissionInSettings`, `readinessBluetoothOff`, `readinessUnsupported`, `preparingCardTitle` with the exact English and Turkish texts of the spec. Run `fvm flutter gen-l10n` → exit 0.

- [ ] **Step 2: Test helper with fake ports** — `test/helpers/pump_app.dart`: wrap both pump helpers' `MaterialApp`s in

```dart
ProviderScope(
  overrides: [
    scannerPortProvider.overrideWithValue(scanner ?? FakeScanner()),
    scanPermissionPortProvider.overrideWithValue(permissions ?? FakePermissions(checkResult: ScanPermission.granted)),
    appLifecycleProvider.overrideWith((ref) => const Stream.empty()),
  ],
  child: ...,
)
```

add optional `FakeScanner? scanner, FakePermissions? permissions` parameters to `pumpRouterApp`, and import `../core/scanning/fakes.dart`, `scanning_providers.dart`, `app_lifecycle.dart`, `scan_types.dart`, `flutter_riverpod`. In `test/app_test.dart` give both `ProviderScope`s the same three overrides (a real `BleService` needs the platform plugin).

- [ ] **Step 3: Failing tests** — add to `test/features/home/home_screen_test.dart`:

```dart
  Future<void> pumpWith(WidgetTester tester, {BluetoothAvailability bluetooth = BluetoothAvailability.on,
      ScanPermission permission = ScanPermission.granted, ScanPermission request = ScanPermission.denied,
      Locale locale = const Locale('en'), FakePermissions? permissions}) async {
    await pumpRouterApp(
      tester,
      locale: locale,
      scanner: FakeScanner()..availability = bluetooth,
      permissions: permissions ?? FakePermissions(checkResult: permission, requestResult: request),
    );
  }

  testWidgets('ready: calm banner above the actions', (tester) async {
    await pumpWith(tester);
    expect(find.text('Bluetooth is on and ready.'), findsOneWidget);
    expect(
      tester.getTopLeft(find.byType(StatusBanner)).dy,
      lessThan(tester.getTopLeft(find.text('Start a search')).dy),
    );
  });

  testWidgets('Bluetooth off: red banner with the instruction, no tap action', (tester) async {
    await pumpWith(tester, bluetooth: BluetoothAvailability.off);
    expect(find.text("Bluetooth is off. Turn it on in your phone's settings."), findsOneWidget);
    expect(tester.widget<StatusBanner>(find.byType(StatusBanner)).kind, StatusKind.blocked);
    expect(tester.widget<StatusBanner>(find.byType(StatusBanner)).onTap, isNull);
  });

  testWidgets('unsupported: tells the user to search with another phone', (tester) async {
    await pumpWith(tester, bluetooth: BluetoothAvailability.unsupported);
    expect(find.textContaining('Search with another phone'), findsOneWidget);
  });

  testWidgets('permission needed: tapping the banner asks again', (tester) async {
    final permissions = FakePermissions(checkResult: ScanPermission.denied, requestResult: ScanPermission.denied);
    await pumpWith(tester, permissions: permissions);
    expect(find.text('Bluetooth permission is needed. Tap to allow it.'), findsOneWidget);
    await tester.tap(find.byType(StatusBanner));
    await tester.pumpAndSettle();
    expect(permissions.calls.where((c) => c == 'request'), hasLength(2));
  });

  testWidgets('permission in Settings: tapping opens the settings', (tester) async {
    final permissions = FakePermissions(checkResult: ScanPermission.permanentlyDenied);
    await pumpWith(tester, permissions: permissions);
    await tester.tap(find.byType(StatusBanner));
    await tester.pumpAndSettle();
    expect(permissions.calls, contains('openSettings'));
  });

  testWidgets('Turkish banner texts', (tester) async {
    await pumpWith(tester, locale: const Locale('tr'));
    expect(find.text('Bluetooth açık ve hazır.'), findsOneWidget);
    await pumpWith(tester, locale: const Locale('tr'), bluetooth: BluetoothAvailability.off);
    expect(find.text('Bluetooth kapalı. Telefonun ayarlarından açın.'), findsOneWidget);
  });

  testWidgets('Start a search stays enabled while blocked', (tester) async {
    await pumpWith(tester, bluetooth: BluetoothAvailability.off);
    await tester.tap(find.text('Start a search'));
    await tester.pumpAndSettle();
    expect(find.byType(NewSiteScreen), findsOneWidget);
  });
```

Add the imports (`StatusBanner` comes from `beneathsos_ui`; `FakeScanner`/`FakePermissions` from `../../core/scanning/fakes.dart`; `scan_types.dart`). The existing small-phone 200 % tests now render the banner too and must still reach both actions.

- [ ] **Step 4: Run — expect RED**: `fvm flutter test test/features/home > S/t6.log 2>&1; echo exit=$?` → `exit=1` (no banner).

- [ ] **Step 5: Implement**

`lib/features/home/presentation/mixins/readiness_banner_mixin.dart`:

```dart
import 'dart:async';

import 'package:beneathsos_app/core/readiness/domain/device_readiness.dart';
import 'package:beneathsos_app/core/readiness/presentation/providers/readiness_controller.dart';
import 'package:beneathsos_app/l10n/generated/app_localizations.dart';
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';

/// What the readiness banner shows.
typedef BannerContent = ({StatusKind kind, String message, IconData? icon, VoidCallback? onTap});

/// Maps device readiness to the home banner: what happened, what to do, and the tap action.
mixin ReadinessBannerMixin {
  /// Banner content for [readiness]; actions go to [controller].
  BannerContent bannerFor(AppLocalizations l10n, DeviceReadiness readiness, ReadinessController controller) =>
      switch (readiness) {
        ReadinessChecking() => (kind: StatusKind.ready, message: l10n.readinessChecking, icon: Icons.hourglass_top_rounded, onTap: null),
        ReadinessReady() => (kind: StatusKind.ready, message: l10n.readinessReady, icon: null, onTap: null),
        ReadinessNeedsPermission() => (
          kind: StatusKind.blocked,
          message: l10n.readinessNeedsPermission,
          icon: null,
          onTap: () => unawaited(controller.requestPermission()),
        ),
        ReadinessPermissionInSettings() => (
          kind: StatusKind.blocked,
          message: l10n.readinessPermissionInSettings,
          icon: null,
          onTap: () => unawaited(controller.openSettings()),
        ),
        // iOS does not let apps switch Bluetooth on: instruction only.
        ReadinessBluetoothOff() => (kind: StatusKind.blocked, message: l10n.readinessBluetoothOff, icon: null, onTap: null),
        ReadinessUnsupported() => (kind: StatusKind.blocked, message: l10n.readinessUnsupported, icon: null, onTap: null),
      };
}
```

`lib/features/home/presentation/widgets/readiness_banner.dart`:

```dart
import 'package:beneathsos_app/core/l10n_extension.dart';
import 'package:beneathsos_app/core/readiness/presentation/providers/readiness_controller.dart';
import 'package:beneathsos_app/features/home/presentation/mixins/readiness_banner_mixin.dart';
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Whether this phone can search right now, above the home actions.
class ReadinessBanner extends ConsumerWidget with ReadinessBannerMixin {
  /// Creates the banner.
  const ReadinessBanner({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final content = bannerFor(
      context.l10n,
      ref.watch(readinessControllerProvider),
      ref.read(readinessControllerProvider.notifier),
    );
    return StatusBanner(kind: content.kind, message: content.message, icon: content.icon, onTap: content.onTap);
  }
}
```

`home_screen.dart`: insert `const ReadinessBanner(), const SizedBox(height: BeneathSpacing.m),` directly before `const HomeActions(),` (import the widget).

- [ ] **Step 6: GREEN + full checks + commit (app)**

`git commit -m "feat(home): readiness banner above the actions (Bluetooth and permission)"`.

---

### Task 7: Cards on the "being prepared" screens (app)

**Files:**
- Modify: `lib/features/sites/presentation/screens/new_site_screen.dart`, `lib/features/victim/presentation/screens/victim_screen.dart`, their tests, `CHANGELOG.md`

- [ ] **Step 1: Failing tests** — add to `new_site_screen_test.dart`:

```dart
  testWidgets('the explanation sits in a "Being prepared" card', (tester) async {
    await pumpLocalized(tester, const NewSiteScreen());
    expect(find.byType(BeneathCard), findsOneWidget);
    expect(find.text('Being prepared'), findsOneWidget);
    expect(find.byIcon(Icons.construction_rounded), findsOneWidget);
  });
```

and to `victim_screen_test.dart`:

```dart
  testWidgets('Turkish: the 112 instruction sits in a "Hazırlanıyor" card', (tester) async {
    await pumpLocalized(tester, const VictimScreen(), locale: const Locale('tr'));
    expect(find.byType(BeneathCard), findsOneWidget);
    expect(find.text('Hazırlanıyor'), findsOneWidget);
  });
```

(import `package:beneathsos_ui/beneathsos_ui.dart`). The existing 200 % portrait/landscape readability tests stay.

- [ ] **Step 2: RED** → `exit=1` (no card).

- [ ] **Step 3: Implement** — both bodies become:

```dart
    // Scrolls so large system text is never cut off (no overflow error would reveal it).
    body: SingleChildScrollView(
      child: BeneathCard(
        title: context.l10n.preparingCardTitle,
        icon: Icons.construction_rounded,
        child: Text(context.l10n.newSitePreparing, style: Theme.of(context).textTheme.bodyLarge),
      ),
    ),
```

(victim: `victimPreparing` with `headlineSmall`). Import `package:beneathsos_ui/beneathsos_ui.dart`.

`CHANGELOG.md` `[Unreleased]` → `### Added`: "- Readiness banner on the home screen: Bluetooth and permission state, live; asks for Bluetooth permission on first launch." and "- \"Being prepared\" screens show their text in a card."

- [ ] **Step 4: GREEN + full checks + commit (app)** — `git commit -m "feat(home): being-prepared screens use BeneathCard"`.

---

### Task 8: Release — package v0.2.0, app on the tag, verification, TestFlight

- [ ] **Step 1: Package release prep** — `pubspec.yaml` `version: 0.2.0`; `CHANGELOG.md` add on top:

```markdown
## 0.2.0
- `StatusBanner` (ready, attention, blocked; tappable, live region) and `BeneathCard`.
- `outlineVariant`, stable theme instances, `BeneathTokens` equality, Atkinson `primaryTextTheme`,
  24 px button icons, lock-up in brand proportions.
```

README "Rules": add "Use `StatusBanner` for state (what happened, then what to do); `blocked` (red) only when something blocks the task." Full checks; commit `chore(release): 0.2.0`; push; wait for `ci` and `goldens` on that commit (both success; fix and re-push if not); `git tag -a v0.2.0 -m "beneathsos_ui 0.2.0" && git push origin v0.2.0`; `gh release create v0.2.0 --repo Berkant35/beneathsos_ui --title "beneathsos_ui 0.2.0" --notes-file CHANGELOG.md`.

- [ ] **Step 2: App on the tag** — `pubspec.yaml` `beneathsos_ui` `ref: v0.2.0`; `fvm flutter pub get`; full checks; commit `chore(deps): beneathsos_ui v0.2.0`. Fresh clone (`git clone` the local app repo into the scratchpad, no overrides) → `fvm flutter pub get` resolves `v0.2.0` from GitHub and `fvm flutter test` exits 0.

- [ ] **Step 3: Visual verification** — iOS simulator light and dark: home (the simulator reports no Bluetooth LE, so it shows the red "unsupported" banner — expected), "New search" and "I am trapped" cards. Send the screenshots plus the `status_banners_*` and `card_*` goldens (they show the ready and Bluetooth-off banners the phone will show).

- [ ] **Step 4: Android** — `fvm flutter build apk --debug > S/apk.log 2>&1; echo exit=$?` → `exit=0`.

- [ ] **Step 5: Docs (hub)** — `docs/architecture.md`: §3 tree adds `core/readiness/` (CheckReadiness, ReadinessController) and the home banner; implementation status "App shell" row mentions the readiness banner; `docs/roadmap.md` `1.2b ✅`; `tasks/todo.md` "Done: Phase 1.2b" with test counts, build number and "On the phone: …". Commit.

- [ ] **Step 6: Publish** — push app and hub (heads equal remote); app CI green on GitHub; `ASC_KEY_ID=$ASC_KEY_ID ASC_ISSUER_ID=$ASC_ISSUER_ID tools/testflight.sh`; poll until `VALID` + `IN_BETA_TESTING`; comment on hub issue #7 with the commits and build number.
