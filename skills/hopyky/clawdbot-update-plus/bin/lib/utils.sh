#!/usr/bin/env bash
# Clawdbot Update Plus - Utility functions
# Version: 2.1.1

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global state
DRY_RUN="${DRY_RUN:-false}"
FORCE_UPDATE="${FORCE_UPDATE:-false}"

# Logging functions (all to stderr so they don't pollute function return values)
log_info() {
  echo -e "${BLUE}ℹ${NC} $1" >&2
}

log_success() {
  echo -e "${GREEN}✓${NC} $1" >&2
}

log_warning() {
  echo -e "${YELLOW}⚠${NC} $1" >&2
}

log_error() {
  echo -e "${RED}✗${NC} $1" >&2
  log_to_file "ERROR: $1"
}

log_to_file() {
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$timestamp] $1" >> "$LOG_FILE" 2>/dev/null || true
}

log_dry_run() {
  if [[ "$DRY_RUN" == true ]]; then
    echo -e "${YELLOW}[DRY-RUN]${NC} $1" >&2
  fi
}

# Path expansion helper
expand_path() {
  local path="$1"
  echo "$path" | sed "s|\${HOME}|$HOME|g" | sed "s|~|$HOME|g"
}

# Check if a command exists
command_exists() {
  command -v "$1" &>/dev/null
}

# Check available disk space (in MB)
get_available_disk_space() {
  local path="${1:-$BACKUP_DIR}"
  local os="$(uname)"

  if [[ "$os" == "Darwin" ]]; then
    df -m "$path" 2>/dev/null | awk 'NR==2 {print $4}'
  else
    df -BM --output=avail "$path" 2>/dev/null | tail -n 1 | sed 's/M//'
  fi
}

# Check disk space with minimum requirement
check_disk_space() {
  local required_mb="${1:-500}"
  local check_enabled="${CHECK_DISK:-true}"

  if [[ "$check_enabled" != true ]]; then
    return 0
  fi

  local available_mb=$(get_available_disk_space)
  available_mb=${available_mb:-0}

  if [[ $available_mb -lt $required_mb ]]; then
    log_error "Insufficient disk space: ${available_mb}MB available, ${required_mb}MB required"
    return 1
  fi

  log_info "Disk space check: ${available_mb}MB available (OK)"
  return 0
}

# Check internet connection
check_connection() {
  log_info "Checking internet connection..."
  if ! ping -c 1 github.com &> /dev/null; then
    log_error "No internet connection detected."
    return 1
  fi
  log_success "Internet connection is available."
  return 0
}

# Check if skill is in excluded list
is_excluded() {
  local skill_name="$1"
  local excluded_json="${EXCLUDED_SKILLS:-[]}"

  if [[ -z "$excluded_json" ]] || [[ "$excluded_json" == "null" ]] || [[ "$excluded_json" == "[]" ]]; then
    return 1
  fi

  # Parse excluded list
  local excluded_list_str="${excluded_json#[\([]}"
  excluded_list_str="${excluded_list_str%[\])]}"

  IFS=',' read -ra excluded_list <<< "$excluded_list_str"

  for excluded in "${excluded_list[@]}"; do
    excluded="${excluded//\'}"
    excluded="${excluded//\"/}"
    excluded="${excluded// /}"

    if [[ -n "$excluded" ]] && [[ "$skill_name" == "$excluded" ]]; then
      return 0
    fi
  done

  return 1
}

# Detect workspace automatically
detect_workspace() {
  log_info "Detecting workspace..."

  local possible_workspaces=(
    "${HOME}/clawd"
    "${HOME}/Documents/clawd"
    "${HOME}/workspace/clawd"
    "$(pwd)"
  )

  for ws in "${possible_workspaces[@]}"; do
    if [[ -d "$ws" ]] && { [[ -f "$ws/CLAWDBOT.md" ]] || [[ -f "$ws/AGENTS.md" ]]; }; then
      WORKSPACE="$ws"
      log_success "Workspace found: $WORKSPACE"
      return 0
    fi
  done

  log_warning "Could not detect workspace automatically, using: $WORKSPACE"
  return 0
}
