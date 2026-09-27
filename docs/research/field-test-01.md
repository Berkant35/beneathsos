# Field test 01 — what can a phone see? (M1)

Goal: answer with real data before building the rescuer UI.

| # | Question | How |
|---|---|---|
| Q1 | Does an **iOS** scanner see an iPhone that has no app (Find My / Nearby)? | iPhone B in airplane mode + Bluetooth on (offline → Find My beacon). iPhone A runs the app: is there an `Apple · Find My` row? Repeat with an Android scanner. |
| Q2 | How often does the identity rotate? | Mark iPhone B as target, keep scanning ≥ 35 min, record CSV. Identity log shows `Disappeared` / `Appeared` pairs; note the timer value at each rotation. |
| Q3 | Does relink work? | After a rotation, does "Possible new identity" propose the right key? |
| Q4 | RSSI vs material | Record with markers: B on open ground at 1 m / 3 m; under 1 concrete block; under a stack of bricks; in a car boot. 30 s per position, marker before each. |
| Q5 | Screen off / app background | Lock the scanner phone for 1 min while recording — how many samples arrive? (iOS expected: almost none.) |

Record per run: phone models, OS versions, weather/location, CSV file name. Results go below.

## Results
_(pending)_
