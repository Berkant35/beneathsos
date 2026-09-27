## What & why

## How it was verified
- [ ] `melos run analyze` (fatal infos) ✅
- [ ] `melos run format:check` ✅
- [ ] `melos run test` ✅
- [ ] `melos run check:deps` / `check:l10n` ✅
- [ ] Screenshots / recordings for UI changes

## Rules checklist (CLAUDE.md)
- [ ] No "victim is here" wording; uncertainty always shown
- [ ] No hard-coded user-facing strings (en + tr ARB updated)
- [ ] Screens ≤ ~200 lines, widget logic in mixins, AppScaffold used
- [ ] Hardware accessed only via `core/services`
- [ ] No network calls / telemetry / secrets added
- [ ] `docs/architecture.md` updated if a boundary, event, route or table changed
