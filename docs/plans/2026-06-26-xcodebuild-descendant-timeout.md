# Xcodebuild Descendant Timeout Containment

## Problem

The timeout wrapper sent `SIGTERM` to the `xcodebuild` process group but then
waited only for the group leader. If that leader exited while a descendant
ignored `SIGTERM`, the wrapper returned 124 and left the descendant running.
An escaped child could also retain inherited output pipes after the wrapper
reported completion.

## Change

- Give the complete process group a two-second termination grace period.
- Escalate the group to `SIGKILL` after the grace period; tolerate the macOS
  stale-group `EPERM` result when no signalable member remains.
- Preserve the existing timeout limit, exit status, environment stripping, and
  unsigned XCTest command.
- Add a hostile regression whose leader exits on `SIGTERM` while its child
  deliberately ignores the signal.
- Keep mutation-sensitive baseline contracts for the escalation and test.

## Alternatives

- Waiting only for the leader preserves the leak and was rejected.
- Killing immediately without a grace period prevents normal cleanup and was
  rejected.
- Enumerating descendant PIDs races with process creation and was rejected in
  favor of the process group already owned by the wrapper.

## Validation

- Confirm the hostile regression fails before implementation because the child
  remains alive.
- Run both focused timeout regressions.
- Run `make check` and all aliases from the checkout and an external absolute
  Makefile path.
- Confirm hosted policy and XCTest checks pass on the exact PR head.

## Scope

- Do not change simulator selection, project overrides, signing, workflow
  permissions, app behavior, deployment targets, or retired-provider policy.

## Completed Evidence

- Pre-fix regression confirmed the signal-resistant descendant survived.
- Both focused timeout regressions and all 16 Python policy tests passed.
- `make check`, `make lint`, `make test`, and `make build` passed from the
  checkout and through an absolute Makefile path from an external directory;
  XCTest skipped locally because Xcode is unavailable.
- Restoring the leader-only wait failed the hostile descendant regression.
- The first hosted head exposed macOS `EPERM` behavior for signal-0 process
  group probes; replacing the probe with fixed-grace escalation keeps the
  containment invariant portable.
