#!/usr/bin/env bash
set -euo pipefail

# Faster scan when you know IP(s)
# Usage: scan-hosts.sh <ip[,ip...]> [timeout]
HOSTS="${1:?hosts (ip or ip,ip) required}"
TIMEOUT="${2:-3}"

atvremote --scan-hosts "$HOSTS" -t "$TIMEOUT" scan
