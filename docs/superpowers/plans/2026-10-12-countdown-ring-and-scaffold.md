# 1.2c — Countdown Ring and BeneathScaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `CountdownRing` and `BeneathScaffold` to `beneathsos_ui` 0.3.0, move the app onto `BeneathScaffold`, and fold in the 1.2b minors that touch the same files.

**Architecture:** A stateless ring widget with a custom painter driven by the caller (`total`, `remaining`); `AppScaffold` moves into the package as `BeneathScaffold` with unchanged behaviour.

**Tech Stack:** Flutter 3.47.5 (FVM), flutter_test (widget + golden), Riverpod 3 (app), gen-l10n.

**Spec:** `docs/superpowers/specs/2026-10-12-countdown-ring-and-scaffold-design.md`

## Global Constraints

- Commit only when format, `analyze --fatal-infos` and tests exit 0 by their own exit codes.
- Ring arc colour is `colorScheme.primary` (never the accent: orange on light is 2.4 < 3); track `outlineVariant`; centre text `onSurface` in `BeneathTokens.numeric`.
- Reduce motion → no arc, number only. Semantics = the app's label only, not a live region.
- `beneathsos_ui` depends on Flutter only; public members documented.
- Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

- **200 % text inside the ring:** the number must shrink to fit, never overflow the circle — pinned in Task 1.
- **Time running past zero or a zero total:** no negative numbers, no division by zero — pinned in Task 1.
- **Screen readers:** the ring is one label, never announced every second — pinned in Task 1.
- **App screens after the scaffold move:** no app bar on home, titles on the others, padding unchanged — pinned by the existing app tests in Task 3.
- **Longest Turkish blocked message at 200 % on a small phone:** actions still reachable — pinned in Task 3.

---

### Task 1: `CountdownRing` (package)

**Files:** Create `lib/src/widgets/countdown_ring.dart`, `test/widgets/countdown_ring_test.dart`, `test/widgets/countdown_ring_golden_test.dart`; modify `lib/beneathsos_ui.dart`.

**Produces:** `CountdownRing({required Duration total, required Duration remaining, required String semanticLabel, double size = 160})`, `static String CountdownRing.centreText(Duration remaining)`, `CountdownRingPainter({required double fraction, required Color track, required Color arc, required bool showArc, required double strokeWidth})`.

- [ ] **Step 1: Failing tests** (`countdown_ring_test.dart`):

