#!/bin/bash
# verify-setup.sh - Pre-flight checks for claude-oauth-refresher

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Tracking
ERRORS=0
WARNINGS=0

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  claude-oauth-refresher verification${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check 1: macOS
echo -n "Checking OS... "
if [[ "$OSTYPE" == "darwin"* ]]; then
    MACOS_VERSION=$(sw_vers -productVersion)
    echo -e "${GREEN}✓${NC} macOS $MACOS_VERSION"
    echo "  → Requires: macOS 10.13 (High Sierra) or newer"
else
    echo -e "${RED}✗${NC} Not macOS (detected: $OSTYPE)"
    echo "  → This skill requires macOS for Keychain access"
    ((ERRORS++))
fi

# Check 2: Claude CLI installed
echo -n "Checking Claude CLI... "
if command -v claude &> /dev/null; then
    CLAUDE_VERSION=$(claude --version 2>&1 | head -n1 || echo "unknown")
    echo -e "${GREEN}✓${NC} Found ($CLAUDE_VERSION)"
else
    echo -e "${RED}✗${NC} Not found"
    echo "  → Install: brew install claude"
    echo "  → Or visit: https://github.com/anthropics/claude-cli"
    ((ERRORS++))
fi

# Check 3: auth-profiles.json exists
echo -n "Checking auth profiles... "
AUTH_PROFILES="$HOME/.clawdbot/agents/main/agent/auth-profiles.json"
if [[ -f "$AUTH_PROFILES" ]]; then
    echo -e "${GREEN}✓${NC} Found"
    
    # Check if it has a default profile
    if command -v jq &> /dev/null; then
        if jq -e '.default' "$AUTH_PROFILES" &> /dev/null; then
            echo "  → Default profile configured"
        else
            echo -e "  ${YELLOW}⚠${NC} No default profile found"
            ((WARNINGS++))
        fi
    fi
else
    echo -e "${RED}✗${NC} Not found"
    echo "  → Authenticate first: claude auth"
    ((ERRORS++))
fi

# Check 4: Keychain credentials
echo -n "Checking Keychain credentials... "

# Scan for ALL "Claude Code-credentials" entries (account name irrelevant)
SERVICE="Claude Code-credentials"
ALL_ACCOUNTS=$(security dump-keychain 2>/dev/null | \
    awk '/^class: "genp"/,/^keychain:/ {
        if (/"acct"<blob>=/) {
            gsub(/.*"acct"<blob>="/, "");
            gsub(/".*/, "");
            account=$0
        }
        if (/"svce"<blob>="'"$SERVICE"'"/) {
            print account
        }
    }' | sort -u)

KEYCHAIN_FOUND=false
VALID_ACCOUNT=""

# Iterate through each entry to find one with complete OAuth data
while IFS= read -r account; do
    [[ -z "$account" ]] && continue
    
    KEYCHAIN_DATA=$(security find-generic-password -s "$SERVICE" -a "$account" -w 2>/dev/null || echo "")
    
    if [[ -n "$KEYCHAIN_DATA" ]]; then
        # Check if it has valid OAuth tokens
        if echo "$KEYCHAIN_DATA" | python3 -c "import sys, json; data=json.load(sys.stdin); exit(0 if 'claudeAiOauth' in data and 'refreshToken' in data['claudeAiOauth'] else 1)" 2>/dev/null; then
            KEYCHAIN_FOUND=true
            VALID_ACCOUNT="$account"
            break
        fi
    fi
done <<< "$ALL_ACCOUNTS"

if [[ "$KEYCHAIN_FOUND" == "true" ]]; then
    echo -e "${GREEN}✓${NC} Found"
    echo "  → Service: $SERVICE"
    echo "  → Account: $VALID_ACCOUNT (label doesn't matter)"
    echo "  → Contains valid OAuth tokens"
else
    echo -e "${RED}✗${NC} Not found"
    echo "  → Service: $SERVICE"
    
    if [[ -n "$ALL_ACCOUNTS" ]]; then
        NUM_ENTRIES=$(echo "$ALL_ACCOUNTS" | wc -l | tr -d ' ')
        echo "  → Found $NUM_ENTRIES entry/entries, but none have complete OAuth data:"
        echo "$ALL_ACCOUNTS" | sed 's/^/      /'
        echo ""
        echo "  Run: claude auth (to refresh authentication)"
    else
        echo "  → No '$SERVICE' entries found in Keychain"
        echo "  → Run: claude auth (to create authentication)"
    fi
    
    echo ""
    echo "  Debug: List all Claude keychain entries:"
    echo "    security find-generic-password -s '$SERVICE' -g"
    ((ERRORS++))
fi

# Check 5: Clawdbot installed
echo -n "Checking Clawdbot... "
if command -v clawdbot &> /dev/null; then
    CLAWDBOT_VERSION=$(clawdbot --version 2>&1 | head -n1 || echo "unknown")
    echo -e "${GREEN}✓${NC} Found ($CLAWDBOT_VERSION)"
else
    echo -e "${RED}✗${NC} Not found"
    echo "  → Install from: https://clawdbot.com"
    ((ERRORS++))
fi

# Check 6: Clawdbot Gateway running
if command -v clawdbot &> /dev/null; then
    echo -n "Checking Clawdbot Gateway... "
    if clawdbot gateway status &> /dev/null; then
        echo -e "${GREEN}✓${NC} Running"
    else
        echo -e "${YELLOW}⚠${NC} Not running"
        echo "  → Start: clawdbot gateway start"
        ((WARNINGS++))
    fi
fi

# Check 7: Clawdbot config (for auto-detection)
echo -n "Checking Clawdbot config... "
CLAWDBOT_CONFIG="$HOME/.clawdbot/clawdbot.json"
if [[ -f "$CLAWDBOT_CONFIG" ]]; then
    echo -e "${GREEN}✓${NC} Found"
    
    # Try auto-detection
    SCRIPT_DIR="$(dirname "$0")"
    if [[ -x "$SCRIPT_DIR/detect-notification-config.sh" ]]; then
        if detection=$("$SCRIPT_DIR/detect-notification-config.sh" 2>/dev/null); then
            CHANNEL=$(echo "$detection" | cut -d'|' -f1)
            TARGET=$(echo "$detection" | cut -d'|' -f2)
            echo "  → Auto-detected: $CHANNEL → $TARGET"
        else
            echo -e "  ${YELLOW}⚠${NC} No enabled channels detected"
            ((WARNINGS++))
        fi
    fi
else
    echo -e "${YELLOW}⚠${NC} Not found"
    echo "  → Auto-detection unavailable (manual config needed)"
    ((WARNINGS++))
fi

# Check 8: Config file
echo -n "Checking config file... "
SCRIPT_DIR_CHECK="$(dirname "$0")"
NEW_CONFIG="$SCRIPT_DIR_CHECK/claude-oauth-refresh-config.json"
OLD_CONFIG="$SCRIPT_DIR_CHECK/config.json"

if [[ -f "$NEW_CONFIG" ]]; then
    CONFIG_FILE="$NEW_CONFIG"
    echo -e "${GREEN}✓${NC} Found (claude-oauth-refresh-config.json)"
    
    # Validate JSON
    if command -v jq &> /dev/null; then
        if jq empty "$CONFIG_FILE" 2>/dev/null; then
            # Check for placeholder values
            if grep -q "YOUR_CHAT_ID" "$CONFIG_FILE"; then
                echo -e "  ${YELLOW}⚠${NC} notification_target needs to be updated"
                echo "  → Run: ./install.sh (for auto-detection)"
                echo "  → Or edit manually: $CONFIG_FILE"
                ((WARNINGS++))
            fi
        else
            echo -e "  ${RED}✗${NC} Invalid JSON"
            ((ERRORS++))
        fi
    fi
elif [[ -f "$OLD_CONFIG" ]]; then
    CONFIG_FILE="$OLD_CONFIG"
    echo -e "${YELLOW}⚠${NC} Found old config.json"
    echo "  → Run ./install.sh to migrate to claude-oauth-refresh-config.json"
    ((WARNINGS++))
else
    echo -e "${YELLOW}⚠${NC} Not found"
    echo "  → Run: ./install.sh (will auto-detect if possible)"
    ((WARNINGS++))
fi

# Check 9: jq (recommended)
echo -n "Checking jq (recommended)... "
if command -v jq &> /dev/null; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${YELLOW}⚠${NC} Not found"
    echo "  → Install: brew install jq"
    echo "  → Required for JSON parsing"
    ((WARNINGS++))
fi

# Check 10: Log directory
echo -n "Checking log directory... "
LOG_DIR="$HOME/clawd/logs"
if [[ -d "$LOG_DIR" ]]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${YELLOW}⚠${NC} Not found"
    echo "  → Will be created on first run"
    ((WARNINGS++))
fi

# Check 11: Script permissions
echo -n "Checking script permissions... "
SCRIPT_DIR="$(dirname "$0")"
if [[ -x "$SCRIPT_DIR/refresh-token.sh" ]]; then
    echo -e "${GREEN}✓${NC} Executable"
else
    echo -e "${YELLOW}⚠${NC} Not executable"
    echo "  → Run: chmod +x $SCRIPT_DIR/*.sh"
    ((WARNINGS++))
fi

# Summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [[ $ERRORS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run: ./install.sh"
    echo "  2. Or test manually: ./refresh-token.sh"
elif [[ $ERRORS -eq 0 ]]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) - setup may work but review above${NC}"
    echo ""
    echo "You can proceed with installation:"
    echo "  → ./install.sh"
else
    echo -e "${RED}✗ $ERRORS error(s), $WARNINGS warning(s)${NC}"
    echo ""
    echo "Fix the errors above before proceeding."
    echo "See SKILL.md for detailed setup instructions."
    exit 1
fi
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
