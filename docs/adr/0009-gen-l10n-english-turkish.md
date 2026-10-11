# 0009. gen-l10n (ARB), English and Turkish mandatory

- Status: Accepted
- Date: 2026-09-27

## Context

The first users are in Türkiye, the project is international and open source, and text in an
emergency app must never fall back to a placeholder or a missing key. Contributors and translators
should be able to work with standard tools.

## Decision

- Flutter's official `gen-l10n` with ARB files: `lib/l10n/app_en.arb` (template) and `app_tr.arb`,
  generated into `lib/l10n/generated/`.
- Widgets read text only through `context.l10n`. Hard-coded user-facing strings are not allowed;
  every new key is added to both files in the same change.

## Alternatives

- **Custom map-based localisation** (as in Qulo) — works, but is not understood by translation
  platforms or new contributors.
- **easy_localization / slang** — good packages, but an extra dependency where the official tool is
  enough.

## Consequences

- Placeholders are typed (e.g. `{devices}` as `int`), so wrong arguments fail at compile time.
- More languages can be added through translation platforms that read ARB.
- A completeness check (`tools/check_l10n.dart`) is still to be written; until then, review checks
  both ARB files.

## References

- `apps/beneathsos_app/l10n.yaml`; `CLAUDE.md` §5 rule 4.
