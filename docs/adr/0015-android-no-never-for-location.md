# 0015. Android: no `neverForLocation`; request location to see Find My beacons

- Status: Accepted
- Date: 2026-09-27

## Context

On Android 12+, an app can declare `BLUETOOTH_SCAN` with `usesPermissionFlags="neverForLocation"` to
avoid asking for location. Android documents that with this flag **some BLE beacons are filtered from
scan results**. The most valuable signal for BeneathSOS is a beacon: an iPhone without internet
broadcasts an Apple Find My advertisement every ~2 seconds, even without our app installed.

On 2026-09-27 an Android phone (Samsung SM A055F) running our scanner detected an iPhone in airplane
mode as `Apple · Find My` at about −35 dBm.

## Decision

- `ble_scanner` declares `BLUETOOTH_SCAN` **without** `neverForLocation`, plus `ACCESS_FINE_LOCATION`
  (and the legacy Bluetooth permissions up to Android 11).
- The app requests Bluetooth scan and location at runtime before scanning.
- The app does not read GPS or store any location; the permission exists only so Android delivers
  beacon advertisements.

## Alternatives

- **`neverForLocation`** — one fewer permission prompt, at the risk of hiding the very beacons we
  look for.

## Consequences

- Users see a location permission request; onboarding must explain why.
- Store review needs a clear justification for the location permission.
- Runtime permissions currently go through `permission_handler`, pinned to 12.x (see backlog).

## References

- `packages/ble_scanner/android/src/main/AndroidManifest.xml`;
  `docs/research/field-test-01.md`.
