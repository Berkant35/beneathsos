# Entry flow (roadmap 4) Implementation Plan

> Executed inline (superpowers:executing-plans) under the maintainer's standing instruction; TDD per
> task (RED watched first), one fresh opus review at the end, TestFlight after the app commits.

**Goal:** "Start a search" leads through a one-time disclaimer to a list of real searches, a new-search
form and a search overview; the preview stays as "Practice with sample data".

**Spec:** `docs/superpowers/specs/2026-10-12-entry-flow-design.md`

## Global constraints

`CLAUDE.md` §4–5 (feature-first, thin notifiers, screens ≤ ~200 lines, logic in mixins, one public
widget per file, no hard-coded strings, `BeneathScaffold`), typed routes only in `core/router`, EN + TR in
the same change, never `--delete-conflicting-outputs`, gate commits on each command's exit code.

## Review focus

1. Victim mode reachable in one tap on every launch, never redirected.
2. Disclaimer gate while the settings stream is still loading (no flash of the list, no loop).
3. Double tap on "Create search" → exactly one session.
4. Long site names (80 characters, Turkish) at 200 % text on a small phone.
5. Back navigation: overview ← list ← home; after creating, Back from the overview goes to the list,
   not to the form.

## Tasks

1. **Settings store** — `core/settings/{domain/settings_store.dart, data/drift_settings_store.dart,
   presentation/providers/settings_providers.dart}`; tests: write/watch/upsert/unknown key.
   Commit `feat(settings): settings store on the settings table`.
2. **Store: searches list** — `SessionSummary.closedAt`, `SessionStore.watchSearches()`; tests: real
   only, open first, newest first, closed flagged, follows changes.
   Commit `feat(sessions): watch the list of real searches`.
3. **Onboarding + gate** — `features/onboarding` (screen, `disclaimerAcceptedProvider`,
   `OnboardingController.accept`), routes `/onboarding`, `/sites` (placeholder list) with redirect;
   home "Start a search" → `/sites`; widget tests for the gate and victim mode.
   Commit `feat(onboarding): first-run disclaimer before the rescuer flow`.
4. **Searches list + new search + overview** — `features/sites` screens, widgets, mixins, providers
   (`searchesProvider`, `NewSearchController` with double-tap guard, `searchOverviewProvider(id)`);
   home card Continue for real searches; preview link; ARB EN/TR; widget tests per spec §6.
   Commit `feat(sites): list, create and open real searches`; push; TestFlight.
5. **Docs** — architecture §5.1/§6/§7, roadmap 4, todo. Hub commit.

**Final** — fresh opus review; Critical/Important fixed RED→GREEN; TestFlight if `lib/` changed.
