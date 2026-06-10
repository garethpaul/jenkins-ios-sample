# jenkins-ios-sample

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/jenkins-ios-sample` is an Apple platform application or Swift sample. Jenkins iOS Sample

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: C/C++ headers (6), Swift (3).

## Repository Contents

- `Crashlytics.framework` - source or example code
- `Fabric.framework` - source or example code
- `VENDORED_FRAMEWORKS.sha256` - exact digests for the retired framework,
  installer, and submission executables; drift detection does not establish
  provenance or make the SDK production-safe
- `Jenkins iOS Sample` - source or example code
- `Jenkins iOS Sample.xcodeproj` - Xcode project file
- `Jenkins iOS SampleTests` - source or example code
- `CHANGES.md` - recent maintenance changes
- `Makefile` - local static verification entry point
- `scripts/check-baseline.py` - static Fabric/Crashlytics baseline checks
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: Crashlytics.framework, Fabric.framework, Jenkins iOS Sample, Jenkins iOS Sample.xcodeproj, Jenkins iOS SampleTests
- Dependency and build manifests: none detected
- Entry points or build surfaces: `make lint`, `make test`, `make build`, `make check`, Jenkins iOS Sample.xcodeproj
- Test-looking files: Jenkins iOS SampleTests/Info.plist, Jenkins iOS SampleTests/Jenkins_iOS_SampleTests.swift

## Getting Started

### Prerequisites

- Git
- Python 3 for static verification with `make lint`, `make test`, `make build`, and `make check`
- macOS with Xcode for building Apple platform projects

### Setup

```bash
git clone https://github.com/garethpaul/jenkins-ios-sample.git
cd jenkins-ios-sample
make lint
make test
make build
make check
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

For CI or local Xcode builds that run Fabric, provide `FABRIC_API_KEY` and
`CRASHLYTICS_BUILD_SECRET` through CI secrets, xcodebuild settings, or a local
ignored xcconfig based on `Jenkins iOS Sample/FabricKeys.xcconfig.example`.

## Running or Using the Project

- Open `Jenkins iOS Sample.xcodeproj` in Xcode, choose the app or sample scheme, and run it on the matching simulator/device.
- The app initializes Fabric with Crashlytics. If the required build settings are missing, the Fabric run script skips instead of using committed credentials.
- The build script placeholder guard also skips unresolved, named, example, or
  replacement placeholder values before invoking the vendored Fabric script.
- The build script also trims CI-provided Fabric values so whitespace-only CI
  secrets skip the vendored Fabric script instead of being treated as
  configured credentials.
- Runtime Fabric initialization also skips when the app plist still contains an empty, whitespace-only, placeholder, embedded placeholder, or named placeholder fragment API key.
- Testable Fabric API key validation keeps the runtime guard covered by XCTest cases for missing, blank, embedded placeholder fragments, named placeholder fragments, case-insensitive placeholder values, and trimmed real values.
- The Xcode scheme is shared under `xcshareddata/xcschemes` so Jenkins and
  command-line `xcodebuild` can discover it without developer-specific
  `xcuserdata`.

## Testing and Verification

- `make lint`, `make test`, `make build`, and `make check` run `scripts/check-baseline.py`, which verifies Xcode project wiring, committed plists, storyboard and asset parsing, Fabric/Crashlytics framework references, placeholder build settings, build script placeholder guarding, runtime placeholder API key guarding, embedded placeholder rejection, named placeholder fragment rejection, case-insensitive placeholder rejection, whitespace-only key rejection, whitespace-only CI secret rejection, testable Fabric API key validation, and CI secret documentation.
- The `lint`, `test`, and `build` targets intentionally alias the static
  baseline on hosts without the legacy Xcode toolchain, keeping the standard
  local gate commands available without claiming to replace Xcode verification.
- Pinned `macos-15` GitHub Actions runs `make check` and parses
  `Jenkins iOS Sample.xcodeproj` with `xcodebuild -list`. This hosted validation
  receives no Fabric/Crashlytics secrets and does not build, sign, run vendored
  scripts, start Crashlytics, launch a simulator, or upload symbols.
- Xcode's test action or `xcodebuild test` with the appropriate scheme and destination

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- Fabric and Crashlytics values belong in CI secret storage, local keychains, xcodebuild settings, or ignored local configuration only.
- Do not commit Fabric API keys, Crashlytics build secrets, signing identities, provisioning profiles, `.env` files, or local xcconfig files.
- Local builds with a placeholder API key should skip Fabric initialization instead of starting Crashlytics with unresolved configuration.

## Security and Privacy Notes

- Review changes touching authentication or token handling; examples from the scan include Crashlytics.framework/Headers/CLSLogging.h, Crashlytics.framework/Headers/CLSReport.h.
- Review changes touching `FABRIC_API_KEY`, `CRASHLYTICS_BUILD_SECRET`, signing, provisioning, or the Fabric run script as CI-secret changes.
- Review changes touching external API calls or credential-adjacent configuration; examples from the scan include Crashlytics.framework/Headers/Crashlytics.h, Crashlytics.framework/Info.plist, Fabric.framework/Headers/FABAttributes.h, Fabric.framework/Headers/Fabric.h, and 2 more.
- Review changes touching network requests, sockets, or service endpoints; examples from the scan include Crashlytics.framework/Headers/Crashlytics.h, Crashlytics.framework/Info.plist, Fabric.framework/Info.plist, Jenkins iOS Sample/Info.plist, and 2 more.
- Review changes touching mobile permissions or privacy-sensitive device data; examples from the scan include Crashlytics.framework/Headers/Crashlytics.h.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include Crashlytics.framework/Headers/Crashlytics.h, Crashlytics.framework/Info.plist, Fabric.framework/Info.plist, Jenkins iOS Sample/Info.plist, and 2 more.

## Maintenance Notes

- This looks like an Apple platform project or sample. Xcode, Swift, CocoaPods, and deployment target versions may need to match the original project era.
- Run `make lint`, `make test`, `make build`, and `make check` before pushing Swift, plist, project, framework-reference, CI-secret, or documentation changes.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-09-make-gate-aliases.md` for the local gate alias guardrail.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