```dart
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

Widget _frame(Widget child, {Brightness brightness = Brightness.light, bool reduceMotion = false, double textScale = 1}) =>
    MaterialApp(
      theme: brightness == Brightness.light ? BeneathTheme.light() : BeneathTheme.dark(),
      home: Builder(
        builder: (context) => MediaQuery(
          data: MediaQuery.of(context).copyWith(disableAnimations: reduceMotion, textScaler: TextScaler.linear(textScale)),
          child: Scaffold(body: Center(child: child)),
        ),
      ),
    );

CountdownRingPainter _painter(WidgetTester tester) => tester
    .widgetList<CustomPaint>(find.descendant(of: find.byType(CountdownRing), matching: find.byType(CustomPaint)))
    .map((paint) => paint.painter)
    .whereType<CountdownRingPainter>()
    .single;

Widget _ring(Duration remaining, {Duration total = const Duration(seconds: 15)}) =>
    CountdownRing(total: total, remaining: remaining, semanticLabel: 'time left');

void main() {
  test('centre text: seconds under a minute, m:ss above, rounded up', () {
    expect(CountdownRing.centreText(const Duration(seconds: 15)), '15');
    expect(CountdownRing.centreText(const Duration(milliseconds: 7500)), '8');
    expect(CountdownRing.centreText(Duration.zero), '0');
    expect(CountdownRing.centreText(const Duration(seconds: 60)), '1:00');
    expect(CountdownRing.centreText(const Duration(minutes: 13, seconds: 5)), '13:05');
    expect(CountdownRing.centreText(const Duration(seconds: -3)), '0');
  });

  testWidgets('full, half and empty fractions; arc in primary, track in outlineVariant', (tester) async {
    await tester.pumpWidget(_frame(_ring(const Duration(seconds: 15))));
    expect(_painter(tester).fraction, 1);
    expect(_painter(tester).arc, BeneathColors.primaryLight);
    expect(_painter(tester).track, BeneathColors.outlineVariantLight);
    await tester.pumpWidget(_frame(_ring(const Duration(milliseconds: 7500))));
    expect(_painter(tester).fraction, 0.5);
    await tester.pumpWidget(_frame(_ring(Duration.zero)));
    expect(_painter(tester).fraction, 0);
  });

  testWidgets('clamps past zero and above total; a zero total does not divide by zero', (tester) async {
    await tester.pumpWidget(_frame(_ring(const Duration(seconds: -2))));
    expect(_painter(tester).fraction, 0);
    await tester.pumpWidget(_frame(_ring(const Duration(seconds: 20))));
    expect(_painter(tester).fraction, 1);
    await tester.pumpWidget(_frame(_ring(const Duration(seconds: 1), total: Duration.zero)));
    expect(_painter(tester).fraction, 0);
  });

  testWidgets('dark theme arc is the dark primary', (tester) async {
    await tester.pumpWidget(_frame(_ring(const Duration(seconds: 10)), brightness: Brightness.dark));
    expect(_painter(tester).arc, BeneathColors.primaryDark);
  });

  testWidgets('reduce motion: number only, no arc', (tester) async {
    await tester.pumpWidget(_frame(_ring(const Duration(seconds: 10)), reduceMotion: true));
    expect(_painter(tester).showArc, isFalse);
    expect(find.text('10'), findsOneWidget);
  });

  testWidgets('screen readers hear one label and it is not a live region', (tester) async {
    final handle = tester.ensureSemantics();
    await tester.pumpWidget(_frame(_ring(const Duration(seconds: 12))));
    expect(tester.getSemantics(find.byType(CountdownRing)), isSemantics(label: 'time left', isLiveRegion: false));
    handle.dispose();
  });

  testWidgets('200 % text: the number shrinks to fit inside the ring', (tester) async {
    await tester.pumpWidget(_frame(_ring(const Duration(minutes: 13, seconds: 5), total: const Duration(minutes: 15)), textScale: 2));
    expect(tester.takeException(), isNull);
    final ring = tester.getRect(find.byType(CountdownRing));
    final text = tester.getRect(find.text('13:05'));
    expect(ring.contains(text.topLeft) && ring.contains(text.bottomRight), isTrue);
  });
}
```

Goldens (`countdown_ring_golden_test.dart`, tag golden, light and dark): a row of three rings — 15/15 s, 7.5/15 s, and 7.5/15 s under `MediaQuery(disableAnimations: true)` — file `goldens/countdown_ring_${brightness.name}.png`, using `goldenFrame` and `loadBeneathFont`.

- [ ] **Step 2: RED** — compile errors (`CountdownRing` undefined).
- [ ] **Step 3: Implement** `lib/src/widgets/countdown_ring.dart`:

