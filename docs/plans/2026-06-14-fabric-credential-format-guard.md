# Fabric Credential Format Guard

status: completed

## Context

The Xcode upload phase rejects missing, placeholder, and whitespace-bearing
Fabric credentials, but other malformed values can still reach the retired
vendored upload script. The legacy contract expects a 40-hex Fabric API key and
a 64-hex Crashlytics build secret.

## Requirements

- Validate both credential shapes before invoking the vendored upload script.
- Keep credentials in environment variables rather than command arguments to
  the validator, and never print their values.
- Preserve outer-whitespace trimming and the existing generic skip behavior.
- Add executable negative coverage for placeholders, embedded whitespace,
  control characters, non-hex values, and incorrect lengths.
- Add mutation-sensitive static contracts and matching operator guidance.

## Scope Boundaries

- Do not add credentials, contact retired services, change vendored binaries,
  or weaken the existing runtime API-key validation.

## Verification

- Run the executable credential matrix, all Make gates, available syntax and
  metadata checks, isolated hostile mutations, and exact diff/secret/artifact
  audits.

## Work Completed

- Added an environment-only POSIX shell validator for the legacy 40-hex Fabric
  API key and 64-hex Crashlytics build secret shapes.
- Routed the Xcode upload phase through the validator before trimming and
  invoking the vendored script, while retaining generic skip output that does
  not expose credential values.
- Added executable positive and negative coverage plus static contracts and
  operator/security documentation.

## Verification Completed

- `scripts/test-fabric-credentials.sh` reported `Fabric credential validation tests passed.`
- `python3 -m py_compile scripts/check-baseline.py` and POSIX shell syntax checks
  for both new scripts passed.
- Six isolated hostile mutations were rejected for API-key length, secret
  length, hex alphabet, Xcode phase wiring, control-character test coverage,
  and completed plan evidence.
- All four Make gates and the absolute-Makefile check from `/tmp` passed; local
  XCTest truthfully remained unavailable because `xcodebuild` is not installed.
- The intended diff passed whitespace, secret-pattern, generated-artifact,
  binary, large-file, conflict-marker, and vendored-framework integrity audits.
