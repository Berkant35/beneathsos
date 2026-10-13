# BeneathSOS — Architecture

Living document — last updated **2026-10-13**. It describes how the system is built **today** and
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
| `rubble_core` (units, geometry, events) | ✅ 2a–2d units, geometry, ids, clock, events, projection | `rubble_core` v0.2.0 |
| Persistence (Drift, event-sourced) | ✅ phase 3: schema, session store, practice search, "last search" card | `beneathsos_app/lib/core/{database,sessions}` |
| Entry flow, onboarding, sites | ✅ phase 4: one-time disclaimer, searches list, new search, overview | `features/{onboarding,sites}` |
| Rubble drawing (`rubble_canvas`) | ✅ phase 5: outline editor, scale step | `rubble_canvas` v0.1.0, `features/site_drawing` |
| Target selection UI, ambient blacklist | ✅ phase 6: 30 s surface scan, ranked candidates with reasons, exclude / track | `features/targets` |
| Measurement | ✅ phase 7: 15 s still points, median per target, no signal stored as data, relink | `features/measurement` |
| `locator_engine` (probability map) | ✅ phase 8: Bayesian grid, 50 % / 90 % regions by count, next point by mutual information | `locator_engine` v0.1.0 |
| Probability map screen | ✅ phase 9: regions, areas, low-information badge, target tabs, suggested point (also on measuring) | `features/probability_map`, `rubble_canvas` v0.3.0 |
| Victim mode (advertising) | ✅ phase 10: beacon, liveness, SOS sound; rescuers rank it first | `features/victim`, `core/beacon`, `ble_scanner` v0.2.1 |
| Export, research mode | ✅ phase 11: JSON + CSV with the disclaimer to the share sheet, non-target keys coded; record where a phone was found and how the map did | `features/{export,research}` |

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
| [`ble_scanner`](https://github.com/Berkant35/ble_scanner) | Flutter plugin (Pigeon) | Raw BLE samples with monotonic timestamps and service data; one-service advertiser (victim beacon) | ✅ v0.2.1 |
| [`beneathsos_ui`](https://github.com/Berkant35/beneathsos_ui) | Flutter | Design tokens, light/dark theme, Atkinson font, logo, core components | ✅ v0.3.1 |
| [`rubble_core`](https://github.com/Berkant35/rubble_core) | pure Dart | Units (`Meters`, `Dbm`, `Hpa`), site geometry, event types, projections, UUIDv7, hybrid logical clock | ✅ v0.2.0 |
| [`locator_engine`](https://github.com/Berkant35/locator_engine) | pure Dart | Grid likelihood, marginalisation, 50/90 % regions, next-best-point, JSON profiles | ✅ v0.1.1 |
| [`rubble_canvas`](https://github.com/Berkant35/rubble_canvas) | Flutter | Metric canvas, outline editor (tap / drag / pan / pinch, 0.5 m snap, side lengths, undo), edge picker; site map with measurement points, probability regions and the suggested point | ✅ v0.3.0 |

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
*Today: "Start a search" opens the disclaimer on first use, then the list of real searches (`/sites`);
the preview journey is "Practice with sample data". "I am trapped" opens the victim-mode preview
(`/victim`), never behind the disclaimer, which still says to call 112.*

### 5.2 Victim mode ✅ phase 10
Spec `docs/superpowers/specs/2026-10-13-victim-mode-design.md`.
1. `/victim` starts the beacon at once (asks for Bluetooth access): service UUID
   `06ad86ef-1e8c-47b4-9c65-c526d5e31581`; Android adds 5 bytes of service data (version, 16-bit beacon
   id drawn per start, battery %, minutes since the phone was last touched or moved), iOS the local name
   `SOS-XXXX`. "Calling out" only after the platform confirms; Bluetooth off / access taken away are
   shown at once; a failed start is retried every minute; the payload is refreshed every minute.
2. Always dark, large text, one action per state, SOS sound (Morse at 3 kHz, alarm stream on Android),
   112 guidance, Back asks before stopping. Screen kept awake.
3. Rescuer side: a beacon is `DeviceKind.trappedBeacon`, keyed `sos-xxxx` by its id (stable across
   address rotation), always first among candidates, never a surface phone; its card shows battery and
   "moved or touched N min ago".
4. Not yet: an Android foreground service (advertising after the app is closed), dimming, flashlight.

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
| `/onboarding` | First use of the rescuer flow: disclaimer (accepted once, `settings`) | ✅ |
| `/sites`, `/sites/new`, `/sites/:sessionId` | Searches list, new search, overview (async redirect to `/onboarding?from=` until the disclaimer is accepted) | ✅ |
| `/preview`, `/preview/site/scan/target/measure/map` | Roadmap 1.4 preview journey (sample data) | ✅ temporary |
| `/sites/:sessionId/draw`, `/sites/:sessionId/scale` | Rubble outline (Back asks when unsaved); optional real size of one side (`ScaleSet`) | ✅ |
| `/sites/:sessionId/ambient` | Surface scan (30 s, phones ≥ −80 dBm median set aside) | ✅ |
| `/sites/:sessionId/targets` | Target picker (relink follows with measurement) | ✅ |
| `/sites/:sessionId/measure` | Measurement (place a point, hold still 15 s) | ✅ |
| `/sites/:sessionId/map` | Probability map; target tabs on the screen (form state) | ✅ |
| `/sites/:sessionId/export` | Export: disclaimer, then JSON + CSV to the share sheet | ✅ |
| `/victim` | Victim mode (beacon, SOS sound) | ✅ |
| `/settings` (`/disclaimer`, `/privacy`, `/licences`) | Settings: language, default rubble type and height, measuring time, signal circles, delete practice / all searches, about | ✅ |
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
| `appDatabaseProvider` | keepAlive | Drift database file `beneathsos` (closed with the scope; in memory in tests) | ✅ |
| `sessionStoreProvider` | keepAlive | `SessionStore` port → `DriftSessionStore` | ✅ |
| `latestOpenSessionProvider` | stream | Newest unfinished session (`SessionSummary`) for the home card | ✅ |
| `practiceSessionProvider` | notifier | Records the preview journey as a practice search; steps queued in order | ✅ |
| `settingsStoreProvider` | keepAlive | `SettingsStore` port → Drift `settings` table | ✅ |
| `finishSearchProvider` | keepAlive | `FinishSearch` use case (appends `SessionClosed`) | ✅ |
| `disclaimerProvider` | async notifier (keepAlive, `core/disclaimer`) | Disclaimer accepted (version 1); the async redirect of `/sites` awaits it | ✅ |
| `searchesProvider`, `searchSummaryProvider(id)`, `searchStateProvider(id)` | stream | Real searches (open first); one search's summary; its projected state | ✅ |
| `newSearchProvider` | notifier | Creates a real search; true while creating (double tap → one) | ✅ |
| `scannerPortProvider`, `scanPermissionPortProvider`, `screenAwakePortProvider` | keepAlive | Port → implementation bindings | ✅ |
| `startScanProvider`, `stopScanProvider` | keepAlive | Use cases | ✅ |
| `scanControllerProvider` | notifier | Sealed `ScanState`: idle / needs permission / Bluetooth off / running / failed | ✅ |
| `trackedDevicesProvider` | notifier | `TrackerSnapshot` (devices + presence log) | ✅ |
| `measurementControllerProvider(sessionId)` | notifier | Measurement state machine | ✅ |
| `mapEngineProvider` | keepAlive | `Isolate.run(computeMap)` (in place in tests) | ✅ |
| `probabilityMapProvider(sessionId, targetId)` | future family | Map + suggested point of one target (outline and points × scale = real metres); null before a point | ✅ |
| `suggestedPointProvider(sessionId)` | future family | The first target's suggested point on the drawing (measuring screen) | ✅ |

## 8. Data (Drift, event-sourced) ✅ phase 3

[ADR 0006](adr/0006-drift-event-sourced-sessions.md). `lib/core/database/app_database.dart` (schema 1,
`PRAGMA foreign_keys = ON`, WAL); `lib/core/sessions/` — `SessionStore` port (domain),
`DriftSessionStore` (data).

| Table | Columns (main) | Notes |
|---|---|---|
| `sessions` | id (UUIDv7), title, engine_profile, practice, created_at, closed_at | one per site; `practice` = preview/training, never mixed with real searches |
| `events` | id (UUIDv7), session_id, seq, device_id, hlc, schema, type, payload (JSON), created_at | append-only (an `UPDATE` trigger aborts); UNIQUE(session, device, seq); index (session, hlc); deleting a session cascades |
| `rssi_samples` | session_id, point_id?, peripheral_key, rssi, tx_power?, company_id?, t_mono_ns, t_wall | batched inserts; cascade with the session. The still-second readings of every device heard at a point (bystanders included: rotating keys, no names or payloads) — kept to re-check a relink; exports must hash or drop non-target keys |
| `settings` | key, value | `device_id` (UUIDv7, created once); later onboarding, units, … |

`create` writes the session row and `SiteCreated` in one transaction; `append` numbers events per device
inside a transaction (`SessionClosed` also sets `closed_at`); a stored row that no longer decodes surfaces
as `UnreadableEvent`, never skipped.

Event types (v1): `SiteCreated`, `RubblePolygonSet`, `ScaleSet`, `RubbleDepthSet`, `StructureAnnotated`,
`AmbientScanCompleted`, `BlacklistEdited`, `TargetSelected`, `TargetRelinked`,
`MeasurementPointPlaced`, `MeasurementCompleted`, `MeasurementDiscarded`, `GroundTruthRecorded`,
`SessionClosed`. They are defined in `rubble_core` (sealed `SessionEvent`) with strict JSON inside an
`EventEnvelope` (`{"schema": 1, "id", "session", "seq", "hlc", "type", "payload"}`); a `MeasurementCompleted`
stores `NoSignal` readings as data (rule 3).

Screen state is `SessionProjection.replay(events)` → `SessionState`: events are applied in hybrid-clock order
(then `seq`, then id), an event id already applied is ignored, a measurement for an unknown point is
kept, a discarded or moved point sets its readings aside (`discardedReadings`) and leaves
`measuredPoints`, and no target identity is ever lost. After a restart the app seeds `HybridClock`
with the greatest stored timestamp (`last:`), so a clock that went backwards cannot reorder events.

### Export and research (phase 11)
`SessionStore.record` reads a search as stored; `ExportBundle` (pure) writes `beneathsos-<date>-<title>.json`
(search row, every event — an unreadable one marked `unreadable` without its text — and the disclaimer)
and `-samples.csv` (disclaimer as `#` lines, raw readings). Keys of phones that are not targets become
`other-` + 12 hex of SHA-256(16-byte salt drawn per export + key) in both files, so events and readings
still join within one file and never across files. `SharePort` (share_plus) hands both files to the
share sheet; the app sends nothing itself. Research: `GroundTruthRecorded` after a confirmation dialog;
`foundReport` says which region the spot is in (a spot on a cell edge counts in the better one) or how far
outside the 90 % area.

## 9. Engine (`locator_engine`) ✅ phase 8

[ADR 0002](adr/0002-probability-map-not-a-point.md), [ADR 0008](adr/0008-pure-dart-engine-python-reference.md).

- 0.25 m grid over the site polygon. Detected point: Gaussian on the median RSSI; not detected:
  `P(RSSI < threshold)` (censored).
- Marginalised unknowns: path-loss exponent, rubble attenuation (profile + structure annotations),
  common offset, device height.
- Outputs: probability grid; 50 % / 90 % regions as the smallest cell sets holding that mass (by count,
  so a drawn region is exactly its reported area); `suggestNextPoint`: a spot 1 m outside every wall,
  ≥ 2 m from measured points, scored by mutual information over the 99 % mass.
- Input checks: no observations or an outline smaller than one cell → `ArgumentError` (the app shows
  the map only once a point is measured).
- Profiles `voided_pancake@1`, `dense@1` (JSON, validated). log Φ from a Hermite table checked against
  scipy. Sites above `maxCells` (6000) get a coarser grid (0.5 m at 40 × 30 m); the suggestion is scored
  against 1 m blocks. Budget tests: 40 × 30 m, 15 points heard nowhere, both profiles < 3 s; 80 × 60 m < 3 s.
- App input (`features/probability_map/domain/map_request.dart`): outline and points × scale (real
  metres); readings within 1 m are one place (majority heard, median of medians — re-measuring a spot is
  not new information); points ≥ 0.5 m inside the outline stand on the rubble and are left out (the map
  says how many); `MapMemo` runs an unchanged request only once.
- Reference: `tools/sim/engine_reference.py`; golden fixtures in `locator_engine/test/fixtures` (tests: < 1e-6 per cell, measured ≈ 1e-12;
  areas exact).
- Not yet: quadrant probabilities, structure annotations in the attenuation.
- Map screen (2026-10-13, after the first field test): the most likely spot is the probability-weighted
  middle of the 50 % area (its most likely cell when the area is split) drawn as a crosshair with the
  dashed circle that holds half the probability; the panel says its radius and how far it lies in from
  the nearest edge (drawing geometry, not signal). Measured points are diamonds with their dBm, warmer
  when stronger. Places within 3 m of each other trigger "measure all around the rubble".
- Signal circles ([ADR 0019](adr/0019-signal-circles-rough-guide.md), on by default, a checkbox on the map and
  measuring screens): per heard point a circle in its own colour, radius = distance at which the profile's
  middle exponent and attenuation give the median; where they meet best inside the outline, with a
  dashed line and its length from the nearest measured point. The suggested point is labelled "Measure
  next".
- The searches list can delete a search (asks first; the session row cascades to events and readings).
- Settings (`AppSettings` over the `settings` table: `language`, `default_profile`, `signal_circles`,
  `measure_seconds`, `default_rubble_height`; an unreadable value falls back to its default): the app
  locale, the profile of new searches, the measuring window, the circles switch and the height assumed
  when a search has no depth all read it.
- Depth (2026-10-13; the signal cannot tell it, rule 2): the overview step "Rubble height and level"
  (`/sites/:sessionId/depth`) stores `RubbleDepthSet` (height, `TrappedLevel` upper / middle / ground floor /
  basement / unknown). The engine runs with that height and the level's likely heights above the ground
  (upper 70–90 %, middle 40–60 %, bottom 10–25 %, basement at ground level; unknown keeps the profile's
  spread); signal circles show their footprint √(slant² − height²). Victim mode sends its barometer
  (service data bytes 5–6 on Android, `SOS-XXXX-PPPPP` name on iOS); a candidate card compares it with the
  rescuer's barometer: above / about your level / 1–3 floors below / deeper (± 8 m, ~8.3 m per hPa).

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
| 1 | Identity goes silent / rotates (~15 min on phones) | "Gone" logged once after 15 s silence; identity leaves the device list after 30 s but stays in the log (`TrackerPolicy`). While measuring and only while the target is silent: "<target> may have changed its Bluetooth identity… Is it the same phone?" — Yes stores `TargetRelinked`, No is remembered (never asked again for that pair) | ✅ (countdown warnings at 10 / 13 min ⏳) |
| 2 | No signal at a point | Recorded as `NoSignal` after 15 still seconds *with the scan running* (fewer than 3 readings or a median below −100 dBm count as not heard); a point where no device at all was heard is discarded (the radio was not working), never stored as a non-detection | ✅ |
| 3 | Rescuer moves during measurement | User accelerometer > 0.8 m/s²: that second does not count and its readings are dropped; "Hold the phone still" | ✅ |
| 4 | Surface devices (team, bystanders) | 30 s surface scan 10 m from the rubble (foreground seconds only) → phones with median ≥ −80 dBm (3+ readings) set aside, the scan time recorded (`lastSurfaceScan`); candidates ranked (Find My, still, "heard only a few times", weak first; very strong ≥ −55 dBm last); Exclude has Undo and every set-aside phone can be put back; a scan older than 10 min asks for a new one (identities rotate) | ✅ |
| 5 | Several targets | One tab per target; one measurement round records all targets | ⏳ |
| 6 | App killed mid-session | Session restored from events; leaving mid-measurement or a point never finished is discarded (`interrupted`) | ✅ |
| 7 | Bluetooth or permission turned off | Scanner shows the blocked state; retries when Bluetooth returns or the user comes back from Settings | ✅ logic · ⏳ UI |
| 8 | Rescuer battery low | Warning at 20 %; screen kept awake only while scanning | ⏳ warning · ✅ keep-awake |
| 9 | Wrong point placement | A tap marks the spot, tapping again moves it, "Measure here" starts; after measuring a move sets the readings aside | ✅ |
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