```dart
import 'dart:math' as math;

import 'package:beneathsos_ui/src/theme/beneath_tokens.dart';
import 'package:flutter/material.dart';

/// A countdown: progress arc for the remaining time and the time in the middle. The caller rebuilds
/// it as time passes (it never animates on its own). With "reduce motion" only the number is shown.
class CountdownRing extends StatelessWidget {
  /// Creates a ring. [semanticLabel] is localised by the app (e.g. "12 seconds left").
  const CountdownRing({
    required this.total,
    required this.remaining,
    required this.semanticLabel,
    this.size = 160,
    super.key,
  });

  /// Full duration.
  final Duration total;

  /// Time left (clamped to 0…[total]).
  final Duration remaining;

  /// What screen readers say; not a live region — the app decides when to announce.
  final String semanticLabel;

  /// Diameter.
  final double size;

  /// `12` under a minute, `13:05` from a minute; rounded up, never negative.
  static String centreText(Duration remaining) {
    final seconds = remaining.isNegative ? 0 : (remaining.inMilliseconds / 1000).ceil();
    if (seconds < 60) return '$seconds';
    return '${seconds ~/ 60}:${(seconds % 60).toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final totalMs = total.inMilliseconds;
    final fraction = totalMs <= 0 ? 0.0 : (remaining.inMilliseconds / totalMs).clamp(0.0, 1.0);
    final style = BeneathTokens.of(context).numeric.copyWith(color: scheme.onSurface, fontSize: size * 0.28);
    return Semantics(
      label: semanticLabel,
      excludeSemantics: true,
      child: SizedBox.square(
        dimension: size,
        child: CustomPaint(
          painter: CountdownRingPainter(
            fraction: fraction,
            track: scheme.outlineVariant,
            arc: scheme.primary,
            showArc: !MediaQuery.disableAnimationsOf(context),
            strokeWidth: size * 12 / 160,
          ),
          child: Padding(
            padding: EdgeInsets.all(size * 0.2),
            child: Center(
              child: FittedBox(fit: BoxFit.scaleDown, child: Text(centreText(remaining), style: style)),
            ),
          ),
        ),
      ),
    );
  }
}

/// Paints the track circle and, unless [showArc] is false, the remaining-time arc from 12 o'clock.
class CountdownRingPainter extends CustomPainter {
  /// Creates the painter.
  const CountdownRingPainter({
    required this.fraction,
    required this.track,
    required this.arc,
    required this.showArc,
    required this.strokeWidth,
  });

  /// Remaining fraction, 0…1.
  final double fraction;

  /// Track colour.
  final Color track;

  /// Arc colour.
  final Color arc;

  /// Whether the arc is drawn (false with "reduce motion").
  final bool showArc;

  /// Stroke width of track and arc.
  final double strokeWidth;

  @override
  void paint(Canvas canvas, Size size) {
    final rect = (Offset.zero & size).deflate(strokeWidth / 2);
    final stroke = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth;
    canvas.drawOval(rect, stroke..color = track);
    if (showArc && fraction > 0) {
      canvas.drawArc(rect, -math.pi / 2, 2 * math.pi * fraction, false, stroke
        ..color = arc
        ..strokeCap = StrokeCap.round);
    }
  }

  @override
  bool shouldRepaint(CountdownRingPainter oldDelegate) =>
      oldDelegate.fraction != fraction ||
      oldDelegate.track != track ||
      oldDelegate.arc != arc ||
      oldDelegate.showArc != showArc ||
      oldDelegate.strokeWidth != strokeWidth;
}
```

Export from `lib/beneathsos_ui.dart`.

- [ ] **Step 4: GREEN; goldens RED (missing) → create → inspect; full checks; commit** `feat(widgets): CountdownRing with goldens`.

### Task 2: `BeneathScaffold` + card title header (package)

**Files:** Create `lib/src/widgets/beneath_scaffold.dart`, `test/widgets/beneath_scaffold_test.dart`; modify `lib/src/widgets/beneath_card.dart`, `test/widgets/beneath_card_test.dart`, `lib/beneathsos_ui.dart`.

- [ ] **Step 1: Failing tests** — `beneath_scaffold_test.dart`:

```dart
import 'package:beneathsos_ui/beneathsos_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

Widget _app(Widget home, {double width = 375}) => MaterialApp(
  theme: BeneathTheme.light(),
  home: MediaQuery(data: MediaQueryData(size: Size(width, 800)), child: home),
);

void main() {
  testWidgets('without a title there is no app bar', (tester) async {
    await tester.pumpWidget(_app(const BeneathScaffold(body: Text('body'))));
    expect(find.byType(AppBar), findsNothing);
    expect(find.text('body'), findsOneWidget);
  });

  testWidgets('with a title the app bar shows it', (tester) async {
    await tester.pumpWidget(_app(const BeneathScaffold(title: 'Title', body: Text('body'))));
    expect(find.widgetWithText(AppBar, 'Title'), findsOneWidget);
  });

  testWidgets('page padding is 16 on phones and none when not padded', (tester) async {
    await tester.pumpWidget(_app(const BeneathScaffold(body: Text('body'))));
    expect(tester.getTopLeft(find.text('body')).dx, greaterThanOrEqualTo(16));
    await tester.pumpWidget(_app(const BeneathScaffold(padded: false, body: Text('body'))));
    expect(find.byType(Padding).evaluate().where((e) => (e.widget as Padding).padding == const EdgeInsets.all(16)), isEmpty);
  });
}
```

