# Retire Fabric and Crashlytics

## Problem

PRs #3–#7 hardened legacy credential validation but retained the unsupported
vendored `Fabric.framework/run` boundary. That executable accepts the API key
and build secret as process arguments, exposing them to process inspection and
making safe stdin-only transport impossible without replacing the uploader.

## Decision

Retire the integration instead of adding another wrapper around unsupported
binaries. Remove runtime initialization, plist settings, framework linkage,
upload shell phases, vendored artifacts, and signing identities. Preserve the
location-independent Make gate from the stack.

## Verification

- repository policy rejects restored imports, plist keys, upload executables,
  shell phases, symlinks, write permissions, workflow secrets, and signing
- fake `xcodebuild` proves legacy variables are absent from child environment
  and arguments
- fake upload tooling proves no configurable upload command is executed
- a hanging fake `xcodebuild` is terminated as a process group at the deadline
- native XCTest remains unsigned and simulator-only
- current-tree and history scans report counts only and never print values

## Residual risk

Git history cannot revoke provider credentials. The owner must revoke/delete
historical Fabric credentials and review provider activity. The old plan files
remain historical documentation and must not be interpreted as setup guidance.
