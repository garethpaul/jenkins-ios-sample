# Named Fabric Placeholder Guard

status: completed

## Context

`isConfiguredFabricAPIKey` already rejects blank values, unresolved build-setting
placeholders, exact example values, lowercase variants, and embedded `$(...)`
fragments. Local configuration can still accidentally pass named placeholder
strings such as `YOUR_FABRIC_API_KEY_HERE` or `YOUR_CRASHLYTICS_BUILD_SECRET`.

## Objectives

- Reject Fabric API key values containing known placeholder fragment names.
- Preserve trimmed real Fabric API key acceptance.
- Cover named placeholder fragments in XCTest.
- Extend the static baseline so the runtime guard remains visible without Xcode.
- Document the guard alongside the Fabric/Crashlytics CI-secret boundary.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
