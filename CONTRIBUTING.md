# Contributing to BeneathSOS

Thanks for helping! This project may be used in real disasters, so correctness beats speed.

1. Read `CLAUDE.md` (rules — they apply to humans too) and `docs/architecture.md`.
2. Install FVM, then `fvm install` and `dart pub global activate melos`.
3. `fvm dart pub get` at the repo root (pub workspace).
4. Open an issue first for anything bigger than a small fix, so the design can be agreed.
5. Branch from `main` (`feat/...`, `fix/...`), use Conventional Commits, open a PR with the template.
6. CI must be green; a code owner reviews every PR. Nobody — including maintainers — merges
   without review, and there is no auto-merge.

Engine changes must keep `tools/sim` golden fixtures passing or update them with justification.
New user-facing text needs both `app_en.arb` and `app_tr.arb` entries.
