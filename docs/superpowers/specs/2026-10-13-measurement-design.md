# Roadmap 7 — Point measurement

- Date: 2026-10-13
- Status: decided by the executor under the maintainer's blanket approval (2026-10-13)
- Builds on: `docs/fizibilite-2026-09-27.md` and `docs/research/sim/circle_prob_sim.py` (per point: the
  median of ~20 readings; a point where the phone is not heard is a censored observation, threshold
  −100 dBm), product rule 3, `docs/architecture.md` §11 rows 1, 2, 3, 6, 9; events
  `MeasurementPointPlaced`, `MeasurementCompleted`, `MeasurementDiscarded`, `TargetRelinked`;
  `rubble_canvas` 0.2.0 `SiteMap`

## 1. Flow (`/sites/:sessionId/measure`)

1. The map shows the outline and the points measured so far (heard / not heard). "Stand at a spot around
   the rubble and tap where you are." A tap places the point (`MeasurementPointPlaced`) and starts the
   measurement.
2. **15 s of still time.** The phone's motion is watched (user accelerometer, gravity removed): while
   the rescuer moves (> 0.8 m/s² within the last second) the countdown pauses and says "Hold the phone
   still"; it resumes when still. Readings stream in; the screen shows "Signal heard" or "Not heard yet"
   per target — never a distance.
3. At the end, for every target: `SignalHeard(median, samples)` from its readings during the still time,
   or `NoSignal` (rule 3); `MeasurementCompleted(point, duration, readings)`; raw readings of the
   window go to `rssi_samples` (`addSamples`). The map shows the new point.
4. **Discard this point** while measuring → `MeasurementDiscarded(userDiscarded)`. Leaving the screen
   while measuring → `MeasurementDiscarded(interrupted)` (row 6: never a half measurement).
5. Measuring needs an outline and at least one target; otherwise the screen says which step to do first.

## 2. Identity rotation (row 1)

While measuring, if a target's identity has gone silent and `suggestRelinks` finds a new identity
(appeared within 30 s, RSSI within 8 dB), a banner asks "The phone may have changed its Bluetooth
identity. Is this it?" — **Yes, same phone** → `TargetRelinked(target, from, to)`; readings of the new
identity count from then on. The rescuer decides; the app never relinks on its own.

## 3. Domain (`features/measurement/domain`)

`MeasurementPolicy` (15 s, 0.8 m/s², 1 s window), `summarizeReadings(targets, samples)` →
`List<TargetReading>` (implausible RSSI dropped), `StillnessTracker` (feeds accelerations, answers
`isStill(now)`), sealed `MeasurementState` (`ChoosingPoint`, `Measuring(point, remaining, moving,
heard)`, `SavingMeasurement`, `MeasurementSaved`, `MeasurementNotSaved`), use cases `PlacePoint`,
`CompleteMeasurement`, `DiscardPoint`, `RelinkTarget`. Hardware: `MotionPort` in `core/services`
(`sensors_plus`), overridden in tests.

## 4. Overview

"Measure at points around the rubble" opens the screen when an outline and a target exist ("N points
measured · M heard").

## 5. Testing

Domain: summary per target (median, sample count, no signal, implausible values), stillness window.
Widgets (fake motion and sample streams, pumped seconds): tap places and measures 15 s; moving pauses the
countdown; heard / not-heard points stored and drawn; discard and leaving store `MeasurementDiscarded`;
relink banner stores `TargetRelinked`; EN/TR, 200 % text.
