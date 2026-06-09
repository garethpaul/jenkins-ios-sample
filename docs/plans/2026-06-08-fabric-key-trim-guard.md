# Fabric Key Trim Guard Plan

status: completed

## Context

`hasConfiguredFabricAPIKey()` skips Fabric startup when the app plist contains an empty or placeholder API key. The check should trim the value first so whitespace-only values and padded placeholders cannot initialize Crashlytics.

## Objectives

- Trim the runtime Fabric API key before validation.
- Reject whitespace-only key values.
- Preserve unresolved and example placeholder rejection.
- Extend the static baseline so runtime startup keeps the trimmed key guard.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
