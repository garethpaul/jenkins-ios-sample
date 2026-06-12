# Hosted Simulator Startup Reliability

status: completed

## Context

The push workflow for commit `16fe0228b977a489aeca45da5d7ed671f376036c`
passed all four XCTest cases, but the pull-request workflow compiled the same
commit and then produced no test-start output until the ten-minute job timeout
cancelled `xcodebuild`. The successful run also spent more than two minutes
between compilation and test startup, identifying CoreSimulator readiness as
the unstable boundary rather than compilation or test behavior.

## Priorities

1. Select one available iPhone simulator by UDID instead of an ambiguous name.
2. Boot that simulator explicitly and wait for readiness with a bounded retry.
3. Disable unnecessary parallel test execution for the four-case suite.
4. Preserve the complete unsigned, credential-free XCTest gate on push and
   pull-request events.
5. Keep the hosted job bounded while allowing one simulator recovery attempt.

## Implementation Units

### Test Runner

File: `scripts/run-tests.sh`

- Discover both simulator name and UDID.
- Boot and await the selected simulator before invoking `xcodebuild`.
- Bound each readiness wait and retry once after a targeted shutdown.
- Pass the exact simulator ID, a bounded destination lookup, and disabled
  parallel testing to `xcodebuild test`.

### Workflow And Static Contract

Files:

- `.github/workflows/check.yml`
- `scripts/check-baseline.py`

Allow a fifteen-minute job envelope for the bounded recovery path and enforce
the exact runner/workflow contract from the credential-free static baseline.

### Documentation

Files:

- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-12-hosted-simulator-startup-reliability.md`

Record the timeout cause, retained coverage, and both canonical hosted results.

## Verification

- `sh -n scripts/run-tests.sh`
- `python3 -m py_compile scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- hostile mutations removing the boot wait, retry, UDID destination, or
  non-parallel test setting
- `git diff --check`
- successful push and pull-request workflows for the same commit

## Verification Completed

- `sh -n scripts/run-tests.sh`, Python compilation, all four Make gates,
  vendored framework digest verification, and `git diff --check` passed.
- Controlled runner tests covered normal explicit boot, failed readiness with
  shutdown/retry, and a caller-supplied destination.
- Five hostile mutations removing the boot wait, retry shutdown, UDID
  destination, non-parallel setting, or fifteen-minute bound were rejected.
- Pull-request run `27396341972` completed successfully on commit
  `7cc026db8cf7ae38ef434b526c7cf7c60705f91e`; it selected a simulator by
  UDID and executed all four XCTest cases with zero failures.
- Push run `27396340857` completed successfully on the same commit and retained
  the complete unsigned, credential-free XCTest gate.

## Boundaries

- Do not skip, filter, or replace XCTest with static-only validation.
- Do not add Fabric/Crashlytics credentials or execute real upload behavior.
- Do not use an unbounded simulator wait or remove the workflow timeout.
