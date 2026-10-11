# 0013. Thin notifiers: ports and use cases

- Status: Accepted
- Date: 2026-10-11

## Context

After the field-test prototype, two providers held most of the logic:

- `ScanController` (156 lines) mixed the permission policy, an iOS adapter quirk, keeping the screen
  awake, reacting to Bluetooth changes and mapping everything to UI state. Each new precondition
  (e.g. "warn below 10 % battery") would have been another `if` in `start()`.
- `DeviceTable` (130 lines) held the tracking rules (warm-up, "gone after 15 s"), a timer reading the
  wall clock, and a `version` counter so the UI would rebuild even though mutable objects leaked out.
  The "gone" rule had no test.

These would have grown into god classes as measurement and target selection arrive.

## Decision

| Layer | Contains | Must not contain |
|---|---|---|
| `presentation/providers` | call a use case, map the result to UI state, wire streams and lifecycle | business rules, precondition chains, platform quirks |
| `domain/` | use cases, pure rule classes, result types, **ports** (abstract interfaces) | Flutter, Riverpod, plugins, `dart:io` |
| `data/` + `core/services` | port implementations, platform quirks | UI state, business decisions |

- A notifier method is *call → map → assign state*. Limits: notifier ≤ ~100 lines, method ≤ ~30.
- New rules are new classes added to a list (e.g. `ScanPrecondition`), not new `if`s (open/closed).
- Domain code depends on ports; providers bind implementations; tests replace ports, not plugins.
- Time is a parameter of domain code (`tick(nowMillis)`), never read inside it.

## Alternatives

- **Logic in notifiers** — common in Riverpod apps and fine for small ones; rejected here because rules
  could not be tested without Riverpod and the classes were already growing.
- **Full clean architecture with repositories for everything** — more ceremony than the app needs;
  ports are added only where a rule needs an outside capability.

## Consequences

- `ScanController` 156 → 85 lines; `DeviceTable` (130) replaced by `TrackedDevices` (46) plus a pure
  `DeviceTracker`. Tests grew from 15 to 52; the rules run as plain Dart tests in milliseconds.
- The iOS "unknown until ready" wait now lives in `BleService`, where platform knowledge belongs.
- More files per feature; each has one reason to change.

## References

- `CLAUDE.md` §4 "Layer responsibilities"; app commits `refactor(scanning)` and `refactor(targets)`.
