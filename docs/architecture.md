# BeneathSOS — Architecture

Living document — last updated **2026-10-11**. It describes how the system is built **today** and
where it is going. *Why* each choice was made lives in the decision records: [`docs/adr/`](adr/README.md).
Product reasoning and physics limits: [`docs/fizibilite-2026-09-27.md`](fizibilite-2026-09-27.md).
Plan: [`docs/roadmap.md`](roadmap.md).

Legend: ✅ built · ⏳ planned

## Implementation status

| Area | Status | Where |
|---|---|---|
| Raw BLE scanning (Android + iOS) | ✅ | `ble_scanner` v0.1.0 |
| Scanning use cases, ports, controller | ✅ | `beneathsos_app/lib/core/scanning` |
| Device readiness (Bluetooth + permission, live banner on home) | ✅ | `beneathsos_app/lib/core/readiness` |
| Device tracking, presence log, relink suggestions | ✅ (domain + provider, no UI yet) | `beneathsos_app/lib/features/targets` |
| App shell: router, l10n (en, tr), `BeneathScaffold` (package), branded home; roadmap 1.4 preview journey (sample data) | ✅ | `beneathsos_app/lib/core`, `features/{home,preview,victim}` |
| Release to TestFlight | ✅ | `beneathsos_app/tools/testflight.sh` |
| Design system (`beneathsos_ui`) | ✅ 1.2: tokens, theme, logo, buttons, status banner, card, countdown ring, scaffold | `beneathsos_ui` v0.3.1 |
| `rubble_core` (units, geometry, events) | 🔄 2a units + geometry (local, repository pending) | `packages/rubble_core` |
| Persistence (Drift, event-sourced) | ⏳ phase 3 | — |
| Entry flow, onboarding, sites | ⏳ phase 4 | — |
| Rubble drawing (`rubble_canvas`) | ⏳ phase 5 | — |
| Target selection UI, ambient blacklist | ⏳ phase 6 | — |
| Measurement | ⏳ phase 7 | — |
| `locator_engine` (probability map) | ⏳ phase 8 | — |
| Probability map screen | ⏳ phase 9 | — |
| Victim mode (advertising) | ⏳ phase 10 | — |
| Export, research mode | ⏳ phase 11 | — |

## 1. Scope

| In v1 | Later |
|---|---|
| Rescuer mode: site drawing, ambient blacklist, target selection, point measurement, probability map, next-best-point, multi-target tabs, export, research mode | Multi-rescuer merge via QR shared workspace (v2) |
| Victim mode (simple): one tap → advertise + SOS sound + guidance | Analytics (opt-in), AR positioning, barometric depth, acoustic last-metre search |
| Android + iOS | Professional (AFAD) mode |
| Fully offline, English + Turkish | More languages |

Target user: civilian volunteer.

**Platform evidence so far.** An Android scanner sees an app-less iPhone in airplane mode as an Apple
Find My beacon (field test 2026-09-27, `docs/research/field-test-01.md`). Whether an **iOS** scanner
can see such beacons has not been tested yet; iOS may hide Apple advertisements from apps.

## 2. Repositories

One public repository per package (owner `Berkant35`), cloned under one local folder; git
dependencies pinned to tags plus a git-ignored `pubspec_overrides.yaml` for local paths
([ADR 0003](adr/0003-one-repository-per-package.md), `CLAUDE.md` §2).

```
rubble_core ◄── locator_engine
     ▲                ▲
     │                │
rubble_canvas         │         ble_scanner, beneathsos_ui (standalone)
     ▲                │               ▲
     └──────── beneathsos_app ────────┘
```

