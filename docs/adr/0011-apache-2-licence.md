# 0011. Apache-2.0 licence

- Status: Accepted
- Date: 2026-09-27

## Context

BeneathSOS is non-profit, but its impact depends on others adopting it: emergency-management agencies,
NGOs, operators and companies may want to integrate the scanner, the engine or the whole app — some
inside closed government or commercial apps. The research found active patents in the area of
locating phones under rubble, so contributors' patent rights matter.

## Decision

All repositories are licensed under **Apache License 2.0**.

## Alternatives

- **MIT** — simple and permissive, but no explicit patent grant.
- **GPL / AGPL** — keeps derivatives open, but blocks integration into closed agency apps, which is
  exactly the adoption path we want.

## Consequences

- Anyone may use, modify and redistribute, including commercially, with attribution and the licence
  notice.
- Contributors grant a patent licence for their contributions.
- Dependencies must stay compatible; this was one reason not to use a package that requires a
  commercial licence ([0007](0007-own-ble-plugin.md)).

## References

- `LICENSE` in each repository.
