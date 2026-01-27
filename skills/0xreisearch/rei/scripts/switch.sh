#!/usr/bin/env bash
# Switch between Rei and Opus
# Usage: ./switch.sh rei|opus

set -e

TARGET="${1:-}"

if [[ -z "$TARGET" ]]; then
  echo "Usage: $0 <rei|opus>"
  echo ""
  echo "  rei   - Switch to rei/rei-qwen3-coder"
  echo "  opus  - Switch to anthropic/claude-opus-4-5"
  exit 1
fi

case "$TARGET" in
  rei)
    echo "Switching to Rei..."
    clawdbot models set rei/rei-qwen3-coder
    ;;
  opus)
    echo "Switching to Opus..."
    clawdbot models set anthropic/claude-opus-4-5
    ;;
  *)
    echo "Unknown target: $TARGET"
    echo "Use 'rei' or 'opus'"
    exit 1
    ;;
esac
