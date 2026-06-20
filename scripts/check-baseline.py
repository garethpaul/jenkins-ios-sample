#!/usr/bin/env python3
"""Validate the credential-free, unsigned Jenkins iOS sample baseline."""

from pathlib import Path
import json
import plistlib
import subprocess
import sys
import xml.etree.ElementTree as ET

from repository_policy import inspect_repository


ROOT = Path(__file__).resolve().parents[1]


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def main():
    failures = inspect_repository(ROOT)

    required = [
        ".github/workflows/check.yml",
        "Jenkins iOS Sample.xcodeproj/project.pbxproj",
        "Jenkins iOS Sample.xcodeproj/xcshareddata/xcschemes/Jenkins iOS Sample.xcscheme",
        "Jenkins iOS Sample/AppDelegate.swift",
        "Jenkins iOS Sample/Info.plist",
        "Jenkins iOS Sample/Base.lproj/Main.storyboard",
        "Jenkins iOS Sample/Base.lproj/LaunchScreen.xib",
        "Jenkins iOS Sample/Images.xcassets/AppIcon.appiconset/Contents.json",
        "Jenkins iOS SampleTests/Jenkins_iOS_SampleTests.swift",
        "Makefile",
        "README.md",
        "SECURITY.md",
        "scripts/run-tests.sh",
        "scripts/run-xcodebuild.py",
        "tests/test_ci_boundary.py",
        "tests/test_repository_policy.py",
    ]
    for relative in required:
        path = ROOT / relative
        require(path.exists(), "required path is missing: {}".format(relative), failures)
        require(not path.is_symlink(), "required path must not be a symlink: {}".format(relative), failures)

    for relative in (
        "Jenkins iOS Sample/Info.plist",
        "Jenkins iOS SampleTests/Info.plist",
    ):
        try:
            with (ROOT / relative).open("rb") as handle:
                plistlib.load(handle)
        except Exception as error:
            failures.append("invalid plist {}: {}".format(relative, error))

    for relative in (
        "Jenkins iOS Sample/Base.lproj/Main.storyboard",
        "Jenkins iOS Sample/Base.lproj/LaunchScreen.xib",
        "Jenkins iOS Sample.xcodeproj/xcshareddata/xcschemes/Jenkins iOS Sample.xcscheme",
    ):
        try:
            ET.parse(str(ROOT / relative))
        except Exception as error:
            failures.append("invalid XML {}: {}".format(relative, error))

    try:
        json.loads((ROOT / "Jenkins iOS Sample/Images.xcassets/AppIcon.appiconset/Contents.json").read_text())
    except Exception as error:
        failures.append("invalid app icon JSON: {}".format(error))

    project = (ROOT / "Jenkins iOS Sample.xcodeproj/project.pbxproj").read_text(encoding="utf-8")
    require(project.count("SWIFT_VERSION = 5.0;") == 4, "all app/test configurations must use Swift 5", failures)
    require(project.count("IPHONEOS_DEPLOYMENT_TARGET = 12.0;") == 2, "project must keep iOS 12 target", failures)
    require("Jenkins iOS SampleTests.xctest" in (ROOT / "Jenkins iOS Sample.xcodeproj/xcshareddata/xcschemes/Jenkins iOS Sample.xcscheme").read_text(),
            "shared scheme must execute XCTest", failures)

    try:
        tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).split(b"\0")
        require(not any(b"/xcuserdata/" in path for path in tracked), "xcuserdata must not be tracked", failures)
    except Exception as error:
        failures.append("unable to inspect tracked paths: {}".format(error))

    if failures:
        for failure in failures:
            print("FAIL: {}".format(failure), file=sys.stderr)
        return 1
    print("Jenkins iOS retired-provider baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
