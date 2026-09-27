# BeneathSOS — Architecture (v1)

Status: **draft, decided 2026-09-27**. Source of decisions: `docs/mimari-sorular.md` (maintainer answers).
Why the product works this way: `docs/fizibilite-2026-09-27.md`.

## 1. Scope

| In v1 | Later |
|---|---|
| Rescuer mode (detailed): site drawing, ambient blacklist, target selection, point measurement, probability map, next-best-point, multi-target tabs, export, research mode | Multi-rescuer merge via QR shared workspace (v2) |
| Victim mode (simple): two-button home → one tap → advertise + SOS sound + guidance | Analytics (opt-in), AR positioning, barometric depth, acoustic last-metre search |
| Android + iOS (iOS scope confirmed by field test) | Professional (AFAD) mode |
| Fully offline, TR + EN | More languages |

Target user: civilian volunteer. Professional mode later.

## 2. Workspace

One public GitHub repo per package (owner `Berkant35`), all cloned under one local folder; git
dependencies in `pubspec.yaml` + git-ignored `pubspec_overrides.yaml` with local paths (see CLAUDE.md §2).

```
rubble_core ◄── locator_engine
     ▲                ▲
     │                │
rubble_canvas         │         ble_scanner (standalone)
     ▲                │               ▲
     └──────── apps/beneathsos ───────┘
```

| Package | Kind | Responsibility |
|---|---|---|
| `rubble_core` | pure Dart | Value types (`Meters`, `Dbm`, `Hpa`, `SitePoint`), site geometry, **event types**, projections (events → state), IDs (UUIDv7), hybrid logical clock |
| `locator_engine` | pure Dart | Probability map on a grid, censored likelihood, marginalisation over n / α / offset / height, HPD regions, next-best-point (expected information gain), engine profiles (JSON) |
| `ble_scanner` | Flutter plugin (Pigeon) | Raw BLE scan samples with monotonic timestamps; later: advertising for victim mode. No domain knowledge |
| `rubble_canvas` | Flutter | Metric canvas: polygon drawing, snapping, edge-length input, pinch/zoom/pan, measurement-point markers, heatmap + HPD contour painter |
| `beneathsos_app` | Flutter app | Composition: features, Riverpod, go_router, Drift, l10n, services |

## 3. App structure

```
apps/beneathsos_app/lib/
├─ main.dart / app.dart                 bootstrap, ProviderScope, lifecycle observer
├─ core/
│  ├─ router/                           typed go_router routes, redirects (first-run → onboarding)
│  ├─ l10n/                             ARB files + context.l10n extension
│  ├─ theme/                            tokens, typography, high-contrast outdoor theme
│  ├─ widgets/                          AppScaffold, AppButton, CountdownRing, ...
│  ├─ services/                         BleService, SensorService, PermissionService,
│  │                                    HapticsService, WakelockService, AudioService
│  ├─ persistence/                      Drift database, DAOs, migrations
│  └─ logging/
└─ features/
   ├─ home/                             two big buttons: "I am trapped" / "I am searching"
   ├─ victim_mode/
   ├─ onboarding/                       disclaimer, units, how it works, permissions
   ├─ sites/                            list, create, resume
   ├─ site_drawing/                     polygon + scale + structure annotations
   ├─ ambient_scan/                     30 s blacklist
   ├─ targets/                          pick target(s), relink after address rotation
   ├─ measurement/                      point measurement state machine
   ├─ probability_map/                  main working screen (canvas + heatmap + target tabs)
   ├─ export/                           JSON / CSV / PDF-like summary, share sheet
   ├─ research_mode/                    ground truth entry, error report, raw CSV
   └─ settings/
```

Each feature: `domain/` (feature-specific use cases), `data/` (repositories over DAOs/services),
`presentation/{screens,widgets,mixins,providers}`.

## 4. Flows

### 4.1 Home
Two full-width buttons, nothing else: **"Enkaz altındayım"** → victim mode; **"Arama yapacağım"** →
rescuer flow (onboarding on first run).

### 4.2 Victim mode (simple)
1. Start advertising immediately (Android: foreground service `connectedDevice`, manufacturer data
   with app id + battery + liveness counter; iOS: foreground service-UUID advertising).
2. Screen: large instructions (stay calm, save battery, tap 3 times when you hear rescuers), SOS
   sound button, flashlight, battery indicator. Screen dims itself.
3. Liveness heartbeat: last touch / motion time is included in the advertisement (Android).

### 4.3 Rescuer flow

