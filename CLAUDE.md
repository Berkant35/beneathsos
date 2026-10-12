# BeneathSOS — Agent & Contributor Rules

BeneathSOS helps volunteers locate phones trapped under earthquake rubble. A rescuer draws the rubble
footprint, measures the BLE RSSI of a target device at several user-placed points, and the app shows a
**probability map** (50 % / 90 % regions) plus the next best measurement point. Fully offline in v1.

Read before any work: `docs/architecture.md` (how the system is built) and
`docs/fizibilite-2026-09-27.md` (why it is built this way — physics limits, simulation results).
Plan and progress live in `tasks/todo.md` (hub); mistakes and their prevention rules in `tasks/lessons.md`.

---

## 1. Non-negotiable product rules

1. **Never claim a location.** UI, logs and docs say "probability region", "signal exit point",
   "most likely area". Never "victim is here", never a single pin without its uncertainty region.
2. **No depth, floor-count or material estimate from RSSI.** Research proved RSSI cannot separate
   distance from attenuation. Depth may only come from non-RF sources (barometer, user input) and
   must be shown as a coarse class with uncertainty.
3. **A point with no signal is data.** Non-detections are stored and fed to the engine (censored
   likelihood). Never drop them.
4. **Offline first.** No feature may require network in v1. No analytics SDK in v1.
5. **Legal disclaimer** is shown on first launch and on every export; the app supports, never
   replaces, professional search & rescue (AFAD / INSARAG procedures).

## 2. Repositories & local layout

Every package is its **own GitHub repository** (owner `Berkant35`). Locally they all live under one
folder so they can be developed together:

```
IdeaProjects/beneathsos/            Berkant35/beneathsos      hub: CLAUDE.md, docs, tools, tasks
├─ apps/beneathsos_app/             Berkant35/beneathsos_app  Flutter app — composition only
└─ packages/
   ├─ rubble_core/                  Berkant35/rubble_core     pure Dart — value types, events, projections
   ├─ locator_engine/               Berkant35/locator_engine  pure Dart — probability map, next-best-point
   ├─ ble_scanner/                  Berkant35/ble_scanner     Flutter plugin — Pigeon + Kotlin + Swift
   ├─ beneathsos_ui/                Berkant35/beneathsos_ui   Flutter — design tokens, theme, core components
   └─ rubble_canvas/                Berkant35/rubble_canvas   Flutter — drawing, zoom/pan, heatmap
```

`apps/` and `packages/` are git-ignored by the hub; each sub-folder is an independent repo.

### Dependency wiring

- `pubspec.yaml` declares sibling packages as **git dependencies** pinned to a tag
  (`git: {url: https://github.com/Berkant35/ble_scanner.git, ref: v0.1.0}`) — a fresh clone of any
  single repo resolves.
- Locally, a git-ignored **`pubspec_overrides.yaml`** points them to the sibling folders
  (`path: ../../packages/ble_scanner`). `tools/link_local.sh` (hub) creates these files.
- Releasing a package = tag it (`vX.Y.Z`, Conventional Commits → CHANGELOG), then bump the `ref`
  in dependants.

### Dependency rules (enforced by `tools/check_deps.dart` in the hub)

| Package | May depend on | Must NOT depend on |
|---|---|---|
| `rubble_core` | Dart SDK, `meta`, `collection` | Flutter, any other BeneathSOS package |
| `locator_engine` | `rubble_core` | Flutter, `ble_scanner`, `rubble_canvas` |
| `ble_scanner` | Flutter, `plugin_platform_interface` | `rubble_core` (stays reusable by others) |
| `rubble_canvas` | Flutter, `rubble_core` | `ble_scanner`, `locator_engine`, Riverpod |
| `beneathsos_ui` | Flutter | Riverpod, go_router, any other BeneathSOS package |
| `beneathsos_app` | everything above | — |

## 3. Toolchain & commands

- Flutter is pinned with **FVM** (`.fvmrc` in every repo, same version). Always `fvm flutter` / `fvm dart`.
- Per repo: `fvm dart format --set-exit-if-changed .`, `fvm flutter analyze --fatal-infos`,
  `fvm flutter test`. Code generation: `fvm dart run build_runner build` (never with
  `--delete-conflicting-outputs`).
- Across all repos (from the hub): `tools/dev.sh analyze|format|test|check` runs the command in
  every repo and fails on the first error. `check` = dependency rules + l10n completeness.

