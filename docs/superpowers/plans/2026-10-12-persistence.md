# Persistence (roadmap 3) Implementation Plan

> Executed inline (superpowers:executing-plans) under the maintainer's standing instruction; TDD per
> task (RED watched first), one fresh opus review of the whole change at the end.

**Goal:** Sessions survive the app being killed; the preview journey records a practice search that
the home screen offers to continue after a restart.

**Architecture:** Drift database in `beneathsos_app/lib/core/database`, a `SessionStore` port in
`core/sessions/domain` with a Drift implementation in `core/sessions/data`, Riverpod providers in
`core/sessions/presentation/providers`; the preview feature and the home feature consume providers only.

**Tech stack:** Flutter 3.47.5 (FVM), drift 2.35.2, drift_flutter 0.3.1, drift_dev 2.35.1,
rubble_core v0.1.0 (git), Riverpod 3 + generator.

**Spec:** `docs/superpowers/specs/2026-10-12-persistence-design.md`

## Global constraints

- `CLAUDE.md` §4–5: hardware/IO only through `core/`; thin notifiers; screens ≤ ~200 lines; no
  hard-coded strings (EN + TR); no `print`; awaited or explicitly `unawaited` futures with a reason.
- Never `--delete-conflicting-outputs`. Gate every commit on each command's own exit code.
- `rubble_core` as a git dependency pinned to `v0.1.0`; local `pubspec_overrides.yaml` via
  `tools/link_local.sh`.
- TestFlight after the app commits that touch `lib/` / `pubspec.*`.

## Review focus

1. Two appends racing (double tap) must still give unique, increasing `seq` and hlc.
2. App killed between the `sessions` insert and the `SiteCreated` append must leave neither.
3. A database opened after the wall clock went backwards must append after the stored events.
4. A stored row that no longer decodes must surface, not vanish.
5. The home card at 200 % text and in dark mode must stay readable; Finish must not be one tap from a
   destructive loss (it only appends `SessionClosed`; the data stays).

## Tasks

### Task 1: Dependencies
- `pubspec.yaml`: `rubble_core` (git v0.1.0), `drift: ^2.35.2`, `drift_flutter: ^0.3.1`; dev
  `drift_dev: ^2.35.1`. `tools/link_local.sh` adds the `rubble_core` override.
- Verify: `fvm flutter pub get`, `fvm dart run build_runner build` succeed; analyze, tests (109) green;
  `tools/dev.sh check` green. Commit `chore(deps): drift and rubble_core v0.1.0`.

### Task 2: Database schema
- `lib/core/database/app_database.dart` (+ `.g.dart`): tables per spec §2, append-only trigger,
  index, `beforeOpen` pragmas, `AppDatabase(QueryExecutor)`.
- Tests `test/core/database/app_database_test.dart` (memory): tables exist; `UPDATE events` throws;
  deleting a session cascades events and samples; duplicate (session, device, seq) rejected.
- Commit `feat(db): Drift schema for sessions, events, samples, settings`.

### Task 3: Session store — writes, identity, clock
- `lib/core/sessions/domain/session_store.dart` (port, `SessionSummary`, `UnreadableEvent`).
- `lib/core/sessions/data/drift_session_store.dart`: `create`, `append`, lazy identity (device id in
  settings, clock seeded from `MAX(hlc)`), injected `int Function() nowMs` and `Random`.
- Tests: create writes row + `SiteCreated` atomically; seq 1,2,3; strictly increasing hlc; parallel
  appends (`Future.wait`) unique seq; device id reused across store instances; reopened store with a
  wall clock in the past appends after stored events; `SessionClosed` sets `closed_at`.
- Commit `feat(sessions): session store appends events in one transaction`.

### Task 4: Session store — reads and samples
- `watch`, `watchLatestOpen`, `addSamples`.
- Tests: watch emits the replayed state and updates after an append; corrupt payload →
  `UnreadableEvent`; latest open summary (count of measured points) and null after close; samples
  batch inserted; file database survives close/reopen.
- Commit `feat(sessions): watch sessions and store raw samples`.

### Task 5: Providers and the practice session
- `session_providers.dart`: `appDatabase`, `sessionStore`, `latestOpenSession`.
- `features/preview/presentation/providers/practice_session.dart`: notifier recording the steps
  (spec §4) with errors logged.
- Tests with overrides (memory database): each step appends the expected event type; a failing store
  does not throw to the caller.
- Commit `feat(preview): record the preview journey as a practice search`.

### Task 6: Visible slice
- Preview screens call the notifier; `features/home/presentation/widgets/last_search_card.dart` +
  mixin for the body text; home screen shows it; ARB keys EN/TR.
- Widget tests: journey → card visible with title/count; Finish hides it; 200 % text readable.
- Commit `feat(home): continue the last search after a restart`; push; TestFlight.

### Task 7: Docs
- Architecture §8 ✅ (practice column, trigger, identity/clock), roadmap 3 ✅, todo. Hub commit.

### Final
- Fresh opus review of the app diff; fix Critical/Important with RED→GREEN; TestFlight again if `lib/`
  changed.
