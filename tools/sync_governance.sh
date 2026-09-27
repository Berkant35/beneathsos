#!/usr/bin/env bash
# Copies shared governance files from the hub into every local repo (run after editing them).
set -euo pipefail
HUB="$(cd "$(dirname "$0")/.." && pwd)"
for dir in "$HUB"/packages/* "$HUB"/apps/*; do
  [ -f "$dir/pubspec.yaml" ] || continue
  mkdir -p "$dir/.github/workflows" "$dir/.github/ISSUE_TEMPLATE" "$dir/.github/rulesets"
  cp "$HUB/.github/CODEOWNERS" "$HUB/.github/pull_request_template.md" "$HUB/.github/dependabot.yml" "$dir/.github/"
  cp "$HUB/.github/ISSUE_TEMPLATE/bug_report.md" "$dir/.github/ISSUE_TEMPLATE/"
  cp "$HUB/.github/rulesets/main.json" "$dir/.github/rulesets/"
  cp "$HUB/tools/templates/ci.yml" "$dir/.github/workflows/ci.yml"
  cp "$HUB/SECURITY.md" "$HUB/CONTRIBUTING.md" "$HUB/LICENSE" "$HUB/.fvmrc" "$dir/"
  echo "synced $(basename "$dir")"
done
