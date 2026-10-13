# Roadmap 11 — Export and research mode

- Date: 2026-10-13
- Status: decided by the executor under the maintainer's blanket approval (2026-10-13)
- Builds on: CLAUDE.md §1 rule 4 (offline: the app never sends anything itself) and rule 5 (the legal
  disclaimer on every export), `docs/architecture.md` §8 (`rssi_samples`: exports must hash or drop
  non-target keys), `GroundTruthRecorded` in `rubble_core`

## 1. Export (`/sites/:sessionId/export`, `features/export`)

- One step from the overview: **Export this search**. The screen first shows the disclaimer (the same
  text as onboarding) and what the files contain; **Export** writes two files to the app's temporary
  folder and opens the system share sheet (`share_plus`) — the person chooses where they go (AirDrop,
  Files, e-mail). The app itself sends nothing (rule 4).
- `beneathsos-<date>-<title>.json` (`schema: 1`): app version, export time, the disclaimer text, the
  session row (id, title, engine profile, practice, created, closed) and every event envelope as stored
  (strict JSON from `rubble_core`). Ground truth and discarded points included — nothing is dropped.
- `beneathsos-<date>-<title>-samples.csv`: `point_id, device, rssi, tx_power, company_id, t_mono_ns,
  t_wall`. `device` is the peripheral key for the search's targets (also in the events) and, for every
  other phone, `other-` + the first 12 hex digits of SHA-256(salt + key) with a random salt drawn per
  export: bystanders stay distinguishable within one file, never across files, never recoverable.
- Pure builder (`ExportBundle.build(session, events, samples, salt)` → two strings) unit-tested; the
  file + share part is a `SharePort` in `core/services`.

## 2. Research mode — ground truth and the error report (`features/research`)

- On the probability map: **Record where it was found** (a text button under the legend). The rescuer
  taps the spot on the map; the app appends `GroundTruthRecorded(target, at)` (append-only; recording
  again replaces it in the projection, the history stays).
- The map then shows the found spot (a distinct mark) and a one-line report in plain words, computed
  from the current map: "Found inside the 50 % area" / "inside the 90 % area" / "outside the 90 % area,
  2.5 m from it", plus "N points measured, M with a signal". Never a claim about the future — it is a
  record for field campaigns (the export carries it).
- Pure `errorReport(map, found)` → region + distance to the nearest 90 % cell (0 inside), unit-tested.

## 3. Testing

Export: target keys kept, bystander keys hashed and stable within one export, different salt → different
hashes, CSV escaping of titles, JSON round-trips through `EventEnvelope.fromJson`, disclaimer present; the
screen shows the disclaimer before exporting and calls the share port with both files. Research: report
for inside 50 %, inside 90 %, outside with distance; recording appends the event and shows the report;
EN/TR, 200 % text.
