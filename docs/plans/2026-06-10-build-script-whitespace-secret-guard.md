# Build Script Whitespace Secret Guard

status: completed

## Context

The Fabric build phase skipped empty and placeholder CI values, but shell
variables containing only spaces or newlines were still non-empty. Those values
should not invoke the vendored Fabric script as configured credentials.

## Completed Scope

- Added a shell trim helper in the Fabric build phase.
- Trimmed `FABRIC_API_KEY` and `CRASHLYTICS_BUILD_SECRET` before placeholder
  checks.
- Passed trimmed values to the vendored Fabric script when both values are real.
- Extended the static baseline and docs so whitespace-only CI secret rejection
  remains visible without Xcode.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