A task is **not done** until format, analyze, test and `tools/dev.sh check` pass in every touched repo.

## 4. Architecture rules (app)

- **Feature-first, layered inside.** `lib/features/<feature>/{domain,data,presentation}`;
  `presentation/{screens,widgets,mixins,providers}`. Cross-feature code goes to `lib/core/`.
- **State management: Riverpod 3 + `riverpod_generator`.** No `setState` for business state,
  no `ChangeNotifier`, no global singletons outside `core/services`.
- **Routing: `go_router` with typed routes (`go_router_builder`).** Never `Navigator.push` with
  a raw `MaterialPageRoute`; never string paths outside `core/router/`.
- **Persistence: Drift (SQLite).** Sessions are **event-sourced**: every user action is an
  immutable event appended in the same transaction it happens; UI state is a projection
  (`rubble_core`). Raw RSSI samples go to a separate batched table.
- **Hardware only through `core/services`.** BLE, sensors (accelerometer, barometer), haptics,
  permissions, wakelock are wrapped in service classes exposed via providers. Features never import
  `ble_scanner`, `sensors_plus` etc. directly.
- **Heavy math off the UI isolate.** Engine calls go through `Isolate.run` in a provider.
- **Units are types.** Use `rubble_core` extension types (`Meters`, `Dbm`, `Hpa`) in APIs; no bare
  `double` for physical quantities in public signatures. Site coordinates are local meters, never
  lat/long in v1.
- **State machines are sealed classes** + exhaustive `switch`. No boolean flag soup
  (`isLoading && !hasError && ...`).

### Layer responsibilities (SOLID / clean architecture)

| Layer | Contains | Must not contain |
|---|---|---|
| `presentation/providers` (Notifiers) | Call a use case, map its result to UI state, wire streams/lifecycle | Business rules, `if` chains of preconditions, platform quirks |
| `domain/` | Use cases (`StartScan`), pure rule classes (`DeviceTracker`), result types, **ports** (abstract interfaces: `ScannerPort`, `PermissionPort`) | Flutter, Riverpod, plugins, `dart:io` |
| `data/` + `core/services` | Port implementations, platform quirks (e.g. iOS reporting `unknown` before CoreBluetooth is ready) | UI state, business decisions |

- **Thin notifiers.** A notifier method is: call → map → assign `state`. Size limits: notifier
  ≤ ~100 lines, any method ≤ ~30 lines; exceed → extract a use case or domain class.
- **Open for extension.** New preconditions/rules are new classes added to a list (e.g. a
  `ScanPrecondition`), not new `if`s inside an existing method.
- **Depend on ports.** Domain code depends on abstract ports; providers bind the concrete
  implementation. Tests replace ports, not plugins.
- **Lifecycle is owned by the consumer.** `app.dart` never calls into features. A notifier that must
  react to app lifecycle (e.g. re-check permissions after returning from Settings) listens to
  `appLifecycleProvider` (`core/services`, wraps `AppLifecycleListener`) inside its own `build()`,
  and only acts when it is in a blocked state.

## 5. Code rules (strict — reviewed on every PR)

1. **Screens ≤ ~200 lines**, orchestration only (lifecycle, state routing). UI parts live in
   `widgets/`, one responsibility per widget, one public widget per file (no `_Private` widgets
   shared across files — make them public in their own file).
2. **Widget logic → mixin.** Formatting, mapping, list building, calculations go to
   `features/<f>/presentation/mixins/<name>_mixin.dart`. Stateful: `mixin XMixin on ConsumerState<X>`;
   stateless: plain `mixin XMixin` with `context`/`ref` passed as parameters. `ref.watch` stays in
   `build`, results are passed to mixin functions.
3. **`AppScaffold` for screens** (`core/widgets/app_scaffold.dart`). Raw `Scaffold` only for
   full-bleed screens (the map canvas, victim mode, camera/AR later) — say why in a comment.
4. **Zero hard-coded user-facing strings.** Flutter `gen-l10n` with ARB files
   (`apps/beneathsos/lib/l10n/app_en.arb`, `app_tr.arb`). Every new key is added to **both** in the
   same change. If you see a hard-coded string in a file you touch, fix it.
5. **Touched file = leave it better.** If a file you edit breaks a rule above, refactor it in the
   same change (and verify).
