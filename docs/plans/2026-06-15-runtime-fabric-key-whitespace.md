# Runtime Fabric API Key Whitespace Boundary

status: in_progress

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
- Use isolated hostile mutations to restore edge trimming, remove exact-value
  equality, weaken focused tests, falsify plan evidence, and desynchronize
  documentation; require the baseline to reject each mutation.
- Audit the exact diff, generated artifacts, vendored binary changes, file
  modes, and credential-shaped additions before committing intended paths.

## Work Completed

Pending implementation.

## Verification Completed

Pending implementation and validation.
