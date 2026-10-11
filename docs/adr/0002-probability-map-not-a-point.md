# 0002. Show a probability map, never a point; no depth or material from RSSI

- Status: Accepted
- Date: 2026-09-27

## Context

The original idea: four rescuers stand around the rubble, each phone measures the Bluetooth signal
strength (RSSI) of a buried phone, each RSSI is converted to a distance, four circles are drawn and
their intersection is "where the victim is" — and the weakness of the signal tells how deep and
through which materials.

We tested this against published measurements and our own simulations (`docs/fizibilite-2026-09-27.md`,
`docs/research/`):

- **Rubble swallows most of the signal.** Phone-to-phone BLE tolerates roughly 45–55 dB of loss beyond
  1 m. A single reinforced-concrete slab costs 13–40 dB; NIST measured 60–80+ dB of extra loss through
  collapsed buildings (below 1.8 GHz; no published 2.4 GHz rubble data exists).
- **RSSI cannot separate distance from attenuation.** One number mixes path length, material loss,
  body loss (0–20 dB), device differences (±10–15 dB) and channel differences (up to 15 dB), with
  shadowing noise of σ 6–14 dB. Depth information is a ~3 dB effect inside that noise.
- **Converting RSSI to metres fails.** In a 12 × 10 m, 4–5 storey pancake-collapse simulation, circles
  from the free-space formula missed by 8–11 m — worse than always guessing the centre of the
  building (~4 m).
- **Material or layer count is not recoverable.** A Bayes-optimal classifier on RSSI reached 47.1 %
  accuracy — exactly the "always guess the most common class" baseline.
- **The same measurements work as a probability map.** Treating each reading as a likelihood band
  (unknown attenuation, path-loss exponent and offset marginalised), and treating a point with **no
  signal** as information too, gives useful prioritisation in voided rubble:

  | Measurement points (voided rubble) | Median error | 90 % region / footprint | Victim in the most likely 25 % |
  |---|---|---|---|
  | 4 corners | 2.4 m | 29 % | 80 % |
  | 8 perimeter points | 1.4 m | 14 % | 98 % |
  | 12 perimeter points | 1.4 m | 10 % | 99 % |

  These numbers come from a model of the same family as the estimator, with an assumed attenuation
  range, so they are optimistic until calibrated with field measurements.

## Decision

1. The app shows a **probability map** with 50 % and 90 % regions and the most informative next
   measurement point — never a single "victim is here" pin.
2. Points where nothing was heard are stored and used (censored likelihood).
3. The app never estimates depth, number of floors or material from RSSI. Depth may only come from
   non-radio sources (e.g. barometer, user input) and is shown as a coarse class with uncertainty.
4. The UI and documentation use wording such as "most likely area" and "signal exit point".
   This is a product rule in `CLAUDE.md` §1.

## Alternatives

- **Circle intersection (trilateration) with a free-space formula** — rejected: 8–11 m error, worse
  than no measurement.
- **Point estimate with an uncertainty radius** — rejected: a single centre invites digging at one spot
  and hides multi-modal or skewed uncertainty.
- **RSSI-based depth or material classes** — rejected: no information beyond chance in our simulation
  and no published validation.

## Consequences

- More measurement points matter more than a better formula; the UI suggests where to measure next.
- The engine is heavier (grid likelihood, marginalisation) and runs off the UI isolate.
- Results depend on the attenuation prior. Field measurements at training rubble sites are required
  to calibrate it, and claims stay modest until then.
- Store reviews and partners see no unverifiable accuracy claims.

## References

- `docs/fizibilite-2026-09-27.md` — feasibility study and both simulation summaries.
- `docs/research/sim/rssi_sim.py`, `docs/research/sim/circle_prob_sim.py` and their outputs.
- NIST TN 1540–1542 (radio propagation in building collapse); ITU-R P.2040.
