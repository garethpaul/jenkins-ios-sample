## Jenkins iOS Sample Vision

Jenkins iOS Sample is a Swift iOS project intended to demonstrate CI setup with
Jenkins-era iOS tooling, Fabric, and Crashlytics.

The repository is useful as a preserved iOS CI sample with a minimal app,
framework integrations, tests, and security policy.

The goal is to keep the sample buildable and credential-safe while documenting
its CI assumptions.

The current focus is:

Priority:

- Preserve the minimal app and test project structure
- Keep Fabric/Crashlytics framework assumptions visible
- Avoid committing CI secrets, signing material, or crash-reporting credentials
- Maintain security policy for the sample

Next priorities:

- Add README setup, Jenkins job, and Xcode verification instructions
- Move any CI-specific values into documented environment configuration
- Modernize Fabric/Crashlytics dependencies only in a dedicated pass
- Add or refresh build scripts for repeatable CI verification

Contribution rules:

- One PR = one focused CI, build, dependency, or documentation change.
- Keep credentials and provisioning profiles out of git.
- Verify the Xcode project or CI command after build changes.
- Preserve sample simplicity over production pipeline complexity.

## Security

CI pipelines can leak signing keys, provisioning profiles, and service tokens.
Those values must stay in CI secret storage or local keychains, never in source.

Crash-reporting credentials should remain local or platform-managed.

## What We Will Not Merge (For Now)

- Committed signing material or CI secrets
- Fabric/Crashlytics credentials in source
- Broad CI rewrites without a reproducible command
- Generated build artifacts

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