```
Onboarding (first run) → Sites → New site
  → Draw rubble (polygon, edge lengths, scale, optional structure annotations)
  → Ambient scan 30 s (blacklist surface/team devices)
  → Pick targets (list of remaining devices, strongest/stable first)
  → Probability map screen ⟲
        tap "measure here" / accept suggested point
        → Measurement (15 s countdown, stillness check) → back to map (map updates)
  → Export / close session
```

Probability map screen = the hub: canvas with heatmap, 50 % / 90 % contours, placed points (detected /
not detected), suggested next point, **target tabs on top** sorted by "most promising"
(smallest 90 % region → strongest median RSSI → most recent liveness), and the address-rotation timer.

## 5. Routes (typed go_router)

| Path | Screen |
|---|---|
| `/` | Home |
| `/victim` | Victim mode (full-bleed) |
| `/onboarding` | First-run onboarding (redirect when not completed) |
| `/sites` | Site list / resume |
| `/sites/new` | Create site |
| `/sites/:siteId/draw` | Rubble drawing |
| `/sites/:siteId/ambient` | Ambient scan |
| `/sites/:siteId/targets` | Target picker / relink |
| `/sites/:siteId/map?target=:targetId` | Probability map hub (full-bleed) |
| `/sites/:siteId/points/:pointId/measure` | Measurement |
| `/sites/:siteId/export` | Export |
| `/settings`, `/research` | Settings, research mode |
| `/join?code=` | **Reserved for v2** (QR shared workspace) — returns "not available" in v1 |

## 6. State management (Riverpod 3)

Chosen over Bloc because: the maintainer's other app (Qulo) uses Riverpod + go_router (one mental
model); BLE data is streams → `StreamProvider`; test overrides are trivial; code-gen reduces
boilerplate.

| Provider | Type | Notes |
|---|---|---|
| `bleServiceProvider` | `Provider` (keepAlive) | wraps `ble_scanner` |
| `scanSamplesProvider` | `StreamProvider` | batched raw samples (every 250 ms) |
| `sessionControllerProvider(siteId)` | `AsyncNotifier` family | appends events, exposes projected `SiteState` |
| `blacklistProvider(siteId)` | derived | from events |
| `targetTrackerProvider(siteId)` | `Notifier` | liveness of target keys, relink proposals, rotation timer |
| `measurementControllerProvider(pointId)` | `Notifier` | sealed state machine: Idle → Collecting → (Moved?) → Completed |
| `probabilityMapProvider(siteId, targetId)` | `FutureProvider` family | debounced; `Isolate.run(engine.estimate)` |
| `nextBestPointProvider(siteId, targetId)` | `FutureProvider` family | from the map |

## 7. Data (Drift, event-sourced)

Why Drift: SQLite WAL gives crash-safe transactional appends (a session survives the app being killed
mid-measurement), type-safe queries, migrations, isolate support, active maintenance. Isar's original
package is unmaintained since 2023; Hive/Sembast are key-value/document stores without relational
queries over high-rate samples; ObjectBox is fast but adds native binaries and a non-SQL model.

### Tables

| Table | Columns (main) | Notes |
|---|---|---|
| `sessions` | id (UUIDv7), created_at, title, engine_profile, closed_at | one per site |
| `events` | id (UUIDv7), session_id, seq, device_id, hlc, type, payload (JSON), created_at | **append-only**, never updated |
| `rssi_samples` | session_id, point_id?, peripheral_key, rssi, tx_power?, company_id?, t_mono_ns, t_wall | batched insert every 250 ms |
| `settings` | key, value | onboarding done, units, etc. |

`device_id` + `hlc` (hybrid logical clock) are stored from day one so v2 can merge events from several
phones (union by id, order by hlc) without migration.

### Event types (v1)

`SiteCreated`, `RubblePolygonSet`, `ScaleSet`, `StructureAnnotated` (floors, slab thickness,
voids — adjusts the α prior), `AmbientScanCompleted` (blacklist keys), `BlacklistEdited`,
`TargetSelected`, `TargetRelinked` (old key, new key, reason, confirmed by user),
`MeasurementPointPlaced`, `MeasurementCompleted` (summary: median RSSI, sample count, detected flag,
stillness ok), `MeasurementDiscarded` (reason), `GroundTruthRecorded` (research mode),
`SessionClosed`.

## 8. Engine (`locator_engine`)

- Grid 0.25 m over the site polygon. Likelihood per point: Gaussian on median RSSI when detected,
  `P(RSSI < threshold)` when not detected (censored).
- Unknowns marginalised: path-loss exponent n, rubble attenuation α (prior from profile +
  structure annotations), common offset c, device height level z.
