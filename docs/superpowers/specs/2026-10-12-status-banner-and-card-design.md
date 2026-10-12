# Roadmap 1.2b — Status banner, card and device readiness on the home screen

- Date: 2026-10-12
- Status: approved in conversation, section by section (2026-10-12)
- Roadmap: phase 1, step 1.2b (1.2a done: tokens, theme, logo, buttons, branded home)
- Builds on: [1.2a spec](2026-10-11-beneathsos-ui-theme-design.md), [`docs/design/`](../../design/principles.md),
  [ADR 0015](../../adr/0015-android-no-never-for-location.md), [ADR 0018](../../adr/0018-design-system-material-theme.md)

## 1. Purpose and success

> A very usable, readable interface for people at a collapsed building in an emergency.

A rescuer must see at a glance whether the phone can search. 1.2b adds two components to
`beneathsos_ui` — `StatusBanner` and `BeneathCard` — and puts a **live device-readiness banner** on
the home screen, above the two actions.

**Success = on the phone (TestFlight):** the home screen shows "✓ Bluetooth is on and ready."; turning
Bluetooth off in Control Center turns it into a red "Bluetooth is off. Turn it on in your phone's
settings." within seconds, and back when it is turned on. The "being prepared" screens show their
text inside an icon card. A fresh install asks for Bluetooth permission on first launch.

Not in 1.2b: the countdown ring and moving `AppScaffold` (1.2c), haptics and sound for events (with the
first real event, phase 6–7), blocking "Start a search" (phase 4 decides), an onboarding explanation of
the Android location permission (phase 4).

## 2. Decisions (made with the maintainer)

| Topic | Decision |
|---|---|
| When to read Bluetooth / ask permission | On the home screen at launch: permission is asked on first launch (iOS system prompt; Android runtime request), both modes need Bluetooth |
| All good | A calm "ready" banner is shown (reassurance; the layout never jumps between states) |
| Architecture | A readiness use case + provider that reuse the existing scan preconditions; never `ScanController` (would start scanning and drain the battery), never logic in widgets |

## 3. Package `beneathsos_ui` 0.2.0

### `StatusBanner`

`StatusBanner({required StatusKind kind, required String message, VoidCallback? onTap, IconData? icon})`

| Kind | Use | Light | Dark | Default icon |
|---|---|---|---|---|
| `ready` | All good, or neutral progress | surface container (white) fill, `onSurface` text, `outlineVariant` border | `#22324F` fill, `#E8ECF5` text | check circle |
| `attention` | Needs attention (later: identity rotation) | accent `#FF7900` fill, `#1A0D00` text (7.3) | `#FF8C2E` fill, `#1A0D00` text (8.2) | warning |
| `blocked` | Something blocks the task | error `#B3261E` fill, white text (6.5) | `#FFB4AB` fill, `#690005` text (7.7) | block |

- Never colour alone: every kind has its own icon and the message says what happened and what to do.
- With `onTap` the whole banner is a button ≥ 56 tall with a trailing chevron, read as a button by
  screen readers; without `onTap` it is not a button.
- `Semantics(liveRegion: true)`: a changed message is announced.
- A change of kind or message cross-fades over `BeneathTokens.motionOf(context).medium` (zero with
  "reduce motion").
- At 200 % text the message wraps and is never clipped.

### `BeneathCard`

`BeneathCard({required Widget child, String? title, IconData? icon, VoidCallback? onTap})` — surface
container fill, radius 16, 1 px `outlineVariant` border, 16 padding; optional title (`titleLarge`)
with a leading icon; with `onTap` it is a button for screen readers.

### 1.2a deferred minors folded in

- `outlineVariant`: light `#D5DAE5`, dark `#33456A` (decorative borders and dividers; never carries
  information).
- Button icons 24 px (`PrimaryButton`, `SecondaryButton`).
- `BeneathTokens` implements `==` and `hashCode` (no theme lerp on every app rebuild).
- `primaryTextTheme` uses Atkinson too.
- Lock-up proportions match the brand source (`tools/brand/brandkit/wordmark.py`): gap = height / 4,
  wordmark size = height / 2. Lock-up goldens are regenerated.
- The golden test helper throws a `StateError` when the Material icon font cannot be found.

## 4. App: device readiness

### Domain (`lib/core/readiness/domain/`)

`sealed class DeviceReadiness` — `ReadinessChecking`, `ReadinessReady`, `ReadinessNeedsPermission`,
`ReadinessPermissionInSettings`, `ReadinessBluetoothOff`, `ReadinessUnsupported`.

`CheckReadiness` runs the **existing** scan preconditions in order — `PermissionPrecondition` (checks;
asks once when missing), then `BluetoothPrecondition` — without starting a scan, and maps the first
blocking result:

| First blocking result | Readiness |
|---|---|
| `PermissionMissing(permanent: false)` | `ReadinessNeedsPermission` |
| `PermissionMissing(permanent: true)` (incl. iOS Bluetooth unauthorised) | `ReadinessPermissionInSettings` |
| `BluetoothUnavailable(unsupported: false)` | `ReadinessBluetoothOff` |
| `BluetoothUnavailable(unsupported: true)` | `ReadinessUnsupported` |
| none | `ReadinessReady` |

