# Location-Independent Jenkins iOS Verification

status: completed

## Context

Absolute Makefile invocations resolve both `scripts/check-baseline.py` and the
conditional XCTest runner relative to the caller instead of the checkout, so
the documented verification aliases fail outside the repository directory.

## Scope

1. Derive the checkout root from the loaded Makefile.
2. Invoke the checker by absolute path and enter the checkout before XCTest.
3. Add exact Makefile, completed-plan, external-run, and guidance contracts.
4. Preserve Fabric credential validation, XCTest coverage, vendored SDK
   integrity, project metadata, and workflow policy.

## Verification Plan

- Run all four Make gates from the checkout and through an absolute Makefile
  path from a temporary directory.
- Run checker compilation, XCTest-runner shell syntax, project metadata parsing,
  vendored digest validation, and diff checks.
- Reject root-derivation, checker-invocation, XCTest-runner, plan-status,
  plan-evidence, and documentation mutations independently.
- Inspect intended paths, secret patterns, conflict markers, generated
  artifacts, and vendored binary changes before commit.

## Risk And Rollback

This changes verification path resolution only. Rollback restores the relative
recipes and removes their checker, plan, and documentation contracts.

## Verification

- All four Make aliases passed in root and external-directory runs by using an
  absolute Makefile path for the latter; `make test` truthfully reported
  that `xcodebuild` is unavailable on the Linux validation host after the
  static baseline passed.
- Python checker compilation, XCTest runner shell syntax, plist/XML/JSON
  project metadata parsing, vendored framework SHA-256 verification, and
  `git diff --check` passed.
- Verification rejected six isolated hostile mutations by their intended
  contracts: root derivation, checker invocation, XCTest runner location, plan
  status, plan evidence, and README guidance.
- The intended five-file diff passed secret-pattern, conflict-marker,
  generated-artifact, and vendored-framework change audits.
