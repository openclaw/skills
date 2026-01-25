#!/usr/bin/env bash
# Clawdbot Update Plus - Backup functions
# Version: 2.1.1

# Create timestamped backup
create_backup() {
  local backup_name="clawdbot-update-$(date +%Y-%m-%d-%H:%M:%S).tar.gz"
  local backup_path="${BACKUP_DIR}/${backup_name}"
  local tmp_backup_dir=$(mktemp -d)
  local dirs_backed_up=0

  # Get backup paths
  local backup_paths_json=$(get_backup_paths)

  # Dry run mode
  if [[ "$DRY_RUN" == true ]]; then
    if [[ "$ENCRYPTION_ENABLED" == "true" ]]; then
      backup_name+=".gpg"
    fi
    log_dry_run "Would create backup: ${BACKUP_DIR}/${backup_name}"
    echo "$backup_paths_json" | jq -r '.[] | "  → \(.label): \(.path)"' | while read -r line; do
      log_dry_run "$line"
    done
    echo "$backup_name"
    return 0
  fi

  log_info "Creating backup archive..."
  log_to_file "Creating backup..."

  # Iterate over backup paths
  while IFS= read -r dir_config; do
    local dir_path=$(echo "$dir_config" | jq -r '.path')
    dir_path=$(expand_path "$dir_path")
    local dir_label=$(echo "$dir_config" | jq -r '.label')
    local dir_excludes=$(echo "$dir_config" | jq -r '.exclude // [] | .[]' 2>/dev/null)

    if [[ ! -d "$dir_path" ]]; then
      log_warning "Directory not found: $dir_path ($dir_label), skipping"
      continue
    fi

    log_info "Backing up $dir_label: $dir_path"

    # Create subdirectory in temp for this label
    mkdir -p "$tmp_backup_dir/$dir_label"

    # Build rsync exclude arguments
    local rsync_args="-a"
    while IFS= read -r exclude; do
      if [[ -n "$exclude" ]]; then
        rsync_args+=" --exclude=$exclude"
      fi
    done <<< "$dir_excludes"

    # Default excludes if none specified
    if [[ -z "$dir_excludes" ]]; then
      rsync_args+=" --exclude=.venv --exclude=node_modules --exclude=*.pyc --exclude=__pycache__"
    fi

    # Copy to temp dir
    eval rsync $rsync_args "$dir_path/" "$tmp_backup_dir/$dir_label/" 2>/dev/null || {
      log_warning "Failed to backup $dir_label, continuing..."
      continue
    }

    dirs_backed_up=$((dirs_backed_up + 1))
  done < <(echo "$backup_paths_json" | jq -c '.[]')

  if [[ $dirs_backed_up -eq 0 ]]; then
    log_error "No directories were backed up"
    rm -rf "$tmp_backup_dir"
    return 1
  fi

  # Create tar archive
  log_info "Compressing backup..."
  if ! tar -czf "$backup_path" -C "$tmp_backup_dir" . 2>/dev/null; then
    log_error "Failed to create backup archive"
    rm -rf "$tmp_backup_dir"
    return 1
  fi

  # Cleanup temp dir
  rm -rf "$tmp_backup_dir"

  # Encrypt if enabled
  if [[ "$ENCRYPTION_ENABLED" == "true" ]]; then
    if ! encrypt_backup "$backup_path"; then
      return 1
    fi
    backup_name+=".gpg"
    backup_path+=".gpg"
  fi

  local backup_size=$(du -h "$backup_path" 2>/dev/null | cut -f1)
  log_success "Backup created: $backup_path ($backup_size)"
  log_to_file "Backup created: $backup_name ($backup_size)"

  # Upload to remote if enabled
  if [[ "$REMOTE_STORAGE_ENABLED" == "true" ]]; then
    log_to_file "Uploading to remote storage..."
  fi
  upload_to_remote "$backup_path"

  # Clean old backups
  clean_old_backups

  echo "$backup_name"
}

# Encrypt backup file
encrypt_backup() {
  local backup_path="$1"

  if ! command_exists gpg; then
    log_error "gpg command not found, cannot encrypt."
    rm -f "$backup_path"
    return 1
  fi

  if [[ -z "$GPG_RECIPIENT" ]]; then
    log_error "Encryption enabled, but no GPG recipient set."
    rm -f "$backup_path"
    return 1
  fi

  log_info "Encrypting backup..."
  if ! gpg --encrypt --recipient "$GPG_RECIPIENT" --output "${backup_path}.gpg" "$backup_path" 2>/dev/null; then
    log_error "Failed to encrypt backup."
    rm -f "$backup_path"
    return 1
  fi

  rm -f "$backup_path"
  return 0
}

# Upload backup to remote storage
upload_to_remote() {
  local file_path="$1"

  if [[ "$REMOTE_STORAGE_ENABLED" != "true" ]]; then
    return 0
  fi

  if ! command_exists rclone; then
    log_warning "rclone command not found, skipping remote upload"
    return 0
  fi

  log_info "Uploading backup to remote storage..."
  if ! rclone copy "$file_path" "${RCLONE_REMOTE}${REMOTE_STORAGE_PATH}" 2>/dev/null; then
    log_warning "Failed to upload backup to remote storage"
    return 1
  fi

  log_success "Backup uploaded to remote storage"
  return 0
}

# Clean old backups (local and remote)
clean_old_backups() {
  local keep_count="${BACKUP_COUNT:-5}"

  log_info "Cleaning old backups (keeping last $keep_count)..."

  # Clean local backups
  local backup_files=$(ls -1t "${BACKUP_DIR}"/*.tar.gz* 2>/dev/null)
  local count=0

  while IFS= read -r backup_file; do
    count=$((count + 1))
    if [[ $count -gt $keep_count ]] && [[ -n "$backup_file" ]]; then
      rm -f "$backup_file"
      log_info "Deleted old backup: $(basename "$backup_file")"
    fi
  done <<< "$backup_files"

  # Clean remote backups if enabled
  if [[ "$REMOTE_STORAGE_ENABLED" == "true" ]] && command_exists rclone; then
    local remote_files=$(rclone lsf "${RCLONE_REMOTE}${REMOTE_STORAGE_PATH}" 2>/dev/null | sort -r)
    count=0

    while IFS= read -r remote_file; do
      count=$((count + 1))
      if [[ $count -gt $keep_count ]] && [[ -n "$remote_file" ]]; then
        rclone deletefile "${RCLONE_REMOTE}${REMOTE_STORAGE_PATH}/${remote_file}" 2>/dev/null
        log_info "Deleted remote backup: $remote_file"
      fi
    done <<< "$remote_files"
  fi
}

# List available backups
list_backups() {
  log_info "Available backups:"

  if [[ ! -d "$BACKUP_DIR" ]]; then
    log_warning "Backup directory not found: $BACKUP_DIR"
    return 1
  fi

  local backup_count=$(ls -1 "${BACKUP_DIR}"/*.tar.gz* 2>/dev/null | wc -l | tr -d ' ')

  if [[ "$backup_count" -eq 0 ]]; then
    log_info "No backups found."
    return 1
  fi

  while IFS= read -r backup_path; do
    local backup_file=$(basename "$backup_path")
    local backup_size=$(du -h "$backup_path" 2>/dev/null | cut -f1)
    local encrypted_symbol=""

    if [[ "${backup_file##*.}" == "gpg" ]]; then
      encrypted_symbol=" 🔒"
    fi

    echo "  • $backup_file ($backup_size)${encrypted_symbol}"
  done < <(ls -1t "${BACKUP_DIR}"/*.tar.gz* 2>/dev/null)

  return 0
}
