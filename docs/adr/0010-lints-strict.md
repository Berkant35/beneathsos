# 0010. Lints: Flutter's recommended set, strict modes, infos are failures

- Status: Accepted
- Date: 2026-09-27

## Context

Many people may contribute, and the maintainer asked for Flutter's own recommended rules as the
base. Warnings that are allowed to pile up stop being read.

## Decision

- Base: `package:flutter_lints/flutter.yaml`.
- Analyzer strict modes: `strict-casts`, `strict-inference`, `strict-raw-types`.
- Extra rules for async safety and clarity (e.g. `unawaited_futures`, `discarded_futures`,
  `cancel_subscriptions`, `close_sinks`, `always_use_package_imports`, `directives_ordering`,
  `exhaustive_cases`, `no_default_cases`, `prefer_single_quotes`).
- `riverpod_lint` as an analyzer plugin; packages add `public_member_api_docs`.
- CI runs `flutter analyze --fatal-infos`: an info fails the build. Rules are not weakened to make
  CI pass; a justified `// ignore:` needs a reason comment.

## Alternatives

- **very_good_analysis** — stricter, but the maintainer chose Flutter's recommended base.
- **Warnings only** — infos accumulate and are ignored.

## Consequences

- Real issues were caught early: unclosed stream controllers in test fakes, import order after file
  moves, constructor style (which led to Dart's private named parameters), redundant arguments.
- Deprecated rules must be removed when Flutter updates (e.g. `unnecessary_await_in_return`).

## References

- `analysis_options.yaml` in each repository; `CLAUDE.md` §6.
