#!/usr/bin/env python3
"""Read-only policy checks for the retired Fabric sample."""

from pathlib import Path
import os
import re


MAX_TEXT_BYTES = 1_048_576
RETIRED_ARTIFACT_PARTS = {"Fabric.framework", "Crashlytics.framework"}
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
    timeout-minutes: 15
    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Validate baseline and XCTest
        run: |
          /usr/bin/python3 scripts/check-baseline.py
          /usr/bin/python3 -m unittest discover -s tests -v
          /bin/sh ./scripts/run-tests.sh
"""


def _read_text(path):
    try:
        if path.stat().st_size > MAX_TEXT_BYTES:
            return None
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None


def inspect_repository(root):
    root = Path(root).resolve()
    failures = []
    text_files = {}

    for directory, directory_names, file_names in os.walk(root, followlinks=False):
        directory_path = Path(directory)
        for name in list(directory_names) + list(file_names):
            path = directory_path / name
            relative = path.relative_to(root)
            if path.is_symlink():
                failures.append("tracked repository content must not be a symlink: {}".format(relative))
                continue
            if RETIRED_ARTIFACT_PARTS.intersection(relative.parts):
                failures.append("vendored retired-provider artifact remains: {}".format(relative))
            if path.is_file():
                text = _read_text(path)
                if text is not None:
                    text_files[str(relative)] = text

    runtime_paths = {
        "Jenkins iOS Sample/AppDelegate.swift",
        "Jenkins iOS Sample/Info.plist",
        "Jenkins iOS Sample.xcodeproj/project.pbxproj",
        ".github/workflows/check.yml",
        "scripts/run-tests.sh",
    }
    combined_source = "\n".join(text_files.get(path, "") for path in runtime_paths)
    if re.search(r"\bimport\s+(Fabric|Crashlytics)\b|\bFabric\.with\s*\(", combined_source):
        failures.append("retired Fabric import or runtime initialization remains")
    if re.search(r"(?:Fabric|Crashlytics)\.framework/(?:run|submit)", combined_source):
        failures.append("retired Fabric upload execution remains")

    for path, text in text_files.items():
        if path.endswith("Info.plist") and re.search(r"<key>Fabric</key>|Crashlytics", text):
            failures.append("retired Fabric plist configuration remains: {}".format(path))

    project = text_files.get("Jenkins iOS Sample.xcodeproj/project.pbxproj", "")
    if "PBXShellScriptBuildPhase" in project or "shellScript =" in project:
        failures.append("Xcode project must not execute shell upload phases")
    if "CODE_SIGN_IDENTITY = \"iPhone Developer\"" in project:
        failures.append("Xcode project must not pin a signing identity")

    workflow = text_files.get(".github/workflows/check.yml", "")
    if workflow:
        if workflow != EXPECTED_WORKFLOW:
            failures.append("workflow must preserve exact reviewed workflow job, checkout, and validation step")
        if not re.search(r"(?m)^permissions:\n\s+contents:\s+read\s*$", workflow) or "write-all" in workflow:
            failures.append("workflow must use read-only workflow permissions")
        if re.search(r"\$\{\{\s*secrets\.", workflow):
            failures.append("workflow secret reference is forbidden")
        if "persist-credentials: false" not in workflow:
            failures.append("workflow checkout must disable persisted credentials")
        if re.search(r"(?i)\b(archive|exportarchive|codesign|notary|upload)\b", workflow):
            failures.append("workflow must not sign, archive, or upload artifacts")

    runner = text_files.get("scripts/run-tests.sh", "")
    for required in (
        "unset FABRIC_API_KEY CRASHLYTICS_BUILD_SECRET FABRIC_UPLOAD_TOOL",
        "CODE_SIGNING_ALLOWED=NO",
        "CODE_SIGNING_REQUIRED=NO",
        "CODE_SIGN_IDENTITY=",
        "run-xcodebuild.py",
        "/usr/bin/xcrun",
        "/usr/bin/xcodebuild",
        "/usr/bin/python3",
        "/usr/bin/awk",
        "/usr/bin/dirname",
    ):
        if required not in runner:
            failures.append("test runner is missing safe boundary: {}".format(required))
    if re.search(r"(?m)^\s*xcodebuild\b[\s\S]*\barchive\b", runner):
        failures.append("test runner must not archive")

    makefile = text_files.get("Makefile", "")
    make_lines = [line.strip() for line in makefile.splitlines()]
    expected_root_line = (
        "override ROOT := $(shell MAKEFILE_LIST_RAW='$(subst ','\"'\"',$(MAKEFILE_LIST))' "
        "python3 -c \"import os, shlex; path = os.environ['MAKEFILE_LIST_RAW']; "
        "marker = ' /'; path = '/' + path.rsplit(marker, 1)[1] if marker in path else path; "
        "print(shlex.quote(os.path.dirname(path) or '.'))\")"
    )
    expected_check_bootstrap_line = (
        "$(eval check: ; python3 $(ROOT)/scripts/check-baseline.py && cd $(ROOT) && "
        "python3 -m unittest discover -s tests -v)"
    )
    expected_command_lines = {
        ("@if command -v xcodebuild >/dev/null 2>&1; then cd $(ROOT) && ./scripts/run-tests.sh; "
         "else printf '%s\\n' \"Skipping XCTest: xcodebuild is not installed.\"; fi"),
    }
    root_assignments = [
        line for line in make_lines
        if re.match(r"^(?:[^:=]+:\s*)?(?:override\s+|export\s+|private\s+)*ROOT\s*(?::=|=|\?=|\+=|!=)", line)
    ]
    makefile_list_guard = (
        "ifneq ($(origin MAKEFILE_LIST),file)\n"
        "$(error MAKEFILE_LIST must not be overridden)\n"
        "endif\n"
    )
    if makefile.count(makefile_list_guard) != 1:
        failures.append("Makefile must reject MAKEFILE_LIST overrides")
    if (make_lines.count(expected_root_line) != 1 or
            make_lines.count(expected_check_bootstrap_line) != 1 or
            root_assignments != [expected_root_line] or
            not expected_command_lines.issubset(set(make_lines))):
        failures.append("Makefile must resolve repository root independently")

    return failures
