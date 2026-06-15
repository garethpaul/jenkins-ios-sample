# Runtime Fabric API Key Format Guard

status: completed

## Context

The Xcode upload phase now requires the legacy 40-hex Fabric API key shape, but
the runtime startup guard still accepts any trimmed non-placeholder token. A
short or non-hex value can therefore initialize retired Fabric/Crashlytics code
even though the same value would be rejected before build-phase upload.

## Priority

Align runtime startup with the existing API-key format boundary without adding
credentials, contacting retired services, or changing vendored binaries.

## Scope

1. Require the trimmed runtime Fabric API key to contain exactly 40 hexadecimal
   characters after existing placeholder, whitespace, and control checks.
2. Preserve acceptance of edge-trimmed uppercase and lowercase real values.
3. Add focused XCTest intent for exact, short, long, and non-hex values.
4. Add mutation-sensitive checker and completed-plan contracts.
5. Synchronize README, SECURITY, VISION, CHANGES, and AGENTS guidance.

## Non-Goals

- Validating the 64-hex Crashlytics build secret at runtime, because it is not
  part of the application plist startup path.
- Adding, rotating, printing, or transmitting credentials.
- Updating or invoking retired Fabric/Crashlytics binaries.
- Claiming live SDK behavior on this Linux host.

## Verification Plan

- Run focused credential tests and all four Make gates from the repository.
- Run the absolute Makefile check from an external directory.
- Compile Python and validate POSIX shell syntax without retaining artifacts.
- Reject runtime length, runtime alphabet, focused-test, plan-evidence, and
  documentation mutations.
- Audit the exact diff, generated artifacts, vendored binaries, and
  credential-shaped additions before commit.
- Capture one bounded exact-head hosted and security snapshot after push.

## Work Completed

- Required the trimmed runtime Fabric API key to contain exactly 40 hexadecimal
  characters before the retired Crashlytics SDK can initialize.
- Added focused XCTest intent for exact lowercase, edge-trimmed uppercase,
  short, long, and non-hex values.
- Added static contracts for the runtime predicate, focused tests, completed
  plan evidence, and synchronized operator documentation.

## Verification Completed

- All four Make gates passed from the repository.
- The absolute Makefile check passed from an external directory.
- `python3 -m py_compile` and POSIX shell syntax validation passed without
  retaining generated artifacts.
- The executable Fabric credential validation tests passed.
- Five isolated hostile mutations covering runtime length, runtime alphabet,
  focused tests, plan evidence, and documentation were rejected.
- `git diff --check`, generated-artifact inspection, credential-shaped addition
  review, and vendored-binary diff inspection passed.
- XCTest execution remains unavailable on this Linux host; the focused cases
  are intended for the existing bounded macOS hosted job.
