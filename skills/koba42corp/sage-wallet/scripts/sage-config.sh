#!/usr/bin/env bash
# sage-config.sh — Configuration management for Sage Wallet skill
# Cross-platform support for Mac, Linux, Windows

set -euo pipefail

# Default config location
SAGE_CONFIG_DIR="${SAGE_CONFIG_DIR:-$HOME/.config/sage-wallet}"
SAGE_CONFIG_FILE="${SAGE_CONFIG_DIR}/config.json"

# Platform detection
detect_platform() {
  case "$(uname -s)" in
    Darwin*)  echo "mac" ;;
    Linux*)   echo "linux" ;;
    MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
    *)        echo "linux" ;;
  esac
}

# Get default cert path for platform
get_default_cert_path() {
  local platform="${1:-$(detect_platform)}"
  case "$platform" in
    mac)     echo "$HOME/Library/Application Support/com.rigidnetwork.sage/ssl/wallet.crt" ;;
    linux)   echo "$HOME/.local/share/sage/ssl/wallet.crt" ;;
    windows) echo "${APPDATA:-$HOME}/com.rigidnetwork.sage/ssl/wallet.crt" ;;
  esac
}

# Get default key path for platform
get_default_key_path() {
  local platform="${1:-$(detect_platform)}"
  case "$platform" in
    mac)     echo "$HOME/Library/Application Support/com.rigidnetwork.sage/ssl/wallet.key" ;;
    linux)   echo "$HOME/.local/share/sage/ssl/wallet.key" ;;
    windows) echo "${APPDATA:-$HOME}/com.rigidnetwork.sage/ssl/wallet.key" ;;
  esac
}

# Initialize config with defaults
init_config() {
  mkdir -p "$SAGE_CONFIG_DIR"
  if [[ ! -f "$SAGE_CONFIG_FILE" ]]; then
    cat > "$SAGE_CONFIG_FILE" << 'EOF'
{
  "platform": "auto",
  "rpc_url": "https://127.0.0.1:9257",
  "cert_path": null,
  "key_path": null,
  "fingerprint": null,
  "auto_login": false
}
EOF
    echo "Created config at $SAGE_CONFIG_FILE"
  fi
}

# Read config value
get_config() {
  local key="$1"
  local default="${2:-}"
  
  if [[ ! -f "$SAGE_CONFIG_FILE" ]]; then
    echo "$default"
    return
  fi
  
  local value
  value=$(jq -r ".$key // empty" "$SAGE_CONFIG_FILE" 2>/dev/null || echo "")
  
  if [[ -z "$value" || "$value" == "null" ]]; then
    echo "$default"
  else
    echo "$value"
  fi
}

# Set config value
set_config() {
  local key="$1"
  local value="$2"
  
  init_config
  
  local tmp_file
  tmp_file=$(mktemp)
  
  # Handle different value types
  if [[ "$value" == "null" || "$value" == "true" || "$value" == "false" || "$value" =~ ^[0-9]+$ ]]; then
    jq ".$key = $value" "$SAGE_CONFIG_FILE" > "$tmp_file"
  else
    jq ".$key = \"$value\"" "$SAGE_CONFIG_FILE" > "$tmp_file"
  fi
  
  mv "$tmp_file" "$SAGE_CONFIG_FILE"
  echo "Set $key = $value"
}

# Reset config to defaults
reset_config() {
  rm -f "$SAGE_CONFIG_FILE"
  init_config
  echo "Config reset to defaults"
}

