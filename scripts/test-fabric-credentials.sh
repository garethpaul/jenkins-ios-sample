#!/bin/sh

set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
validator="$root/scripts/validate-fabric-credentials.sh"
valid_key=0123456789abcdef0123456789abcdef01234567
valid_secret=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef

expect_valid() {
  description=$1
  key=$2
  secret=$3
  if ! FABRIC_API_KEY=$key CRASHLYTICS_BUILD_SECRET=$secret "$validator"; then
    printf 'expected valid: %s\n' "$description" >&2
    exit 1
  fi
}

expect_invalid() {
  description=$1
  key=$2
  secret=$3
  if FABRIC_API_KEY=$key CRASHLYTICS_BUILD_SECRET=$secret "$validator"; then
    printf 'expected invalid: %s\n' "$description" >&2
    exit 1
  fi
}

expect_valid "exact lowercase hex" "$valid_key" "$valid_secret"
expect_valid "trimmed uppercase hex" "  $(printf '%s' "$valid_key" | tr '[:lower:]' '[:upper:]')  " " $(printf '%s' "$valid_secret" | tr '[:lower:]' '[:upper:]') "
expect_invalid "missing key" "" "$valid_secret"
expect_invalid "placeholder key" '$(FABRIC_API_KEY)' "$valid_secret"
expect_invalid "embedded whitespace" "${valid_key%?} " "$valid_secret"
expect_invalid "control character" "${valid_key%?}$(printf '\001')" "$valid_secret"
expect_invalid "non-hex key" "${valid_key%?}g" "$valid_secret"
expect_invalid "short key" "${valid_key%?}" "$valid_secret"
expect_invalid "non-hex secret" "$valid_key" "${valid_secret%?}g"
expect_invalid "short secret" "$valid_key" "${valid_secret%?}"

printf '%s\n' "Fabric credential validation tests passed."
