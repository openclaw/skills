#!/usr/bin/env bash
# Clawdbot Update Plus - Configuration management
# Version: 2.1.1

# Default paths
WORKSPACE_DEFAULT="${HOME}/clawd"
BACKUP_DIR_DEFAULT="${HOME}/.clawdbot/backups"
CONFIG_FILE="${HOME}/.clawdbot/clawdbot-update.json"
LOG_FILE="${HOME}/.clawdbot/backups/update.log"

# Load configuration from JSON
load_config() {
  # Default values
  WORKSPACE="${WORKSPACE:-$WORKSPACE_DEFAULT}"
  BACKUP_DIR="${BACKUP_DIR:-$BACKUP_DIR_DEFAULT}"
  AUTO_UPDATE="false"
  BACKUP_BEFORE_UPDATE="true"
  BACKUP_COUNT="5"
  EXCLUDED_SKILLS=""

  # Backup paths (new v2 format)
  BACKUP_PATHS_JSON=""

  # Skills dirs (for updates)
  SKILLS_DIRS_JSON=""

  # Remote storage
  REMOTE_STORAGE_ENABLED="false"
  RCLONE_REMOTE=""
  REMOTE_STORAGE_PATH=""

  # Encryption
  ENCRYPTION_ENABLED="false"
  GPG_RECIPIENT=""

  # Notifications
  NOTIFY_ENABLED="false"
  NOTIFY_TARGET=""
  NOTIFY_ON_SUCCESS="true"
  NOTIFY_ON_ERROR="true"

  # Load from JSON config if exists
  if [[ -f "$CONFIG_FILE" ]]; then
    WORKSPACE=$(jq -r '.workspace // "'"$WORKSPACE_DEFAULT"'"' "$CONFIG_FILE")
    BACKUP_DIR=$(jq -r '.backup_dir // "'"$BACKUP_DIR_DEFAULT"'"' "$CONFIG_FILE")
    AUTO_UPDATE=$(jq -r '.auto_update // "false"' "$CONFIG_FILE")
    BACKUP_BEFORE_UPDATE=$(jq -r '.backup_before_update // "true"' "$CONFIG_FILE")
    BACKUP_COUNT=$(jq -r '.backup_count // 5' "$CONFIG_FILE")
    EXCLUDED_SKILLS=$(jq -r '.excluded_skills | @json' "$CONFIG_FILE" 2>/dev/null || echo "[]")

    # Remote storage
    REMOTE_STORAGE_ENABLED=$(jq -r '.remote_storage.enabled // "false"' "$CONFIG_FILE")
    RCLONE_REMOTE=$(jq -r '.remote_storage.rclone_remote // ""' "$CONFIG_FILE")
    REMOTE_STORAGE_PATH=$(jq -r '.remote_storage.path // ""' "$CONFIG_FILE")

    # Encryption
    ENCRYPTION_ENABLED=$(jq -r '.encryption.enabled // "false"' "$CONFIG_FILE")
    GPG_RECIPIENT=$(jq -r '.encryption.gpg_recipient // ""' "$CONFIG_FILE")

    # Notifications
    NOTIFY_ENABLED=$(jq -r '.notifications.enabled // "false"' "$CONFIG_FILE")
    NOTIFY_TARGET=$(jq -r '.notifications.target // ""' "$CONFIG_FILE")
    NOTIFY_ON_SUCCESS=$(jq -r '.notifications.on_success // "true"' "$CONFIG_FILE")
    NOTIFY_ON_ERROR=$(jq -r '.notifications.on_error // "true"' "$CONFIG_FILE")

    # Load backup_paths (v2 format)
    if jq -e '.backup_paths' "$CONFIG_FILE" >/dev/null 2>&1; then
      BACKUP_PATHS_JSON=$(jq -c '.backup_paths' "$CONFIG_FILE")
    fi

    # Load skills_dirs
    if jq -e '.skills_dirs' "$CONFIG_FILE" >/dev/null 2>&1; then
      SKILLS_DIRS_JSON=$(jq -c '.skills_dirs' "$CONFIG_FILE")
    else
      # Legacy: single skills_dir
      local skills_dir=$(jq -r '.skills_dir // "'"${HOME}/.clawdbot/skills"'"' "$CONFIG_FILE")
      SKILLS_DIRS_JSON=$(jq -n --arg path "$skills_dir" '[{path: $path, label: "default", update: true}]')
    fi
  else
    # No config file, use defaults
    SKILLS_DIRS_JSON=$(jq -n '[{path: "~/.clawdbot/skills", label: "default", update: true}]')
  fi

  # Ensure directories exist
  mkdir -p "$WORKSPACE" 2>/dev/null || true
  mkdir -p "$BACKUP_DIR" 2>/dev/null || true
}

# Validate configuration
validate_config() {
  log_info "Validating configuration..."

  if [[ -f "$CONFIG_FILE" ]]; then
    if ! jq . "$CONFIG_FILE" >/dev/null 2>&1; then
      log_error "Configuration file $CONFIG_FILE is not valid JSON."
      return 1
    fi
  fi

  if [[ ! -d "$WORKSPACE" ]]; then
    log_warning "Workspace directory $WORKSPACE does not exist, creating..."
    mkdir -p "$WORKSPACE"
  fi

  if [[ ! -d "$BACKUP_DIR" ]]; then
    log_warning "Backup directory $BACKUP_DIR does not exist, creating..."
    mkdir -p "$BACKUP_DIR"
  fi

  log_success "Configuration is valid."
  return 0
}

# Get backup paths (for backup operations)
get_backup_paths() {
  if [[ -n "$BACKUP_PATHS_JSON" ]] && [[ "$BACKUP_PATHS_JSON" != "null" ]]; then
    echo "$BACKUP_PATHS_JSON"
  else
    # Legacy fallback: derive from skills_dirs
    echo "$SKILLS_DIRS_JSON" | jq -c '[.[] | {path: .path, label: .label, exclude: [".venv", "node_modules", "*.pyc", "__pycache__"]}]'
  fi
}

# Get skills dirs (for update operations)
get_skills_dirs() {
  echo "$SKILLS_DIRS_JSON"
}

# Get a specific config value
get_config() {
  local key="$1"
  local default="$2"

  if [[ -f "$CONFIG_FILE" ]]; then
    local value=$(jq -r ".$key // \"$default\"" "$CONFIG_FILE" 2>/dev/null)
    echo "${value:-$default}"
  else
    echo "$default"
  fi
}
