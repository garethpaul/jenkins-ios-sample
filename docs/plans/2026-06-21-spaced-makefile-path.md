# Spaced Makefile Path

## Problem

The documented absolute `make -f` invocation failed when the checkout path
contained spaces because GNU Make list functions split `MAKEFILE_LIST` on
whitespace while deriving the repository root.

## Change

- Derive the root from the raw Makefile path with shell-safe single-quote
  escaping.
- Keep the `override ROOT` assignment so callers cannot redirect verification
  to another tree.
- Cover an external dry-run against a checkout path containing spaces and
  shell metacharacters.

## Validation

- Run `make check`, `make lint`, `make test`, and `make build` from the checkout.
- Run the same targets with an absolute Makefile path from another directory.
- Confirm the native XCTest stage remains an explicit skip when Xcode is not
  installed.
