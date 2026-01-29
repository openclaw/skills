#!/usr/bin/env bash
set -euo pipefail

SPEAKER="${1:?speaker name required}"
VOL="${2:?volume 0-100 required}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AIRFOIL_SH="$SCRIPT_DIR/../../airfoil/airfoil.sh"

"$AIRFOIL_SH" volume "$SPEAKER" "$VOL"
