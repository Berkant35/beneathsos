# 0014. App lifecycle is owned by its consumers

- Status: Accepted
- Date: 2026-10-11

## Context

When the user leaves the app to grant a permission in Settings and comes back, the scanner must
retry. The first implementation (copied from the pattern in Qulo) made `app.dart` observe the
lifecycle and call `scanController.onAppResumed()`. That meant the root widget depended on a feature,
every new lifecycle-aware provider required editing `app.dart`, and forgetting to do so produced a bug
that only shows when returning from Settings.

## Decision

- `appLifecycleProvider` (`core/services`) exposes app lifecycle changes as a stream, wrapping
  Flutter's `AppLifecycleListener`.
- A provider that must react listens to it inside its own `build()` and only acts when it is in a
  blocked state (e.g. missing permission, Bluetooth off).
- `app.dart` sets up theme, localisation and routing only; it never calls into features.

## Alternatives

- **Root observer calling features** — the original pattern; rejected for the reasons above.
- **`WidgetsBindingObserver` inside each provider** — couples providers to Flutter bindings and is hard
  to test.

## Consequences

- Features are self-contained; adding a lifecycle-aware provider touches only that provider.
- Tests send fake lifecycle events through a stream.
- Combined with Riverpod 3 pausing unwatched providers ([0004](0004-riverpod-state-management.md)),
  a provider reacts only while some screen watches it — the desired behaviour.

## References

- `apps/beneathsos_app/lib/core/services/app_lifecycle.dart`; `CLAUDE.md` §4.