- Outputs: normalised probability grid, 50 % / 90 % HPD regions (area in m² and % of site),
  quadrant probabilities, suggested next point (max expected information gain among walkable
  candidate cells / perimeter).
- Reference: `docs/research/sim/circle_prob_sim.py`. `tools/sim/export_fixtures.py` emits golden
  JSON; Dart tests assert equality within tolerance.

## 9. BLE plugin (`ble_scanner`, Pigeon)

```dart
// Host API (Dart → native)
void startScan(ScanConfig config);     // mode: lowLatency, allowDuplicates: true, optional service UUID filter
void stopScan();
ScannerCapabilities capabilities();    // codedPhy, extendedAdv, maxAdvLen, platform
// Flutter API (native → Dart)
void onSamples(List<ScanSample> batch);

class ScanSample {
  String peripheralKey;   // Android: address; iOS: CBPeripheral.identifier
  int rssi; int? txPower; int? companyId;
  Uint8List? manufacturerData; List<String> serviceUuids;
  int monotonicNanos;     // Android ScanResult.timestampNanos; iOS mach time
  bool connectable;
}
```

Android: one long-running scan (never exceed 5 starts / 30 s), `BLUETOOTH_SCAN` + location **without**
`neverForLocation` (that flag makes Android filter some beacon advertisements, e.g. Find My). iOS: foreground scan with `allowDuplicates`; Apple-company packets may be hidden
by the OS — capability reported, not assumed. Advertising API added for victim mode in a later step.

## 10. Edge cases (decided behaviour)

| # | Situation | Behaviour |
|---|---|---|
| 1 | Target address rotates (~15 min) | Animated countdown since first seen (warn at 10 / 13 min); when key disappears > 20 s and a new key appears with similar RSSI within ±10 s → animated relink proposal, user confirms → `TargetRelinked` |
| 2 | No signal at a point | Record as non-detection after the full 15 s; it still updates the map |
| 3 | Rescuer moves during measurement | Accelerometer stillness check; moving samples flagged, prompt to hold still, extend timer |
| 4 | Surface devices (team, bystanders) | 30 s ambient scan → blacklist; very strong (> −50 dBm) or high-variance devices auto-flagged; user can edit. Blacklisted keys also rotate → re-run ambient scan when prompted |
| 5 | Several targets | One tab per target, same measurement round records all targets' RSSI at once |
| 6 | App killed / phone restarts mid-session | Session restored from events; an interrupted measurement is discarded with reason, not half-saved |
| 7 | Bluetooth / permission turned off | Blocking banner, resume re-check (`onAppResumed`) |
| 8 | Rescuer battery low | Warning at 20 %, wakelock only during measurement |
| 9 | Wrong point placement | Points are movable before measuring; after measuring, move = new event, map recomputes |
| 10 | Fewer than 3 detected points | Map still shown (non-detections inform it) with a "low information" badge and next-point hint |

## 11. Quality & CI

GitHub Actions on `pull_request` and `push` to `main`: format check, `analyze --fatal-infos`,
tests + coverage, dependency rules, l10n completeness, Android debug build; iOS build on macOS runner
for `main`. Least-privilege permissions, SHA-pinned actions, Dependabot for pub + actions.
Branch rules: see `.github/rulesets/main.json` and `SECURITY.md`.

## 12. Decision log

| # | Decision | Alternatives rejected |
|---|---|---|
| D1 | Separate public repo per package, one local folder, git deps + local `pubspec_overrides.yaml` | Monorepo with pub workspaces (maintainer wants independent repos) |
| D2 | Riverpod 3 + generator | Bloc (fine, but second mental model vs Qulo) |
| D3 | go_router typed routes, `/join` reserved for v2 | auto_route |
| D4 | Drift, event-sourced sessions + raw sample table | Isar (unmaintained), Hive, Sembast, ObjectBox |
| D5 | Own BLE plugin via Pigeon | flutter_blue_plus (commercial licence for orgs), third-party plugins hiding raw fields |
| D6 | Pure Dart engine in isolate; Python sim as reference | FFI / native |
| D7 | Flutter `gen-l10n` (ARB), en + tr mandatory | Custom map-based l10n (not contributor-friendly) |
| D8 | `flutter_lints` + strict modes + extra rules + `riverpod_lint`, infos fatal | very_good_analysis (maintainer asked for Flutter's recommended base) |
| D9 | Apache-2.0 licence | GPL (limits AFAD / partner integration) |
| D10 | FVM-pinned Flutter stable | unpinned |
