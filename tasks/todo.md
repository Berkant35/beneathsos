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

## Current: Phase 2 — `rubble_core` (2a–2d)
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
- [ ] Create public repository `Berkant35/rubble_core` + tag v0.1.0 — **waits for the maintainer's yes**

**2a–2d (2026-10-12):** deferred minors from the final review — `Duration` below 1 ms is lost and
negative/oversized durations and `seq ≤ 0` are accepted; `HybridTimestamp.parse` accepts a leading
space or `+`, an empty device id does not parse back, a counter above 0xffffffff breaks the fixed
width; a negative `samples` error names `"medianDbm"`; the engine must handle measured points with
`at == null`.

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
