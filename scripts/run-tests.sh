#!/bin/sh

set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PROJECT=${XCODE_PROJECT:-Jenkins iOS Sample.xcodeproj}
SCHEME=${XCODE_SCHEME:-Jenkins iOS Sample}
CONFIGURATION=${CONFIGURATION:-Debug}
XCODEBUILD_TIMEOUT_SECONDS=${XCODEBUILD_TIMEOUT_SECONDS:-600}
SIMULATOR_ID=

case "$PROJECT" in
    /*|*..*|-) printf '%s\n' "XCODE_PROJECT must name a regular repository project directory." >&2; exit 2 ;;
esac

PROJECT_PATH=$ROOT/$PROJECT
old_ifs=$IFS
IFS=/
set -f
set -- $PROJECT
set +f
IFS=$old_ifs
current_path=$ROOT
for component in "$@"; do
    current_path=$current_path/$component
    if [ -L "$current_path" ]; then
        printf '%s\n' "XCODE_PROJECT must name a regular repository project directory." >&2
        exit 2
    fi
done
if [ ! -d "$PROJECT_PATH" ] || [ "${PROJECT_PATH##*.}" != xcodeproj ]; then
    printf '%s\n' "XCODE_PROJECT must name a regular repository project directory." >&2
    exit 2
fi

case "$SCHEME$CONFIGURATION" in
    *[![:print:]]*|*-*) printf '%s\n' "Xcode scheme and configuration must be printable non-option values." >&2; exit 2 ;;
esac

unset FABRIC_API_KEY CRASHLYTICS_BUILD_SECRET FABRIC_UPLOAD_TOOL

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

python3 "$ROOT/scripts/run-xcodebuild.py" "$XCODEBUILD_TIMEOUT_SECONDS" xcodebuild \
    -project "$PROJECT_PATH" \
    -scheme "$SCHEME" \
    -configuration "$CONFIGURATION" \
    -destination "$DESTINATION" \
    -destination-timeout 120 \
    -parallel-testing-enabled NO \
    CODE_SIGNING_ALLOWED=NO \
    CODE_SIGNING_REQUIRED=NO \
    CODE_SIGN_IDENTITY= \
    test