6. **No `print`**; use the `core/logging` logger. No `// ignore:` without a reason comment.
7. **Tests with every change:** domain & engine code needs unit tests; providers need tests with
   overrides; custom painters need golden tests.

### Good / bad examples

```dart
// BAD — raw double, meaning and unit unclear
double distance(double rssi) => pow(10, (-59 - rssi) / 25).toDouble();

// GOOD — typed units; and we never convert RSSI to a distance in the app anyway
Meters span(SitePoint a, SitePoint b) => a.distanceTo(b);
```

```dart
// BAD — logic and hard-coded text inside build
@override
Widget build(BuildContext context) {
  final label = samples.isEmpty ? 'Sinyal yok' : '${samples.median} dBm';
  return Text(label);
}

// GOOD — logic in mixin, text from ARB
class PointSummaryTile extends ConsumerWidget with PointSummaryTileMixin {
  const PointSummaryTile({required this.point, super.key});
  final MeasurementPoint point;

  @override
  Widget build(BuildContext context, WidgetRef ref) =>
      Text(summaryLabel(context.l10n, point));
}
```

```dart
// BAD — boolean flags
bool isMeasuring = false; bool hasError = false; bool isDone = false;

// GOOD — sealed state + exhaustive switch
sealed class MeasurementState {}
final class Idle extends MeasurementState {}
final class Collecting extends MeasurementState { Collecting(this.remaining); final Duration remaining; }
final class Completed extends MeasurementState { Completed(this.summary); final PointSummary summary; }

Widget body(MeasurementState s) => switch (s) {
  Idle() => const StartButton(),
  Collecting(:final remaining) => CountdownRing(remaining: remaining),
  Completed(:final summary) => SummaryCard(summary: summary),
};
```

```dart
// BAD — feature imports the plugin directly
import 'package:ble_scanner/ble_scanner.dart';

// GOOD — feature depends on the service provider
final samples = ref.watch(scanSamplesProvider);
```

```dart
// BAD — fire-and-forget future, silent failure
db.appendEvent(event);

// GOOD — awaited, or explicitly unawaited with a reason
await sessionRepository.append(event);
```

## 6. Lints

Root `analysis_options.yaml` = `package:flutter_lints/flutter.yaml` (Flutter's recommended set) +
strict analyzer modes (`strict-casts`, `strict-inference`, `strict-raw-types`) + extra rules listed
there + `riverpod_lint` plugin. Packages add `public_member_api_docs`. CI runs
`dart analyze --fatal-infos`: **infos are failures**. Do not weaken rules to make CI pass.

## 7. Engine rules (`locator_engine`)

- Pure, deterministic functions. Same input → same output (seeded RNG only in tests).
- Every model change must keep the golden fixtures from `tools/sim/` passing within tolerance, or
  update both the Python reference and fixtures in the same PR with a written justification.
- Engine parameters live in versioned JSON profiles (`voided_pancake@1`, `dense@1`). Never inline
  magic numbers.

## 8. Git, PRs, security

- Conventional Commits (`feat(engine): ...`, `fix(ble): ...`); versions and CHANGELOGs derive from them.
- `main` and `release/*` rulesets (`.github/rulesets/`): no force push, deletion or merge commits for
  anyone (linear history); contributors change them only through PRs with green CI; **no auto-merge**. While the project has one maintainer,
  the maintainer (admin) may push directly — never force-push or rewrite `main` history.
- Never commit secrets, keystores, `.env`, signing files. Never add network calls or telemetry.
- GitHub Actions: `pull_request` trigger only (never `pull_request_target`), `permissions:
  contents: read` by default, actions pinned to commit SHA.
- Docs are part of the change: update `docs/architecture.md` when a boundary, event type, route or
  table changes.

## 9. Working rules for Claude

- Non-trivial task (3+ steps) → plan in `tasks/todo.md` first; mark progress; add a review section.
- After any correction from the maintainer → add the pattern to `tasks/lessons.md`.
- Verify before claiming done: run the commands in §3 and show the result.
- **TestFlight after every app change.** When a commit in `beneathsos_app` touches `lib/`, `ios/`,
  `android/` or `pubspec.*`, push it and run `tools/testflight.sh` (see the app README); report the
  build number and processing state. Docs-only commits are not uploaded.
- Language: code, comments, docs, commits in **English**; conversation with the maintainer in Turkish.
