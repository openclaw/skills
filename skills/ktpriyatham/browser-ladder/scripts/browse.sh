#!/bin/bash
# browse.sh - Hierarchical browser with fallback chain
# Usage: browse.sh <url> [options]
#
# Options:
#   --screenshot <path>   Take screenshot
#   --pdf <path>          Generate PDF  
#   --html                Output page HTML
#   --level <1-4>         Force specific level
#   --verbose             Show which level was used

set -euo pipefail

URL="${1:-}"
SCREENSHOT=""
PDF=""
HTML=false
FORCE_LEVEL=""
VERBOSE=false

# Parse args
shift || true
while [[ $# -gt 0 ]]; do
  case $1 in
    --screenshot) SCREENSHOT="$2"; shift 2 ;;
    --pdf) PDF="$2"; shift 2 ;;
    --html) HTML=true; shift ;;
    --level) FORCE_LEVEL="$2"; shift 2 ;;
    --verbose) VERBOSE=true; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [[ -z "$URL" ]]; then
  echo "Usage: browse.sh <url> [--screenshot path] [--pdf path] [--html] [--level 1-4]"
  exit 1
fi

log() {
  if $VERBOSE; then echo "[browse] $1" >&2; fi
}

# Level 1: web_fetch (via curl)
try_level1() {
  log "Trying Level 1: web_fetch (curl)"
  if $HTML; then
    curl -sL "$URL" 2>/dev/null && return 0
  elif [[ -n "$SCREENSHOT" ]] || [[ -n "$PDF" ]]; then
    # Can't do screenshots/PDFs with curl
    return 1
  else
    # Just check if page loads
    curl -sL -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null | grep -q "200" && return 0
  fi
  return 1
}

# Level 2: Playwright Docker
try_level2() {
  log "Trying Level 2: Playwright Docker"
  
  if ! command -v docker &>/dev/null; then
    log "Docker not available"
    return 1
  fi
  
  # Check if Docker is running
  if ! docker info &>/dev/null; then
    log "Docker daemon not running"
    return 1
  fi
  
  if [[ -n "$SCREENSHOT" ]]; then
    local OUTPUT_DIR=$(dirname "$SCREENSHOT")
    local OUTPUT_FILE=$(basename "$SCREENSHOT")
    mkdir -p "$OUTPUT_DIR"
    
    docker run --rm -v "$OUTPUT_DIR:/output" \
      mcr.microsoft.com/playwright:v1.58.0-jammy \
      npx playwright screenshot "$URL" "/output/$OUTPUT_FILE" 2>/dev/null && return 0
      
  elif [[ -n "$PDF" ]]; then
    local OUTPUT_DIR=$(dirname "$PDF")
    local OUTPUT_FILE=$(basename "$PDF")
    mkdir -p "$OUTPUT_DIR"
    
    docker run --rm -v "$OUTPUT_DIR:/output" \
      mcr.microsoft.com/playwright:v1.58.0-jammy \
      npx playwright pdf "$URL" "/output/$OUTPUT_FILE" 2>/dev/null && return 0
      
  elif $HTML; then
    # For HTML, we need a script since npx playwright doesn't have a content command
    docker run --rm mcr.microsoft.com/playwright:v1.58.0-jammy \
      npx -y playwright-cli-extra content "$URL" 2>/dev/null && return 0
    
    # Fallback: just use curl if we got here for HTML
    return 1
  fi
  
  return 1
}

# Level 3: BrowserCat (free cloud)
try_level3() {
  log "Trying Level 3: BrowserCat"
  
  if [[ -z "${BROWSERCAT_API_KEY:-}" ]]; then
    log "BROWSERCAT_API_KEY not set"
    return 1
  fi
  
  # TODO: Implement BrowserCat API
  return 1
}

# Level 4: Browserless.io (paid)
try_level4() {
  log "Trying Level 4: Browserless.io"
  
  if [[ -z "${BROWSERLESS_TOKEN:-}" ]]; then
    log "BROWSERLESS_TOKEN not set"
    return 1
  fi
  
  if [[ -n "$SCREENSHOT" ]]; then
    curl -s -X POST "https://production-sfo.browserless.io/screenshot?token=$BROWSERLESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"url\": \"$URL\", \"options\": {\"fullPage\": true}}" \
      -o "$SCREENSHOT" 2>/dev/null && return 0
  elif [[ -n "$PDF" ]]; then
    curl -s -X POST "https://production-sfo.browserless.io/pdf?token=$BROWSERLESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"url\": \"$URL\"}" \
      -o "$PDF" 2>/dev/null && return 0
  elif $HTML; then
    curl -s -X POST "https://production-sfo.browserless.io/content?token=$BROWSERLESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"url\": \"$URL\"}" 2>/dev/null && return 0
  fi
  
  return 1
}

# Main execution
main() {
  local LEVELS=(1 2 3 4)
  
  # If level forced, only try that one
  if [[ -n "$FORCE_LEVEL" ]]; then
    LEVELS=("$FORCE_LEVEL")
  fi
  
  for level in "${LEVELS[@]}"; do
    case $level in
      1) try_level1 && { log "Success at Level 1"; exit 0; } ;;
      2) try_level2 && { log "Success at Level 2"; exit 0; } ;;
      3) try_level3 && { log "Success at Level 3"; exit 0; } ;;
      4) try_level4 && { log "Success at Level 4"; exit 0; } ;;
    esac
  done
  
  echo "All levels failed for URL: $URL" >&2
  exit 1
}

main
