# Fabric Credential Whitespace Guard

status: completed

## Context

Runtime and build-phase validation trim leading and trailing whitespace, but a
non-placeholder value containing embedded spaces, tabs, or newlines can still
be treated as configured. Fabric API keys and Crashlytics build secrets are
opaque tokens, so remaining whitespace indicates malformed configuration and
must not reach runtime initialization or the vendored upload script.

## Priorities

1. Reject a trimmed runtime Fabric API key when any whitespace remains.
2. Apply the same rule to both build-phase credentials before invoking the
   vendored Fabric script.
3. Preserve acceptance of a real token surrounded only by removable edge
   whitespace.
4. Keep the behavior covered by XCTest and the credential-free static gate.

## Implementation Units

### Runtime Validator And XCTest

Files:

- `Jenkins iOS Sample/AppDelegate.swift`
- `Jenkins iOS SampleTests/Jenkins_iOS_SampleTests.swift`

Use `CharacterSet.whitespacesAndNewlines` to reject spaces, tabs, or newlines
remaining after trimming. Add focused examples for embedded spaces and
newlines while retaining the trimmed-real-value assertion.

### Build Guard And Static Contract

Files:

- `Jenkins iOS Sample.xcodeproj/project.pbxproj`
- `scripts/check-baseline.py`

Treat remaining shell whitespace as invalid for both `FABRIC_API_KEY` and
`CRASHLYTICS_BUILD_SECRET`. Extend static assertions so removing either the
runtime or build-phase whitespace guard fails on hosts without Xcode.

### Documentation

Files:

- `README.md`
- `VISION.md`
- `SECURITY.md`
- `CHANGES.md`
- `docs/plans/2026-06-12-fabric-credential-whitespace.md`

Document malformed embedded whitespace separately from already-rejected blank
values and mark this plan completed after verification.

## Verification

- `python3 -m py_compile scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `sh -n` against the extracted Fabric build-phase script
- `sha256sum -c VENDORED_FRAMEWORKS.sha256`
- hostile mutations removing the runtime and build-phase whitespace guards
- `git diff --check`
- hosted macOS XCTest run for the pushed commit

## Boundaries

- Do not add, print, or execute with real Fabric/Crashlytics credentials.
- Do not modify the vendored retired SDK artifacts.
- This guard detects malformed configuration; it does not make the retired SDK
  suitable for production use.
