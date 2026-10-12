# Roadmap 1.2c — Countdown ring and `BeneathScaffold` in `beneathsos_ui`

- Date: 2026-10-12
- Status: decided by the executor under the maintainer's standing instruction "continue until I say
  stop, never ask" (2026-10-12); every decision below cites the doc it follows
- Roadmap: phase 1, step 1.2c (closes 1.2)
- Builds on: [1.2b spec](2026-10-12-status-banner-and-card-design.md), `docs/architecture.md` §5.3 and
  §11 (15 s measurement, identity-rotation countdown), `docs/design/accessibility.md`

## 1. Purpose and success

The measurement screen (phase 7) shows a 15 s countdown; the identity-rotation warning (phase 6) counts
down minutes. Both need one calm, legible countdown. `AppScaffold` moves into the package so every
BeneathSOS screen frame comes from the design system (roadmap 1.2c).

**Success:** `CountdownRing` and `BeneathScaffold` exist in `beneathsos_ui` 0.3.0 with tests and goldens;
the app uses `BeneathScaffold` everywhere `AppScaffold` was used; the 1.2b deferred minors that touch
these files are fixed; TestFlight build `VALID`.

**On the phone:** no visible change except screen-reader headings (card titles and the home headline are
announced as headings). The countdown ring first appears on a real screen in phase 7; it is visible in
the goldens and in the component catalogue (1.3). This is stated up front because the maintainer
expects a visible change after each step (`tasks/lessons.md`).

## 2. `CountdownRing`

`CountdownRing({required Duration total, required Duration remaining, required String semanticLabel, double size = 160})`

- **Drawing:** a full track circle in `outlineVariant` and a progress arc for the remaining fraction,
  clockwise from 12 o'clock, stroke 12 at size 160 (scales with size), round caps; the remaining time in
  the centre with `BeneathTokens.numeric` (bold tabular figures, so digits never jump).
- **Colour:** the arc uses **`primary`** (navy light / light navy dark), not the accent. The ring carries
  information, and orange on the light background is 2.4 — below the 3:1 non-text minimum
  (`docs/design/accessibility.md`). Text uses `onSurface`.
- **Centre text:** whole seconds under one minute (`12`), `m:ss` from one minute (`13:05`); digits only,
  so no localisation is needed in the package. Remaining time is clamped to `0…total`.
- **Reduce motion:** "animations that carry information (a countdown) become a simple indicator"
  (`accessibility.md`). With `MediaQuery.disableAnimations` the arc is not drawn; the number stays,
  inside the track circle. The ring itself never animates between values — the caller rebuilds it, so
  the progress moves in steps.
- **Screen readers:** `semanticLabel` (localised by the app, e.g. "12 seconds left") is the whole
  semantics of the widget; it is not a live region (announcing every second would drown the screen
  reader — the app decides when to announce).
- Custom painter → golden tests (CLAUDE.md §5.7).

## 3. `BeneathScaffold`

`AppScaffold` moves to the package unchanged in behaviour and is renamed `BeneathScaffold`: optional
title (no app bar when null), actions, bottom, safe area, page padding from `BeneathSpacing.pageFor`,
max content width 720. The app deletes `lib/core/widgets/app_scaffold.dart` and uses
`BeneathScaffold`; `CLAUDE.md` §5.3 and `docs/architecture.md` §3 are updated.

## 4. 1.2b deferred minors folded in

- `BeneathCard` title is a semantics header; the home headline is a semantics header.
- `CheckReadiness` maps the impossible `ScanStarted` / `StartFailed` to `ReadinessFailed` (never a
  silent "ready").
- Home 200 % small-phone tests also render the longest blocked message (Turkish "unsupported").
- The "Checking…" state is asserted on the home screen (text and hourglass icon).

Not folded: the golden tolerance (widget tests already pin the small glyphs) and the `bannerFor` length
(a pure mapping table).

## 5. Testing and release

**Package:** ring — fraction drawn for 15 s of 15 s / 7.5 s / 0 s (painter values), centre text `15`,
`8`, `0`, `1:00`, `13:05`, clamping (negative and above total), reduce motion draws no arc, semantics label
only, not a live region, goldens light/dark (full, half, reduce motion); scaffold — the 1.2a/2b
`AppScaffold` tests move to the package; card title header semantics.

**App:** all screens use `BeneathScaffold`; headline header semantics; readiness mapping of impossible
results; longest-message 200 % test; Checking assertion; existing tests pass.

**Release:** package `0.3.0`, green `ci` + `goldens`, tag `v0.3.0`, app on `v0.3.0`, fresh clone check,
APK, push, TestFlight `VALID`, roadmap 1.2 ✅ (1.2c), todo, issue #7 closed (1.2 complete).
