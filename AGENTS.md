# AGENTS.md

## Repository purpose

`garethpaul/jenkins-ios-sample` is an Apple platform application or Swift sample. Jenkins iOS Sample

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `Jenkins iOS Sample.xcodeproj` - Xcode project
- `Crashlytics.framework` - repository source or sample assets
- `Fabric.framework` - repository source or sample assets
- `Jenkins iOS Sample` - repository source or sample assets
- `Jenkins iOS SampleTests` - repository source or sample assets

## Development commands

- Install dependencies: no repository-specific install command is documented.
- Full baseline: `make check`
- Hosted/local XCTest gate: `make test`
- Simulator overrides: `IOS_DESTINATION` or `IOS_SIMULATOR_NAME`
- Local Apple development: `open Jenkins iOS Sample.xcodeproj`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: C/C++ headers (6), Swift (3).
- Preserve legacy Xcode project settings and signing assumptions unless the change is explicitly about modernization.

## Testing guidance

- Test-related files detected: `docs/plans/2026-06-08-testable-fabric-key-validation.md`, `Jenkins iOS SampleTests/Jenkins_iOS_SampleTests.swift`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- Fabric and Crashlytics values belong in CI secret storage, local keychains, xcodebuild settings, or ignored local configuration only.
- Do not commit Fabric API keys, Crashlytics build secrets, signing identities, provisioning profiles, `.env` files, or local xcconfig files.
- Local builds with a placeholder API key should skip Fabric initialization instead of starting Crashlytics with unresolved configuration.
- This looks like an Apple platform project or sample. Xcode, Swift, CocoaPods, and deployment target versions may need to match the original project era.
- Run `make lint`, `make test`, `make build`, and `make check` before pushing Swift, plist, project, framework-reference, CI-secret, or documentation changes.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
