#!/usr/bin/env bash
# Clawdbot Update Plus - Cron management functions
# Version: 2.1.1

# Install cron job for automatic updates
install_cron() {
  local cron_schedule="${1:-0 2 * * *}"  # Default: 2 AM daily
  local script_path="${SCRIPT_DIR}/clawdbot-update-plus"
  local log_path="${BACKUP_DIR}/cron-update.log"
  local cron_comment="# Clawdbot Update Plus - Auto-update"
  local cron_cmd="${cron_schedule} ${script_path} update >> ${log_path} 2>&1"

  # Check if already installed
  if crontab -l 2>/dev/null | grep -q "clawdbot-update-plus"; then
    log_warning "Cron job already installed. Use 'uninstall-cron' first to reinstall."
    echo ""
    echo "Current cron entry:"
    crontab -l 2>/dev/null | grep -A1 "Clawdbot Update Plus"
    return 1
  fi

  log_info "Installing cron job..."
  echo ""
  echo "  Schedule: ${cron_schedule}"
  echo "  Command:  ${script_path} update"
  echo "  Log file: ${log_path}"
  echo ""

  # Append to crontab
  {
    crontab -l 2>/dev/null || true
    echo ""
    echo "$cron_comment"
    echo "$cron_cmd"
  } | crontab -

  log_success "Cron job installed!"
  echo ""
  log_info "To change schedule, edit with: crontab -e"
  log_info "To remove, run: clawdbot-update-plus uninstall-cron"

  return 0
}

# Uninstall cron job
uninstall_cron() {
  if ! crontab -l 2>/dev/null | grep -q "clawdbot-update-plus"; then
    log_warning "No cron job found for clawdbot-update-plus"
    return 1
  fi

  log_info "Removing cron job..."

  # Remove lines containing clawdbot-update-plus
  crontab -l 2>/dev/null | grep -v "clawdbot-update-plus" | grep -v "Clawdbot Update Plus" | crontab -

  log_success "Cron job removed!"
  return 0
}

# Clean old log files
clean_logs() {
  log_info "Cleaning old log files..."
  find "${BACKUP_DIR}" -name "*.log" -mtime +30 -delete 2>/dev/null
  log_success "Old logs cleaned."
}
