#!/bin/bash
# n8n API wrapper - uses virtual environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Activate venv and run python script
source "$SKILL_DIR/.venv/bin/activate"
python3 "$SCRIPT_DIR/n8n_api.py" "$@"
