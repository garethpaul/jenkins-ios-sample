# Jenkins iOS Sample Vision

This repository preserves a minimal Swift iOS project and a reproducible,
unsigned CI test boundary. It is not a supported Fabric or Crashlytics sample.

Priorities:

- keep `make check` and `make test` location-independent
- keep GitHub Actions read-only, secret-free, and unsigned
- prevent shell build phases, signing, archives, uploads, and vendored provider binaries
- retain focused hostile tests for subprocess environment and path boundaries
- terminate the entire native test process group when its bounded deadline expires
- document historical credential exposure without reproducing secret values

Any future crash-reporting integration must use a supported SDK, disclose its
data flow, avoid committed or argv-visible credentials, and arrive in a
dedicated reviewed change. Historical Fabric plans remain evidence only.
