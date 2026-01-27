#!/bin/bash
# Craft CLI Helper Script
# Quick shortcuts for common operations

CRAFT="$HOME/clawd/skills/craft-cli/craft"

# API URLs
WAVEDEPTH_API="https://connect.craft.do/links/5VruASgpXo0/api/v1"
PERSONAL_API="https://connect.craft.do/links/HHRuPxZZTJ6/api/v1"

case "$1" in
  "wavedepth"|"business"|"wd")
    "$CRAFT" config set-api "$WAVEDEPTH_API"
    echo "✅ Switched to wavedepth space"
    ;;
  "personal"|"me")
    "$CRAFT" config set-api "$PERSONAL_API"
    echo "✅ Switched to personal space"
    ;;
  "which"|"current")
    "$CRAFT" config get-api
    ;;
  *)
    # Pass through to craft
    "$CRAFT" "$@"
    ;;
esac
