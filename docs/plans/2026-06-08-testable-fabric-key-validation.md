# Testable Fabric Key Validation Plan

status: completed

## Context

The app already skips Fabric startup when the plist API key is missing, blank, unresolved, or a known placeholder. That behavior lived inside `AppDelegate`, while the checked-in XCTest file still contained generated placeholder tests.

## Objectives

- Extract the runtime Fabric API key decision into a shared helper.
- Cover missing, blank, unresolved, placeholder, and trimmed real key values in XCTest.
- Keep the app target testable so the unit test target can import the helper.
- Extend the static baseline and docs to preserve the testable Fabric API key validation behavior.

## Verification

- `make check`
- `git diff --check`