| Package | Kind | Responsibility | Status |
|---|---|---|---|
| [`beneathsos`](https://github.com/Berkant35/beneathsos) | hub | Rules, docs, ADRs, research, tools | ✅ |
| [`beneathsos_app`](https://github.com/Berkant35/beneathsos_app) | Flutter app | Composition: features, Riverpod, go_router, l10n, services | ✅ in progress |
| [`ble_scanner`](https://github.com/Berkant35/ble_scanner) | Flutter plugin (Pigeon) | Raw BLE samples with monotonic timestamps; later advertising | ✅ v0.1.0 |
| [`beneathsos_ui`](https://github.com/Berkant35/beneathsos_ui) | Flutter | Design tokens, light/dark theme, Atkinson font, logo, core components | ✅ v0.3.1 |
| `rubble_core` | pure Dart | Units (`Meters`, `Dbm`, `Hpa`), site geometry, event types, projections, UUIDv7, hybrid logical clock | ⏳ |
| `locator_engine` | pure Dart | Grid likelihood, marginalisation, 50/90 % regions, next-best-point, JSON profiles | ⏳ |
| `rubble_canvas` | Flutter | Metric canvas, polygon drawing, zoom/pan, heatmap and contour painters | ⏳ |

## 3. App structure

### Today

```
apps/beneathsos_app/lib/
├─ main.dart, app.dart          ProviderScope; BeneathTheme light/dark (beneathsos_ui), l10n, router —
│                               never calls into features
├─ l10n/                        app_en.arb, app_tr.arb → generated/
├─ core/
│  ├─ l10n_extension.dart       context.l10n
│  ├─ logging/                  AppLogger
│  ├─ models/                   BleSample (plugin-independent sample)
│  ├─ router/                   typed go_router routes (only place that knows paths)
│  ├─ services/                 BleService, PermissionService, WakelockService,
│  │                            appLifecycle, clock — implement domain ports
│  ├─ readiness/                CheckReadiness (scan preconditions without scanning), ReadinessController
│  └─ scanning/
│     ├─ domain/                ports, StartScan / StopScan, preconditions, availability policy
│     └─ presentation/providers ScanController, ScanState, port + use-case bindings
└─ features/
   ├─ home/                     branded home: logo, readiness banner, Start a search, I am trapped, fine print
   ├─ preview/                  roadmap 1.4 mockups with sample data: notice → outline → ambient scan →
   │                            target → measurement → map (each marked "Preview"; replaced phase by phase)
   ├─ victim/                   VictimScreen — victim-mode preview, still says call 112 (phase 10)
   └─ targets/
      ├─ domain/                DeviceTracker, TrackerPolicy, classification, relink, stats
      └─ presentation/providers TrackedDevices
```

### Target (v1)

```
core/  + persistence/ (Drift), more services (sensors, haptics, audio)
features/
   home/ victim/ onboarding/ sites/ site_drawing/ ambient_scan/ targets/
   measurement/ probability_map/ export/ research_mode/ settings/
```

Each feature: `domain/` (rules, use cases, ports), `data/` (port implementations),
`presentation/{screens,widgets,mixins,providers}`.

## 4. Layers

Rules are pure Dart; providers only connect them to Flutter
([ADR 0013](adr/0013-thin-notifiers-ports-use-cases.md)). The scanner is the reference example:

```
Screen ──watch──► ScanController ──calls──► StartScan (use case)
                  (call → map → state)          │ runs preconditions in order:
                                                │   PermissionPrecondition ─► ScanPermissionPort
                                                │   BluetoothPrecondition  ─► ScannerPort
                                                └─ starts ─► ScannerPort, ScreenAwakePort
                                                                 ▲ implemented by
                                     BleService ── ble_scanner plugin ── Kotlin / Swift
```

- **domain/** — no Flutter, Riverpod, plugins or `dart:io`; time is a parameter (`tick(nowMillis)`).
- **presentation/providers** — call a use case, map its result to a sealed UI state, wire streams and
  app lifecycle ([ADR 0014](adr/0014-lifecycle-owned-by-consumers.md)).
- **core/services, data/** — implement ports and hold platform quirks (e.g. iOS reports the adapter as
  `unknown` until CoreBluetooth is ready; `BleService.settledAvailability` waits for the real state).

## 5. Flows (target)

### 5.1 Home
Logo, one message, **"Start a search"** (primary) → rescuer flow (onboarding on first run),
**"I am trapped"** (secondary) → victim mode, the independence note and "Powered by Socrepho".
*Today: "Start a search" opens the preview journey (`/preview/...`, sample data); "I am trapped" opens the victim-mode preview (`/victim`), which still says to call 112.*

### 5.2 Victim mode
1. Start advertising immediately (Android: foreground service `connectedDevice`, manufacturer data
   with app id + battery + liveness counter; iOS: foreground service-UUID advertising).
2. Large instructions (stay calm, save battery, tap 3 times when you hear rescuers), SOS sound,
   flashlight, battery indicator. Screen dims itself.
3. Liveness: last touch / motion time is included in the advertisement (Android).

### 5.3 Rescuer flow

```
Onboarding (first run) → Sites → New site
  → Draw rubble (polygon, edge lengths, scale, optional structure annotations)
  → Ambient scan 30 s (blacklist surface/team devices)
  → Pick targets (Find My first, stationary, weak)
  → Probability map ⟲
        accept suggested point / tap "measure here"
        → Measurement (15 s countdown, stillness check) → back to map
  → Export / close session
```

The probability map is the hub: heatmap, 50 % / 90 % contours, measured points (heard / not heard),
suggested next point, target tabs sorted by "most promising", identity-rotation timer.

## 6. Routes (typed go_router)

| Path | Screen | Status |
|---|---|---|
| `/` | Home | ✅ |
| `/victim` | Victim mode (full-bleed) | ✅ preview |
| `/onboarding` | First-run onboarding | ⏳ |
| `/sites`, `/sites/new` | Site list, create | ⏳ |
| `/preview`, `/preview/site/scan/target/measure/map` | Roadmap 1.4 preview journey (sample data) | ✅ temporary |
| `/sites/:siteId/draw` | Rubble drawing | ⏳ |
| `/sites/:siteId/ambient` | Ambient scan | ⏳ |
| `/sites/:siteId/targets` | Target picker / relink | ⏳ |
| `/sites/:siteId/map?target=:targetId` | Probability map (full-bleed) | ⏳ |
| `/sites/:siteId/points/:pointId/measure` | Measurement | ⏳ |
| `/sites/:siteId/export`, `/settings`, `/research` | Export, settings, research | ⏳ |
| `/join?code=` | Reserved for v2 (shared workspace) | ⏳ |

## 7. Providers (Riverpod 3)

[ADR 0004](adr/0004-riverpod-state-management.md). Riverpod 3 pauses providers nobody watches;
tests keep a listener (`container.listen`).

| Provider | Kind | Role | Status |
|---|---|---|---|
| `bleServiceProvider` | keepAlive | `BleService` (wraps the plugin) | ✅ |
| `bleSamplesProvider` | stream | Sample batches every 250 ms | ✅ |
| `permissionServiceProvider`, `wakelockServiceProvider` | keepAlive | Services | ✅ |
| `appLifecycleProvider` | stream | App lifecycle changes | ✅ |
| `clockProvider` | keepAlive | Wall clock (overridable) | ✅ |
| `scannerPortProvider`, `scanPermissionPortProvider`, `screenAwakePortProvider` | keepAlive | Port → implementation bindings | ✅ |
| `startScanProvider`, `stopScanProvider` | keepAlive | Use cases | ✅ |
| `scanControllerProvider` | notifier | Sealed `ScanState`: idle / needs permission / Bluetooth off / running / failed | ✅ |
| `trackedDevicesProvider` | notifier | `TrackerSnapshot` (devices + presence log) | ✅ |
| `sessionControllerProvider(siteId)` | async notifier family | Appends events, projects site state | ⏳ |
| `measurementControllerProvider(pointId)` | notifier | Measurement state machine | ⏳ |
| `probabilityMapProvider(siteId, targetId)` | future family | `Isolate.run(engine.estimate)` | ⏳ |
| `nextBestPointProvider(siteId, targetId)` | future family | From the map | ⏳ |

## 8. Data (Drift, event-sourced) ⏳ phase 3

[ADR 0006](adr/0006-drift-event-sourced-sessions.md).

| Table | Columns (main) | Notes |
|---|---|---|
| `sessions` | id (UUIDv7), created_at, title, engine_profile, closed_at | one per site |
| `events` | id (UUIDv7), session_id, seq, device_id, hlc, type, payload (JSON), created_at | append-only |
| `rssi_samples` | session_id, point_id?, peripheral_key, rssi, tx_power?, company_id?, t_mono_ns, t_wall | batched inserts |
| `settings` | key, value | onboarding done, units, … |

Event types (v1): `SiteCreated`, `RubblePolygonSet`, `ScaleSet`, `StructureAnnotated`,
`AmbientScanCompleted`, `BlacklistEdited`, `TargetSelected`, `TargetRelinked`,
`MeasurementPointPlaced`, `MeasurementCompleted`, `MeasurementDiscarded`, `GroundTruthRecorded`,
`SessionClosed`.

## 9. Engine (`locator_engine`) ⏳ phase 8

[ADR 0002](adr/0002-probability-map-not-a-point.md), [ADR 0008](adr/0008-pure-dart-engine-python-reference.md).

- 0.25 m grid over the site polygon. Detected point: Gaussian on the median RSSI; not detected:
  `P(RSSI < threshold)` (censored).
- Marginalised unknowns: path-loss exponent, rubble attenuation (profile + structure annotations),
  common offset, device height.
- Outputs: probability grid, 50 % / 90 % regions (m² and % of site), quadrant probabilities,
  next best point (expected information gain).
- Reference: `docs/research/sim/circle_prob_sim.py`; golden fixtures from `tools/sim`.

## 10. BLE plugin (`ble_scanner`) ✅

[ADR 0007](adr/0007-own-ble-plugin.md). Pigeon contract `pigeons/messages.dart`:

```dart
// Dart → native
AdapterState adapterState();                 // unknown | unsupported | unauthorized | poweredOff | poweredOn
ScannerCapabilities capabilities();          // platform, codedPhySupported, extendedAdvertisingSupported
void startScan(ScanConfig config);           // mode (lowLatency…), serviceUuids filter, batchIntervalMs
void stopScan();
// native → Dart
void onSamples(List<ScanSample> samples);    // batched, default every 250 ms
void onAdapterStateChanged(AdapterState state);
void onScanError(int code, String message);

class ScanSample {
  String peripheralKey;                      // Android: address; iOS: CBPeripheral.identifier
  int rssi; int? txPower; int? companyId;    // companyId 0x004C = Apple
  Uint8List? manufacturerData;               // without the 2-byte company id
  List<String> serviceUuids; String? localName; bool? connectable;
  int monotonicNanos; int wallClockMillis;
}
```

- Android: one long-running scan; restarts are delayed, never dropped, to respect the 5-starts-per-
  30-s limit. `BLUETOOTH_SCAN` + location **without** `neverForLocation`
  ([ADR 0015](adr/0015-android-no-never-for-location.md)).
- iOS: foreground scan with `allowDuplicates`; Apple advertisements may be hidden by the OS.

## 11. Edge cases (decided behaviour)

| # | Situation | Behaviour | Status |
|---|---|---|---|
| 1 | Identity goes silent / rotates (~15 min on phones) | "Gone" logged once after 15 s silence; identity leaves the device list after 30 s but stays in the log (`TrackerPolicy`). Relink suggestion: an identity appearing within 30 s of the target going silent, RSSI within 8 dB. UI: countdown with warnings at 10 / 13 min, user confirms relink | ✅ rules · ⏳ UI |
| 2 | No signal at a point | Recorded as a non-detection after the full 15 s; it still updates the map | ⏳ |
| 3 | Rescuer moves during measurement | Stillness check; moving samples flagged, prompt to hold still, extend timer | ⏳ |
| 4 | Surface devices (team, bystanders) | 30 s ambient scan → blacklist; very strong (> −50 dBm) or high-variance devices flagged; re-run when identities rotate | ⏳ |
| 5 | Several targets | One tab per target; one measurement round records all targets | ⏳ |
| 6 | App killed mid-session | Session restored from events; an interrupted measurement is discarded with a reason | ⏳ |
| 7 | Bluetooth or permission turned off | Scanner shows the blocked state; retries when Bluetooth returns or the user comes back from Settings | ✅ logic · ⏳ UI |
| 8 | Rescuer battery low | Warning at 20 %; screen kept awake only while scanning | ⏳ warning · ✅ keep-awake |
| 9 | Wrong point placement | Movable before measuring; after measuring, a move is a new event | ⏳ |
| 10 | Fewer than 3 detected points | Map still shown (non-detections inform it), "low information" badge | ⏳ |

## 12. Quality, CI and release

- **Per repository CI** (GitHub Actions, `tools/templates/ci.yml`): `pull_request` and push to `main`;
  FVM Flutter from `.fvmrc`; `dart format --set-exit-if-changed`, `flutter analyze --fatal-infos`,
  `flutter test`. Read-only token permissions. ✅
- **Dependabot** for pub and GitHub Actions. ✅
- **Branch protection** ✅ (`.github/rulesets/`, `main` and `release/*`): no force push, deletion or
  merge commits for anyone; contributors
  via pull requests with green CI; the single maintainer may push directly (admin bypass);
  auto-merge disabled; private vulnerability reporting enabled.
- **Hub checks** `tools/check_deps.dart` (dependency rules) and `tools/check_l10n.dart`
  (ARB completeness). ⏳
- **Release:** `tools/testflight.sh` archives, signs with the App Store Connect API key and uploads;
  build number = git commit count; internal TestFlight group "Core team"
  ([ADR 0016](adr/0016-testflight-api-key-signing.md)). ✅ Automated upload from CI ⏳ (needs the key
  as a repository secret).

## 13. Decisions

All decisions with context, alternatives and consequences: [`docs/adr/`](adr/README.md) (0001–0018).
