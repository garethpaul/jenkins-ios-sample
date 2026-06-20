override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: build check lint test

lint: check

test: check
	@if command -v xcodebuild >/dev/null 2>&1; then cd "$(ROOT)" && ./scripts/run-tests.sh; else printf '%s\n' "Skipping XCTest: xcodebuild is not installed."; fi

build: check

check:
	python3 "$(ROOT)/scripts/check-baseline.py"
	cd "$(ROOT)" && python3 -m unittest discover -s tests -v
