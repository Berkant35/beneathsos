#!/usr/bin/env bash
# Runs a command in every local BeneathSOS repo. Usage: tools/dev.sh analyze|format|test|get|check
# check = dependency rules between repos (CLAUDE.md §2) + l10n completeness (tools/check).
set -euo pipefail
HUB="$(cd "$(dirname "$0")/.." && pwd)"
cmd="${1:?analyze|format|test|get|check}"
if [ "$cmd" = check ]; then
  ( cd "$HUB/tools/check" && fvm dart pub get >/dev/null && fvm dart run bin/check.dart "$HUB" )
  exit
fi
for dir in "$HUB"/packages/* "$HUB"/apps/*; do
  [ -f "$dir/pubspec.yaml" ] || continue
  echo "── $(basename "$dir") ──"
  ( cd "$dir"
    # Flutter packages use the flutter tools; pure Dart packages (rubble_core) the dart tools.
    tool=dart; grep -q "sdk: flutter" pubspec.yaml && tool=flutter
    case "$cmd" in
      get)     fvm $tool pub get ;;
      format)  fvm dart format --set-exit-if-changed . ;;
      analyze) fvm $tool analyze --fatal-infos ;;
      test)    if [ -d test ]; then fvm $tool test; else echo "no tests"; fi ;;
      *) echo "unknown command $cmd"; exit 2 ;;
    esac )
done
