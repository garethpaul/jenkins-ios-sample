# Runtime Fabric Placeholder Guard Plan

status: completed

## Context

`jenkins-ios-sample` keeps Fabric and Crashlytics values in CI secrets or ignored local configuration. The build script already skips when required values are missing, but a local app launch can still see an unresolved `FABRIC_API_KEY` placeholder in the app plist.

## Objectives

- Keep Fabric/Crashlytics startup when a real Fabric API key is configured.
- Skip runtime Fabric initialization for empty, unresolved, or example placeholder API key values.
- Preserve the existing CI run-script secret guard.
- Extend `make check` so future AppDelegate changes keep the runtime placeholder guard.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
