#!/usr/bin/env bash
# Runs a command in every local BeneathSOS repo. Usage: tools/dev.sh analyze|format|test|get
set -euo pipefail
HUB="$(cd "$(dirname "$0")/.." && pwd)"
cmd="${1:?analyze|format|test|get}"
for dir in "$HUB"/packages/* "$HUB"/apps/*; do
  [ -f "$dir/pubspec.yaml" ] || continue
  echo "── $(basename "$dir") ──"
  ( cd "$dir"
    case "$cmd" in
      get)     fvm flutter pub get ;;
      format)  fvm dart format --set-exit-if-changed . ;;
      analyze) fvm flutter analyze --fatal-infos ;;
      test)    if [ -d test ]; then fvm flutter test; else echo "no tests"; fi ;;
      *) echo "unknown command $cmd"; exit 2 ;;
    esac )
done
