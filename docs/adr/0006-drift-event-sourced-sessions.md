# 0006. Drift with event-sourced sessions

- Status: Accepted (implementation planned in roadmap phase 3)
- Date: 2026-09-27

## Context

A search session must survive the app being killed in the middle of a measurement, a phone restart or
a dead battery. Measurements are the evidence behind a probability map, so their history matters
(export, research replay, later review). In v2, several rescuers' phones will merge their sessions.
Raw RSSI arrives at hundreds of samples per second.

## Decision

- **Drift** (SQLite) as the local database.
- Sessions are **event-sourced**: every user action (site drawn, target selected, point measured,
  relinked…) is an immutable event appended in its own transaction; screen state is a projection of
  the events (in `rubble_core`).
- Events carry a device id and a hybrid logical clock from day one, so v2 can merge sessions from
  several phones without a migration.
- Raw RSSI samples go to a separate table, inserted in batches.

## Alternatives

- **Isar** — the original package has not been released since 2023 (a community fork exists).
- **Hive CE / Sembast** — key-value / document stores; poor fit for querying high-rate samples.
- **ObjectBox** — fast, but adds native binaries and a non-SQL model.
- **Mutable rows (update in place)** — simpler, but loses history and makes multi-device merge hard.

## Consequences

- Crash safety comes from SQLite transactions (WAL).
- Projection code and schema migrations must be written and tested.
- Exports and research tools can replay a session event by event.

## References

- `docs/architecture.md` §7 (tables and event types); drift 2.35.
