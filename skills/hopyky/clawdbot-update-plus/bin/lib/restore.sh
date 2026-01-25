#!/usr/bin/env bash
# Clawdbot Update Plus - Restore functions
# Version: 2.1.1

# Restore from backup
restore_backup() {
  local backup_id="$1"
  local restore_label="${2:-}"
  local force_restore="${3:-}"

  # Handle --force as second argument
  if [[ "$restore_label" == "--force" ]]; then
    force_restore="--force"
    restore_label=""
  fi

  if [[ -z "$backup_id" ]]; then
    log_error "Please specify a backup ID"
    list_backups
    return 1
  fi

  local backup_path="${BACKUP_DIR}/${backup_id}"
  local tmp_extract_dir=$(mktemp -d)
  local decrypted_path=""
  local should_cleanup_decrypted=false

  if [[ ! -f "$backup_path" ]]; then
    log_error "Backup not found: $backup_path"
    list_backups
    return 1
  fi

  # Decrypt if needed
  if [[ "${backup_path##*.}" == "gpg" ]]; then
    if ! decrypt_backup "$backup_path" decrypted_path; then
      rm -rf "$tmp_extract_dir"
      return 1
    fi
    backup_path="$decrypted_path"
    should_cleanup_decrypted=true
  fi

  # Extract to temp directory
  log_info "Extracting backup..."
  if ! tar -xzf "$backup_path" -C "$tmp_extract_dir" 2>/dev/null; then
    log_error "Failed to extract backup."
    cleanup_restore "$tmp_extract_dir" "$decrypted_path" "$should_cleanup_decrypted"
    return 1
  fi

  # Detect backup structure
  local labels_found=()
  for dir in "$tmp_extract_dir"/*/; do
    if [[ -d "$dir" ]]; then
      labels_found+=("$(basename "$dir")")
    fi
  done

  # Restore based on format
  if [[ ${#labels_found[@]} -eq 0 ]]; then
    restore_legacy_backup "$tmp_extract_dir" "$force_restore"
  else
    restore_labeled_backup "$tmp_extract_dir" "$restore_label" "$force_restore" "${labels_found[@]}"
  fi

  local result=$?

  # Cleanup
  cleanup_restore "$tmp_extract_dir" "$decrypted_path" "$should_cleanup_decrypted"

  if [[ $result -eq 0 ]]; then
    log_success "Restore completed from: $backup_id"
  fi

  return $result
}

# Decrypt backup file
decrypt_backup() {
  local backup_path="$1"
  local -n output_path=$2

  if ! command_exists gpg; then
    log_error "gpg command not found, cannot decrypt."
    return 1
  fi

  log_info "Decrypting backup..."
  output_path=$(mktemp)

  if ! gpg --decrypt --output "$output_path" "$backup_path" 2>/dev/null; then
    log_error "Failed to decrypt backup."
    rm -f "$output_path"
    return 1
  fi

  return 0
}

# Restore legacy backup (flat structure)
restore_legacy_backup() {
  local tmp_dir="$1"
  local force_restore="$2"

  log_info "Detected legacy backup format"

  # Get default skills dir
  local skills_dir=$(echo "$SKILLS_DIRS_JSON" | jq -r '.[0].path // "~/.clawdbot/skills"')
  skills_dir=$(expand_path "$skills_dir")

  if [[ "$force_restore" != "--force" ]]; then
    log_warning "This will restore to: ${skills_dir}"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      log_info "Restore cancelled"
      return 0
    fi
  fi

  log_info "Restoring to $skills_dir"
  rsync -a "$tmp_dir/" "$skills_dir/" 2>/dev/null
  log_success "Restored legacy backup"
  return 0
}

# Restore labeled backup (new format)
restore_labeled_backup() {
  local tmp_dir="$1"
  local restore_label="$2"
  local force_restore="$3"
  shift 3
  local labels_found=("$@")

  log_info "Detected backup labels: ${labels_found[*]}"

  # Build restore mapping
  declare -A restore_map
  restore_map=()

  # From backup_paths config
  local backup_paths_json=$(get_backup_paths)
  if [[ -n "$backup_paths_json" ]] && [[ "$backup_paths_json" != "null" ]]; then
    while IFS= read -r path_config; do
      local label=$(echo "$path_config" | jq -r '.label')
      local path=$(echo "$path_config" | jq -r '.path')
      path=$(expand_path "$path")
      restore_map["$label"]="$path"
    done < <(echo "$backup_paths_json" | jq -c '.[]')
  fi

  # Default mappings for common labels
  [[ -z "${restore_map[config]}" ]] && restore_map["config"]="${HOME}/.clawdbot"
  [[ -z "${restore_map[workspace]}" ]] && restore_map["workspace"]="${HOME}/clawd"
  [[ -z "${restore_map[prod]}" ]] && restore_map["prod"]="${HOME}/.clawdbot/skills"
  [[ -z "${restore_map[dev]}" ]] && restore_map["dev"]="${HOME}/clawd/skills"
  [[ -z "${restore_map[default]}" ]] && restore_map["default"]="${HOME}/.clawdbot/skills"

  # Show restore plan
  echo ""
  log_info "Restore plan:"
  for label in "${labels_found[@]}"; do
    local target="${restore_map[$label]:-unknown}"
    if [[ -n "$restore_label" ]] && [[ "$label" != "$restore_label" ]]; then
      echo "  ○ $label → $target (skipped)"
    else
      echo "  → $label → $target"
    fi
  done
  echo ""

  # Confirm
  if [[ "$force_restore" != "--force" ]]; then
    log_warning "This will overwrite the above directories!"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      log_info "Restore cancelled"
      return 0
    fi
  fi

  # Execute restore
  local restored_count=0
  for label in "${labels_found[@]}"; do
    # Skip if specific label requested
    if [[ -n "$restore_label" ]] && [[ "$label" != "$restore_label" ]]; then
      continue
    fi

    local target="${restore_map[$label]}"
    if [[ -z "$target" ]] || [[ "$target" == "unknown" ]]; then
      log_warning "Unknown label '$label', skipping"
      continue
    fi

    log_info "Restoring $label → $target"

    # Ensure target parent exists
    mkdir -p "$(dirname "$target")"

    # Restore with rsync
    if rsync -a --delete "$tmp_dir/$label/" "$target/" 2>/dev/null; then
      log_success "Restored $label"
      restored_count=$((restored_count + 1))
    else
      log_error "Failed to restore $label"
    fi
  done

  if [[ $restored_count -eq 0 ]]; then
    log_error "No labels were restored"
    return 1
  fi

  return 0
}

# Cleanup restore temp files
cleanup_restore() {
  local tmp_dir="$1"
  local decrypted_path="$2"
  local should_cleanup="$3"

  rm -rf "$tmp_dir"
  if [[ "$should_cleanup" == true ]] && [[ -n "$decrypted_path" ]]; then
    rm -f "$decrypted_path"
  fi
}

# Compare two backups
diff_backups() {
  local backup1="$1"
  local backup2="$2"

  if [[ -z "$backup1" ]] || [[ -z "$backup2" ]]; then
    log_error "Please provide two backup IDs to compare."
    list_backups
    return 1
  fi

  local backup1_path="${BACKUP_DIR}/${backup1}"
  local backup2_path="${BACKUP_DIR}/${backup2}"

  if [[ ! -f "$backup1_path" ]]; then
    log_error "Backup not found: $backup1_path"
    return 1
  fi
  if [[ ! -f "$backup2_path" ]]; then
    log_error "Backup not found: $backup2_path"
    return 1
  fi

  local tmp_dir1=$(mktemp -d)
  local tmp_dir2=$(mktemp -d)

  log_info "Extracting backups for comparison..."

  if ! tar -xzf "$backup1_path" -C "$tmp_dir1" 2>/dev/null; then
    log_error "Failed to extract $backup1"
    rm -rf "$tmp_dir1" "$tmp_dir2"
    return 1
  fi

  if ! tar -xzf "$backup2_path" -C "$tmp_dir2" 2>/dev/null; then
    log_error "Failed to extract $backup2"
    rm -rf "$tmp_dir1" "$tmp_dir2"
    return 1
  fi

  log_info "Comparing backups..."
  diff -r -u "$tmp_dir1" "$tmp_dir2" || true

  rm -rf "$tmp_dir1" "$tmp_dir2"
  log_info "Comparison complete."
  return 0
}
