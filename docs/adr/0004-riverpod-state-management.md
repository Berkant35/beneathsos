# 0004. Riverpod 3 with code generation for state management

- Status: Accepted
- Date: 2026-09-27

## Context

Most state in BeneathSOS is derived from streams: batches of BLE samples arrive every 250 ms, the
adapter state changes, the app goes to the background and back. Several features read the same
sources (scanning, target selection, measurement), and every rule must be testable with fake inputs.
The maintainer's other production app (Qulo) uses Riverpod and go_router, so one mental model across
projects lowers the cost of switching.

## Decision

- `flutter_riverpod` 3 with `riverpod_annotation` / `riverpod_generator` (`@riverpod`) for all app
  state. No `setState` for business state, no `ChangeNotifier`, no global singletons.
- Providers are thin (see [0013](0013-thin-notifiers-ports-use-cases.md)); rules live in pure Dart.
- `riverpod_lint` runs as an analyzer plugin.

## Alternatives

- **Bloc / Cubit** — explicit events and good tooling; rejected as a second mental model next to Qulo,
  with more boilerplate for stream-derived state.
- **Provider** — older, weaker composition and testing story than Riverpod.
- **Plain `setState` + inherited widgets** — does not scale past one screen and is hard to test.

## Consequences

- Tests replace dependencies with `overrideWithValue` / `overrideWith`; the controller tests run on
  fake ports without Flutter widgets.
- Code generation adds a `build_runner` step (never with `--delete-conflicting-outputs`).
- **Riverpod 3 pauses providers nobody listens to.** A paused provider does not receive stream or
  lifecycle events. Tests that drive such providers keep a listener with `container.listen(...)` —
  learned when a lifecycle test stayed red under `container.read`.

## References

- `apps/beneathsos_app/lib/core/scanning/presentation/providers/`
- `tasks/lessons.md`; flutter_riverpod 3.4, riverpod_generator 4.0.
