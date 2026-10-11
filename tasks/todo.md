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

## Current: Phase 0.1 — remove field-test UI, keep domain logic
- [x] Agree the exact delete / keep / move list with the maintainer
- [x] Apply, verify (analyze, tests), walk through the diff
- [ ] Maintainer review → commit

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

## Backlog
- [x] NDK 28.2.13676358 installed manually (sdkmanager download kept dying on a flaky connection;
      resumable `curl -C -` + unzip). Back on `flutter.ndkVersion`. Note: `path_provider_android`
      → `jni` compiles C code, so the NDK version *does* matter for dependencies.
- [ ] `permission_handler` pinned to ^12.0.3 (Android impl 13.0.1, compileSdk 35). 13.x → android 14.x
      needs compileSdk 37; AGP 9.1.0 looks for platform `android-37` but the SDK installs `android-37.0`.
      Unpin when Flutter's template ships an AGP that resolves `android-37.0` (verify, then bump).
- [ ] Consider dropping `permission_handler`: let `ble_scanner` request its own Android runtime
      permissions (it already declares them) — one less third-party dependency.
