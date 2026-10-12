# Roadmap 1.3 — Component catalogue (Widgetbook)

- Date: 2026-10-12
- Status: decided by the executor under the maintainer's standing instruction "continue until I say
  stop, never ask" (2026-10-12). **Publishing the catalogue to GitHub Pages waits for the maintainer's
  explicit yes** (a repository setting and a new public site).
- Roadmap: phase 1, step 1.3

## 1. Purpose and success

Contributors, designers and reviewers can browse every `beneathsos_ui` component in light and dark, at
large text sizes and with "reduce motion", without running the app. It is the visual source of truth
next to the goldens.

**Success:** a Widgetbook app inside the `beneathsos_ui` repository builds for the web in CI on every
pull request; every public component has use cases; theme, text-scale and reduce-motion are switchable.
After the maintainer's yes, the web build is deployed to GitHub Pages and the README links it.

**On the phone:** nothing changes (the catalogue is a web page for people, not part of the app).

## 2. Decisions

| Topic | Decision | Why |
|---|---|---|
| Location | `packages/beneathsos_ui/widgetbook/` — a separate Flutter app with `beneathsos_ui: path: ..` | The catalogue changes with the components (same pull request); it is not part of the published package (`.pubignore`) |
| Version | `widgetbook` 3.25.0 (latest, Flutter ≥ 3.44), no code generation | Fewer moving parts; use cases are plain functions |
| Addons | Theme (BeneathSOS light / dark), text scale (100 %, 150 %, 200 %), reduce motion (on / off), viewport (phone 375 × 667 and 402 × 874) | The accessibility targets of `docs/design/accessibility.md` |
| Use cases | Logo (symbol, lock-up); PrimaryButton / SecondaryButton (with and without icon, disabled); StatusBanner (ready, attention, blocked, tappable, long message); BeneathCard (plain, with title and icon, tappable); CountdownRing (knob: remaining seconds of a 15 s total, and a 15 min total); BeneathScaffold (with and without title); Typography (all text roles); Colours (palette swatches with their contrast ratios) | One use case per state a reviewer has to judge |
| Strings | English demo text inside the catalogue (it is a developer tool, not the app) | The app's ARB rule applies to the app |
| CI | A package workflow `catalogue.yml` (pull request + push to `main`) tests and builds the catalogue for the web; `ci.yml` stays the shared hub template | A broken catalogue fails the pull request; the template is overwritten by `tools/sync_governance.sh` |
| Publishing | A deploy job in `catalogue.yml` (push to `main` only, SHA-pinned actions, `pages: write` + `id-token: write` only on the deploy job) deploys to GitHub Pages — added only after the maintainer says yes | Public site + repository setting |

## 3. Testing

- `widgetbook/test/catalogue_test.dart`: the catalogue builds, and every directory entry renders in
  light and dark without exceptions (each use case pumped once).
- CI web build of the catalogue.
