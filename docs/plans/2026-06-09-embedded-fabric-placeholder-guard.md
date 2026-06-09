# Embedded Fabric Placeholder Guard

status: completed

## Context

The runtime Fabric API key validator rejected empty values, known examples, and
build-setting placeholders at the start of the string. A malformed local value
such as `prefix-$(FABRIC_API_KEY)` should not start Crashlytics either because
it still contains an unresolved build-setting placeholder.

## Objectives

- Reject unresolved build-setting placeholder fragments anywhere in the trimmed
  Fabric API key value.
- Preserve real trimmed API key acceptance.
- Add XCTest coverage for embedded unresolved placeholders.
- Extend static checks and docs so the runtime guard remains visible without
  Xcode.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
