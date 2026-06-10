# Hosted Project Validation

status: completed

## Context

The repository has focused static checks for Fabric placeholders, CI secret
handling, runtime initialization, project wiring, and vendored framework
references, but no current hosted validation. When Xcode is present, the
checker prints a manual reminder instead of proving the project is parseable.

## Priorities

1. Add pinned, read-only, bounded macOS CI for the canonical `make check` gate.
2. Parse `Jenkins iOS Sample.xcodeproj` whenever Xcode is available.
3. Enforce the workflow contract from `scripts/check-baseline.py`.
4. Keep Fabric/Crashlytics secrets, build scripts, signing, symbol upload,
   simulator execution, and runtime initialization outside hosted validation.

## Implementation Units

### Workflow And Checker

Files:

- `.github/workflows/check.yml`
- `scripts/check-baseline.py`

Add push, pull-request, and manual triggers; read-only permissions; concurrency
cancellation; a bounded `macos-15` job; commit-pinned checkout; and `make check`.
Require those properties and run `xcodebuild -list -project
"Jenkins iOS Sample.xcodeproj"` when Xcode exists.

### Documentation

Files:

- `README.md`
- `VISION.md`
- `SECURITY.md`
- `CHANGES.md`
- `docs/plans/2026-06-10-hosted-project-validation.md`

Document project parsing as structural validation only, not a secret-enabled
build, simulator test, Crashlytics startup, or symbol upload.

## Verification

- `python3 -m py_compile scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- workflow YAML parse
- `git diff --check`
- successful hosted macOS `Check` workflow for the pushed commit

## Boundaries

- Do not provide Fabric/Crashlytics credentials or execute vendored run scripts.
- Do not introduce signing material or claim full legacy Swift build support.
