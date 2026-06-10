# Changes

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
