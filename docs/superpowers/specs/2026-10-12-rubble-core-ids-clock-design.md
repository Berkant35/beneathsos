# Roadmap 2b — `rubble_core`: UUIDv7 identifiers and a hybrid logical clock

- Date: 2026-10-12
- Status: decided by the executor under the maintainer's standing instruction "continue"
- Builds on: [ADR 0006](../../adr/0006-drift-event-sourced-sessions.md) (events carry a device id and a
  hybrid logical clock from day one so v2 can merge sessions), `docs/architecture.md` §8

## 1. Identifiers

- **UUIDv7** (RFC 9562): 48-bit Unix milliseconds, version 7, 12-bit `rand_a`, variant `10`, 62-bit
  `rand_b`. Time-ordered, so database rows and event ids sort by creation.
- `Uuid7Generator({required int Function() nowMs, required Random random})` — the clock and the random
  source are injected (pure, deterministic in tests). **Monotonic:** within the same millisecond the
  next id uses the previous `rand_a + 1`; when `rand_a` would overflow, the timestamp advances by 1 ms.
  A clock that goes backwards never produces a smaller id (the last timestamp is kept).
- `Uuid7.parse(String)` validates the canonical lower-case form (version 7, variant `10`) and exposes
  `timestampMs`; ids compare lexicographically = chronologically.
- Typed ids as extension types over the string: `SessionId`, `EventId`, `DeviceId`, `PointId`,
  `TargetId` — a `PointId` can never be passed where a `TargetId` is expected.

## 2. Hybrid logical clock

- `HybridTimestamp(int physicalMs, int counter, DeviceId device)` — total order: physical time, then
  counter, then device id. Serialises to a fixed-width string that sorts the same way
  (`000001760000000000-0003-<device>`), and parses back.
- `HybridClock({required DeviceId device, required int Function() nowMs})`:
  - `now()` for a local event: `physical = max(last.physical, wall)`; counter resets to 0 when physical
    advanced, otherwise increments;
  - `receive(HybridTimestamp remote)` when merging another device's event: `physical = max(last, remote,
    wall)`, counter per the HLC paper (Kulkarni et al., 2014);
  - every returned timestamp is strictly greater than the previous one, even if the wall clock jumps
    backwards.

## 3. Testing

UUIDv7: version/variant bits, timestamp round-trip, monotonic within one millisecond (1000 ids in the
same ms are strictly increasing), `rand_a` overflow advances the timestamp, a backwards clock still
increases, parse rejects v4 / wrong variant / upper-case / wrong length. Typed ids do not mix (compile
check). HLC: local events strictly increase with a frozen and a backwards clock; receive from a device
ahead in time adopts its physical time; serialised strings sort like the timestamps; parse round-trip.
