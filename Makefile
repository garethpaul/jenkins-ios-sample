ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell MAKEFILE_LIST_RAW='$(subst ','"'"',$(MAKEFILE_LIST))' python3 -c "import os, shlex; path = os.environ['MAKEFILE_LIST_RAW']; marker = ' /'; path = '/' + path.rsplit(marker, 1)[1] if marker in path else path; print(shlex.quote(os.path.dirname(path) or '.'))")
$(eval check: ; python3 $(ROOT)/scripts/check-baseline.py && cd $(ROOT) && python3 -m unittest discover -s tests -v)

.PHONY: build check lint test

lint: check

test: check
	@if command -v xcodebuild >/dev/null 2>&1; then cd $(ROOT) && ./scripts/run-tests.sh; else printf '%s\n' "Skipping XCTest: xcodebuild is not installed."; fi

build: check

check:
