#!/bin/sh
set -eu

expect_eta() {
    expected=$1
    shift
    actual=$(./transfer-eta "$@")
    if [ "$actual" != "$expected" ]; then
        printf 'Expected %s, got %s\n' "$expected" "$actual" >&2
        exit 1
    fi
}

reject() {
    if ./transfer-eta "$@" > /dev/null 2>&1; then
        printf 'Invalid input was accepted: %s\n' "$*" >&2
        exit 1
    else
        status=$?
        [ "$status" -eq 2 ]
    fi
}

expect_eta eta_seconds=13 100 8
configured_rate=$(awk '$1 == "#define" && $2 == "DEFAULT_RATE_MIB_S" {print $3}' defaults.h)
[ -n "$configured_rate" ]
expect_eta "$(./transfer-eta 100 "$configured_rate")" 100
expect_eta eta_seconds=20 100 5
expect_eta eta_seconds=12 96 8
expect_eta eta_seconds=1 1 8
reject 100 0
reject 0 8
reject 10x 8
reject -100 8
reject '100 ' 8
reject 999999999999999999999999999999 8
reject
reject 100 8 5
./transfer-eta --help | grep -Fx "Default transfer rate: $configured_rate MiB/s"
printf 'transfer-eta smoke tests passed\n'
