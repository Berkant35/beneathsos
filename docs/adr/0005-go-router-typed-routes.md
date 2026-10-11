# 0005. go_router with typed routes

- Status: Accepted
- Date: 2026-09-27

## Context

The app will have a small but deep navigation tree (home → site → drawing → measurement → map) and,
in v2, deep links for joining a shared workspace by QR code. String paths spread across screens break
silently when a route changes.

## Decision

- `go_router` with `go_router_builder` typed routes (`@TypedGoRoute`, `GoRouteData` with the generated
  `$Route` mixin). Screens navigate with `SomeRoute(...).go(context)`.
- Only `lib/core/router/` knows paths. `/join` is reserved for the v2 shared workspace.

## Alternatives

- **auto_route** — capable, but another code generator and API next to Riverpod's; go_router is the
  Flutter team's package and is used in Qulo.
- **Navigator 2.0 directly** — too much boilerplate for the value.
- **String-based go_router calls** — rejected: typos and missing parameters are only found at runtime.

## Consequences

- Route parameters are type-checked at compile time.
- Code generation is required (shared with Riverpod's `build_runner` step).
- Deep links can be added without touching screens.

## References

- `apps/beneathsos_app/lib/core/router/app_router.dart`; go_router 18, go_router_builder 4.5.
