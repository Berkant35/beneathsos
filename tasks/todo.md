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

## M1 — Field test tool (answers the iOS question before building UI)
- [x] `ble_scanner` Pigeon API + Android (Kotlin, throttle-safe single scan) + iOS (Swift) — Dart tests green, analyze clean
- [x] App skeleton per architecture (Riverpod 3, typed go_router, gen-l10n en+tr, AppScaffold, services)
- [x] Field test feature: device list + filters, target marking, live RSSI chart, identity timer (10/13 min), identity log, relink suggestions, CSV recording + markers + share — 13 tests green
- [ ] Native builds verified (Android APK, iOS device install)
- [ ] Test: airplane-mode iPhone (Find My), Android beacon; Android vs iOS rescuer visibility
- [ ] Run protocol `docs/research/field-test-01.md` and record results

## M2 — Core + engine
- [ ] `rubble_core`: value types, geometry, events, projection, UUIDv7, HLC
- [ ] `locator_engine`: grid likelihood (censored), marginalisation, HPD, next-best-point, profiles
- [ ] `tools/sim/export_fixtures.py` + golden tests

## M3 — Rescuer flow
- [ ] Drift schema + event store + sample batching
- [ ] Onboarding (disclaimer, units, scale), sites, rubble drawing (`rubble_canvas`: pinch/zoom/pan, edge lengths, structure annotations)
- [ ] Ambient scan blacklist (30 s)
- [ ] Target picker + relink + rotation timer with animated warnings
- [ ] Measurement state machine (15 s, stillness check)
- [ ] Probability map hub: heatmap, 50/90 contours, target tabs sorted by promise, next point
- [ ] Export + research mode

## M4 — Victim mode (simple)
- [ ] Home two buttons, advertising (Android FGS + manufacturer data, iOS foreground), SOS sound, guidance

## Review
_(filled after each milestone)_
