# Build Script Placeholder Guard

status: completed

## Context

The runtime Fabric guard rejected empty and placeholder API key values, but the
Xcode Fabric build phase only checked whether `FABRIC_API_KEY` and
`CRASHLYTICS_BUILD_SECRET` were non-empty. Placeholder values from local
configuration or CI could still invoke the vendored Fabric script.

## Completed Scope

- Added a shell helper in the Fabric build phase that normalizes CI values
  case-insensitively.
- Skipped the Fabric script for empty, unresolved, named, example, or
  replacement placeholder values.
- Preserved the existing Fabric invocation for real-looking CI values.
- Extended the static baseline and docs to preserve the build script placeholder
  guard.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
