#!/bin/bash
# install.sh - One-time setup for claude-oauth-refresher

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/claude-oauth-refresh-config.json"
PLIST_FILE="com.clawdbot.claude-oauth-refresher.plist"
LAUNCHAGENTS_DIR="$HOME/Library/LaunchAgents"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  claude-oauth-refresher installer${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${CYAN}This installer runs ONCE to set up automatic token refresh.${NC}"
echo -e "${CYAN}The refresh job will run every 2 hours in the background.${NC}"
echo ""
echo -e "${CYAN}To change settings later:${NC}"
echo -e "  1. Edit: $CONFIG_FILE"
echo -e "  2. Ask Clawdbot: \"disable Claude refresh notifications\""
echo -e "  3. Changes apply automatically - no need to re-run installer!"
echo ""
read -p "Press Enter to continue..." -r
echo ""

# Step 1: Verify setup
echo -e "${BLUE}[1/6]${NC} Running verification..."
if "$SCRIPT_DIR/verify-setup.sh"; then
    echo ""
else
    echo ""
    echo -e "${RED}Verification failed. Please fix the errors above.${NC}"
    exit 1
fi

# Step 2: Config
echo -e "${BLUE}[2/6]${NC} Setting up config..."

# Try to auto-detect notification settings
DETECTED_CHANNEL=""
DETECTED_TARGET=""
if [[ -x "$SCRIPT_DIR/detect-notification-config.sh" ]]; then
    if detection=$("$SCRIPT_DIR/detect-notification-config.sh" 2>/dev/null); then
        DETECTED_CHANNEL=$(echo "$detection" | cut -d'|' -f1)
        DETECTED_TARGET=$(echo "$detection" | cut -d'|' -f2)
        echo -e "${GREEN}✓${NC} Auto-detected: $DETECTED_CHANNEL → $DETECTED_TARGET"
    fi
fi

# Check if config already exists (from old config.json or new name)
EXISTING_CONFIG=""
if [[ -f "$SCRIPT_DIR/config.json" ]]; then
    EXISTING_CONFIG="$SCRIPT_DIR/config.json"
elif [[ -f "$CONFIG_FILE" ]]; then
    EXISTING_CONFIG="$CONFIG_FILE"
fi

if [[ -n "$EXISTING_CONFIG" ]]; then
    echo -e "${YELLOW}⚠${NC} Config already exists: $EXISTING_CONFIG"
    echo ""
    read -p "Overwrite with new interactive config? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        # Migrate old config.json to new name if needed
        if [[ "$EXISTING_CONFIG" == "$SCRIPT_DIR/config.json" ]]; then
            echo "Migrating config.json → claude-oauth-refresh-config.json"
            # Check if it has old notification structure
            if jq -e '.notify_on_success' "$EXISTING_CONFIG" &> /dev/null; then
                # Migrate old format to new
                OLD_SUCCESS=$(jq -r '.notify_on_success // false' "$EXISTING_CONFIG")
                OLD_FAILURE=$(jq -r '.notify_on_failure // true' "$EXISTING_CONFIG")
                jq --argjson on_success "$OLD_SUCCESS" \
                   --argjson on_failure "$OLD_FAILURE" \
                   'del(.notify_on_success, .notify_on_failure) | .notifications = {on_success: $on_success, on_failure: $on_failure}' \
                   "$EXISTING_CONFIG" > "$CONFIG_FILE"
                echo -e "${GREEN}✓${NC} Migrated to new config format with notification types"
                rm "$EXISTING_CONFIG"
            else
                mv "$EXISTING_CONFIG" "$CONFIG_FILE"
                echo -e "${GREEN}✓${NC} Renamed to new config filename"
            fi
        fi
        echo "Keeping existing config"
        echo ""
    else
        # User wants to reconfigure
        CREATE_NEW_CONFIG=true
    fi
else
    CREATE_NEW_CONFIG=true
fi

# Interactive notification setup
if [[ "$CREATE_NEW_CONFIG" == "true" ]]; then
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  Configure Notifications${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}💡 Recommendation:${NC} Keep all enabled for the first run to verify it works."
    echo "   You can disable them later by:"
    echo "   1. Editing: $CONFIG_FILE"
    echo "   2. Asking Clawdbot: \"disable Claude refresh notifications\""
    echo ""
    
    # Prompt for each notification type
    read -p "Enable \"✅ Token refreshed!\" notification? [Y/n] " -n 1 -r NOTIFY_SUCCESS_INPUT
    echo ""
    if [[ $NOTIFY_SUCCESS_INPUT =~ ^[Nn]$ ]]; then
        NOTIFY_SUCCESS="false"
    else
        NOTIFY_SUCCESS="true"
    fi
    
    read -p "Enable \"❌ Refresh failed\" notification? [Y/n] " -n 1 -r NOTIFY_FAILURE_INPUT
    echo ""
    if [[ $NOTIFY_FAILURE_INPUT =~ ^[Nn]$ ]]; then
        NOTIFY_FAILURE="false"
    else
        NOTIFY_FAILURE="true"
    fi
    
    echo ""
    echo -e "${GREEN}✓${NC} Notification preferences saved"
    echo ""
    
    # Create config with detected values or prompts
    if [[ -n "$DETECTED_CHANNEL" ]] && [[ -n "$DETECTED_TARGET" ]]; then
        cat > "$CONFIG_FILE" << EOF
{
  "refresh_buffer_minutes": 30,
  "log_file": "~/clawd/logs/claude-oauth-refresh.log",
  "notifications": {
    "on_success": $NOTIFY_SUCCESS,
    "on_failure": $NOTIFY_FAILURE
  },
  "notification_channel": "$DETECTED_CHANNEL",
  "notification_target": "$DETECTED_TARGET"
}
EOF
        echo -e "${GREEN}✓${NC} Created config with auto-detected values"
        echo "  → Channel: $DETECTED_CHANNEL"
        echo "  → Target: $DETECTED_TARGET"
    else
        cat > "$CONFIG_FILE" << EOF
{
  "refresh_buffer_minutes": 30,
  "log_file": "~/clawd/logs/claude-oauth-refresh.log",
  "notifications": {
    "on_success": $NOTIFY_SUCCESS,
    "on_failure": $NOTIFY_FAILURE
  },
  "notification_channel": "telegram",
  "notification_target": "YOUR_CHAT_ID"
}
EOF
        echo -e "${YELLOW}⚠${NC} Could not auto-detect notification settings"
        echo ""
        echo "Please configure your notification target:"
        echo "  → Edit: $CONFIG_FILE"
        echo "  → See SKILL.md section: 'Finding Your Target ID'"
        echo ""
        read -p "Press Enter when ready to continue..." -r
    fi
fi
echo ""

# Step 3: Test refresh
echo -e "${BLUE}[3/6]${NC} Testing token refresh..."
chmod +x "$SCRIPT_DIR"/*.sh
if "$SCRIPT_DIR/refresh-token.sh"; then
    echo -e "${GREEN}✓${NC} Refresh successful"
else
    echo -e "${RED}✗${NC} Refresh failed - check logs"
    tail -10 ~/clawd/logs/claude-oauth-refresh.log
    exit 1
fi
echo ""

# Step 4: Create launchd plist
echo -e "${BLUE}[4/6]${NC} Creating launchd service..."
cat > "$SCRIPT_DIR/$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.clawdbot.claude-oauth-refresher</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$SCRIPT_DIR/refresh-token.sh</string>
    </array>
    
    <key>StartInterval</key>
    <integer>7200</integer>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>$HOME/clawd/logs/claude-oauth-refresher-stdout.log</string>
    
    <key>StandardErrorPath</key>
    <string>$HOME/clawd/logs/claude-oauth-refresher-stderr.log</string>
    
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin</string>
    </dict>
</dict>
</plist>
EOF
echo -e "${GREEN}✓${NC} Created $PLIST_FILE"
echo ""

# Step 5: Install launchd plist
echo -e "${BLUE}[5/6]${NC} Installing launchd service..."
mkdir -p "$LAUNCHAGENTS_DIR"

# Unload if already loaded
if launchctl list | grep -q "com.clawdbot.claude-oauth-refresher"; then
    launchctl unload "$LAUNCHAGENTS_DIR/$PLIST_FILE" 2>/dev/null || true
    echo "  → Unloaded existing service"
fi

cp "$SCRIPT_DIR/$PLIST_FILE" "$LAUNCHAGENTS_DIR/$PLIST_FILE"
launchctl load "$LAUNCHAGENTS_DIR/$PLIST_FILE"
echo -e "${GREEN}✓${NC} Loaded service (runs every 2 hours)"
echo ""

# Step 6: Verify
echo -e "${BLUE}[6/6]${NC} Verifying installation..."
sleep 2
if launchctl list | grep -q "com.clawdbot.claude-oauth-refresher"; then
    echo -e "${GREEN}✓${NC} Service is running"
else
    echo -e "${YELLOW}⚠${NC} Service may not be loaded (check: launchctl list)"
fi
echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Installation complete!${NC}"
echo ""
echo "What happens now:"
echo "  • Refresh runs automatically 30 minutes before token expiry"
echo "  • Claude tokens expire ~8 hours after refresh"
echo "  • Next refresh in ~7.5 hours from last successful refresh"
echo "  • Config changes apply automatically (just edit the file)"
echo "  • Only re-run this installer to reinstall/fix"
echo ""
echo "Notification settings:"
if [[ -f "$CONFIG_FILE" ]]; then
    SHOW_SUCCESS=$(jq -r '.notifications.on_success' "$CONFIG_FILE" 2>/dev/null || echo "unknown")
    SHOW_FAILURE=$(jq -r '.notifications.on_failure' "$CONFIG_FILE" 2>/dev/null || echo "unknown")
    echo "  • Success (✅): $SHOW_SUCCESS"
    echo "  • Failure (❌): $SHOW_FAILURE"
fi
echo ""
echo "Change settings:"
echo "  • Edit: $CONFIG_FILE"
echo "  • Or ask Clawdbot: \"disable Claude refresh notifications\""
echo ""
echo "Monitor:"
echo "  • Logs: tail -f ~/clawd/logs/claude-oauth-refresh.log"
echo "  • Status: launchctl list | grep claude-oauth-refresher"
echo "  • Manual test: $SCRIPT_DIR/refresh-token.sh"
echo ""
echo "Uninstall:"
echo "  • Run: $SCRIPT_DIR/uninstall.sh"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
