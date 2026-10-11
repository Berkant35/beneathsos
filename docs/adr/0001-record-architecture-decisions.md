# 0001. Record architecture decisions

- Status: Accepted
- Date: 2026-10-11

## Context

BeneathSOS is an open-source project meant for real disasters. People who were not in the room —
contributors, search-and-rescue organisations, reviewers, potential partners — need to understand why
the system is built the way it is before they can trust it or change it.

Until now, decisions lived in a table at the end of `docs/architecture.md` and in chat history. A
table row says *what* was chosen but not *why*, what was rejected, or what it costs. Several decisions
were also corrected after field results (for example the Android location permission and the iOS
signing method), and that history was invisible.

## Decision

Every significant decision is recorded as an Architecture Decision Record (ADR) in `docs/adr/` of the
hub repository:

- one Markdown file per decision, numbered `NNNN-short-title.md`, listed in `docs/adr/README.md`;
- fixed sections: **Context**, **Decision**, **Alternatives**, **Consequences**, **References**;
- written in English, about one page, based on evidence from this project (measurements, simulations,
  build logs) rather than general opinion;
- records are immutable once accepted. A changed decision gets a new record; the old one is marked
  `Superseded by NNNN` and stays.

"Significant" means: hard to reverse, affects more than one package, or a newcomer would reasonably
ask "why not X?". Small implementation details stay in code comments.

## Alternatives

- **Decision table in `architecture.md` only** — compact, but loses the reasoning and the rejected
  options. Kept as a short summary that links here.
- **Wiki** — separate from the code, not reviewed in pull requests, easily outdated.
- **No written record** — decisions get re-argued, and contributors cannot tell an intentional
  constraint from an accident.

## Consequences

- Decisions are reviewable in PRs like code, and their history is visible.
- Writing a record costs time; the one-page limit keeps it small.
- `docs/architecture.md` describes the current structure; ADRs explain how it came to be.

## References

- Michael Nygard, *Documenting Architecture Decisions* (2011).
- `docs/architecture.md` — current structure and decision summary.