`BluetoothUnavailable` gains `final bool unsupported` (default `false`); `BluetoothPrecondition` sets it
for `BluetoothAvailability.unsupported`. When both permission and Bluetooth are missing, permission is
shown first (it is the one the app can fix with a tap).

### Provider (`lib/core/readiness/presentation/providers/readiness_controller.dart`)

Thin notifier, state `DeviceReadiness` (initial `ReadinessChecking`):

- `build()` runs `CheckReadiness` once, listens to `ScannerPort.availabilityChanges` (re-check on every
  change) and to `appLifecycleProvider` (re-check on resume **only** when the state is a blocked one).
- `requestPermission()` and `openSettings()` call the permission port, then re-check.
- Never starts a scan.

### Home

`ReadinessBanner` (`features/home/presentation/widgets/`) above `HomeActions`; mapping from
`DeviceReadiness` to kind, message and action lives in `ReadinessBannerMixin`
(`features/home/presentation/mixins/`).

| Readiness | Kind | Message key | On tap |
|---|---|---|---|
| Checking | `ready` (hourglass icon) | `readinessChecking` | — |
| Ready | `ready` | `readinessReady` | — |
| NeedsPermission | `blocked` | `readinessNeedsPermission` | `requestPermission()` |
| PermissionInSettings | `blocked` | `readinessPermissionInSettings` | `openSettings()` |
| BluetoothOff | `blocked` | `readinessBluetoothOff` | — (iOS cannot switch Bluetooth on for apps) |
| Unsupported | `blocked` | `readinessUnsupported` | — |

"Start a search" stays enabled in every state; the real flow (phase 4) handles blocking.

### "Being prepared" screens

`NewSiteScreen` and `VictimScreen` show their text inside a `BeneathCard` (construction icon, title
`preparingCardTitle`). The victim screen keeps the 112 sentence large and bold inside the card. Both
stay scrollable.

### Strings (ARB, English and Turkish in the same change)

| Key | English | Türkçe |
|---|---|---|
| `readinessChecking` | Checking Bluetooth… | Bluetooth kontrol ediliyor… |
| `readinessReady` | Bluetooth is on and ready. | Bluetooth açık ve hazır. |
| `readinessNeedsPermission` | Bluetooth permission is needed. Tap to allow it. | Bluetooth izni gerekli. İzin vermek için dokunun. |
| `readinessPermissionInSettings` | Bluetooth permission is off. Tap to turn it on in Settings. | Bluetooth izni kapalı. Ayarlarda açmak için dokunun. |
| `readinessBluetoothOff` | Bluetooth is off. Turn it on in your phone's settings. | Bluetooth kapalı. Telefonun ayarlarından açın. |
| `readinessUnsupported` | This phone does not support Bluetooth LE. Search with another phone. | Bu telefon Bluetooth LE desteklemiyor. Başka bir telefonla arayın. |
| `preparingCardTitle` | Being prepared | Hazırlanıyor |

On Android the scan permission includes location (ADR 0015); the banner says "Bluetooth permission"
and the system dialog names what is asked.

## 5. Testing and verification

**Package**

- `StatusBanner`: colours and icon per kind, light and dark; the text pairs above pinned in the
  contrast test; `onTap` → button ≥ 56 tall, semantics button; no `onTap` → not a button; live region
  set; 200 % text not clipped; "reduce motion" → zero cross-fade.
- `BeneathCard`: title and icon shown; border is `outlineVariant`; with `onTap` a semantics button.
- Minors: button icon size 24; `BeneathTokens.light() == BeneathTokens.light()` and equal hash codes;
  `primaryTextTheme` uses Atkinson; lock-up gap and text size equal height / 4 and height / 2; golden
  helper throws without the icon font.
- Goldens (macOS, 0.5 % tolerance): banner × 3 kinds and card, light and dark; regenerated lock-ups.

**App**

- `CheckReadiness` with fake ports: each row of the mapping table; permission asked once; permission
  shown before Bluetooth-off when both fail; a scan is never started.
- `ReadinessController` with overrides: Bluetooth off → on changes the state; resume re-checks only
  when blocked; `requestPermission()` / `openSettings()` call the port and re-check.
- Home: each readiness state shows its message (English and Turkish); tappable states call the right
  action; at 200 % text on a small phone both actions stay reachable with the banner present.
- Being-prepared screens: the card is shown; the 112 sentence stays fully readable at 200 % portrait and
  landscape.
- Existing tests still pass.

**Done when** format, `analyze --fatal-infos` and tests pass in package and app; iOS simulator
screenshots (ready banner, card screens; light and dark) and the blocked-banner goldens are sent to the
maintainer; the package is tagged `v0.2.0` with green `ci` and `goldens`; the app depends on `v0.2.0`
and a fresh clone resolves it; Android debug APK builds; package, app and hub are pushed; TestFlight
build `VALID`; roadmap 1.2b marked done; issue #7 comment.

**On the phone the maintainer sees:** the ready banner above the buttons; it turns red when Bluetooth is
switched off and back when on; the card on both "being prepared" screens; a slightly larger search icon
and the lock-up in brand proportions; on a fresh install, the Bluetooth permission prompt on first
launch. Not yet: the countdown ring (1.2c), the real search flow (phase 4).
