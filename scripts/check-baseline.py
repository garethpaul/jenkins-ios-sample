#!/usr/bin/env python3
"""Static baseline checks for the Jenkins iOS Fabric/Crashlytics sample."""

from __future__ import print_function

import hashlib
import json
import plistlib
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FAILURES = []
HOSTED_XCTEST_PLAN = "docs/plans/2026-06-12-hosted-xctest.md"
EXPECTED_MAKEFILE = """.PHONY: build check lint test

lint: check

test: check
\t@if command -v xcodebuild >/dev/null 2>&1; then ./scripts/run-tests.sh; else printf '%s\\n' "Skipping XCTest: xcodebuild is not installed."; fi

build: check

check:
\tpython3 scripts/check-baseline.py
"""
EXPECTED_TEST_RUNNER = """#!/bin/sh

set -eu

PROJECT=${XCODE_PROJECT:-Jenkins iOS Sample.xcodeproj}
SCHEME=${XCODE_SCHEME:-Jenkins iOS Sample}
CONFIGURATION=${CONFIGURATION:-Debug}

if ! command -v xcodebuild >/dev/null 2>&1; then
    printf '%s\\n' "xcodebuild is required to run Jenkins iOS Sample tests." >&2
    exit 127
fi

if [ -n "${IOS_DESTINATION:-}" ]; then
    DESTINATION=$IOS_DESTINATION
elif [ -n "${IOS_SIMULATOR_NAME:-}" ]; then
    DESTINATION="platform=iOS Simulator,name=${IOS_SIMULATOR_NAME}"
else
    SIMULATOR_NAME=$(xcrun simctl list devices available | awk -F '[()]' '/^[[:space:]]+iPhone/ { name=$1; sub(/^[[:space:]]+/, "", name); sub(/[[:space:]]+$/, "", name); print name; exit }')
    if [ -z "$SIMULATOR_NAME" ]; then
        printf '%s\\n' "No available iPhone simulator was found." >&2
        exit 1
    fi
    DESTINATION="platform=iOS Simulator,name=${SIMULATOR_NAME}"
fi

xcodebuild \\
    -project "$PROJECT" \\
    -scheme "$SCHEME" \\
    -configuration "$CONFIGURATION" \\
    -destination "$DESTINATION" \\
    CODE_SIGNING_ALLOWED=NO \\
    test
"""
EXPECTED_WORKFLOW = """name: Check

on:
  pull_request:
  push:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: check-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  baseline:
    runs-on: macos-15
    timeout-minutes: 10
    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Validate baseline and XCTest
        run: make test
"""


def rel(path):
    return ROOT / path


def expect(condition, message):
    if not condition:
        FAILURES.append(message)


def read_text(path):
    target = rel(path)
    expect(target.exists(), "{} is missing".format(path))
    if not target.exists():
        return ""
    return target.read_text(encoding="utf-8", errors="replace")


def parse_xml(path):
    target = rel(path)
    expect(target.exists(), "{} is missing".format(path))
    if not target.exists():
        return None
    try:
        return ET.parse(str(target))
    except ET.ParseError as exc:
        FAILURES.append("{} is not valid XML: {}".format(path, exc))
        return None


def parse_json(path):
    target = rel(path)
    expect(target.exists(), "{} is missing".format(path))
    if not target.exists():
        return None
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except ValueError as exc:
        FAILURES.append("{} is not valid JSON: {}".format(path, exc))
        return None


def parse_plist(path):
    target = rel(path)
    expect(target.exists(), "{} is missing".format(path))
    if not target.exists():
        return None
    try:
        with target.open("rb") as handle:
            return plistlib.load(handle)
    except Exception as exc:
        FAILURES.append("{} is not a valid plist: {}".format(path, exc))
        return None


