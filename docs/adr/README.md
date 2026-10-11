# Architecture Decision Records

Each significant decision in BeneathSOS is recorded here as a short, numbered document: the context,
what we decided, what we rejected and what it costs. Records are never deleted; a changed decision
gets a new record and the old one is marked *Superseded by NNNN*.

Format: see [0001](0001-record-architecture-decisions.md). New record: copy the newest file, take the
next number, open a PR.

| # | Decision | Status |
|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-probability-map-not-a-point.md) | Show a probability map, never a point; no depth or material from RSSI | Accepted |
| [0003](0003-one-repository-per-package.md) | One repository per package, one local folder | Accepted |
| [0004](0004-riverpod-state-management.md) | Riverpod 3 with code generation | Accepted |
| [0005](0005-go-router-typed-routes.md) | go_router with typed routes | Accepted |
| [0006](0006-drift-event-sourced-sessions.md) | Drift with event-sourced sessions | Accepted (planned: phase 3) |
| [0007](0007-own-ble-plugin.md) | Own BLE plugin (Pigeon) instead of a third-party BLE package | Accepted |
| [0008](0008-pure-dart-engine-python-reference.md) | Pure-Dart probability engine with a Python reference simulation | Accepted (planned: phase 8) |
| [0009](0009-gen-l10n-english-turkish.md) | gen-l10n (ARB), English and Turkish mandatory | Accepted |
| [0010](0010-lints-strict.md) | Lints: Flutter's recommended set, strict modes, infos are failures | Accepted |
| [0011](0011-apache-2-licence.md) | Apache-2.0 licence | Accepted |
| [0012](0012-fvm-pinned-flutter.md) | Flutter pinned with FVM | Accepted |
| [0013](0013-thin-notifiers-ports-use-cases.md) | Thin notifiers: ports and use cases | Accepted |
| [0014](0014-lifecycle-owned-by-consumers.md) | App lifecycle is owned by its consumers | Accepted |
| [0015](0015-android-no-never-for-location.md) | Android: no `neverForLocation`; request location to see Find My beacons | Accepted |
| [0016](0016-testflight-api-key-signing.md) | iOS signing and TestFlight with an App Store Connect API key | Accepted |
| [0017](0017-visual-identity.md) | Visual identity: palette, typeface, logo, voice, accessibility targets | Accepted |
