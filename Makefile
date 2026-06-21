ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell MAKEFILE_LIST_RAW='$(subst ','"'"',$(MAKEFILE_LIST))' /usr/bin/python3 -c "import os, shlex; path = os.environ['MAKEFILE_LIST_RAW']; marker = ' /'; path = '/' + path.rsplit(marker, 1)[1] if marker in path else path; print(shlex.quote(os.path.dirname(path) or '.'))")
$(eval check: ; /usr/bin/python3 $(ROOT)/scripts/check-baseline.py && cd $(ROOT) && /usr/bin/python3 -m unittest discover -s tests -v)

.PHONY: build check lint test

lint: check

test: check
	@if [ -x /usr/bin/xcodebuild ]; then cd $(ROOT) && ./scripts/run-tests.sh; else printf '%s\n' "Skipping XCTest: xcodebuild is not installed."; fi

build: check

check:
