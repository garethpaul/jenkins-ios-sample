# Jenkins iOS Sample Baseline Plan

status: completed

## Context

`jenkins-ios-sample` is a legacy Swift iOS CI sample with bundled Fabric and
Crashlytics frameworks. The original project stored crash-reporting values in
the app plist and Fabric run script; those values belong in CI secret storage
or local build settings.

## Objectives

- Preserve the minimal app, test target, storyboard, launch screen, and bundled framework references.
- Keep Fabric/Crashlytics configuration visible without committing real keys or build secrets.
- Make the Fabric run script safe for local static checks when CI secrets are absent.
- Keep local xcconfig, env files, generated Xcode state, signing material, and CI secrets out of git.
- Add a reproducible `make check` baseline for project metadata, plist/storyboard/asset parsing, source guardrails, framework wiring, and documentation.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
