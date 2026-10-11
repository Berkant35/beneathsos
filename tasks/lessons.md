# Lessons

Rules learned from corrections. Newest first. Format: **Pattern** → rule that prevents it.

## 2026-09-27 — Went too fast on code; maintainer lost track
**Pattern:** After the maintainer said "go to the next step", I built the plugin, the app skeleton,
the whole field-test feature, installed it on the phone and committed — without explaining or
asking between steps. The maintainer could not follow what the code does.
**Rule:** In BeneathSOS, code work is step by step. For each step: (1) explain what and why in
plain Turkish, (2) show the small plan and wait for approval, (3) implement only that step,
(4) walk through the changed files, (5) verify and show the result. Never chain several steps.
Research/docs may still run ahead; code, device installs and commits may not.

## 2026-10-11 — Unquoted heredoc ran Markdown backticks as shell commands
**Pattern:** A Python edit script passed through `<<EOF` (unquoted) contained Markdown with
backticks; the shell executed them (`main`, `release/*`), the replacement strings no longer matched,
and the docs part of the commit was silently empty.
**Rule:** Always use `<<'EOF'` for scripts that contain Markdown or code. Make replacement helpers
`assert old in text` so a non-match fails loudly instead of committing a no-op.
