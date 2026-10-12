# Roadmap 2a — `rubble_core`: units and rubble geometry

- Date: 2026-10-12
- Status: decided by the executor under the maintainer's standing instruction "continue"; creating the
  public repository `Berkant35/rubble_core` waits for the maintainer's explicit yes.
- Roadmap: phase 2 split into 2a (this), 2b (UUIDv7 ids, hybrid logical clock), 2c (event types and
  JSON), 2d (session projection).
- Builds on: `CLAUDE.md` §2 (dependency rules), §4 ("units are types"), `docs/architecture.md` §2, §8

## 1. Purpose

Every later layer — drawing (phase 5), measurement (7), engine (8), map (9) — talks about lengths,
signal strength and the rubble outline. 2a gives them one vocabulary: typed units instead of bare
`double`s, and a validated rubble polygon in local metres (never latitude/longitude in v1).

## 2. Package

`packages/rubble_core` — pure Dart (no Flutter), depends only on `meta` and `collection`
(`CLAUDE.md` §2). Lints: the shared rule set plus `public_member_api_docs`. Tests: `package:test`.

## 3. Units (extension types, zero cost)

| Type | Wraps | Meaning | Operations |
|---|---|---|---|
| `Meters` | `double` | lengths and local coordinates (may be negative as a coordinate) | `+`, `-`, unary `-`, `*` / `/` by a number, `abs()`, `compareTo`, `zero` |
| `SquareMeters` | `double` | areas | `+`, `-`, `compareTo` |
| `Dbm` | `double` | received signal strength (RSSI, a mean may be fractional) | `-` → `Decibels`, `compareTo`; `isPlausible` (−127 … +20 dBm) |
| `Decibels` | `double` | a difference between two levels | `+`, `-`, `abs()` |
| `Hpa` | `double` | barometric pressure (depth is never derived from RSSI, rule 2) | `-` → `Hpa`, `compareTo` |

Extension types do **not** implement `double`, so a `Meters` can never be added to a `Dbm` or passed
where a bare `double` is expected. `.value` is the explicit way out (for maths and storage).

## 4. Geometry

- `SitePoint(Meters x, Meters y)` — a point on the site in local metres (x east, y north from an
  arbitrary origin); value equality; `distanceTo(SitePoint) → Meters`; `+`/`-` as vectors.
- `RubblePolygon` — the outline drawn by the rescuer:
  - at least 3 finite corners; no two consecutive corners closer than 0.1 m; not self-intersecting;
    at least 0.01 m² enclosed; otherwise `RubblePolygon.validate` returns a `PolygonProblem` (sealed:
    `TooFewCorners`, `NonFiniteCorner`, `CornersTooClose`, `SelfIntersecting`, `DegenerateOutline`) and the constructor throws `ArgumentError` with it;
  - `edges` (with `length`), `perimeter → Meters`, `area → SquareMeters` (shoelace, always positive),
    `contains(SitePoint)` (ray casting; points on the edge count as inside), `bounds`
    (`SiteBounds` with min/max corners), `centroid`;
  - value equality on the corner list.

## 5. Testing

Unit tests for every operation, including: units do not mix (compile-time — documented by a
commented-out line in a test file), `Dbm` difference is `Decibels`, polygon validation for each
problem, area/perimeter of a known rectangle and a concave L-shape, `contains` for inside, outside,
on-edge and concave-notch points, and a square drawn clockwise and counter-clockwise giving the same
positive area.
