# Roadmap 3 — Persistence: Drift, event-sourced sessions

- Date: 2026-10-12
- Status: decided by the executor under the maintainer's standing instruction "continue" (phase 3
  started on the maintainer's "devam et, faz 3'e geç")
- Builds on: [ADR 0006](../../adr/0006-drift-event-sourced-sessions.md), `docs/architecture.md` §8,
  `rubble_core` v0.1.0 (events, `EventEnvelope`, `SessionProjection`, `HybridClock(last:)`, `Uuid7Generator`)

## 1. Purpose

A search session survives the app being killed, the phone restarting or the battery dying. Every user
action is an immutable event appended in its own SQLite transaction; screens show
`SessionProjection.replay(events)`.

Phase 3 is split so the maintainer sees a change on the phone:

- **3a — data layer** (no visible change): database, session store, device identity, restart-safe clock,
  raw RSSI sample writer.
- **3b — visible slice**: the preview journey records a real **practice search**; after the app is
  killed and reopened, the home screen shows a "Last search" card (title, points measured, start time)
  with **Continue** and **Finish**.

## 2. Database (`lib/core/database/`)

Drift 2.35 with `drift_flutter` (`driftDatabase(name: 'beneathsos')`, SQLite bundled by `sqlite3` 3.x
build hooks — no `sqlite3_flutter_libs`). `schemaVersion = 1`. `onCreate` runs in one transaction and is
safe to repeat (a first launch killed before drift saved the schema version runs it again). `beforeOpen`: `PRAGMA foreign_keys = ON`,
`PRAGMA journal_mode = WAL`.

| Table | Columns | Rules |
|---|---|---|
| `sessions` | `id` TEXT PK (UUIDv7), `title` TEXT, `engine_profile` TEXT, `practice` BOOL, `created_at` INT (ms), `closed_at` INT? (ms) | written in the same transaction as `SiteCreated` / `SessionClosed` |
| `events` | `id` TEXT PK, `session_id` TEXT FK → sessions ON DELETE CASCADE, `seq` INT, `device_id` TEXT, `hlc` TEXT, `schema` INT, `type` TEXT, `payload` TEXT (JSON), `created_at` INT (ms) | UNIQUE(`session_id`, `device_id`, `seq`); index on (`session_id`, `hlc`); a trigger aborts every `UPDATE` (append-only) |
| `rssi_samples` | `id` INT PK autoincrement, `session_id` FK ON DELETE CASCADE, `point_id` TEXT?, `peripheral_key` TEXT, `rssi` INT, `tx_power` INT?, `company_id` INT?, `t_mono_ns` INT, `t_wall` INT (ms) | inserted in batches |
| `settings` | `key` TEXT PK, `value` TEXT | `device_id` lives here |

`practice` marks sessions made by the preview journey (and later a training mode); they are never
mixed with real searches in exports.

## 3. Session store (`lib/core/sessions/`)

Port in `domain/session_store.dart` (pure Dart, no Drift types):

```dart
abstract interface class SessionStore {
  Future<SessionId> create({required String title, required String engineProfile, required bool practice});
  Future<void> append(SessionId session, SessionEvent event);
  Stream<SessionState> watch(SessionId session);
  Stream<SessionSummary?> watchLatestOpen();
  Future<void> addSamples(SessionId session, PointId? point, List<BleSample> samples);
}
```

- `create` inserts the `sessions` row and appends `SiteCreated(title, engineProfile)` in **one**
  transaction.
- `append` runs in one transaction: `seq` = max for (session, this device) + 1; `hlc` = `clock.now()`;
  `id` = next UUIDv7; insert the row; a `SessionClosed` also sets `sessions.closed_at`. Appending to a
  closed session is allowed (rule: late events are applied, projection §2 of 2d).
- `watch` re-reads the session's events whenever the table changes and emits `replay(...)`.
  A stored event that no longer decodes emits an error `UnreadableEvent(eventId, message)` (logged)
  — it is never skipped silently.
- `watchLatestOpen` emits a `SessionSummary` (`id`, `title`, `practice`, `createdAt`,
  `measuredPoints` count, `readable`) for the newest open real search, else the newest open practice
  search, or null. A search with an event that no longer decodes is still offered (`readable: false`).
- `addSamples` inserts the batch with one `batch()` call.
- **Identity and time** (lazy, once per store): the device id is read from `settings`, or created
  (UUIDv7) and stored; the `HybridClock` is seeded with `last:` = `SELECT MAX(hlc) FROM events`
  (the serialised form sorts like the timestamps), so a wall clock that went backwards while the app
  was closed cannot reorder events.
- Drift implementation in `data/drift_session_store.dart`; providers in
  `presentation/providers/session_providers.dart`: `appDatabaseProvider` (keepAlive, closes on
  dispose), `sessionStoreProvider`, `latestOpenSessionProvider` (stream). Tests override
  `appDatabaseProvider` with `NativeDatabase.memory()`.

## 4. Visible slice (3b)

- `PracticeSession` notifier (keepAlive) holds the current practice session id and records the preview
  steps with sample data that matches the screens:
  - notice "Start" → `create(title: l10n.practiceTitle, engineProfile: 'voided_pancake@1', practice: true)`;
  - site "Outline done" → `RubblePolygonSet` (18.2 × 12.4 m rectangle);
  - scan "Continue" → `AmbientScanCompleted` (two sample keys, 30 s);
  - target "Track this phone" → `TargetSelected` (`Apple · Find My`);
  - measure "Show the map" → `MeasurementPointPlaced` + `MeasurementCompleted` (−71 dBm, 30 samples);
  - measure "Discard this point" → `MeasurementDiscarded(userDiscarded)` for the last point.
  Steps are queued in call order; each is caught and logged; a failed write never blocks navigation.
  A failed "Start" clears the current session (later steps never go into the previous search).
  `resume(SessionSummary)` is queued too, refuses real searches and restores the point counter.
- Home: `LastSearchCard` above the actions when `latestOpenSessionProvider` has a session —
  title "Last search" (+ "practice" when `practice`), body "<title> · N points measured · started HH:mm",
  **Continue** (practice searches only: `go` to the preview map) and **Finish** (asks for confirmation,
  then appends `SessionClosed`; the card disappears). Unreadable data shows a note instead of the count.
- All strings in EN and TR ARB files.

## 5. Testing

Store (in-memory database): create writes the row and `SiteCreated` together; append assigns seq 1, 2,
3 per device and strictly increasing hlc; events survive closing and reopening the database (file
database in a temp dir); a store reopened with a wall clock earlier than the stored events still
appends after them; device id is created once and reused; `UPDATE events` is rejected; a corrupt
payload makes `watch` emit `UnreadableEvent`; `SessionClosed` sets `closed_at` and
`watchLatestOpen` turns null; samples are inserted in one batch and cascade with the session.
3b: widget tests — walking the preview journey records the events; the home card shows title, count
and Continue/Finish; Finish hides it; text scales to 200 % without overflow (existing helpers).
