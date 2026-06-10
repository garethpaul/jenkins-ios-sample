# Vendored Crash SDK Integrity

status: completed

## Problem

The repository commits retired Fabric and Crashlytics framework, installer, and
submission executables without a deterministic integrity manifest.

## Scope

- Pin SHA-256 digests for all five committed framework/tool executables.
- Recompute every digest in `make check`.
- Reject missing, duplicate, malformed, unexpected, or unsafe manifest paths.
- Document that digest verification detects drift but does not establish
  provenance, patch vulnerabilities, or make the retired SDK production-safe.
- Keep credentials, uploads, signing, and SDK execution outside CI.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- mutation check against a changed Crashlytics submission executable
- `git diff --check`
