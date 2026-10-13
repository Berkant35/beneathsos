# BeneathSOS — Roadmap to v1

BeneathSOS is an open-source, offline mobile app that helps volunteers estimate **where** a phone
trapped under earthquake rubble most likely is — shown as a probability map, never as a false
certainty. This roadmap is public so contributors, partners and supporters can see what is done,
what is next and why.

**Tracking:** every step is a GitHub issue, every phase a
[milestone](https://github.com/Berkant35/beneathsos/milestones). Looking for a place to help? See
[`good first issue`](https://github.com/Berkant35/beneathsos/labels/good%20first%20issue) and
[`help wanted`](https://github.com/Berkant35/beneathsos/labels/help%20wanted).

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

## Phase 1 — Design system 🔄
Professional, calm and legible under stress, dust and sunlight; accessible (contrast, large touch
targets, screen readers).

| Step | What |
|---|---|
| 1.1 ✅ | Design principles and brand: name treatment, logo, colour palette (outdoor high contrast, light/dark), typography, iconography, tone of voice (TR + EN) — [`docs/design/`](design/principles.md), [`docs/brand/`](brand/README.md), [ADR 0017](adr/0017-visual-identity.md) |
| 1.2a ✅ | Design tokens, light/dark theme, Atkinson font, logo, primary and secondary buttons in `beneathsos_ui`; branded home screen with "Start a search" and "I am trapped" |
| 1.2b ✅ | Status banners and cards; live Bluetooth/permission readiness banner on the home screen |
| 1.2c ✅ | Countdown ring; `AppScaffold` moves into `beneathsos_ui` (`BeneathScaffold`) |
| 1.3 ✅ | Component catalogue (Widgetbook) published so anyone can browse the UI kit — live at <https://berkant35.github.io/beneathsos_ui/>, built without a CDN and deployed from `main` by CI |
| 1.4 🔄 | Flow mockups for the rescuer and victim journeys, reviewed before any screen is built — 7 screens ready for the maintainer's review (`beneathsos_ui/widgetbook`, Flows) |

## Phase 2 — `rubble_core` package ✅ ([v0.1.0](https://github.com/Berkant35/rubble_core/releases/tag/v0.1.0))
Pure Dart: unit types (`Meters`, `Dbm`), rubble geometry (polygon, points), event types, identifiers.

| Step | What |
|---|---|
| 2a ✅ | Typed units and rubble geometry in local metres |
| 2b ✅ | UUIDv7 identifiers, hybrid logical clock (restart-safe with `last:`) |
| 2c ✅ | Event types (v1) and their strict JSON (`EventEnvelope`, schema 1) |
| 2d ✅ | Session projection from events (idempotent, hybrid-clock order) |

## Phase 3 — Persistence ✅
Drift database: sessions, append-only event log, raw RSSI samples. A session survives the app being
killed. Visible: the preview journey records a practice search; after a restart the home screen offers
"Continue the search" / "Finish this search".

## Phase 4 — Entry flow ✅
Home (two large buttons: *I am trapped* / *Start a search*), disclaimer on the first search (permissions
stay on the home screen, decided in 1.2b), list of real searches, new search, search overview with the
steps of the flow. Practice with sample data keeps the preview journey.

## Phase 5 — Rubble drawing (`rubble_canvas` package) ✅ ([v0.1.0](https://github.com/Berkant35/rubble_canvas/releases/tag/v0.1.0))
Metric canvas, polygon drawing with edge lengths, pinch-zoom and pan; one real side corrects the scale.
Placing measurement points moves to phase 7 (measurement).

## Phase 6 — Target selection ✅
30-second surface scan (phones heard strongly set aside), candidate ranking (Find My, still, weak) with
plain-language reasons, "hold a rescuer's phone next to yours" exclusion. The identity-rotation countdown
and relink move to phase 7, where a target is followed for minutes.

## Phase 7 — Measurement ✅
15-second point measurement with countdown and stillness check; "no signal" is recorded as data.

## Phase 8 — `locator_engine` package ✅ ([v0.1.0](https://github.com/Berkant35/locator_engine/releases/tag/v0.1.0))
Probability-map engine matching the Python reference simulation: 50 % / 90 % regions, next best
measurement point. Golden tests against the reference.

## Phase 9 — Probability map screen ✅
Heatmap, uncertainty regions, target tabs, suggested next point — the end-to-end rescuer journey.

## Phase 10 — Victim mode ✅
*I am trapped*: beacon advertising (Android background, iOS foreground), SOS sound, guidance.

## Phase 11 — Export and research mode ✅
Session export, ground-truth entry and error reports, raw CSV — ready for field campaigns with
training rubble sites.

## Phase 12 — Release 🔄
Store readiness, privacy review, first public release. Prepared: privacy manifest and policy
([`privacy.md`](privacy.md)), store texts ([`store/listing.md`](store/listing.md)), Android release signing,
the maintainer's checklist ([`releasing.md`](releasing.md)). Store submission is the maintainer's step.

---

## Not in v1 (planned)
Multi-rescuer shared workspace (QR), opt-in analytics, AR positioning, barometric depth, acoustic
last-metre search, professional (AFAD) mode.
