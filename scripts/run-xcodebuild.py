#!/usr/bin/env python3
"""Run one unsigned xcodebuild command with a process-group deadline."""

import os
import signal
import subprocess
import sys


def main(arguments):
    if len(arguments) < 3:
        print("usage: run-xcodebuild.py TIMEOUT COMMAND [ARG ...]", file=sys.stderr)
        return 2
    try:
        timeout = int(arguments[1])
    except ValueError:
        print("XCODEBUILD_TIMEOUT_SECONDS must be an integer.", file=sys.stderr)
        return 2
    if timeout < 1 or timeout > 1800:
        print("XCODEBUILD_TIMEOUT_SECONDS must be between 1 and 1800.", file=sys.stderr)
        return 2

    environment = os.environ.copy()
    for name in ("FABRIC_API_KEY", "CRASHLYTICS_BUILD_SECRET", "FABRIC_UPLOAD_TOOL"):
        environment.pop(name, None)

    process = subprocess.Popen(arguments[2:], env=environment, start_new_session=True)
    try:
        return process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        print("xcodebuild timed out after {} seconds.".format(timeout), file=sys.stderr)
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        return 124


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
