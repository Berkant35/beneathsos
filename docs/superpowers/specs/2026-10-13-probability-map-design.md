# Roadmaps 8–9 — `locator_engine` and the probability map screen

- Date: 2026-10-13
- Status: decided by the executor under the maintainer's blanket approval (2026-10-13)
- Builds on: `docs/fizibilite-2026-09-27.md`, `docs/research/sim/circle_prob_sim.py` (`bayes`), hub
  `tools/sim/engine_reference.py` (golden fixtures), CLAUDE.md §1 (never a single location; no distance or
  depth from RSSI; non-detections are data), §4 (heavy math in `Isolate.run`), §7 (engine rules),
  `docs/architecture.md` §5.3 ("the probability map is the hub") and §11 rows 5 and 10

## 1. Engine (`packages/locator_engine`, pure Dart, depends on `rubble_core`)

- `estimate(outline, observations, profile) → ProbabilityMap`: 0.25 m cells inside the outline; unknowns
  marginalised (phone height 25 % / 60 % of 4 m, path-loss exponent 2 / 2.5 / 3, rubble attenuation per
  profile, common offset ±12 dB, sd 5 dB); heard: Gaussian on the median; not heard: log Φ((−100 − μ)/σ).
  Output: probabilities, 50 % / 90 % areas and thresholds.
- `suggestNextPoint(...)`: spots 1 m outside the rubble every 1 m, ≥ 2 m from measured points, scored by
  expected information (binary entropy of "heard" + heard · ½ ln(1 + Var μ / σ²)).
- `EngineProfile`: `voided_pancake@1` (2–6 dB/m), `dense@1` (5–15 dB/m). Golden fixtures within 1e-6 per
  cell and exact 50 % / 90 % areas.

## 2. Map screen (`/sites/:sessionId/map`, `features/probability_map`)

- The hub of a search once an outline, a target and one point exist. Full-width `SiteMap` with the 50 %
  region (strong) and 90 % region (light) of the selected target, measured points (heard / not heard) and
  the suggested next point.
- Under the map: "Most likely area: 4.4 m² (50 %) · 14 m² (90 %)" — areas, never a spot; "Low information:
  fewer than 3 points with a signal" when that holds (row 10); target tabs when there are several targets
  (row 5); **Measure next point** (opens measuring) and the legend.
- `probabilityMapProvider(sessionId, targetId)`: observations of that target from the measured points
  (`SignalHeard` → heard with its median, `NoSignal` → not heard), outline and the session's engine profile;
  runs `estimate` and `suggestNextPoint` in `Isolate.run`; recomputed when the session changes.
- Overview: a "See the probability map" step once a point is measured. The measuring screen shows the
  suggested point too.

## 3. Testing

Engine: fixtures, log Φ against scipy, suggestion rules. App: the provider maps readings to observations
(heard / not heard / other targets ignored / points without a position skipped); the screen shows areas,
the low-information badge, target tabs, and never a single-point claim; EN/TR, 200 % text.
