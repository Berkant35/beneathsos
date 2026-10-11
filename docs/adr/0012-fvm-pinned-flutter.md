# 0012. Flutter pinned with FVM

- Status: Accepted
- Date: 2026-09-27

## Context

The current packages (Riverpod 3, go_router 18, drift 2.35) require Dart 3.12–3.13, while the
maintainer's machine ran Flutter 3.35 for another project. Different Flutter versions between
developers or CI cause confusing build and lint differences.

## Decision

- Every repository has `.fvmrc` pinning the same Flutter version (currently 3.47.5, Dart 3.13).
- Commands always run through `fvm flutter` / `fvm dart`; CI reads the version from `.fvmrc`.
- Upgrades are deliberate: bump `.fvmrc` in all repositories together and fix what breaks.

## Alternatives

- **Global Flutter installation** — couples projects; upgrading one breaks another.
- **Version only in documentation** — not enforced.

## Consequences

- Other projects on the same machine are unaffected.
- Upgrades surface toolchain changes explicitly (e.g. NDK and SDK platform versions on Android).

## References

- `.fvmrc`; `tools/templates/ci.yml`.
