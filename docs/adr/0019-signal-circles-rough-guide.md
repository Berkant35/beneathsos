# ADR 0019 — Signal circles as a switchable rough guide

- Status: accepted (maintainer, 2026-10-13)
- Amends: CLAUDE.md §1 rule 2; ADR 0002 (probability map, not a point)

## Context
In two field tests the maintainer could not read the probability map alone: they expected, around every
measured point, a circle sized by the signal, in its own colour, and the place where the circles meet
with a distance in metres — the way a rescuer reasons. The feasibility study found free-space circles
8–11 m off, against 1.2–2.4 m for the probability map.

## Decision
- A **signal circles** layer, on by default, switchable on the map and while measuring.
- Radius: the distance at which a signal crossing the engine profile's typical rubble all the way (middle
  path-loss exponent and attenuation) arrives at the measured median — not free space, which draws circles
  3–4 times too large.
- Where they meet: the spot inside the rubble outline with the least Σ (distance − radius)²; a dashed line
  with its length from the nearest measured point.
- Always labelled "rough guide"; the probability map, its 50 % / 90 % areas and the likely spot stay.

## Consequences
The rescuer gets the picture they expect; the text keeps saying it is rough. Field data (export + record
found) will show how far the meeting point and the likely spot are from where phones are found.
