#!/bin/sh

set -eu

PROJECT=${XCODE_PROJECT:-Jenkins iOS Sample.xcodeproj}
SCHEME=${XCODE_SCHEME:-Jenkins iOS Sample}
CONFIGURATION=${CONFIGURATION:-Debug}
SIMULATOR_ID=

find_simulator_id() {
    requested_name=$1
    xcrun simctl list devices available | awk -F '[()]' -v requested_name="$requested_name" '
        /^[[:space:]]+iPhone/ {
            name=$1
            sub(/^[[:space:]]+/, "", name)
            sub(/[[:space:]]+$/, "", name)
            if (requested_name == "" || name == requested_name) {
                print $2
                exit
            }
        }
    '
}

wait_for_simulator() {
    python3 - "$1" <<'PY'
import subprocess
import sys

try:
    completed = subprocess.run(
        ["xcrun", "simctl", "bootstatus", sys.argv[1], "-b"],
        timeout=180,
    )
except subprocess.TimeoutExpired:
    sys.exit(124)

sys.exit(completed.returncode)
PY
}

if ! command -v xcodebuild >/dev/null 2>&1; then
    printf '%s\n' "xcodebuild is required to run Jenkins iOS Sample tests." >&2
    exit 127
fi

if [ -n "${IOS_DESTINATION:-}" ]; then
    DESTINATION=$IOS_DESTINATION
else
    SIMULATOR_ID=$(find_simulator_id "${IOS_SIMULATOR_NAME:-}")
    if [ -z "$SIMULATOR_ID" ]; then
        printf '%s\n' "No matching available iPhone simulator was found." >&2
        exit 1
    fi
    DESTINATION="platform=iOS Simulator,id=${SIMULATOR_ID}"
fi

if [ -n "$SIMULATOR_ID" ]; then
    xcrun simctl boot "$SIMULATOR_ID" >/dev/null 2>&1 || true
    if ! wait_for_simulator "$SIMULATOR_ID"; then
        xcrun simctl shutdown "$SIMULATOR_ID" >/dev/null 2>&1 || true
        xcrun simctl boot "$SIMULATOR_ID"
        wait_for_simulator "$SIMULATOR_ID"
    fi
fi

xcodebuild \
    -project "$PROJECT" \
    -scheme "$SCHEME" \
    -configuration "$CONFIGURATION" \
    -destination "$DESTINATION" \
    -destination-timeout 120 \
    -parallel-testing-enabled NO \
    CODE_SIGNING_ALLOWED=NO \
    test
