#!/usr/bin/env python3
"""Static baseline checks for the Jenkins iOS Fabric/Crashlytics sample."""

from __future__ import print_function

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
        "CHANGES.md",
        "Crashlytics.framework/Crashlytics",
        "Crashlytics.framework/Headers/Crashlytics.h",
        "Fabric.framework/Fabric",
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
        "docs/plans/2026-06-08-jenkins-ios-baseline.md",
        "docs/readme-overview.svg",
        "scripts/check-baseline.py",
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
    expect("IPHONEOS_DEPLOYMENT_TARGET = 8.3;" in pbxproj, "legacy deployment target should remain visible")
    expect('CODE_SIGN_IDENTITY = "iPhone Developer";' in pbxproj, "sample code signing identity should remain visible")
    expect("$FABRIC_API_KEY" in pbxproj, "Fabric run script should use FABRIC_API_KEY")
    expect("$CRASHLYTICS_BUILD_SECRET" in pbxproj, "Fabric run script should use CRASHLYTICS_BUILD_SECRET")
    expect("Skipping Fabric run script" in pbxproj, "Fabric run script should skip when secrets are absent")
    expect(not re.search(r"Fabric\.framework/run\s+[0-9a-f]{40}\s+[0-9a-f]{64}", pbxproj), "Fabric run script should not commit raw key material")
    expect("Jenkins iOS SampleTests.xctest" in scheme, "shared Xcode scheme should include the test target")

    tracked_xcuserdata = [path for path in tracked_paths() if "/xcuserdata/" in path]
    expect(not tracked_xcuserdata, "tracked xcuserdata should be moved to xcshareddata: {}".format(", ".join(tracked_xcuserdata)))


def check_swift_and_secret_guardrails():
    swift_paths = sorted(rel("Jenkins iOS Sample").glob("*.swift")) + sorted(rel("Jenkins iOS SampleTests").glob("*.swift"))
    source = "\n".join(strip_swift_comments(path.read_text(encoding="utf-8")) for path in swift_paths)

    expect("Fabric.with([Crashlytics()])" in source, "AppDelegate should initialize Fabric/Crashlytics")
    expect("Crashlytics.sharedInstance().crash()" not in source, "sample should not include forced crash behavior")
    expect(not re.search(r"\b(?:print|println|NSLog)\s*\(", source), "first-party Swift should not add console logging")

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
    gitignore = read_text(".gitignore")

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

    expect("scripts/check-baseline.py" in readme, "README should name the baseline checker")
    expect("xcshareddata/xcschemes" in readme or "shared" in readme.lower(), "README should document the shared CI scheme")
    expect("FABRIC_API_KEY" in readme and "CRASHLYTICS_BUILD_SECRET" in readme, "README should document required build settings")
    expect("Twitter" not in readme, "README should not describe this Crashlytics sample as Twitter configuration")
    expect("placeholders" in changes.lower(), "CHANGES should mention placeholders")
    expect("status: completed" in plan, "baseline plan should be marked completed")

    for pattern in ("*.local.xcconfig", "*.secrets.xcconfig", "FabricKeys.xcconfig", ".env", ".env.*", "__pycache__/", "*.pyc"):
        expect(pattern in gitignore, ".gitignore should keep {} out of git".format(pattern))


def main():
    check_required_files()
    check_parsable_resources()
    check_project_wiring()
    check_swift_and_secret_guardrails()
    check_docs()

    if shutil.which("xcodebuild"):
        print("xcodebuild is available; run a simulator/CI build separately for legacy Fabric validation.")
    else:
        print("xcodebuild unavailable; skipping legacy iOS build/test and using static baseline checks.")

    if FAILURES:
        print("Static baseline failed:")
        for failure in FAILURES:
            print("- {}".format(failure))
        return 1

    print("Static baseline passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
