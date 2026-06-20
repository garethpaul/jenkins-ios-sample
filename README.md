# jenkins-ios-sample

Preserved Swift iOS sample for validating an unsigned Jenkins-style build and
test boundary. The retired Fabric and Crashlytics SDKs were removed in June
2026 because their vendored upload tool required credentials on the process
command line and the provider no longer offers a supported migration path for
that binary integration.

## Security posture

- The app does not initialize Fabric or Crashlytics.
- The Xcode project contains no upload shell phase, signing identity, or
  provider credential setting.
- CI uses read-only GitHub permissions, does not persist checkout credentials,
  receives no secrets, and runs tests with code signing disabled.
- `scripts/run-tests.sh` removes legacy provider variables before spawning
  `xcodebuild`, rejects symlinked/out-of-repository project overrides, and never
  archives, signs, retries, or uploads an artifact. A bounded process-group
  deadline terminates hung simulator or build subprocesses.
- Historical Fabric credentials must be treated as compromised even though no
  values remain in the current tree.

## Verification

```sh
make check
make test
```

`make check` validates repository policy and runs hostile tests with fake
`xcodebuild` and upload tools. `make test` additionally executes the native
XCTest suite when Xcode is available. Both commands resolve paths from the
Makefile location, so this also works from another directory:

```sh
make -f /path/to/jenkins-ios-sample/Makefile check
```

The native gate is unsigned and simulator-only. It does not create an archive,
export an IPA, contact a retired provider, or validate a physical-device build.

## Historical context

The repository originally demonstrated Fabric/Crashlytics integration. The
documents under `docs/plans/` describe earlier defensive work and are retained
as review history, not as current setup instructions. Do not restore the
vendored frameworks or their upload executables. Add a currently supported
crash-reporting SDK only through a separate dependency and privacy review.
