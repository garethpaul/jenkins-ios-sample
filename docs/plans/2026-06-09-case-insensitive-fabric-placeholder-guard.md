# Case-Insensitive Fabric Placeholder Guard

status: completed

## Context

`isConfiguredFabricAPIKey` rejects empty, whitespace-only, unresolved, example,
and replacement Fabric API key placeholders before Crashlytics startup.
Unresolved build-setting placeholders should be rejected anywhere in the value,
and lowercase example variants should not bypass the same runtime guard.

## Objectives

- Normalize trimmed Fabric API key values before comparing example and
  replacement placeholders.
- Preserve unresolved build-setting placeholder rejection anywhere in the value.
- Cover embedded unresolved placeholders plus lowercase example and replacement
  placeholders in XCTest.
- Extend the static baseline so case-insensitive placeholder rejection remains
  visible without Xcode.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
