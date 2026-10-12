# 1.3 — Widgetbook Catalogue Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** A Widgetbook web catalogue of every `beneathsos_ui` component, tested and built in CI.

**Architecture:** `packages/beneathsos_ui/widgetbook/` is a Flutter web app (`beneathsos_ui: path: ..`,
`widgetbook` 3.25.0, no codegen). Use cases are plain functions grouped per component; addons switch
theme, text scale, reduce motion and viewport.

**Spec:** `docs/superpowers/specs/2026-10-12-widgetbook-catalogue-design.md`

## Global Constraints
- Same toolchain and gates as the package (format, `analyze --fatal-infos`, tests by exit code).
- The catalogue is excluded from the published package (`.pubignore: widgetbook/`).
- Actions pinned to commit SHAs, `permissions: contents: read`; no deploy job until the maintainer says yes.

## Review Focus
- **Every use case renders in light and dark without exceptions** — pinned by the catalogue test (Task 1).
- **200 % text** in the catalogue does not break the catalogue shell — manual check of the web build (Task 2).

### Task 1: Catalogue app, use cases, test
- Create: `widgetbook/` (`flutter create --platforms web --project-name beneathsos_catalogue`), `pubspec.yaml`
  (`widgetbook: ^3.25.0`, `beneathsos_ui: {path: ..}`), `analysis_options.yaml`, `lib/main.dart`,
  `lib/use_cases/{brand,buttons,status,cards,countdown,layout,foundations}.dart`, `test/catalogue_test.dart`.
- RED: `catalogue_test.dart` pumps `CatalogueApp` and, for every leaf use case in `catalogueDirectories()`,
  pumps its builder inside `MaterialApp(theme: BeneathTheme.light()/dark())` and expects no exception.
- GREEN: implement `CatalogueApp` with `Widgetbook.material` and the addons; `catalogueDirectories()`
  returns the components of the spec table.
- Package `.pubignore` gains `widgetbook/`; README "Catalogue" section.
- Commit `feat(catalogue): Widgetbook catalogue of every component`.

### Task 2: CI build + verification
- Create `.github/workflows/catalogue.yml`: `pull_request` + push to `main`; SHA-pinned checkout and
  fvm setup; `flutter pub get`, `flutter analyze --fatal-infos`, `flutter test`, `flutter build web --release`
  in `widgetbook/`.
- Local: `fvm flutter build web` in `widgetbook/` exits 0; serve the build locally and screenshot the
  catalogue (light / dark, 200 %) for the maintainer.
- Push; the workflow is green on GitHub.
- Hub: roadmap 1.3 (built; publishing pending the maintainer), todo, issue #8 comment.
- Stop for the maintainer: enable GitHub Pages + add the deploy job (yes / no).
