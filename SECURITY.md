# Security Policy

## Retired Fabric/Crashlytics integration

The current tree contains no Fabric or Crashlytics runtime, upload executable,
credential setting, signing identity, or provider workflow. The historical
integration passed a Fabric API key and Crashlytics build secret as process
arguments to an unsupported vendored binary. Those historical credentials must
be revoked or deleted at the retired provider even if the repositories or apps
are no longer active. Review provider audit logs for unexpected symbol uploads
or account activity before resolving any secret-scanning alert. The repository
cannot verify provider-side rotation, revocation, deletion, or audit-log review,
so removal from the current tree must not be described as proof that any of
those actions occurred.

Do not restore the old frameworks or upload scripts. A replacement provider
requires a separate dependency, privacy, network, credential, and retention
review.

## Supported Versions

The supported security scope for `jenkins-ios-sample` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained. As of June 19, 2026, GitHub reports this public repository as unarchived; that hosting state does not make this legacy sample production-supported software.

Project summary: Jenkins iOS Sample

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/jenkins-ios-sample` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- The current default branch is a legacy UIKit sample with the retired
  Fabric/Crashlytics integration removed. It has no provider frameworks,
  executables, plist configuration, runtime initialization, Xcode upload phase,
  credential input, or provider workflow.
- Repository policy checks reject reintroduced Fabric/Crashlytics artifacts,
  runtime initialization, plist configuration, upload execution, Xcode shell
  phases, pinned signing identities, workflow secret references, and workflow
  signing, archiving, or upload commands.
- `make check` validates that policy together with required project files,
  parseable plist/XML/JSON metadata, the shared XCTest scheme, Swift 5 project
  settings, the iOS 12 deployment target, and the absence of tracked
  `xcuserdata`. Make aliases invoke `/usr/bin/python3` explicitly so a fake
  `python3` earlier on `PATH` cannot claim policy or Python-test success.
- `make test` runs the baseline first and, when `xcodebuild` is available,
  invokes simulator XCTest with the retired provider environment variables
  unset and code signing disabled. Without `xcodebuild`, the local target prints
  a skip message and exits successfully; use the pinned hosted workflow for
  authoritative XCTest evidence. The target does not archive, export, notarize,
  or upload an application.
- The pinned macOS workflow uses read-only repository permissions, disables
  persisted checkout credentials, references no repository secrets, and runs
  repository policy, Python tests, and the native test runner directly rather
  than delegating its bootstrap to mutable Make targets.
- The workflow contract permits only the pinned checkout and exact validation
  step, with no job/step environment, custom shell, extra steps, or command
  additions. The native runner uses absolute system paths for Apple and parsing
  tools so checked-in or `PATH`-injected replacements cannot claim XCTest success.
- The workflow remains pull-request editable. Branch protection must require
  the GitHub Actions `baseline` context, and workflow changes require review as
  changes to verification authority; repository code cannot independently
  guarantee those provider-side settings.
- Local Make aliases do not establish trust in a modified Makefile. The hosted
  direct-command order and review of changes to that workflow are the intended
  verification boundary.
- A coordinated change to both the workflow and its repository policy remains
  reviewable code, not a self-authenticating boundary; provider branch
  protection and review of the required `baseline` context remain necessary.
- Hosted XCTest selects one simulator by UDID, waits for an explicit bounded
  boot with one recovery attempt, and disables parallel workers without
  skipping any validation cases.
- The native test deadline owns the complete `xcodebuild` process group,
  escalating from `SIGTERM` to `SIGKILL` so a signal-resistant descendant
  cannot survive CI or retain inherited output pipes.
- Signing identities, provisioning profiles, `.env` files, local xcconfig files,
  and replacement provider credentials must stay out of git.
- Historical credentials and retired binaries may remain visible in git history.
  Their removal from the current tree reduces the active attack surface but
  does not establish provider-side credential rotation, revocation, deletion,
  or absence of past misuse.
- Current checks cover repository policy, metadata contracts, and unsigned
  simulator XCTest. They do not establish device-build compatibility,
  production signing, archive/export readiness, App Store suitability, trust in
  historical vendored binaries, or safety of unsupported historical revisions.
- Reintroducing Fabric/Crashlytics or adding another reporting provider requires
  a separate dependency, privacy, network, credential, and retention review.
- No primary dependency manifest was detected in the repository root. If dependencies are added later, include a manifest and prefer reproducible installation instructions.

## Mobile Privacy Notes

If this project requests device permissions such as location, camera, microphone, contacts, Bluetooth, health data, or local storage access, reports should describe the permission involved and whether sensitive data can be accessed, persisted, or transmitted unexpectedly. Please avoid testing against real third-party user data or accounts you do not control.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
