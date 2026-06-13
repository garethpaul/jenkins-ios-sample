# Fabric API Key Control Character Guard

status: completed

## Context

Runtime Fabric API key validation rejects empty values, placeholders, and
embedded whitespace. Non-whitespace Unicode control or format characters can
still pass validation and reach the retired vendored SDK as malformed
configuration.

## Requirements

- Reject API key values containing Unicode control or format characters after
  outer whitespace trimming.
- Preserve existing placeholder, embedded-whitespace, and trimmed-value
  behavior.
- Add executable XCTest coverage and mutation-sensitive static contracts.
- Document the runtime credential boundary and completed verification.

## Scope Boundaries

- Do not add credentials, contact Fabric or Crashlytics services, upload crash
  reports, change SDK binaries, or alter build-script secret handling.

## Verification

- Run all Make gates and available syntax, metadata, digest, mutation, diff,
  artifact, and secret scans.

## Work Completed

- Rejected Unicode control and format characters after outer whitespace
  trimming and before placeholder normalization or SDK startup.
- Added XCTest cases for null and bidirectional format controls while
  preserving existing valid trimmed-value behavior.
- Added mutation-sensitive static contracts and matching runtime credential
  documentation.

## Verification Completed

- `make lint`, `make test`, `make build`, and `make check` passed locally; the
  Linux environment truthfully skipped unavailable Xcode execution.
- Python compilation, plist/XML/JSON/YAML parsing, vendored digest checks, and
  `git diff --check` passed.
- Six hostile mutations covering the source guard, XCTest method, null case,
  format-control case, documentation contract, and completed plan evidence
  were rejected.
