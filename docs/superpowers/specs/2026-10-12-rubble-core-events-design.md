# Roadmap 2c — `rubble_core`: session events (v1) and their JSON

- Date: 2026-10-12
- Status: decided by the executor under the maintainer's standing instruction "continue"; payloads
  are minimal and versioned so phases 4–11 can extend them without breaking stored sessions
- Builds on: `docs/architecture.md` §8 (event list, `events` table), [ADR 0006](../../adr/0006-drift-event-sourced-sessions.md),
  product rules 1–3 (`CLAUDE.md` §1)

## 1. Envelope

`EventEnvelope { EventId id, SessionId session, int seq, HybridTimestamp hlc, SessionEvent event }` —
`seq` counts from 1 per session and device; the `hlc` carries the device id. JSON:
`{"schema": 1, "id", "session", "seq", "hlc": "<serialised>", "type", "payload": {…}}`.

## 2. Events (sealed `SessionEvent`, exhaustive `switch`)

| Type | Payload | Notes |
|---|---|---|
| `SiteCreated` | `title`, `engineProfile` (e.g. `voided_pancake@1`) | |
| `RubblePolygonSet` | `RubblePolygon` (corners in metres) | replaces the previous outline |
| `ScaleSet` | `factor` (> 0), `ScaleSource` (`steps`, `tape`, `estimate`) | multiplies drawn lengths |
| `StructureAnnotated` | `StructureKind` (`pancake`, `voids`, `dense`), `at` (`SitePoint`) | feeds the engine profile |
| `AmbientScanCompleted` | `blacklisted` (peripheral keys), `duration` | surface phones, never targets |
| `BlacklistEdited` | `added`, `removed` (peripheral keys) | |
| `TargetSelected` | `TargetId`, `peripheralKey`, `label` | a target is a device, never a person |
| `TargetRelinked` | `TargetId`, `from`, `to` (peripheral keys) | identity rotation (architecture §11) |
| `MeasurementPointPlaced` | `PointId`, `at` (`SitePoint`) | |
| `MeasurementCompleted` | `PointId`, `duration`, `readings`: per target `SignalHeard(TargetId, median: Dbm, samples)` or `NoSignal(TargetId)` | rule 3: "no signal" is stored as data |
| `MeasurementDiscarded` | `PointId`, `DiscardReason` (`userDiscarded`, `moved`, `interrupted`) | |
| `GroundTruthRecorded` | `TargetId`, `at` (`SitePoint`) | research mode: where the phone was found |
| `SessionClosed` | — | |

No event carries a location claim, a distance from RSSI or a depth (rules 1–2).

## 3. JSON rules

Units as plain numbers in their unit (metres, dBm, milliseconds); `SitePoint` as `{"x": …, "y": …}`;
enums by name. Decoding is strict: an unknown `type`, a missing or mistyped field, an invalid polygon or
an unknown enum name throws `FormatException` naming the field — never a silent default.

## 4. Testing

Every event round-trips through JSON (envelope included); each decoding failure above throws
`FormatException`; `NoSignal` survives the round trip as a non-detection; `ScaleSet` rejects a factor
≤ 0; `MeasurementCompleted` rejects implausible dBm (outside −127 … +20) and a negative sample count.
