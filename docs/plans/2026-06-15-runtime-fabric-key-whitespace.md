# Runtime Fabric API Key Whitespace Boundary

status: completed

## Context

The runtime guard trims the `Info.plist` Fabric API key before validating it,
but `Fabric.with(...)` subsequently initializes the retired SDK from the
original bundle value. A whitespace-wrapped 40-hex key can therefore pass the
guard even though the SDK receives a different, malformed value.

## Goal

Require the runtime predicate to validate the exact key value consumed by the
SDK, without adding credentials, invoking retired services, or changing
vendored binaries.

## Scope

1. Reject leading or trailing whitespace instead of validating a normalized
   copy that is not supplied to Fabric.
2. Preserve exact lowercase and uppercase 40-hex key acceptance plus existing
   placeholder, embedded-whitespace, control-character, and length checks.
3. Add focused XCTest intent and static contracts that fail if edge trimming is
   restored or edge-whitespace rejection disappears.
4. Synchronize operator, security, changelog, vision, and repository guidance.

## Non-Goals

- Adding, rotating, printing, or transmitting credentials.
- Initializing Fabric or Crashlytics during local validation.
- Changing the build-phase credential validator or vendored SDK artifacts.
- Claiming executable XCTest on Linux; the existing bounded macOS workflow
  remains the executable source of truth.

## Verification Plan

- Run all four Make gates from the repository and the absolute Makefile check
  from an external directory.
- Run POSIX shell syntax, Python compilation, and the executable Fabric
  credential tests.
- Use five isolated hostile mutations to restore edge trimming, remove exact-value
  equality, weaken focused tests, falsify plan evidence, and desynchronize
  documentation; require the baseline to reject each mutation.
- Run `git diff --check` and audit the exact diff, generated artifacts, vendored binary changes, file
  modes, and credential-shaped additions before committing intended paths.

## Work Completed

- Required the original bundle value to equal its whitespace-trimmed form
  before runtime Fabric API key validation can succeed.
- Preserved exact lowercase and uppercase 40-hex acceptance while rejecting
  leading, trailing, embedded, and control-character whitespace.
- Added focused XCTest intent for leading space, trailing space, and mixed
  newline/tab boundaries.
- Extended the static baseline to enforce the source predicate, exact negative
  assertions, completed plan evidence, and synchronized guidance.

## Verification Completed

- All four Make gates passed in a disposable Git-backed copy of the exact
  worktree content; Linux correctly reported that executable XCTest requires
  Xcode.
- The absolute Makefile check passed from an external directory.
- POSIX shell syntax, Python compilation, and the executable Fabric credential
  tests passed.
- Five isolated hostile mutations covering source exact-value equality, leading
  and trailing negative assertions, plan evidence, and documentation were
  rejected.
- `git diff --check`, generated-artifact inspection, vendored-binary review,
  file-mode review, and credential-shaped addition review completed without
  findings.
