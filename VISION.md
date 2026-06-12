## Jenkins iOS Sample Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

Jenkins iOS Sample is a Swift iOS project intended to demonstrate CI setup with
Jenkins-era iOS tooling, Fabric, and Crashlytics.

The repository is useful as a preserved iOS CI sample with a minimal app,
framework integrations, tests, and security policy.

The goal is to keep the sample buildable and credential-safe while documenting
its CI assumptions.

Current baseline: `make lint`, `make build`, and `make check` run
`scripts/check-baseline.py` to verify the Xcode project shape,
Fabric/Crashlytics framework wiring, placeholder build settings, CI secret
boundaries, build script placeholder handling, committed
plist/storyboard/asset parsing, whitespace-only CI secret rejection, shared
scheme placement, Swift 5 settings, and documentation. `make test` adds the
executable Fabric API key validation XCTest suite when Xcode is available.

The current focus is:

Priority:

- Preserve the minimal app and test project structure
- Keep Fabric/Crashlytics framework assumptions visible
- Keep all vendored framework and tool executables SHA-256 pinned
- Avoid committing CI secrets, signing material, or crash-reporting credentials
- Keep `FABRIC_API_KEY` and `CRASHLYTICS_BUILD_SECRET` supplied by CI or local ignored config
- Keep the Fabric build script placeholder guard aligned with runtime validation
- Reject whitespace-only CI secret values before invoking the Fabric build script
- Reject embedded whitespace in both build credentials after trimming
- Skip runtime Fabric initialization when the plist contains a placeholder API key, whitespace-only value, or embedded whitespace
- Preserve testable Fabric API key validation for the runtime startup guard
- Keep embedded placeholder and case-insensitive placeholder rejection before Crashlytics startup
- Reject named placeholder fragments such as `FABRIC_API_KEY` before Crashlytics startup
- Keep `make lint`, `make test`, `make build`, and `make check` available as
  local verification gates
- Keep hosted validation pinned, credential-free, and unsigned on macOS through
  the complete `make test` simulator gate with bounded explicit startup and one
  recovery attempt
- Maintain security policy for the sample

Next priorities:

- Add README setup, Jenkins job, and Xcode verification instructions
- Move any CI-specific values into documented environment configuration
- Modernize Fabric/Crashlytics dependencies only in a dedicated pass
- Replace the retired Fabric/Crashlytics binaries only in a dedicated dependency pass
- Keep the CI scheme in `xcshareddata/xcschemes`, not tracked `xcuserdata`

Contribution rules:

- One PR = one focused CI, build, dependency, or documentation change.
- Keep credentials and provisioning profiles out of git.
- Run `make lint`, `make test`, `make build`, and `make check` before pushing
  source, plist, project, CI-secret, or security documentation changes.
- Verify the Xcode project or CI command after build changes.
- Preserve the runtime placeholder API key guard around Fabric startup.
- Preserve sample simplicity over production pipeline complexity.

## Security

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

CI pipelines can leak signing keys, provisioning profiles, and service tokens.
Those values must stay in CI secret storage or local keychains, never in source.

Crash-reporting credentials should remain local or platform-managed.
The sample should not require committed Fabric or Crashlytics values to pass static checks.

## What We Will Not Merge (For Now)

- Committed signing material or CI secrets
- Fabric/Crashlytics credentials in source
- Broad CI rewrites without a reproducible command
- Generated build artifacts

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
