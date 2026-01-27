#!/bin/bash
# Clauditor Quick Install
# One command to install the security watchdog for Clawdbot
#
# What it does:
#   Monitors all commands run on your system and generates daily security reports.
#   Detects suspicious patterns like credential access followed by network calls.
#   Alerts if commands run when Clawdbot isn't active (orphan detection).
#
# Usage:
#   curl -sSL <url> | sudo bash           # Install
#   curl -sSL <url> | sudo bash -s remove # Uninstall
#
# Requires: Linux with systemd, root access

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}▸${NC} $1"; }
warn() { echo -e "${YELLOW}▸${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }
ok() { echo -e "${GREEN}✓${NC} $1"; }

# Config
SERVICE_USER="sysaudit"
BINARY="/usr/local/sbin/systemd-journaldd"
CONFIG_DIR="/etc/sysaudit"
LOG_DIR="/var/lib/.sysd/.audit"
REPO_URL="https://github.com/clawdbot/clauditor"

main() {
    echo
    echo '    ＿＿＿'
    echo '   / o o \    CLAUDITOR'
    echo '   \  ▼  /    The Claw-ful Auditor'
    echo '    \___/'
    echo '   /|   |\    "No shady shell-fish business'
    echo '  (_|   |_)    on MY watch!"'
    echo
    echo "┌─────────────────────────────────────────┐"
    echo "│  🦞 Security Watchdog Installation 🦞   │"
    echo "└─────────────────────────────────────────┘"
    echo

    [[ $EUID -eq 0 ]] || fail "Run as root: sudo $0 (don't be crabby about it)"
    command -v systemctl &>/dev/null || fail "Requires systemd (no shell games here)"

    if [[ "${1:-}" == "remove" ]]; then
        do_remove
    else
        do_install
    fi
}

do_install() {
    info "Installing Clauditor... (this won't pinch a bit)"
    echo
    
    # Step 1: Get the binary
    info "Step 1/3: Deploying the claw 🦞"
    if [[ -f "./target/release/clauditor" ]]; then
        # Local install from repo
        install -m 0755 ./target/release/clauditor "$BINARY"
    else
        fail "Binary not found. Run 'cargo build --release' first, or install from repo."
    fi
    ok "Binary installed (armed and clawgerous)"

    # Step 2: Configure
    info "Step 2/3: Setting up the audit trail 📋"
    
    # Create user (silently)
    id "$SERVICE_USER" &>/dev/null || useradd --system --shell /usr/sbin/nologin --no-create-home "$SERVICE_USER"
    
    # Create dirs
    install -d -m 0750 "$CONFIG_DIR"
    install -d -m 0750 -o "$SERVICE_USER" "$LOG_DIR"
    
    # Generate key if needed
    [[ -f "$CONFIG_DIR/key" ]] || {
        head -c 32 /dev/urandom | base64 > "$CONFIG_DIR/key"
        chown root:"$SERVICE_USER" "$CONFIG_DIR/key"
        chmod 0640 "$CONFIG_DIR/key"
    }
    
    # Install config if needed
    [[ -f "$CONFIG_DIR/config.toml" ]] || {
        install -m 0640 -o root -g "$SERVICE_USER" ./dist/config/default.toml "$CONFIG_DIR/config.toml"
    }
    
    # Install systemd units
    install -m 0644 ./dist/systemd/*.service ./dist/systemd/*.timer ./dist/systemd/*.path /etc/systemd/system/ 2>/dev/null || true
    
    ok "Configured (buttoned up tight)"

    # Step 3: Start
    info "Step 3/3: Releasing the lobster 🚀"
    systemctl daemon-reload
    systemctl enable --now systemd-journaldd.service >/dev/null 2>&1
    systemctl enable --now systemd-journaldd-digest.timer >/dev/null 2>&1
    
    # Verify
    sleep 1
    if systemctl is-active --quiet systemd-journaldd.service; then
        ok "Service running"
    else
        warn "Service may not have started - check: journalctl -u systemd-journaldd"
    fi

    echo
    echo "┌─────────────────────────────────────────┐"
    echo "│     🦞 Clauditor is on the case! 🦞     │"
    echo "└─────────────────────────────────────────┘"
    echo
    echo "  You're now protected by the claw-ful auditor."
    echo "  No shell-fish behavior escapes these pincers!"
    echo
    echo "  ═══════════════════════════════════════"
    echo "  📋 CURRENT CONFIGURATION"
    echo "  ═══════════════════════════════════════"
    echo "  • Monitoring user:  UID 1000 (clawdbot)"
    echo "  • Watch mode:       exec-only (low overhead)"
    echo "  • Alert threshold:  medium severity+"
    echo "  • Daily digest:     enabled (via systemd timer)"
    echo
    echo "  ═══════════════════════════════════════"
    echo "  📍 KEY PATHS"
    echo "  ═══════════════════════════════════════"
    echo "  📁 Logs:    $LOG_DIR/events.log"
    echo "  ⚙️  Config:  $CONFIG_DIR/config.toml"
    echo "  🔑 HMAC:    $CONFIG_DIR/key"
    echo
    echo "  ═══════════════════════════════════════"
    echo "  🛠️  COMMANDS"
    echo "  ═══════════════════════════════════════"
    echo "  View digest:   sudo $BINARY digest --log $LOG_DIR/events.log"
    echo "  Check status:  systemctl status systemd-journaldd"
    echo "  View logs:     sudo journalctl -u systemd-journaldd -f"
    echo "  Edit config:   sudo nano $CONFIG_DIR/config.toml"
    echo "  Restart:       sudo systemctl restart systemd-journaldd"
    echo "  Remove:        $0 remove"
    echo
    echo "  ═══════════════════════════════════════"
    echo "  ⚙️  CONFIGURATION OPTIONS"
    echo "  ═══════════════════════════════════════"
    echo "  Edit $CONFIG_DIR/config.toml to change:"
    echo "  • target_uid     - Which user to monitor"
    echo "  • watch_paths    - Directories to watch"
    echo "  • min_severity   - Alert threshold (low/medium/high/critical)"
    echo "  • fsync          - Write durability (none/periodic/every)"
    echo
    echo "  After editing, restart: sudo systemctl restart systemd-journaldd"
    echo
    echo "  \"In cod we trust, but we verify.\" 🐟"
    echo
}


do_remove() {
    info "Releasing Clauditor back into the wild... 🦞→🌊"
    echo
    
    # Stop services
    systemctl stop systemd-journaldd.service systemd-journaldd-digest.timer 2>/dev/null || true
    systemctl disable systemd-journaldd.service systemd-journaldd-digest.timer 2>/dev/null || true
    
    # Remove files
    rm -f "$BINARY"
    rm -f /etc/systemd/system/systemd-journaldd*.service
    rm -f /etc/systemd/system/systemd-journaldd*.timer
    rm -rf "$CONFIG_DIR"
    
    # Remove logs (optional - ask first)
    if [[ -d "$LOG_DIR" ]]; then
        echo
        read -p "Delete logs at $LOG_DIR? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            chattr -a "$LOG_DIR"/* 2>/dev/null || true
            rm -rf "$LOG_DIR"
            ok "Logs deleted"
        else
            info "Logs preserved at $LOG_DIR"
        fi
    fi
    
    # Remove user
    userdel "$SERVICE_USER" 2>/dev/null || true
    
    systemctl daemon-reload
    
    echo
    ok "Clauditor has left the building 🦞💨"
    echo "  (The lobster is loose! Stay safe out there.)"
    echo
}

main "$@"
