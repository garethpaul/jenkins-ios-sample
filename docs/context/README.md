# Repository Context

## Purpose
This repository is a preserved Swift iOS sample for validating an unsigned Jenkins-style build and test boundary. The retired Fabric and Crashlytics SDKs were removed in June 2026 because their vendored upload tool required credentials on the process command line and the provider no longer offers a supported migration path.

## Technology
- Main language: Swift, Objective-C
- Frameworks or platforms: iOS, Xcode
- Package/build tooling: Make, Xcode project files

## Important Paths
- `Jenkins iOS Sample.xcodeproj`: Xcode project file
- `Jenkins iOS Sample/`: Application source code
- `Jenkins iOS SampleTests/`: Test code
- `Makefile`: Repository verification targets
- `scripts/`: Baseline checks and helper scripts
- `docs/`: Plans and documentation
- `SECURITY.md`: Security reporting and disclosure guidance
- `VISION.md`: Project direction and contribution guardrails
- `CHANGES.md`: Maintenance history

## How To Work Here
- Setup: No repository-specific install command documented
- Test: `make test` (hosted/local XCTest gate)
- Run/build: `make check` (full baseline)
- Lint: `make lint` (static architecture and policy checks)

## Architecture Notes
The application must remain unsigned and simulator-only. It does not create an archive, export an IPA, contact retired providers, or validate physical-device builds. The repository focuses on CI verification boundaries.

## Constraints And Unknowns
- Historical Fabric/Crashlytics integration must remain removed
- No production deployment configuration included
- Local and hosted verification must remain unsigned
- Runtime Fabric startup requires exact 40-hex API key format
- This looks like an Apple platform project - Xcode, Swift versions may need to match original era