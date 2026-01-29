#!/usr/bin/env bash
set -euo pipefail

TIMEOUT="${1:-5}"

# atvremote uses -t / --scan-timeout
atvremote scan -t "$TIMEOUT"
