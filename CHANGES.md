# Changes

## 2026-06-21

- Made absolute external Makefile invocations work when the checkout path
  contains spaces while preserving the protected repository-root override and
  rejecting attempts to replace GNU Make's automatic `MAKEFILE_LIST` value.
- Moved hosted policy, Python, and XCTest bootstrap commands outside mutable
  Make targets and documented the remaining workflow and required-context
  trust boundary.
- Required the exact two-step hosted workflow and absolute system native-tool
  paths, rejecting environment, shell, step, command, and `PATH` shadowing.
- Made Make aliases use `/usr/bin/python3` so fake interpreters on `PATH`
  cannot claim repository policy or Python-test success.

## 2026-06-19

- Retired the unsupported Fabric and Crashlytics runtime and upload integration.
- Removed vendored frameworks, executables, plist credentials, Xcode linkage,
  upload shell phase, credential validators, and pinned signing identities.
- Hardened the simulator test runner to strip legacy credentials, reject
  symlinked project overrides, disable signing, and avoid archives/uploads.
- Replaced credential-shape checks with repository-policy and hostile fake-tool
  tests that verify the retired boundary cannot execute.
- Kept the PR #3–#7 Makefile location-independence improvement while
  superseding their legacy credential-validation approach.

## 2026-06-15

- Rejected leading and trailing whitespace in runtime Fabric API keys so the
  guard validates the same bundle value consumed by the retired SDK.
- Required an exact 40-hex runtime Fabric API key before the retired Crashlytics
  SDK can initialize.

## 2026-06-14

- Required exact 40-hex Fabric API keys and 64-hex Crashlytics build secrets
  before invoking the retired vendored upload script.

## 2026-06-13

- Made every Make verification alias resolve the checker and conditional XCTest
  runner from the checkout, including absolute Makefile invocations elsewhere.
- Rejected Unicode control and format characters in runtime Fabric API keys
  before the retired SDK can receive malformed configuration.

## 2026-06-12

- Migrated the app and XCTest target to Swift 5 with an iOS 12 deployment floor
  while preserving guarded Fabric/Crashlytics startup behavior.
- Added portable simulator discovery and changed pinned macOS CI from project
  parsing to the executable Fabric API key validation XCTest suite.
- Disabled persisted checkout credentials and retained unsigned, secret-free
  hosted verification that skips the vendored upload script.
- Rejected embedded whitespace in runtime Fabric API keys and both build-phase
  credentials while preserving edge-trimmed real values.
- Made hosted XCTest select and explicitly boot one simulator by UDID, retry a
  bounded readiness failure once, and run the full suite without parallel test
  workers.

## 2026-06-10

- Added SHA-256 integrity pinning for all vendored Fabric and Crashlytics
  framework, installer, and submission executables.
- Added pinned, read-only macOS hosted validation for `make check` and
  `Jenkins iOS Sample.xcodeproj` parsing without Fabric/Crashlytics secrets.
- Trimmed Fabric build script values before placeholder checks so
  whitespace-only CI secrets skip the vendored Fabric script.

## 2026-06-09

- Added local `make lint`, `make test`, and `make build` gate aliases for the
  static Jenkins iOS baseline.
- Made runtime Fabric API key case-insensitive placeholder checks and covered
  lowercase example placeholders in tests.
- Rejected embedded placeholder fragments in Fabric API key values before
  Crashlytics startup.
- Rejected named placeholder fragments such as `FABRIC_API_KEY` and
  `CRASHLYTICS_BUILD_SECRET` before Crashlytics startup.
- Added a build script placeholder guard so unresolved, named, example, or
  replacement CI values skip the vendored Fabric script.

## 2026-06-08

- Replaced committed Fabric/Crashlytics values with `FABRIC_API_KEY` and `CRASHLYTICS_BUILD_SECRET` placeholders.
- Changed the Fabric run script to skip gracefully unless CI or local Xcode provides both values.
- Guarded runtime Fabric initialization so empty or placeholder API key values do not start Crashlytics.
- Trimmed runtime Fabric API key values so whitespace-only placeholders do not start Crashlytics.
- Added testable Fabric API key validation coverage for missing, blank, placeholder, and trimmed real values.
- Added `Jenkins iOS Sample/FabricKeys.xcconfig.example` to document local placeholder names without storing secrets.
- Added `make check` with a static baseline for Xcode project wiring, plist/storyboard/asset parsing, framework references, credential guardrails, and CI documentation.
- Moved the Xcode scheme from tracked `xcuserdata` into shared project data for CI discovery.
