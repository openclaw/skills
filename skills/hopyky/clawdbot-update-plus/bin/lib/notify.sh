#!/usr/bin/env bash
# Clawdbot Update Plus - Notification functions
# Version: 2.1.1

# Detect channel from target format
detect_channel() {
  local target="$1"

  if [[ "$target" == +* ]]; then
    echo "whatsapp"
  elif [[ "$target" == @* ]]; then
    echo "telegram"
  elif [[ "$target" == channel:* ]]; then
    echo "discord"
  else
    echo "whatsapp"  # Default
  fi
}

# Send notification via Clawdbot messaging
send_notification() {
  local status="$1"  # "success", "info", or "error"
  local details="${2:-}"

  # Check if notifications are enabled
  if [[ "$NOTIFY_ENABLED" != "true" ]] && [[ "$NOTIFICATION_ENABLED" != "true" ]]; then
    return 0
  fi

  # Check notification type preference
  if [[ "$status" == "success" || "$status" == "info" ]] && [[ "$NOTIFY_ON_SUCCESS" != "true" ]]; then
    return 0
  fi
  if [[ "$status" == "error" ]] && [[ "$NOTIFY_ON_ERROR" != "true" ]]; then
    return 0
  fi

  # Check if target is configured
  if [[ -z "$NOTIFY_TARGET" ]]; then
    log_warning "Notification enabled but no target configured"
    return 0
  fi

  if [[ "$DRY_RUN" == true ]]; then
    log_dry_run "Would send notification to $NOTIFY_TARGET"
    return 0
  fi

  log_info "Sending notification..."

  # Check if clawdbot command is available
  if ! command_exists clawdbot; then
    log_warning "clawdbot command not found, skipping notification"
    return 0
  fi

  # Detect channel from target format
  local channel=$(detect_channel "$NOTIFY_TARGET")

  # Build message
  local message=""
  if [[ "$status" == "success" ]]; then
    message="✅ *Clawdbot Update Complete*"
    message+="\n\n📦 Updates applied successfully."
  elif [[ "$status" == "info" ]]; then
    message="ℹ️ *Clawdbot Update Check*"
    message+="\n\n📋 Everything is already up to date."
  else
    message="❌ *Clawdbot Update Failed*"
    message+="\n\n⚠️ An error occurred during the update."
  fi

  if [[ -n "$details" ]]; then
    message+="\n\n$details"
  fi

  message+="\n\n🕐 $(date '+%Y-%m-%d %H:%M:%S')"

  # Send via clawdbot message
  if clawdbot message send --channel "$channel" --target "$NOTIFY_TARGET" --message "$message" 2>/dev/null; then
    log_success "Notification sent to $NOTIFY_TARGET via $channel"
    log_to_file "Notification sent to $NOTIFY_TARGET via $channel"
  else
    log_warning "Could not send notification (check gateway status)"
    log_to_file "WARNING: Could not send notification"
  fi
}

# Force enable notifications for this run
enable_notifications() {
  NOTIFICATION_ENABLED="true"
}
