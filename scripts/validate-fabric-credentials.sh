#!/bin/sh

trim_value() {
  printf '%s' "$1" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'
}

is_hex_value() {
  value=$(trim_value "$1")
  expected_length=$2
  printf '%s' "$value" | LC_ALL=C grep -Eq "^[0-9A-Fa-f]{$expected_length}$"
}

is_hex_value "${FABRIC_API_KEY-}" 40 &&
  is_hex_value "${CRASHLYTICS_BUILD_SECRET-}" 64
