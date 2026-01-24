#!/bin/bash
# test-detection.sh - Test auto-detection without modifying config

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo -e "${BLUE}Testing notification auto-detection...${NC}"
echo ""

# Test detection
if [[ -x "$SCRIPT_DIR/detect-notification-config.sh" ]]; then
    if result=$("$SCRIPT_DIR/detect-notification-config.sh" 2>/dev/null); then
        channel=$(echo "$result" | cut -d'|' -f1)
        target=$(echo "$result" | cut -d'|' -f2)
        
        echo -e "${GREEN}✓ Detection successful!${NC}"
        echo ""
        echo "Would configure:"
        echo "  notification_channel: $channel"
        echo "  notification_target: $target"
        echo ""
        
        # Show what config would look like
        echo "Generated config would be:"
        echo ""
        cat << EOF
{
  "refresh_buffer_minutes": 30,
  "log_file": "~/clawd/logs/claude-oauth-refresh.log",
  "notifications": {
    "on_success": false,
    "on_failure": true
  },
  "notification_channel": "$channel",
  "notification_target": "$target"
}
EOF
        echo ""
        
        # Check if current config matches
        if [[ -f "$SCRIPT_DIR/claude-oauth-refresh-config.json" ]]; then
            current_channel=$(jq -r '.notification_channel // ""' "$SCRIPT_DIR/claude-oauth-refresh-config.json" 2>/dev/null)
            current_target=$(jq -r '.notification_target // ""' "$SCRIPT_DIR/claude-oauth-refresh-config.json" 2>/dev/null)
            
            if [[ "$current_channel" == "$channel" ]] && [[ "$current_target" == "$target" ]]; then
                echo -e "${GREEN}✓ Current config matches detected values${NC}"
            else
                echo -e "${YELLOW}! Current config differs:${NC}"
                echo "  Current: $current_channel → $current_target"
                echo "  Detected: $channel → $target"
                echo ""
                echo "Run ./install.sh to update config with detected values"
            fi
        else
            echo "No claude-oauth-refresh-config.json found - run ./install.sh to create"
        fi
    else
        echo -e "${YELLOW}⚠ Auto-detection failed${NC}"
        echo ""
        echo "Possible reasons:"
        echo "  • Clawdbot config not found (~/.clawdbot/clawdbot.json)"
        echo "  • No messaging channels enabled in Clawdbot"
        echo "  • Channel config missing target ID fields"
        echo ""
        echo "You'll need to configure manually during install"
        echo "See SKILL.md section: 'Finding Your Target ID'"
    fi
else
    echo -e "${YELLOW}⚠ Detection script not found${NC}"
    echo "Run: chmod +x $SCRIPT_DIR/detect-notification-config.sh"
fi

echo ""
echo "Next step: ./verify-setup.sh"