def tracked_paths():
    try:
        output = subprocess.check_output(["git", "ls-files"], cwd=str(ROOT), universal_newlines=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        FAILURES.append("unable to inspect tracked files: {}".format(exc))
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def strip_swift_comments(text):
    lines = []
    for line in text.splitlines():
        lines.append("" if line.lstrip().startswith("//") else line)
    return "\n".join(lines)


def check_required_files():
    required = [
        ".gitignore",
        ".github/workflows/check.yml",
        "CHANGES.md",
        "Crashlytics.framework/Crashlytics",
        "Crashlytics.framework/run",
        "Crashlytics.framework/submit",
        "Crashlytics.framework/Headers/Crashlytics.h",
        "Fabric.framework/Fabric",
        "Fabric.framework/run",
        "Fabric.framework/Headers/Fabric.h",
        "Jenkins iOS Sample.xcodeproj/project.pbxproj",
        "Jenkins iOS Sample.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
        "Jenkins iOS Sample.xcodeproj/xcshareddata/xcschemes/Jenkins iOS Sample.xcscheme",
        "Jenkins iOS Sample/AppDelegate.swift",
        "Jenkins iOS Sample/Base.lproj/LaunchScreen.xib",
        "Jenkins iOS Sample/Base.lproj/Main.storyboard",
        "Jenkins iOS Sample/FabricKeys.xcconfig.example",
        "Jenkins iOS Sample/Images.xcassets/AppIcon.appiconset/Contents.json",
        "Jenkins iOS Sample/Info.plist",
        "Jenkins iOS Sample/ViewController.swift",
        "Jenkins iOS SampleTests/Info.plist",
        "Jenkins iOS SampleTests/Jenkins_iOS_SampleTests.swift",
        "Makefile",
        "README.md",
        "SECURITY.md",
        "VISION.md",
        "VENDORED_FRAMEWORKS.sha256",
        "docs/plans/2026-06-08-fabric-key-trim-guard.md",
        "docs/plans/2026-06-08-jenkins-ios-baseline.md",
        "docs/plans/2026-06-08-runtime-fabric-placeholder-guard.md",
        "docs/plans/2026-06-08-testable-fabric-key-validation.md",
        "docs/plans/2026-06-09-case-insensitive-fabric-placeholder-guard.md",
        "docs/plans/2026-06-09-embedded-fabric-placeholder-guard.md",
        "docs/plans/2026-06-09-make-gate-aliases.md",
        "docs/plans/2026-06-09-named-fabric-placeholder-guard.md",
        "docs/plans/2026-06-09-build-script-placeholder-guard.md",
        "docs/plans/2026-06-10-build-script-whitespace-secret-guard.md",
        "docs/plans/2026-06-10-hosted-project-validation.md",
        "docs/plans/2026-06-10-vendored-crash-sdk-integrity.md",
        HOSTED_XCTEST_PLAN,
        "docs/readme-overview.svg",
        "scripts/check-baseline.py",
        "scripts/run-tests.sh",
    ]

    for path in required:
        expect(rel(path).exists(), "{} is missing".format(path))


def check_parsable_resources():
    parse_xml("docs/readme-overview.svg")
    parse_xml("Jenkins iOS Sample.xcodeproj/project.xcworkspace/contents.xcworkspacedata")
    parse_xml("Jenkins iOS Sample.xcodeproj/xcshareddata/xcschemes/Jenkins iOS Sample.xcscheme")
    parse_xml("Jenkins iOS Sample/Base.lproj/Main.storyboard")
    parse_xml("Jenkins iOS Sample/Base.lproj/LaunchScreen.xib")

    app_plist = parse_plist("Jenkins iOS Sample/Info.plist")
    test_plist = parse_plist("Jenkins iOS SampleTests/Info.plist")
    parse_plist("Fabric.framework/Info.plist")
    parse_plist("Crashlytics.framework/Info.plist")
    app_icon = parse_json("Jenkins iOS Sample/Images.xcassets/AppIcon.appiconset/Contents.json")

    if app_plist:
        fabric = app_plist.get("Fabric", {})
        kits = fabric.get("Kits", [])
        kit = kits[0] if kits else {}
        expect(app_plist.get("CFBundlePackageType") == "APPL", "app Info.plist should describe an application")
        expect(app_plist.get("UIMainStoryboardFile") == "Main", "app Info.plist should point at Main storyboard")
        expect(app_plist.get("UILaunchStoryboardName") == "LaunchScreen", "app Info.plist should point at LaunchScreen")
        expect(fabric.get("APIKey") == "$(FABRIC_API_KEY)", "app Info.plist should use FABRIC_API_KEY placeholder")
        expect(kit.get("KitName") == "Crashlytics", "app Info.plist should keep the Crashlytics kit")

    if test_plist:
        expect(test_plist.get("CFBundlePackageType") == "BNDL", "test Info.plist should describe a bundle")

    if app_icon:
        images = app_icon.get("images", [])
        idioms = {image.get("idiom") for image in images}
        expect("iphone" in idioms and "ipad" in idioms, "AppIcon asset should keep iPhone and iPad slots")


def check_project_wiring():
    pbxproj = read_text("Jenkins iOS Sample.xcodeproj/project.pbxproj")
    scheme = read_text("Jenkins iOS Sample.xcodeproj/xcshareddata/xcschemes/Jenkins iOS Sample.xcscheme")

    for framework in ("Fabric.framework", "Crashlytics.framework"):
        expect(framework in pbxproj, "{} should remain referenced in the Xcode project".format(framework))
        expect("{} in Frameworks".format(framework) in pbxproj, "{} should be linked in the app target".format(framework))

    expect("Main.storyboard in Resources" in pbxproj, "Main.storyboard should be an app resource")
    expect("LaunchScreen.xib in Resources" in pbxproj, "LaunchScreen.xib should be an app resource")
    expect("Images.xcassets in Resources" in pbxproj, "Images.xcassets should be an app resource")
    expect('INFOPLIST_FILE = "Jenkins iOS Sample/Info.plist";' in pbxproj, "app plist should stay wired")
    expect('INFOPLIST_FILE = "Jenkins iOS SampleTests/Info.plist";' in pbxproj, "test plist should stay wired")
    expect(pbxproj.count("IPHONEOS_DEPLOYMENT_TARGET = 12.0;") == 2 and
           "IPHONEOS_DEPLOYMENT_TARGET = 8.3;" not in pbxproj,
           "Xcode project should use the iOS 12 deployment target")
    expect(pbxproj.count("SWIFT_VERSION = 5.0;") == 4,
           "app and test configurations should use Swift 5")
    expect('CODE_SIGN_IDENTITY = "iPhone Developer";' in pbxproj, "sample code signing identity should remain visible")
    expect("ENABLE_TESTABILITY = YES;" in pbxproj, "app Debug build should keep testability enabled for XCTest")
    expect("$FABRIC_API_KEY" in pbxproj, "Fabric run script should use FABRIC_API_KEY")
    expect("$CRASHLYTICS_BUILD_SECRET" in pbxproj, "Fabric run script should use CRASHLYTICS_BUILD_SECRET")
    expect("Skipping Fabric run script" in pbxproj, "Fabric run script should skip when secrets are absent")
    expect("trim_value()" in pbxproj and "sed 's/^[[:space:]]*//;s/[[:space:]]*$//'" in pbxproj and
           "trimmed_value=$(trim_value" in pbxproj and
           "./Fabric.framework/run \\\"$fabric_api_key\\\" \\\"$crashlytics_build_secret\\\"" in pbxproj,
           "Fabric run script should trim CI values before placeholder checks and vendored invocation")
    expect("is_placeholder_value()" in pbxproj and "normalized_value=$(printf '%s' \\\"$trimmed_value\\\"" in pbxproj and
           "tr '[:lower:]' '[:upper:]')" in pbxproj and "'$('" in pbxproj and
           "*FABRIC_API_KEY*" in pbxproj and "*CRASHLYTICS_BUILD_SECRET*" in pbxproj and
           "YOUR_*|REPLACE_*" in pbxproj and "set real FABRIC_API_KEY" in pbxproj and
           'if is_placeholder_value \\"$FABRIC_API_KEY\\" || is_placeholder_value \\"$CRASHLYTICS_BUILD_SECRET\\"; then' in pbxproj,
           "Fabric run script should skip empty, unresolved, named, and replacement placeholder values")
    expect(not re.search(r"Fabric\.framework/run\s+[0-9a-f]{40}\s+[0-9a-f]{64}", pbxproj), "Fabric run script should not commit raw key material")
    expect("Jenkins iOS SampleTests.xctest" in scheme, "shared Xcode scheme should include the test target")
    expect(scheme.count('BlueprintIdentifier = "88C69EAE1B03CD1F001A9C82"') >= 2 and
           scheme.count('BlueprintIdentifier = "88C69EC31B03CD20001A9C82"') >= 2 and
           "<TestableReference" in scheme and 'skipped = "NO"' in scheme,
           "shared scheme should build the app and execute Jenkins iOS SampleTests")

    tracked_xcuserdata = [path for path in tracked_paths() if "/xcuserdata/" in path]
    expect(not tracked_xcuserdata, "tracked xcuserdata should be moved to xcshareddata: {}".format(", ".join(tracked_xcuserdata)))


def check_vendored_integrity():
    expected_paths = {
        "Fabric.framework/Fabric",
        "Fabric.framework/run",
        "Crashlytics.framework/Crashlytics",
        "Crashlytics.framework/run",
        "Crashlytics.framework/submit",
    }
    entries = {}
    for line_number, line in enumerate(read_text("VENDORED_FRAMEWORKS.sha256").splitlines(), 1):
        parts = line.split("  ", 1)
        expect(len(parts) == 2 and re.fullmatch(r"[0-9a-f]{64}", parts[0]) is not None,
               "VENDORED_FRAMEWORKS.sha256 line {} should contain a lowercase SHA-256 digest and path".format(line_number))
        if len(parts) != 2:
            continue
        digest, path = parts
        expect(path not in entries and not Path(path).is_absolute() and ".." not in Path(path).parts,
               "VENDORED_FRAMEWORKS.sha256 line {} should contain a unique repository-relative path".format(line_number))
        entries[path] = digest

    expect(set(entries) == expected_paths,
           "vendored framework manifest should cover exactly the committed Fabric/Crashlytics executables")
    for path, expected_digest in entries.items():
        artifact = rel(path)
        if artifact.is_file():
            actual_digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            expect(actual_digest == expected_digest, "vendored artifact digest mismatch: {}".format(path))


def check_swift_and_secret_guardrails():
    swift_paths = sorted(rel("Jenkins iOS Sample").glob("*.swift")) + sorted(rel("Jenkins iOS SampleTests").glob("*.swift"))
    source = "\n".join(strip_swift_comments(path.read_text(encoding="utf-8")) for path in swift_paths)

    expect("Fabric.with([Crashlytics.sharedInstance()])" in source, "AppDelegate should initialize Fabric/Crashlytics")
    expect("if hasConfiguredFabricAPIKey()" in source, "AppDelegate should guard Fabric initialization with configured API key check")
    expect("func hasConfiguredFabricAPIKey() -> Bool" in source, "AppDelegate should keep the Fabric API key check explicit")
    expect("func isConfiguredFabricAPIKey(_ apiKey: String?) -> Bool" in source,
           "AppDelegate should expose a testable Fabric API key validator")
    expect("return isConfiguredFabricAPIKey(apiKey)" in source,
           "AppDelegate should share the testable Fabric API key validator")
    expect("object(forInfoDictionaryKey: \"Fabric\")" in source and
           "let trimmedAPIKey = apiKey.trimmingCharacters(in: .whitespacesAndNewlines)" in source and
           "let normalizedAPIKey = trimmedAPIKey.uppercased()" in source and
           "!trimmedAPIKey.isEmpty" in source,
           "AppDelegate should trim, normalize, and inspect the Fabric API key from Info.plist")
    expect("trimmedAPIKey.range(of: \"$(\") == nil" in source and
           "normalizedAPIKey != \"YOUR_FABRIC_API_KEY\"" in source and
           "!normalizedAPIKey.hasPrefix(\"REPLACE_\")" in source,
           "AppDelegate should reject embedded unresolved, example, and replacement Fabric API key placeholders case-insensitively")
    expect("let placeholderFragments = [\"FABRIC_API_KEY\", \"CRASHLYTICS_BUILD_SECRET\"]" in source and
           "normalizedAPIKey.range(of: placeholderFragment) != nil" in source,
           "AppDelegate should reject named Fabric and Crashlytics placeholder fragments")
    expect("Crashlytics.sharedInstance().crash()" not in source, "sample should not include forced crash behavior")
    expect(not re.search(r"\b(?:print|println|NSLog)\s*\(", source), "first-party Swift should not add console logging")

    tests = strip_swift_comments(read_text("Jenkins iOS SampleTests/Jenkins_iOS_SampleTests.swift"))
    expect("@testable import Jenkins_iOS_Sample" in tests, "unit tests should import the app module as testable")
    expect("testFabricAPIKeyValidationRejectsMissingOrBlankValues" in tests, "unit tests should cover missing and blank Fabric keys")
    expect("testFabricAPIKeyValidationRejectsPlaceholders" in tests, "unit tests should cover placeholder Fabric keys")
    expect("testFabricAPIKeyValidationAcceptsTrimmedRealValues" in tests, "unit tests should cover trimmed real Fabric keys")
    expect("isConfiguredFabricAPIKey(nil)" in tests and "isConfiguredFabricAPIKey(\"$(FABRIC_API_KEY)\")" in tests and
           "isConfiguredFabricAPIKey(\"prefix-$(FABRIC_API_KEY)\")" in tests,
           "unit tests should call the shared Fabric key validator")
    expect("isConfiguredFabricAPIKey(\"your_fabric_api_key\")" in tests and
           "isConfiguredFabricAPIKey(\"replace_with_fabric_api_key\")" in tests,
           "unit tests should cover lowercase Fabric key placeholders")
    expect("isConfiguredFabricAPIKey(\"YOUR_FABRIC_API_KEY_HERE\")" in tests and
           "isConfiguredFabricAPIKey(\"prefix-FABRIC_API_KEY\")" in tests and
           "isConfiguredFabricAPIKey(\"YOUR_CRASHLYTICS_BUILD_SECRET\")" in tests,
           "unit tests should cover named placeholder fragments")

    selected_text = "\n".join(
        read_text(path)
        for path in (
            "Jenkins iOS Sample.xcodeproj/project.pbxproj",
            "Jenkins iOS Sample/Info.plist",
            "Jenkins iOS Sample/FabricKeys.xcconfig.example",
            "README.md",
            "VISION.md",
            "SECURITY.md",
            "CHANGES.md",
        )
    )
    for secret in (
        "abb870ac2c6cd77fc0a3ee166f786a86748f4eb9",
        "47d331d25396fd56e08c5c5891c16a003ba5647e584bf8fc07feb0e8ae92ab92",
    ):
        expect(secret not in selected_text, "committed project files should not contain the old Fabric/Crashlytics secret")

    xcconfig = read_text("Jenkins iOS Sample/FabricKeys.xcconfig.example")
    expect("FABRIC_API_KEY = YOUR_FABRIC_API_KEY" in xcconfig, "xcconfig example should document FABRIC_API_KEY")
    expect("CRASHLYTICS_BUILD_SECRET = YOUR_CRASHLYTICS_BUILD_SECRET" in xcconfig, "xcconfig example should document CRASHLYTICS_BUILD_SECRET")


def check_docs():
    readme = read_text("README.md")
    vision = read_text("VISION.md")
    security = read_text("SECURITY.md")
    changes = read_text("CHANGES.md")
    plan = read_text("docs/plans/2026-06-08-jenkins-ios-baseline.md")
    runtime_plan = read_text("docs/plans/2026-06-08-runtime-fabric-placeholder-guard.md")
    trim_plan = read_text("docs/plans/2026-06-08-fabric-key-trim-guard.md")
    validation_plan = read_text("docs/plans/2026-06-08-testable-fabric-key-validation.md")
    case_plan = read_text("docs/plans/2026-06-09-case-insensitive-fabric-placeholder-guard.md")
    embedded_plan = read_text("docs/plans/2026-06-09-embedded-fabric-placeholder-guard.md")
    make_gates_plan = read_text("docs/plans/2026-06-09-make-gate-aliases.md")
    named_plan = read_text("docs/plans/2026-06-09-named-fabric-placeholder-guard.md")
    build_script_plan = read_text("docs/plans/2026-06-09-build-script-placeholder-guard.md")
    build_script_whitespace_plan = read_text("docs/plans/2026-06-10-build-script-whitespace-secret-guard.md")
    hosted_validation_plan = read_text("docs/plans/2026-06-10-hosted-project-validation.md")
    vendored_integrity_plan = read_text("docs/plans/2026-06-10-vendored-crash-sdk-integrity.md")
    hosted_xctest_plan = read_text(HOSTED_XCTEST_PLAN)
    workflow = read_text(".github/workflows/check.yml")
    gitignore = read_text(".gitignore")
    makefile = read_text("Makefile")

    test_runner = read_text("scripts/run-tests.sh")
    expect(makefile == EXPECTED_MAKEFILE,
           "Makefile should exactly preserve static and executable XCTest gates")
    expect(test_runner == EXPECTED_TEST_RUNNER,
           "test runner should exactly preserve portable unsigned XCTest execution")
    expect(rel("scripts/run-tests.sh").stat().st_mode & 0o111,
           "test runner should be executable")

    for text_name, text in (
        ("README.md", readme),
        ("VISION.md", vision),
        ("SECURITY.md", security),
    ):
        lowered = text.lower()
        expect("make check" in lowered, "{} should document the static verification command".format(text_name))
        expect("fabric" in lowered and "crashlytics" in lowered, "{} should document Fabric/Crashlytics".format(text_name))
        expect("ci secret" in lowered or "ci secrets" in lowered, "{} should document CI secret handling".format(text_name))
        expect("credential" in lowered or "secret" in lowered, "{} should document credential handling".format(text_name))
        expect("named placeholder" in lowered, "{} should document named placeholder fragment handling".format(text_name))
        expect("build script placeholder" in lowered, "{} should document build script placeholder handling".format(text_name))
        expect("whitespace-only ci" in lowered, "{} should document whitespace-only CI secret handling".format(text_name))

    expect("make lint" in readme and "make test" in readme and "make build" in readme,
           "README should document the standard local verification gates")
    expect("make lint" in vision and "make test" in vision and "make build" in vision,
           "VISION should document the standard local verification gates")
    expect("make lint" in changes and "make test" in changes and "make build" in changes,
           "CHANGES should mention the standard local verification gates")
    expect("scripts/check-baseline.py" in readme, "README should name the baseline checker")
    expect("xcshareddata/xcschemes" in readme or "shared" in readme.lower(), "README should document the shared CI scheme")
    expect("FABRIC_API_KEY" in readme and "CRASHLYTICS_BUILD_SECRET" in readme, "README should document required build settings")
    expect("placeholder API key" in readme and "placeholder API key" in vision and "placeholder API key" in security,
           "docs should describe the runtime Fabric placeholder guard")
    expect("whitespace-only" in readme and "whitespace-only" in vision and "whitespace-only" in security,
           "docs should describe trimming Fabric API key values before startup")
    expect("testable fabric api key validation" in readme.lower() and
           "testable fabric api key validation" in vision.lower() and
           "testable fabric api key validation" in security.lower(),
           "docs should describe the shared testable Fabric key validation helper")
    expect("case-insensitive placeholder" in readme.lower() and
           "case-insensitive placeholder" in vision.lower() and
           "case-insensitive placeholder" in security.lower(),
           "docs should describe case-insensitive placeholder rejection")
    expect("embedded placeholder" in readme.lower() and
           "embedded placeholder" in vision.lower() and
           "embedded placeholder" in security.lower(),
           "docs should describe embedded placeholder rejection")
    expect("named placeholder" in readme.lower() and
           "named placeholder" in vision.lower() and
           "named placeholder" in security.lower(),
           "docs should describe named placeholder fragment rejection")
    expect("build script placeholder" in readme.lower() and
           "build script placeholder" in vision.lower() and
           "build script placeholder" in security.lower(),
           "docs should describe build script placeholder rejection")
    expect("Twitter" not in readme, "README should not describe this Crashlytics sample as Twitter configuration")
    expect("placeholders" in changes.lower(), "CHANGES should mention placeholders")
    expect("whitespace-only" in changes, "CHANGES should mention whitespace-only Fabric API key handling")
    expect("runtime Fabric initialization" in changes, "CHANGES should mention runtime Fabric initialization guarding")
    expect("testable fabric api key validation" in changes.lower(), "CHANGES should mention testable Fabric key validation")
    expect("case-insensitive placeholder" in changes.lower(), "CHANGES should mention case-insensitive placeholder handling")
    expect("embedded placeholder" in changes.lower(), "CHANGES should mention embedded placeholder handling")
    expect("named placeholder" in changes.lower(), "CHANGES should mention named placeholder fragment handling")
    expect("build script placeholder" in changes.lower(), "CHANGES should mention build script placeholder handling")
    expect("whitespace-only CI" in changes, "CHANGES should mention whitespace-only CI secret handling")
    expect("status: completed" in plan, "baseline plan should be marked completed")
    expect("status: completed" in runtime_plan, "runtime Fabric placeholder guard plan should be marked completed")
    expect("status: completed" in trim_plan, "Fabric key trim guard plan should be marked completed")
    expect("status: completed" in validation_plan, "testable Fabric key validation plan should be marked completed")
    expect("status: completed" in case_plan, "case-insensitive Fabric placeholder plan should be marked completed")
    expect("status: completed" in embedded_plan, "embedded Fabric placeholder plan should be marked completed")
    expect("status: completed" in make_gates_plan, "make gate aliases plan should be marked completed")
    expect("status: completed" in named_plan, "named Fabric placeholder plan should be marked completed")
    expect("status: completed" in build_script_plan, "build script placeholder guard plan should be marked completed")
    expect("status: completed" in build_script_whitespace_plan,
           "build script whitespace secret guard plan should be marked completed")
    expect("status: completed" in hosted_validation_plan and "make check" in hosted_validation_plan,
           "hosted validation plan should be marked completed")
    expect("status: completed" in vendored_integrity_plan and "does not establish" in vendored_integrity_plan,
           "vendored crash SDK integrity plan should be marked completed and state its trust boundary")
    expect("status: completed" in hosted_xctest_plan and "make test" in hosted_xctest_plan and
           "hosted macOS XCTest run" in hosted_xctest_plan,
           "hosted XCTest plan should record executable test verification")
    expect(workflow == EXPECTED_WORKFLOW,
           "Check workflow should exactly match the bounded, credential-free XCTest contract")

    for pattern in ("*.local.xcconfig", "*.secrets.xcconfig", "FabricKeys.xcconfig", ".env", ".env.*", "__pycache__/", "*.pyc"):
        expect(pattern in gitignore, ".gitignore should keep {} out of git".format(pattern))


def main():
    check_required_files()
    check_parsable_resources()
    check_project_wiring()
    check_vendored_integrity()
    check_swift_and_secret_guardrails()
    check_docs()

    if shutil.which("xcodebuild"):
        result = subprocess.run(
            ["xcodebuild", "-list", "-project", "Jenkins iOS Sample.xcodeproj"],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        expect(result.returncode == 0,
               "xcodebuild could not parse Jenkins iOS Sample.xcodeproj: {}".format(result.stderr.strip()))
    else:
        print("xcodebuild unavailable; static iOS baseline only.")

    if FAILURES:
        print("Static baseline failed:")
        for failure in FAILURES:
            print("- {}".format(failure))
        return 1

    print("Static baseline passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
