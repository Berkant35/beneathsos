# BeneathSOS — Roadmap to v1

BeneathSOS is an open-source, offline mobile app that helps volunteers estimate **where** a phone
trapped under earthquake rubble most likely is — shown as a probability map, never as a false
certainty. This roadmap is public so contributors, partners and supporters can see what is done,
what is next and why.

**How we work:** every phase is split into small steps. Each step is explained, agreed, implemented,
reviewed and verified before the next one starts. Every step ends with green CI and updated docs.

Status legend: ✅ done · 🔄 in progress · ⏳ planned

---

## Done so far

| | Milestone | Evidence |
|---|---|---|
| ✅ | Feasibility research: physics limits, prior art, platform limits | `docs/fizibilite-2026-09-27.md`, `docs/research/` |
| ✅ | Simulations: why "4 circles" fails as a point estimate and works as a probability map | `docs/research/sim/` |
| ✅ | Architecture decisions and contributor rules | `docs/architecture.md`, `CLAUDE.md` |
| ✅ | `ble_scanner` plugin (Android + iOS, raw RSSI, batched) | `packages/ble_scanner` |
| ✅ | Field test: an Android phone detects an **app-less iPhone in airplane mode** via its Find My beacon | `docs/research/field-test-01.md` |

---

## Phase 0 — Clean foundation ⏳
Turn the field-test prototype into a clean base.

| Step | What |
|---|---|
| 0.1 | Remove the field-test UI; keep and relocate the useful domain logic (device classification, RSSI statistics, device tracking, identity-rotation detection and relink suggestions) |
| 0.2 | Clean layering: ports + use cases + pure domain classes, thin notifiers (see `CLAUDE.md` §4) |
| 0.3 | Documentation baseline: per-repo README, decision records (`docs/adr/`), code of conduct, changelogs, API docs |
| 0.4 | Public GitHub: repositories, branch protection, project board with one issue per roadmap step, CI badges, first tagged releases |

## Phase 1 — Design system ⏳
Professional, calm and legible under stress, dust and sunlight; accessible (contrast, large touch
targets, screen readers).

| Step | What |
|---|---|
| 1.1 | Design principles and brand: name treatment, logo, colour palette (outdoor high contrast, light/dark), typography, iconography, tone of voice (TR + EN) |
| 1.2 | Design tokens and the `beneathsos_ui` package: colours, spacing, typography, motion, core components (scaffold, buttons, cards, countdown ring, status banners) |
| 1.3 | Component catalogue (Widgetbook) published so anyone can browse the UI kit |
| 1.4 | Flow mockups for the rescuer and victim journeys, reviewed before any screen is built |

## Phase 2 — `rubble_core` package ⏳
Pure Dart: unit types (`Meters`, `Dbm`), rubble geometry (polygon, points), event types, identifiers.

## Phase 3 — Persistence ⏳
Drift database: sessions, append-only event log, raw RSSI samples. A session survives the app being
killed.

## Phase 4 — Entry flow ⏳
Home (two large buttons: *I am trapped* / *I am searching*), first-run onboarding (disclaimer,
permissions), rubble site list and creation.

## Phase 5 — Rubble drawing (`rubble_canvas` package) ⏳
Metric canvas, polygon drawing with edge lengths, pinch-zoom and pan, placing measurement points.

## Phase 6 — Target selection ⏳
30-second ambient scan (blacklist surface devices), candidate ranking (Find My, stationary, weak),
"hold your phone next to it" proximity pick, identity-rotation countdown with animated warnings and
relink.

## Phase 7 — Measurement ⏳
15-second point measurement with countdown and stillness check; "no signal" is recorded as data.

## Phase 8 — `locator_engine` package ⏳
Probability-map engine matching the Python reference simulation: 50 % / 90 % regions, next best
measurement point. Golden tests against the reference.

## Phase 9 — Probability map screen ⏳
Heatmap, uncertainty regions, target tabs, suggested next point — the end-to-end rescuer journey.

## Phase 10 — Victim mode ⏳
*I am trapped*: beacon advertising (Android background, iOS foreground), SOS sound, guidance.

## Phase 11 — Export and research mode ⏳
Session export, ground-truth entry and error reports, raw CSV — ready for field campaigns with
training rubble sites.

## Phase 12 — Release ⏳
Store readiness, privacy review, first public release.

---

## Not in v1 (planned)
Multi-rescuer shared workspace (QR), opt-in analytics, AR positioning, barometric depth, acoustic
last-metre search, professional (AFAD) mode.
