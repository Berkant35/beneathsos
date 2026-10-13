# BeneathSOS — v1 plan

Decisions: `docs/mimari-sorular.md` (answers) → `docs/architecture.md`. Rules: `CLAUDE.md`.

## M0 — Foundation (current)
- [x] Feasibility research + simulations (`docs/fizibilite-2026-09-27.md`)
- [x] Architecture questions answered (30/30)
- [x] CLAUDE.md, architecture.md, lint config, governance files, licence
- [ ] Maintainer review of CLAUDE.md + architecture.md
- [x] Decisions: separate repos under one local folder, git deps + `pubspec_overrides.yaml`, English docs, owner Berkant35
- [x] Upgrade local Flutter via FVM (3.35.3 → 3.47.5 stable, Dart 3.13)
- [x] Hub tools: `tools/link_local.sh`, `tools/dev.sh`, `tools/sync_governance.sh`
- [ ] Hub tools: `tools/check_deps.dart`, `tools/check_l10n.dart`
- [ ] GitHub repos (public, Berkant35): ruleset applied, auto-merge off, fork workflow approval on, actions SHA-pinned

## Roadmap
Public roadmap: `docs/roadmap.md` (phases 0–12). This file tracks the **current step** in detail.

## Done: Phase 0.1 — remove field-test UI, keep domain logic
- [x] Agree the exact delete / keep / move list with the maintainer
- [x] Apply, verify (analyze, tests), walk through the diff
- [x] Maintainer review → commit

## Done: Phase 0.2 — thin notifiers
- [x] 0.2a scanning: ports + StartScan/StopScan + preconditions + availability policy; services implement
      ports; ScanController 156 → 85 lines; 39 tests (app `refactor(scanning)` commit)
- [x] 0.2b targets: pure `DeviceTracker` + `TrackerPolicy` (forget after 30 s, log cap 500); `DeviceTable` (130) →
      `TrackedDevices` (46); 52 tests (app `refactor(targets)` commit)

