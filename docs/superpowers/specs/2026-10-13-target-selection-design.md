# Roadmap 6 — Target selection: surface scan and candidates

- Date: 2026-10-13
- Status: decided by the executor under the maintainer's blanket approval ("her şeyi onaylıyorum,
  projeyi bitirmeye odaklanalım", 2026-10-13)
- Builds on: the 1.4 mockups (ambient scan: "Stand 10 m away from the rubble"; target choice with
  plain-language reasons), `docs/architecture.md` §5.3 and §11 rows 1 and 4, events `AmbientScanCompleted`,
  `BlacklistEdited`, `TargetSelected`; existing `DeviceTracker`, `classify`, `ScanController`,
  `trackedDevicesProvider`

## 1. Surface scan (`/sites/:sessionId/ambient`)

- The rescuer stands about 10 m from the rubble with the team; the app scans for 30 s (countdown ring,
  "N phones heard so far").
- **Rule:** a device heard at least 3 times with a median of **−80 dBm or stronger** is a surface phone
  (`AmbientPolicy`). Weaker devices are *not* excluded: the trapped phone may be heard faintly even
  10 m away. Result: `AmbientScanCompleted(blacklisted, duration)`; the screen says how many phones
  were set aside and returns to the overview.
- Blocked states (Bluetooth off, permission missing) show the existing readiness messages with the
  same actions; the countdown starts only while scanning. Leaving the screen stops the scan.

## 2. Candidates (`/sites/:sessionId/targets`)

- Live list of devices heard now that are not surface phones (`blacklist`) and not already targets,
  ranked: Find My first (+3), still (+2: spread ≤ 4 dB over the last 30 s with ≥ 5 samples), weak
  (+1: median < −75 dBm), strong (−2: median ≥ −55 dBm).
- Each card: what it is ("Apple · Find My", "Samsung phone", "Unknown device"…), the reason in plain words
  ("Not moving · weak signal · not seen on the surface", "Moving — probably on the surface", "Very strong
  — probably right next to you"), the signal in dBm, and two actions: **Track this phone** →
  `TargetSelected(new TargetId, peripheralKey, label)` and back to the overview; **Exclude — it is on
  the surface** → `BlacklistEdited(added: [key])`.
- Hint on top: "Hold a rescuer's phone next to yours: it shows as very strong — exclude it." If no surface
  scan was done (blacklist empty), a calm note suggests doing it first. Empty list: "No phones heard yet.
  Keep the screen open."
- No distance from RSSI is shown or implied (rule 2); dBm is the measured signal.
- Identity rotation (relink) UI follows with measurement (phase 7), where a target is followed for minutes.

## 3. Domain additions (`features/targets/domain`)

`DeviceSummary` gains `median: Dbm?` and `spread: Decibels?` over the last 30 s; `AmbientPolicy` +
`surfacePhones(devices)`; `CandidatePolicy` + `rankCandidates(devices, {blacklist, targets})` →
`TargetCandidate {device, still, strength, onSurfaceList}`; use cases `CompleteAmbientScan`,
`ExcludeDevice`, `SelectTarget` append the events through `SessionStore`.

## 4. Overview

"Find the phones on the surface" and "Choose the phone to search for" become tappable for open searches;
done when the blacklist is not empty / a target exists ("Done · 3 phones set aside", "Done · Apple · Find
My").

## 5. Testing

Domain: surface rule (threshold, sample minimum), ranking order and reasons, median/spread windows.
Providers: ambient controller with a fake sample stream and a fake clock — countdown, completion event,
blocked states, stop on dispose. Widgets: candidates appear, exclude moves a device to the blacklist,
track stores the target and the overview shows it; EN/TR, 200 % text.