# Show current config
show_config() {
  if [[ ! -f "$SAGE_CONFIG_FILE" ]]; then
    echo "No config file found. Run 'init' to create one."
    return 1
  fi
  
  local platform rpc_url cert_path key_path fingerprint auto_login
  
  platform=$(get_config "platform" "auto")
  rpc_url=$(get_config "rpc_url" "https://127.0.0.1:9257")
  cert_path=$(get_config "cert_path" "")
  key_path=$(get_config "key_path" "")
  fingerprint=$(get_config "fingerprint" "")
  auto_login=$(get_config "auto_login" "false")
  
  # Resolve effective paths
  local effective_platform="$platform"
  [[ "$platform" == "auto" ]] && effective_platform=$(detect_platform)
  
  local effective_cert="${cert_path:-$(get_default_cert_path "$effective_platform")}"
  local effective_key="${key_path:-$(get_default_key_path "$effective_platform")}"
  
  echo "Sage Wallet Configuration"
  echo "========================="
  echo "Config file: $SAGE_CONFIG_FILE"
  echo ""
  echo "Settings:"
  echo "  platform:    $platform (effective: $effective_platform)"
  echo "  rpc_url:     $rpc_url"
  echo "  cert_path:   ${cert_path:-<default>}"
  echo "  key_path:    ${key_path:-<default>}"
  echo "  fingerprint: ${fingerprint:-<not set>}"
  echo "  auto_login:  $auto_login"
  echo ""
  echo "Effective paths:"
  echo "  cert: $effective_cert"
  echo "  key:  $effective_key"
  echo ""
  
  # Check if files exist
  if [[ -f "$effective_cert" ]]; then
    echo "  ✓ Certificate found"
  else
    echo "  ✗ Certificate NOT found"
  fi
  
  if [[ -f "$effective_key" ]]; then
    echo "  ✓ Key found"
  else
    echo "  ✗ Key NOT found"
  fi
}

# Resolve effective config values (for use by other scripts)
resolve_config() {
  local platform rpc_url cert_path key_path
  
  platform=$(get_config "platform" "auto")
  [[ "$platform" == "auto" ]] && platform=$(detect_platform)
  
  rpc_url=$(get_config "rpc_url" "https://127.0.0.1:9257")
  cert_path=$(get_config "cert_path" "")
  key_path=$(get_config "key_path" "")
  
  [[ -z "$cert_path" ]] && cert_path=$(get_default_cert_path "$platform")
  [[ -z "$key_path" ]] && key_path=$(get_default_key_path "$platform")
  
  echo "SAGE_PLATFORM=$platform"
  echo "SAGE_RPC_URL=$rpc_url"
  echo "SAGE_CERT_PATH=$cert_path"
  echo "SAGE_KEY_PATH=$key_path"
  echo "SAGE_FINGERPRINT=$(get_config "fingerprint" "")"
  echo "SAGE_AUTO_LOGIN=$(get_config "auto_login" "false")"
}

# Main command handler
main() {
  local cmd="${1:-show}"
  shift || true
  
  case "$cmd" in
    init)
      init_config
      ;;
    show|config)
      show_config
      ;;
    get)
      get_config "$@"
      ;;
    set)
      set_config "$@"
      ;;
    reset)
      reset_config
      ;;
    resolve)
      resolve_config
      ;;
    platform)
      if [[ -n "${1:-}" ]]; then
        set_config "platform" "$1"
      else
        detect_platform
      fi
      ;;
    cert)
      set_config "cert_path" "$1"
      ;;
    key)
      set_config "key_path" "$1"
      ;;
    rpc)
      set_config "rpc_url" "$1"
      ;;
    fingerprint)
      set_config "fingerprint" "$1"
      ;;
    autologin)
      local val="false"
      [[ "$1" == "on" || "$1" == "true" || "$1" == "1" ]] && val="true"
      set_config "auto_login" "$val"
      ;;
    help|--help|-h)
      echo "Usage: sage-config.sh <command> [args]"
      echo ""
      echo "Commands:"
      echo "  init                  Initialize config file"
      echo "  show, config          Show current configuration"
      echo "  get <key>             Get config value"
      echo "  set <key> <value>     Set config value"
      echo "  reset                 Reset to defaults"
      echo "  resolve               Output resolved config as env vars"
      echo "  platform [value]      Get/set platform (auto|mac|linux|windows)"
      echo "  cert <path>           Set certificate path"
      echo "  key <path>            Set key path"
      echo "  rpc <url>             Set RPC URL"
      echo "  fingerprint <fp>      Set default fingerprint"
      echo "  autologin <on|off>    Set auto-login"
      ;;
    *)
      echo "Unknown command: $cmd"
      echo "Run 'sage-config.sh help' for usage"
      exit 1
      ;;
  esac
}

# Only run main if executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
