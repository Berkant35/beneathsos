# Roadmap 2d — `rubble_core`: session projection

- Date: 2026-10-12
- Status: decided by the executor under the maintainer's standing instruction "continue"
- Builds on: 2c events, [ADR 0006](../../adr/0006-drift-event-sourced-sessions.md) ("UI state is a
  projection of the event log")

## 1. Purpose

The app never stores screen state; it replays the session's events into a `SessionState`. 2d is that
replay: a pure function, deterministic, safe to run again and again.

## 2. Decisions

- `SessionProjection.replay(Iterable<EventEnvelope>) → SessionState` sorts by hybrid timestamp, then
  `seq`, then event id (a total order, so ties are deterministic) and folds `SessionProjection.apply(SessionState, EventEnvelope)` over them. The order of the
  input list does not matter, so logs merged from several devices (v2) give the same state.
- **Idempotent:** an event id already applied is ignored (`appliedIds`), so replaying a log twice or
  receiving a duplicate does not double-count.
- `SessionState` (immutable): `title`, `engineProfile`, `outline` (`RubblePolygon?`), `scale` (factor,
  default 1), `structures`, `blacklist` (set of peripheral keys), `targets` (by `TargetId`: current
  peripheral key, label — null when known only from a relink — and identity history), `points` (by
  `PointId`: `at`, `readings`, `discardedReadings`, `status`: `placed` / `measured` / `discarded`), `groundTruths`, `closed`, `appliedIds`.
- **Rules:** a relink or a new selection changes the target's current key; the previous key and the
  relink's `from` both join the history, so no identity is ever lost; a measurement for an unknown
  point is kept as a point without a position (`at: null`) rather than dropped (rule 3: no data is
  lost); a discard moves the point's readings to `discardedReadings` (kept for the record, never sent
  to the engine) and a later measurement starts fresh; placing a point at a new position sets its
  readings aside the same way (they were heard elsewhere); state lists are unmodifiable; events after `SessionClosed` are still applied
  (late events from other devices in v2) and `closed` stays true.

## 3. Testing

A full rescuer session replays into the expected state; shuffled input gives the same state as sorted
input; a duplicated event is applied once; relink updates the key and history; discard excludes the
point from `measuredPoints` but keeps its readings; a measurement before its point is placed is kept;
non-detections stay in the readings; blacklist edits add and remove; two devices apply in clock order
not `seq` order; equal clock and `seq` are ordered by id; discard then re-measure and move then
re-measure never mix in set-aside readings; concurrent relinks keep every key.

`apply` alone equals `replay` only while events arrive in sorted order; a late event with an older
timestamp (merged logs, v2) needs a full `replay`.