Add to `beneath_card_test.dart`:

```dart
  testWidgets('the title is a heading for screen readers', (tester) async {
    final handle = tester.ensureSemantics();
    await tester.pumpWidget(_frame(const BeneathCard(title: 'Being prepared', child: Text('Body'))));
    expect(tester.getSemantics(find.text('Being prepared')), isSemantics(label: 'Being prepared', isHeader: true));
    handle.dispose();
  });
```

- [ ] **Step 2: RED.**
- [ ] **Step 3: Implement** — `beneath_scaffold.dart` is the app's `AppScaffold` (1.2a version) renamed `BeneathScaffold`, importing `BeneathSpacing` from `../tokens/spacing.dart`, with the doc comment "Standard screen frame … Use a raw `Scaffold` only for full-bleed screens and say why." In `BeneathCard` wrap the title `Text` in `Semantics(header: true, child: …)`. Export.
- [ ] **Step 4: GREEN, full checks, commit** `feat(widgets): BeneathScaffold; card titles are headings`.

### Task 3: App on `BeneathScaffold` + minors (app, local package via override)

**Files:** Delete `lib/core/widgets/app_scaffold.dart` and `test/core/widgets/app_scaffold_test.dart`; modify every screen using `AppScaffold`, `home_screen.dart` (headline header), `check_readiness.dart` (+ public `@visibleForTesting static DeviceReadiness readinessFor(StartScanResult)`), tests.

- [ ] **Step 1: Failing tests**
  - `check_readiness_test.dart`: `expect(CheckReadiness.readinessFor(const ScanStarted()), isA<ReadinessFailed>()); expect(CheckReadiness.readinessFor(const StartFailed('x')), isA<ReadinessFailed>());`
  - `home_screen_test.dart`: headline header — `isSemantics(label: 'Search for a phone under rubble', isHeader: true)`; Checking state — `pumpWith(tester, bluetooth: BluetoothAvailability.unknown)` shows `Checking Bluetooth…` and `Icons.hourglass_top_rounded`; Turkish unsupported at 200 % on a small phone — no exception, `Aramayı başlat` and `Enkaz altındayım` reachable (`_expectReachable`).
- [ ] **Step 2: RED.**
- [ ] **Step 3: Implement** — replace `AppScaffold(` with `BeneathScaffold(` and its import with `package:beneathsos_ui/beneathsos_ui.dart` in all screens; delete the old file and its test (the package now owns those tests); `Semantics(header: true, child: Text(l10n.homeHeadline, …))`; rename `_readiness` to public `readinessFor` with `@visibleForTesting` and map `ScanStarted() || StartFailed() => const ReadinessFailed()`. Update `CLAUDE.md` §5.3 ("`BeneathScaffold` for screens (`beneathsos_ui`)") and `docs/architecture.md` §3 (remove `widgets/ AppScaffold`).
- [ ] **Step 4: GREEN, full checks, commit (app and hub).**

### Task 4: Release

- [ ] Package `version: 0.3.0`, CHANGELOG `## 0.3.0` ("`CountdownRing`; `BeneathScaffold` (moved from the app); card titles are headings"), commit, push, green `ci` + `goldens`, tag `v0.3.0`, release.
- [ ] App `ref: v0.3.0`, checks, commit, fresh clone (pub get + tests), APK, push, app CI green, TestFlight → `VALID`.
- [ ] Hub: roadmap `1.2c ✅`, `docs/architecture.md` design-system row `v0.3.0`, `tasks/todo.md` "Done: Phase 1.2c", close issue #7 (1.2 complete) with links; commit, push.
- [ ] Final whole-change review by a fresh reviewer; fix Critical/Important with tests; minors to todo.
