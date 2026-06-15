# Runtime Fabric API Key Format Guard

status: in_progress

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

Pending implementation.

## Verification Completed

Pending implementation and validation.
