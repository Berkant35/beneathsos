# Roadmap 4 — Entry flow: onboarding, searches list, new search

- Date: 2026-10-12
- Status: decided by the executor under the maintainer's standing instruction "continue" ("devam et"
  after phase 3)
- Builds on: `docs/architecture.md` §5.1, §5.3, §6; product rule 5 (legal disclaimer on first launch);
  phase 3 (`SessionStore`, settings table); maintainer decision in 1.2b: Bluetooth permission is asked
  on the home screen at launch (so onboarding has no permission step)

## 1. Purpose

"Start a search" stops opening the sample-data preview and starts the real rescuer flow:
first-run disclaimer → list of searches → new search (site name) → the search's overview. The preview
stays reachable as "Practice with sample data". Victim mode is never behind onboarding: a trapped person
reaches `/victim` in one tap, always.

## 2. Onboarding (`/onboarding`, `features/onboarding`)

- One screen, "Before you start": what BeneathSOS does / does not do (the texts of the preview notice),
  the independence note, and **I understand**. Accepting writes `settings['disclaimer_accepted'] = '1'`
  (version of the disclaimer text) and goes to `/sites`.
- Gate: `/sites` and its children redirect to `/onboarding?from=<location>` while the disclaimer of the
  current version is not accepted. The redirect is asynchronous: it awaits the stored state (an error
  counts as "not accepted"), so a returning rescuer never sees the disclaimer again; after accepting,
  the rescuer continues to `from` (only `/sites…` locations). The provider and the disclaimer text live
  in `core/disclaimer` (used by onboarding and the practice notice).
- `SettingsStore` port in `core/settings` (`watch(key)`, `write(key, value)`) with a Drift implementation
  on the `settings` table (upsert).

## 3. Searches (`/sites`, `features/sites`)

- **List** (`/sites`): **New search** (primary), then real searches — open ones first, newest first —
  each a card: title, "started 12 Oct, 14:05", "N points measured", and "Finished" for closed ones; tap →
  overview. Empty state: "No searches yet." At the bottom, **Practice with sample data** (secondary) →
  the preview journey. Practice searches are not listed (they live on the home card).
- **New search** (`/sites/new`): one text field "Name of the site" (hint "e.g. Atatürk Cad. 12,
  Antakya"), trimmed, 1–80 characters; empty → inline error "Enter a name so you can find this search
  later."; **Create search** → `SessionStore.create(title, engineProfile: 'voided_pancake@1',
  practice: false)` → replaces the route with the overview. A double tap creates one search.
- **Overview** (`/sites/:sessionId`): title, start time, the steps of the rescuer flow with their state
  from the projection (the search itself is read with `SessionStore.watchSummary(id)`, never looked up in
  the list, which may lag behind a search created a moment ago) — outline drawn, surface phones scanned (blacklist not empty), target chosen,
  points measured (count) — each marked "Next update" while its screen does not exist yet; **Finish this
  search** (confirmation dialog from phase 3). Unknown id, a load error (also while Riverpod retries) or
  unreadable data → a calm message and a way back, never a crash or a blank screen. A failed create shows
  an inline error under the field; a failed finish a snackbar.
- `SessionStore.watchSearches()` → `Stream<List<SessionSummary>>` of real searches (open first, newest
  first); `SessionSummary.closedAt` added.

## 4. Home

- **Start a search** → `/sites` (onboarding first on the first run).
- The last-search card: Continue opens the overview for a real search, the preview map for a practice
  one.

## 5. Strings, accessibility

All new text in EN and TR (voice-and-tone: short, calm, "siz" in Turkish). Every screen scrolls at 200 %
text on a 375 × 667 phone; the text field has a visible label; error text is announced (live region).

## 6. Testing

Settings store: write then watch, upsert, unknown key → null. Gate: first "Start a search" opens
onboarding; after "I understand" → searches list; next time straight to the list; victim mode never
gated. List: empty state; open before closed; practice excluded; tap → overview. New search: empty name
error; trimmed title stored; double tap → one search; route replaced (Back from overview → list).
Overview: step states from events; unknown id message; Finish → closed and shown as finished in the list.
Home: real search Continue → overview. EN/TR, 200 % text.
