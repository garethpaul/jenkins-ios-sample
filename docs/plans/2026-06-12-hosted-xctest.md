# Hosted XCTest

status: completed

## Context

The repository had meaningful Fabric API key validation tests and a shared
scheme, but its Swift 2-era source could not compile on current Xcode and hosted
CI only parsed the project.

## Completed Scope

- Migrated the app and test target to Swift 5 with an iOS 12 deployment floor.
- Preserved guarded Fabric/Crashlytics startup and placeholder-secret handling.
- Added portable iPhone simulator discovery with explicit destination overrides.
- Made `make test` execute the existing validation tests whenever Xcode exists.
- Changed pinned macOS CI to run the complete unsigned, credential-free gate.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `sh -n scripts/run-tests.sh`
- hosted macOS XCTest run
- hostile mutations of checkout credentials, the test command, Swift settings,
  simulator discovery, signing behavior, framework digests, and secret guards
  must fail
- `git diff --check`
