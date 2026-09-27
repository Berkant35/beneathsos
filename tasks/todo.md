# BeneathSOS — v1 plan

Decisions: `docs/mimari-sorular.md` (answers) → `docs/architecture.md`. Rules: `CLAUDE.md`.

## M0 — Foundation (current)
- [x] Feasibility research + simulations (`docs/fizibilite-2026-09-27.md`)
- [x] Architecture questions answered (30/30)
- [x] CLAUDE.md, architecture.md, lint config, governance files, licence
- [ ] Maintainer review of CLAUDE.md + architecture.md
- [ ] Upgrade local Flutter via FVM (3.35.3 → 3.47.5 stable, Dart 3.13)
- [ ] Workspace skeleton: root pubspec (workspace + melos scripts), 4 packages + app, `tools/check_deps.dart`, `tools/check_l10n.dart`
- [ ] GitHub repo (public), ruleset applied, auto-merge off, fork workflow approval on, actions SHA-pinned

## M1 — Field test tool (answers the iOS question before building UI)
- [ ] `ble_scanner` Pigeon API + Android + iOS implementation (scan only)
- [ ] Minimal debug screen: device list, pick target, live RSSI chart, key-rotation log, CSV export
- [ ] Test: airplane-mode iPhone (Find My), Android beacon; Android vs iOS rescuer visibility
- [ ] Record results in `docs/research/field-test-01.md`

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
