#!/usr/bin/env bash
set -euo pipefail

SPEAKER="${1:?speaker name required}"

# Delegate to the existing Airfoil skill.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AIRFOIL_SH="$SCRIPT_DIR/../../airfoil/airfoil.sh"

"$AIRFOIL_SH" connect "$SPEAKER"
