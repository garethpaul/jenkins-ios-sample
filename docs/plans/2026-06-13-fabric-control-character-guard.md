# Fabric API Key Control Character Guard

status: planned

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
