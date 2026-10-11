# 0008. Pure-Dart probability engine with a Python reference simulation

- Status: Accepted (implementation planned in roadmap phase 8)
- Date: 2026-09-27

## Context

The probability map ([0002](0002-probability-map-not-a-point.md)) evaluates a likelihood on a
0.25 m grid over the site, marginalising unknown attenuation, path-loss exponent, offset and height
— a few thousand cells times a few hundred parameter combinations per update. The model was first
built and evaluated in Python (numpy/scipy) during the feasibility study. The engine must be
deterministic, testable without a device, and reusable outside the app.

## Decision

- `locator_engine` is a **pure Dart** package (no Flutter), run in a background isolate
  (`Isolate.run`) by the app.
- The Python simulation in `tools/sim` is the **reference**: it exports golden fixtures, and the Dart
  engine must match them within a tolerance. A model change updates both, with a written reason.
- Model parameters live in versioned JSON profiles (`voided_pancake@1`, `dense@1`), not in code.

## Alternatives

- **Native code via FFI (C/Rust)** — faster, but two more toolchains and harder contributions; not
  needed at this grid size.
- **Port Python logic without a reference** — no way to tell whether the port is correct.
- **Run the model on a server** — breaks the offline-first rule.

## Consequences

- Two implementations to keep in sync; golden tests make drift visible.
- Researchers can change the model in Python first and compare.
- Performance must be measured on low-end Android phones before the map screen ships.

## References

- `docs/research/sim/circle_prob_sim.py`; `CLAUDE.md` §7.
