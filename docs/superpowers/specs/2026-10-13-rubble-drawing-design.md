# Roadmap 5 — Rubble drawing: `rubble_canvas` and the outline step

- Date: 2026-10-13
- Status: decided by the executor under the maintainer's standing instruction "continue"; creating the
  public repository `Berkant35/rubble_canvas` waits for the maintainer's explicit yes (until then the
  package is developed locally and the app build cannot ship it)
- Builds on: `CLAUDE.md` §2 (`rubble_canvas` may depend on Flutter and `rubble_core` only — not
  `beneathsos_ui`, not Riverpod), `docs/architecture.md` §5.3, events `RubblePolygonSet` and `ScaleSet`
  (`factor`, `ScaleSource.steps|tape|estimate`: "multiplies drawn lengths"), the 1.4 site mockup
  ("Walk around the rubble and tap each corner", edge lengths on the sides)

## 1. Purpose

The rescuer sketches the rubble footprint quickly, with gloves, on a metric grid, then corrects the scale
with one real measurement. The engine needs the outline in metres; nobody has a plan of a collapsed
building.

## 2. Drawing model (decided)

1. A **1 m grid** (5 m major lines) on a 100 × 100 m workspace; pinch to zoom (0.3×–8×), drag with one
   finger on empty space to pan.
2. **Tap** adds a corner at the end of the outline (snapped to 0.5 m); only a tap that snaps exactly
   onto an existing corner adds nothing. **Drag** a corner handle (touch radius 24 px) to move it
   (snapped) — only with one finger down: a second finger never starts a corner drag and undoes one in
   progress, so pinching over the outline never distorts it. **Undo** removes the last change (a corner
   dragged away and back leaves no step); **Clear** starts again (asks first when there are ≥ 3 corners).
   **Back** with unsaved corners asks first (app bar, Android, iOS swipe).
3. Each side shows its length (drawn length × current scale, one decimal, "m"); the summary under the
   canvas shows corners, perimeter and area, or what is wrong (fewer than 3 corners, two corners closer than
   0.1 m, crossing sides, no area) — never a silent failure.
4. **Outline done** validates and appends `RubblePolygonSet` (only when the outline changed).
5. **Scale** (next screen, optional): the longest side is pre-selected (tap another side to choose it);
   "How long is this side really?" in metres (0.5–500) and how it was measured: *tape measure*, *paced
   steps*, *estimate*; Save appends `ScaleSet(factor = real / drawn, source)`; **Skip** keeps the current
   scale. A factor below ×0.5 or above ×2 is probably a typo: "Is this right?" before it is stored.
   The overview shows the outline step as done with its area ("216 m²").

No location claim is involved (rule 1); the outline is the rescuer's own sketch.

## 3. Package `rubble_canvas` (Flutter + `rubble_core`)

Pure parts (unit-tested):
- `CanvasGeometry` — workspace in metres, `pixelsPerMeter`, `Offset toCanvas(SitePoint)`,
  `SitePoint toSite(Offset)`, `SitePoint snap(SitePoint, Meters step)`.
- `OutlineDraft` — immutable: `corners`, `add`, `move(index, to)`, `removeLast`, `clear`, `undo` (history),
  `cornerNear(SitePoint, Meters tolerance)`, `edgeNear(...)`, `problem` (`RubblePolygon.validate` when ≥ 3
  corners, else `TooFewCorners`), `polygon` (null while invalid), value equality.

Widgets and painters (golden-tested; colours and text styles come from a `RubbleCanvasStyle` passed by
the app — no design-system dependency):
- `SiteGridPainter`, `OutlinePainter` (sides, corner handles, length labels via an injected
  `String Function(Meters)`, an optional highlighted side).
- `OutlineEditor` — `InteractiveViewer` around the metric canvas; corner drags use raw pointer events
  (`Listener`) and switch the viewer's panning off while one finger is on a corner; every pointer is
  tracked so a pinch never drags a corner; taps add corners. Reports changes with `ValueChanged<OutlineDraft>`; semantics label summarises corners and
  perimeter (the visual canvas has a text twin in the app).
- `EdgePicker` — read-only outline; tap a side to select it (for the scale step).

## 4. App (`features/site_drawing`)

- Routes `/sites/:sessionId/draw` and `/sites/:sessionId/scale` (children of the overview, so Back
  returns there).
- `OutlineDraftController(sessionId)` notifier: starts from the stored outline (or empty); the screen
  shows the editor full-width (`BeneathScaffold(padded: false)`), hint banner, summary, Undo / Clear /
  **Outline done**. `SetOutline` and `SetScale` use cases append the events through `SessionStore`.
- Overview: the outline step becomes tappable and shows the area when done.
- Strings EN + TR; 200 % text keeps the buttons and summary readable (the canvas shrinks, never the text).

## 5. Testing

Package: geometry round trip and snapping; draft add/move/undo/clear, `cornerNear` tolerance, problems for
each invalid case; goldens for grid and outline (light/dark style, labels) tagged `golden` (macOS CI);
widget tests: tap adds a snapped corner, dragging a handle moves it, a drag on empty space pans (the
corner does not move), pinch zooms. App: tap corners → Outline done → `RubblePolygonSet` stored and the
overview shows the area; invalid outline → message, nothing stored; scale save → `ScaleSet` with the
right factor and source; Skip stores nothing; reopening the draw screen shows the stored outline.