## Current: Phase 0.3–0.4 — documentation and public GitHub
- [x] 0.3 ADRs 0001–0016, architecture rewritten to "as built", README, Code of Conduct, CHANGELOG
- [x] 0.4 Soft branch protection (rulesets on main + release/*), private vulnerability reporting,
      app v0.1.0 tag + GitHub release, 13 milestones + 24 issues in the hub
- [ ] 0.4 GitHub Projects board (needs `gh auth refresh -s project` by the maintainer)

## Review
**0.1 (2026-10-10):** field-test UI removed (28 files, ~1,100 lines). Kept and moved with git history:
targets domain (classify, tracking, presence, relink, stats) → `features/targets/domain/`,
`DeviceTable` → `features/targets/presentation/providers/`, `ScanController` → `core/scanning/`.
Placeholder `HomeScreen` behind `HomeRoute('/')`; ARB trimmed to 3 keys (en + tr).
Dropped `path_provider` + `share_plus` → `jni` / NDK native build gone from the dependency tree.
Verified: format ✓, analyze --fatal-infos ✓, 15/15 tests ✓, iOS simulator shows the placeholder.

## Done: TestFlight pipeline (2026-10-11)
- [x] Bundle ID `org.beneathsos.app` registered; App Store Connect app 6821632633 (SKU beneathsos-ios)
- [x] `tools/testflight.sh` (API-key signing, no Xcode login) — 0.1.0 (4) uploaded, VALID
- [x] Internal TestFlight group "Core team" (all builds), maintainer invited
- [ ] GitHub Actions: TestFlight on tag (store ASC key as repository secret)

## Done: Phase 1.1 — design principles and brand (2026-10-11)
Spec `docs/superpowers/specs/2026-10-11-brand-and-design-principles-design.md`, plan
`docs/superpowers/plans/2026-10-11-brand-and-design-principles.md` (8 tasks, executed inline).
- [x] Hub: `tools/brand/` (palette, contrast, symbol, wordmark, assets, `build.py`) — 16 tests incl.
      contrast table, 16 px legibility, iOS tinted / Android monochrome layers
- [x] Hub: `docs/brand/` (generated SVG/PNG masters, Atkinson font + OFL, README), ADR 0017,
      `docs/design/` (principles, voice and tone + TR/EN glossary, accessibility + PR checklist)
- [x] App + plugin: PR template links the accessibility checklist
- [x] App: icon (iOS light/dark/tinted, Android adaptive + themed) and launch screen
      (`flutter_launcher_icons`, `flutter_native_splash`); 52/52 tests, analyze clean
- [x] Verified: iOS simulator launch screen light `#F5F6F9` / dark `#0C111D` (pixel-sampled),
      home-screen icon; Android debug APK; TestFlight 0.1.0 (13)

### Review
**1.1 (2026-10-11):** Rulings — `flutter_launcher_icons` rewrote a boolean Xcode setting
(`ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS`) to `AppIcon`; reverted to `YES`,
iOS build clean. iOS 26 home-screen icon style is a user setting, so the dark/tinted icons were
verified in the compiled asset catalog (47 dark + 45 tintable renditions), and on the phone via
TestFlight. Open: the app body still uses Material's default seed colour — brand theme arrives
with `beneathsos_ui` tokens (1.2).

## Done: Phase 1.2a — beneathsos_ui tokens, theme and branded home (2026-10-12)
Spec `docs/superpowers/specs/2026-10-11-beneathsos-ui-theme-design.md`, plan
`docs/superpowers/plans/2026-10-11-beneathsos-ui-theme.md` (12 tasks, inline, final review by a fresh reviewer).
- [x] Hub: static Atkinson weights from `tools/brand` (25 tests), ADR 0018, architecture, roadmap 1.2a/b/c
- [x] Package `beneathsos_ui` v0.1.0 (public, rulesets, release): colours + contrast table, typography,
      spacing/sizes/motion, `BeneathTokens`, `BeneathTheme` light/dark, `BeneathLogo`, `PrimaryButton`,
      `SecondaryButton`; 44 tests incl. 6 goldens (Linux skips, macOS workflow runs them, 0.5 % tolerance)
- [x] App: theme from the package, branded home, `/sites/new` and `/victim` "being prepared" screens
      (victim says call 112), en + tr; 75 tests; TestFlight 0.1.0 (19) VALID
- [x] Final review fixes: 112 text clipped at 200 % landscape (now scrolls), Back target 48 → 56,
      dark-theme wiring test, architecture tree

On the phone: new home screen (logo, navy/orange, Atkinson, "Start a search", "I am trapped",
independence note, "Powered by Socrepho") in light and dark; both buttons open "being prepared" screens.
Not yet: real search flow, banners, cards, countdown ring (1.2b–c).

### Review
**1.2a (2026-10-12):** deferred minors from the final review — lock-up proportions vs brand source,
`outlineVariant`, `primaryTextTheme` Roboto, `BeneathTokens` ==/hashCode, 24 px button icons, golden
helper should throw when MaterialIcons is missing, spec §7 golden wording, `rubble_canvas` CLAUDE.md row
may list `beneathsos_ui`.

## Done: Phase 1.2b — status banner, card and device readiness (2026-10-12)
Spec `docs/superpowers/specs/2026-10-12-status-banner-and-card-design.md`, plan
`docs/superpowers/plans/2026-10-12-status-banner-and-card.md` (8 tasks, inline, final review by a fresh reviewer).
- [x] `beneathsos_ui` v0.2.1: `StatusBanner` (ready / attention / blocked, tappable, live region),
      `BeneathCard`, outlineVariant, stable themes, 24 px icons, brand lock-up; 70 tests incl. goldens
- [x] App: `CheckReadiness` (scan preconditions without scanning), `ReadinessController` (asks once per
      session, re-checks on Bluetooth changes and on resume when blocked, latest check wins, failures
      shown and re-tried), readiness banner on home, cards on being-prepared screens, en + tr; 107 tests
- [x] Final review fixes: no endless "Checking…" on a platform error, no false "ready" while the iOS
      permission prompt is open, one permission dialog at a time, screen readers hear only the new message
- [x] TestFlight 0.1.0 (25) VALID; Android debug APK; fresh clone resolves `v0.2.1`

On the phone: a banner above the buttons — "Bluetooth is on and ready."; it turns red when Bluetooth is
switched off and back when on; the being-prepared screens show a card; on a fresh install the Bluetooth
permission is asked at first launch. Not yet: countdown ring (1.2c), real search flow (phase 4).

### Review
**1.2b (2026-10-12):** deferred minors — impossible precondition results map to Ready; 0.5 % golden
tolerance can miss tiny glyphs; home 200 % tests use the short message only; card title header
semantics; `bannerFor` is a ~40-line mapping table.

## Done: Phase 1.2c — countdown ring and BeneathScaffold (2026-10-12)
Spec `docs/superpowers/specs/2026-10-12-countdown-ring-and-scaffold-design.md` (decided by the executor
under "continue until I say stop"), plan `docs/superpowers/plans/2026-10-12-countdown-ring-and-scaffold.md`.
- [x] `beneathsos_ui` v0.3.1: `CountdownRing` (primary arc, fixed-size tabular number, number only with
      reduce motion), `BeneathScaffold` (moved from the app), card titles are headings (plain cards only);
      87 tests incl. goldens
- [x] App: all screens on `BeneathScaffold`, home headline is a heading, impossible readiness results →
      "could not check"; 109 tests; TestFlight 0.1.0 (28)

On the phone: no visible change except screen-reader headings; the ring first appears in phase 7
(measurement) and in the 1.3 catalogue.

### Review
**1.2c (2026-10-12):** open question for the maintainer — with "reduce motion" the ring hides its arc
(spec reading of `accessibility.md`), although the ring never animates; keep it or show the stepped arc?
Deferred minors: scaffold padding test half is empty; `readinessFor` is `@visibleForTesting` (injecting
preconditions would fit "depend on ports" better).

## Current: Phase 1.3 — component catalogue (Widgetbook)
Spec `docs/superpowers/specs/2026-10-12-widgetbook-catalogue-design.md`, plan
`docs/superpowers/plans/2026-10-12-widgetbook-catalogue.md`.
- [x] `beneathsos_ui/widgetbook/`: 9 components, 21 use cases, light/dark, text scale 1–2, viewports,
      reduce-motion knob; test opens every use case in both themes (43 tests); `catalogue.yml` builds the
      web catalogue in CI (green)
- [ ] Publish to GitHub Pages — **waits for the maintainer's yes** (repository setting + public site)
- [x] Review fixes: `.pubignore` kept `build/` in the publish archive (71 MB → 256 KB); catalogue uses the
      package's full lint set; missing button use cases (47 catalogue tests)
- [ ] Before Pages: build with `--no-web-resources-cdn` (no Google CDN requests), `--base-href /beneathsos_ui/`,
      real README / title / brand colours in `web/`, custom home instead of Widgetbook's marketing page
- [ ] Deferred minors: 200 % pass in the catalogue test; coverage list derived from exports; typography labels
      from tokens; palette swatches (spec) vs theme roles; reduce motion as an addon; nested `.fvmrc`;
      Dependabot entry for `widgetbook/`

## Done: Phase 2 — `rubble_core` (2a–2d), v0.1.0 (2026-10-12)
Specs `docs/superpowers/specs/2026-10-12-rubble-core-{units-geometry,ids-clock,events,projection}-design.md`.
- [x] `packages/rubble_core` (pure Dart): `Meters`, `SquareMeters`, `Dbm`, `Decibels`, `Hpa` extension types
      (mixing units does not compile — verified); `SitePoint`, `RubblePolygon` (validation, perimeter, area,
      bounds, centroid, contains); 19 tests; analyze/format clean
- [x] Shared CI template: actions pinned to commit SHAs; dart tools for pure Dart packages (green in app,
      ble_scanner, beneathsos_ui)
- [x] 2b: monotonic `Uuid7Generator` (injected clock/random), typed ids (`SessionId`, `EventId`, `DeviceId`,
      `PointId`, `TargetId` — mixing does not compile), `HybridClock` / `HybridTimestamp` (sortable text); 31 tests
- [x] 2c: sealed `SessionEvent` (13 types) + `EventEnvelope` (schema 1) with strict JSON (`FormatException`
      naming the field); `NoSignal` round-trips as data
- [x] 2d: `SessionProjection.replay` / `apply` → immutable `SessionState`; idempotent, hybrid-clock order
      (two-device test), unknown-point measurements kept; 62 tests; mutations on ordering and duplicate
      guard are caught
- [x] Final review (opus, fresh) of 2a–2d: 1 critical + 7 important fixed, each RED→GREEN, suite 75/75 —
      clock seed after restart (`HybridClock(last:)`), discard/move set readings aside, id tie-break,
      finite numbers only, degenerate outline rejected, unmodifiable state lists, no lost identities
- [ ] Phase 3 must seed `HybridClock(last:)` with the greatest stored hlc at startup
- [x] `tools/dev.sh check` existed only on paper: `tools/check` (Dart, 8 tests, own CI workflow) now
      enforces the dependency table of `CLAUDE.md` §2 (unknown repos fail, so a new repo needs a rule)
      and EN/TR ARB key parity with no empty strings; `dev.sh` uses dart tools for pure Dart repos
- [x] Public repository `Berkant35/rubble_core`, rulesets, private vulnerability reporting, CI green,
      tag + release v0.1.0 (2026-10-12); resolves as a git dependency from a clean project

**2a–2d (2026-10-12):** deferred minors from the final review — `Duration` below 1 ms is lost and
negative/oversized durations and `seq ≤ 0` are accepted; `HybridTimestamp.parse` accepts a leading
space or `+`, an empty device id does not parse back, a counter above 0xffffffff breaks the fixed
width; a negative `samples` error names `"medianDbm"`; the engine must handle measured points with
`at == null`.

## Done: Phase 3 — persistence (2026-10-12)
Spec `docs/superpowers/specs/2026-10-12-persistence-design.md`, plan `docs/superpowers/plans/2026-10-12-persistence.md`.
- [x] Drift schema (append-only trigger, FKs, WAL, repeatable onCreate); `SessionStore` port +
      `DriftSessionStore` (atomic create, per-device seq in a transaction, device id, clock seeded with
      `MAX(hlc)`), watch / latest open / samples; `UnreadableEvent`
- [x] Preview journey records a practice search; home "last search" card (Continue / Finish with
      confirmation); TestFlight 37 (+ review fixes build)
- [x] Final review (opus): 4 important + 1 upgraded minor fixed RED→GREEN; suite 152/152

**Phase 3 (2026-10-12):** deferred minors from the final review — a second `DriftSessionStore` on the
same database keeps its own clock (read the device's `MAX(hlc)` inside the append transaction);
`INSERT OR REPLACE`/`DELETE` on events are not blocked; double taps can record two steps; "Discard
this point" adds a new point instead of discarding the last one; card says only "started HH:mm" for
an earlier day and ignores the 24-hour setting; practice title is stored localised; `finishSearch`
writes from a widget mixin (move to a notifier with the real-search flow); home layout jumps when the
card appears and may push "I am trapped" below the fold on a 375×667 phone; no WAL / dark-mode card
tests.

## Done: Phase 4 — entry flow (2026-10-12)
Spec `docs/superpowers/specs/2026-10-12-entry-flow-design.md`, plan `docs/superpowers/plans/2026-10-12-entry-flow.md`.
- [x] Settings store; disclaimer once before the rescuer flow (async gate, `from`), victim mode never
      gated; searches list (open first), new search (1–80 characters, double tap → one), overview
      with the flow's steps and Finish; practice with sample data; home card opens real searches
- [x] Final review (opus): 4 important fixed RED→GREEN (false "could not be opened" flash, silent
      failures, racy gate, blank overview on error) + 2 minors (core/disclaimer, TR "Tamamlandı");
      suite 177/177; TestFlight 41 and the review-fix build

**Phase 4 (2026-10-12):** deferred minors from the final review — `watchSearches` replays every
search on every change (switch to aggregated counts before phase 7 adds many events); finished or
unreadable searches still list steps as "Coming in the next update"; "next update" wording vs "no
promises"; glossary "enkaz alanı" vs "Alanın adı"; load-failed texts say what happened but not what to
do; primary actions ("New search", "Create search") at the top, not in the thumb zone; rune count vs
grapheme `maxLength`; practice path asks "I understand" twice and Back from practice skips the list;
tests for dark mode on new screens and an 80-character name.

## Done: Phase 5 — rubble drawing (2026-10-13)
Spec `docs/superpowers/specs/2026-10-13-rubble-drawing-design.md`.
- [x] `packages/rubble_canvas` (local repo): `CanvasGeometry`, `OutlineDraft` (undo, validation),
      `OutlineEditor`, `EdgePicker`, painters + goldens; 28 tests
- [x] App `features/site_drawing`: draw screen (summary, Undo / Clear / Outline done, Back guard), scale
      step (side, real length, tape / steps / estimate, unusual-factor confirmation); overview shows the
      area; 197 tests (app commits local, not pushed — the git dependency needs the public repo)
- [x] Final review (opus): 1 critical (pinch near a corner moved it) + 5 important fixed RED→GREEN
- [x] Public repository `Berkant35/rubble_canvas` (rulesets, private vulnerability reporting, CI and
      goldens green), tag + release v0.1.0; app pushed, CI green, TestFlight uploaded

**Phase 5 (2026-10-13):** deferred minors from the final review — a tap during a fling adds a corner
far away (stop the inertia on pointer-down); highlighted side is 2.4:1 on the light surface (add a
non-colour cue or a darker shade); canvas labels ignore the system text size; the grid stays in drawn
metres once a scale is set, and a redrawn outline inherits the old factor; finished searches are only
hidden from the draw/scale routes, not blocked; repaint cost (no RepaintBoundary, NumberFormat per
label per frame, `RubbleCanvasStyle` without `==`); golden tolerance 0.5 % could miss a small label;
goldens use fixed colours, not the app theme; no tests for the save-failure snackbar, comma input in
the widget, or an existing-scale path.

## Done: Phase 6 — target selection (2026-10-13)
Spec `docs/superpowers/specs/2026-10-13-target-selection-design.md`.
- [x] Surface scan (30 s, −80 dBm median / 3 readings), candidates ranked with reasons, exclude / track;
      overview steps open both; 208 tests; pushed; TestFlight
- [x] Final review (opus): 2 critical + 6 important fixed RED→GREEN (Undo and a "Set aside" list with Put
      back; honest "heard only a few times" reason; recorded surface scan via rubble_core 0.2.0
      `lastSurfaceScan` and a stale-scan warning; very-strong wording; stable card order; one choice at
      a time; foreground-only countdown; start/stop race); suite 222/222; rubble_core and rubble_canvas
      0.2.0 released

**Phase 6 (2026-10-13):** deferred minors — median/spread recomputed for every device on every batch on
the UI isolate; `AmbientSaving` shows an empty body; Track and Exclude look alike (both secondary);
two targets of the same type ("Unknown device") cannot be told apart on the overview; spec field
`onSurfaceList` not implemented (named `surface`); tests for leaving the surface scan early and for
ambient → targets scan continuity.

## Done: Phase 7 — measurement (2026-10-13)
Spec `docs/superpowers/specs/2026-10-13-measurement-design.md`.
- [x] Measure screen (SiteMap from rubble_canvas 0.2.0): tap the spot, Measure here, 15 still seconds while
      scanning (MotionPort / sensors_plus), SignalHeard / NoSignal per target, raw readings stored; discard,
      interrupted, relink question with Yes / No; overview step opens it
- [x] Final review (opus): 1 critical (false "not heard" with Bluetooth off) + 4 important fixed RED→GREEN;
      suite 237/237

**Phase 7 (2026-10-13):** deferred minors — the map margin is fixed at 5 m and has no zoom or distance-to-wall
aid (a rescuer 8 m out can only tap the 5 m edge); the controller is ~200 lines (split the relink and
cleanup parts); samples and the completion event are not one transaction; no message when the phone has
no motion sensor; a screen reader cannot place a point (no semantic action on the map); widget tests for
the relink banner and for several targets.

## Done: Phases 8–9 — `locator_engine` and the probability map (2026-10-13)
Spec `docs/superpowers/specs/2026-10-13-probability-map-design.md`.
- [x] `locator_engine` v0.1.0 → v0.1.1 (public repo): Bayesian grid matching the Python reference, regions
      by count, next point by mutual information, profile validation, speed budget on flat maps
- [x] `rubble_canvas` v0.3.0: `HeatLayer` with per-cell regions, suggested point
- [x] App: `/sites/:sessionId/map` (areas, low information, target tabs, legend, Measure next point),
      engine in `Isolate.run`, suggestion on the measuring screen; TestFlight 50 and 51
- [x] Final review (opus): 0 critical, 5 important fixed RED→GREEN (legend in dark mode, same-spot
      repeats, points on the rubble, reruns for unchanged readings, speed); suite 260/260

**Phases 8–9 (2026-10-13):** deferred minors — the suggestion ring stays on the old spot while the map
recomputes, and the measuring screen suggests for the first target only; the map screen shows
"Calculating…" instead of the previous map while recomputing; the legend does not explain filled vs hollow
dots and the ring shares the region colour; `HeatLayer` has no `==` and paints one rectangle per cell
(merge runs); `EngineProfile` exposes bare doubles; `next_point.dart`/`link.dart` constants are not in the
profile; `EngineProfile.fromJson` throws `TypeError` on a missing key and `ProbabilityMap` does not check
lengths; the map's screen-reader label omits the suggestion and the areas are read twice; the overview's
"Open the probability map" condition is inline in `site_screen.dart` (move to the mixin, make it a step).

## Done: Phase 10 — victim mode (2026-10-13)
Spec `docs/superpowers/specs/2026-10-13-victim-mode-design.md`.
- [x] `ble_scanner` v0.2.0 → v0.2.1: one-service advertiser (Android legacy advert + scan response, iOS
      CBPeripheralManager), service data on scan samples
- [x] `/victim`: beacon with id, battery, liveness; SOS sound; always dark; Back confirmation
- [x] Rescuers: `trappedBeacon` first, never set aside, battery and last touch on the card
- [x] Final review (opus): 1 critical + 6 important — fixed RED→GREEN (confirmed start, Bluetooth / access
      changes while calling out, retries, late start after leaving, beacons without id, dark screen, alarm
      stream) ; suite 297/297; TestFlight 52, 53, 54

Rulings (phase 10): payload refresh stays stop + start (Android `AdvertisingSet.setAdvertisingData` would
update in place) — a failure is retried within a minute; cost if wrong: a gap of up to a minute.
"Moved or touched" instead of separate bits — cost: shaking rubble reads as a sign of life, now worded so.

**Phase 10 (2026-10-13):** deferred minors — no Android foreground service (advertising stops when the
app is closed) and no dimming / flashlight; adapter state is emitted by both iOS managers (duplicates);
`advertisingSupported` is hard-coded on iOS; no `StopBeacon` use case (the notifier stops the port
directly); 112 is text only (a `tel:112` button would work offline); the accelerometer runs at UI rate;
native code is compiled, not unit-tested.

## Done: Phase 11 — export and research mode (2026-10-13)
Spec `docs/superpowers/specs/2026-10-13-export-research-design.md`.
- [x] Export: disclaimer first, JSON + CSV to the share sheet, non-target keys coded in both files
- [x] Research: record where the phone was found (confirmed), found cross (`rubble_canvas` v0.4.0), report
- [x] Final review (opus): 1 critical (bystander MACs in the JSON) + 7 important fixed RED→GREEN; suite
      307/307; TestFlight 57, 58

Rulings (phase 11): an unreadable event keeps its row but not its text (privacy over completeness) — cost:
a researcher cannot recover that one payload. The export is built on the UI isolate with memoized hashes
(no `Isolate.run`) — cost: a short pause on very large searches.

**Phase 11 (2026-10-13):** deferred minors — share_plus temp files are not deleted after sharing; the HLC
device suffix links exports from one phone; a screen reader cannot place the found spot (double tap = map
centre); the found report uses the current map, not the one at the time; no `GroundTruthCleared` (record
again to move it); the share popover is not anchored on iPad.

## Current: Phase 12 — release (2026-10-13)
- [x] iOS privacy manifest (no tracking, nothing collected) bundled; Android release signing from a
      git-ignored `key.properties`
- [x] `docs/privacy.md` (EN/TR), `docs/store/listing.md`, `docs/releasing.md`
- [ ] Maintainer: TestFlight walk-through, screenshots, App Store submission, Play upload key + upload
- [ ] Widgetbook catalogue on GitHub Pages (phase 1.3 leftovers first)

## Backlog
- [ ] Brand toolkit: test the tinted grayscale conversion step itself and the generated Android
      monochrome resources (only the source assets are tested today)
- [ ] `tools/brand/brandkit/render.py`: remove the temp file when `rsvg-convert` fails (try/finally)
- [ ] Future plans: use `$ASC_KEY_ID` / `$ASC_ISSUER_ID` placeholders, not the real identifiers
- [x] NDK 28.2.13676358 installed manually (sdkmanager download kept dying on a flaky connection;
      resumable `curl -C -` + unzip). Back on `flutter.ndkVersion`. Note: `path_provider_android`
      → `jni` compiles C code, so the NDK version *does* matter for dependencies.
- [ ] `permission_handler` pinned to ^12.0.3 (Android impl 13.0.1, compileSdk 35). 13.x → android 14.x
      needs compileSdk 37; AGP 9.1.0 looks for platform `android-37` but the SDK installs `android-37.0`.
      Unpin when Flutter's template ships an AGP that resolves `android-37.0` (verify, then bump).
- [ ] Consider dropping `permission_handler`: let `ble_scanner` request its own Android runtime
      permissions (it already declares them) — one less third-party dependency.
