# Roadmap 1.4 — Flow mockups (rescuer and victim journeys)

- Date: 2026-10-12
- Status: **proposal for the maintainer's review** — roadmap 1.4 says the mockups are "reviewed before
  any screen is built". Prepared by the executor under "continue until I say stop"; every screen below
  waits for the maintainer's yes or changes.
- Builds on: `docs/architecture.md` §5 (flows), §11 (edge cases), `docs/roadmap.md` phases 4–10,
  `docs/design/` (principles, voice, accessibility), `beneathsos_ui` 0.3.1

## 1. Form

Mockups are real Flutter screens built from `beneathsos_ui` components with static sample data, in the
catalogue (`widgetbook/lib/flows/`, category "Flows (mockups)"). They render in light and dark, at 200 %
text and on the small-phone viewport, and are exported as PNGs (golden tests) for review. Code-first:
an approved mockup becomes the starting point of its phase, not a picture to redraw.

Sample strings are English (catalogue rule); every screen also lists its Turkish text in the review
sheet so tone and length can be judged.

## 2. Screens

| # | Screen | Phase | What it shows | Primary action | Product rules checked |
|---|---|---|---|---|---|
| 1 | First-run notice | 4 | What the app can and cannot do; "supports, never replaces professional rescue; call 112"; independence statement | "I understand" | Legal disclaimer on first launch (rule 5) |
| 2 | Rubble site | 4–5 | Site name, hint "Walk around the rubble and tap each corner", metric canvas with the drawn outline and edge lengths | "Outline done" | Local metres, no map/GPS (offline) |
| 3 | Ambient scan | 6 | 30 s `CountdownRing`, "Stand 10 m away from the rubble", count of surface devices that will be ignored | — (runs by itself) | Surface phones are blacklisted, not targets |
| 4 | Choose the target | 6 | Candidates ranked: Find My / stationary / weak, each with signal level and reason; "Hold a phone next to yours to exclude it" | "Track this phone" | Never "victim found"; a target is a device |
| 5 | Measurement | 7 | 15 s `CountdownRing`, "Hold the phone still at this point", stillness state, "signal heard / no signal" | — (runs by itself); "Discard" secondary | "No signal" is information, not failure (rule 3) |
| 6 | Probability map | 9 | Outline, heat (placeholder scale), 50 % "most likely area" and 90 % region labelled, measured points (heard filled, not heard hollow), suggested next point, target tab, identity-rotation `StatusBanner` | "Measure here" | Never a single pin without its region (rule 1); no depth (rule 2) |
| 7 | Victim mode | 10 | Full-bleed, very large text: "Your phone is sending a help signal", "Stay calm. Save battery.", "Tap 3 times when you hear rescuers", battery %, SOS sound toggle; dimmed | "SOS sound" toggle | Simplest screen, dark, no animation (principle 7) |

The heat-scale colours are placeholders (navy tints) until phase 9 chooses a perceptually uniform,
colour-blind-safe scale (`docs/design/principles.md`).

## 3. Review questions for the maintainer

Each screen: keep / change. Plus: (a) is the target ranking reason text understandable to an untrained
volunteer; (b) on the map, should the suggested next point be a button on the map or only the primary
action; (c) victim mode: SOS sound on by default or off (battery vs being found).

## 4. Verification

The catalogue test opens every new use case in light and dark without exceptions; golden PNGs (macOS)
for the seven screens in light and dark; a review sheet image sent to the maintainer.
