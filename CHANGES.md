# Changes

## 2026-06-08

- Replaced committed Fabric/Crashlytics values with `FABRIC_API_KEY` and `CRASHLYTICS_BUILD_SECRET` placeholders.
- Changed the Fabric run script to skip gracefully unless CI or local Xcode provides both values.
- Guarded runtime Fabric initialization so empty or placeholder API key values do not start Crashlytics.
- Added `Jenkins iOS Sample/FabricKeys.xcconfig.example` to document local placeholder names without storing secrets.
- Added `make check` with a static baseline for Xcode project wiring, plist/storyboard/asset parsing, framework references, credential guardrails, and CI documentation.
- Moved the Xcode scheme from tracked `xcuserdata` into shared project data for CI discovery.
