.PHONY: build check lint test

lint: check

test: check
	@if command -v xcodebuild >/dev/null 2>&1; then ./scripts/run-tests.sh; else printf '%s\n' "Skipping XCTest: xcodebuild is not installed."; fi

build: check

check:
	python3 scripts/check-baseline.py
