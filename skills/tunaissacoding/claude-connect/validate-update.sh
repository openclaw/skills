#!/bin/bash
# validate-update.sh - Verify production update was successful

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Validating Production Update${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0

# Check 1: New config example exists
echo -n "Checking new config example... "
if [[ -f "$SCRIPT_DIR/claude-oauth-refresh-config.example.json" ]]; then
    if jq -e '.notifications | type == "object"' "$SCRIPT_DIR/claude-oauth-refresh-config.example.json" &> /dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} Missing notification structure"
        ((CHECKS_FAILED++))
    fi
else
    echo -e "${RED}✗${NC} File not found"
    ((CHECKS_FAILED++))
fi

# Check 2: Old config example removed
echo -n "Checking old config removed... "
if [[ ! -f "$SCRIPT_DIR/config.example.json" ]]; then
    echo -e "${GREEN}✓${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Old file still exists"
    # Not a failure, just a warning
fi

# Check 3: refresh-token.sh uses new config
echo -n "Checking refresh-token.sh config... "
if grep -q "claude-oauth-refresh-config.json" "$SCRIPT_DIR/refresh-token.sh"; then
    echo -e "${GREEN}✓${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC} Still uses old config filename"
    ((CHECKS_FAILED++))
fi

# Check 4: refresh-token.sh has notification types
echo -n "Checking notification types... "
if grep -q "notifications.on_success" "$SCRIPT_DIR/refresh-token.sh" && \
   grep -q "notifications.on_failure" "$SCRIPT_DIR/refresh-token.sh"; then
    echo -e "${GREEN}✓${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC} Missing notification type support"
    ((CHECKS_FAILED++))
fi

# Check 5: refresh-token.sh has error handling
echo -n "Checking error handling... "
if grep -q "error_exit" "$SCRIPT_DIR/refresh-token.sh"; then
    echo -e "${GREEN}✓${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC} Missing error handling"
    ((CHECKS_FAILED++))
fi

# Check 6: install.sh has interactive prompts
echo -n "Checking interactive prompts... "
if grep -q "Token refreshed" "$SCRIPT_DIR/install.sh" && grep -q "NOTIFY_SUCCESS_INPUT" "$SCRIPT_DIR/install.sh"; then
    echo -e "${GREEN}✓${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC} Missing interactive notification config"
    ((CHECKS_FAILED++))
fi

# Check 7: install.sh has migration logic
echo -n "Checking migration logic... "
if grep -q "Migrating config.json" "$SCRIPT_DIR/install.sh"; then
    echo -e "${GREEN}✓${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC} Missing migration logic"
    ((CHECKS_FAILED++))
fi

# Check 8: SKILL.md exists
echo -n "Checking SKILL.md... "
if [[ -f "$SCRIPT_DIR/SKILL.md" ]]; then
    echo -e "${GREEN}✓${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC} SKILL.md not found"
    ((CHECKS_FAILED++))
fi

# Check 9: README.md exists
echo -n "Checking README.md... "
if [[ -f "$SCRIPT_DIR/README.md" ]]; then
    echo -e "${GREEN}✓${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC} README.md not found"
    ((CHECKS_FAILED++))
fi

# Check 10: UPGRADE.md exists
echo -n "Checking upgrade guide... "
if [[ -f "$SCRIPT_DIR/UPGRADE.md" ]]; then
    echo -e "${GREEN}✓${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} UPGRADE.md not found"
    # Not critical
fi

# Check 11: verify-setup.sh checks both configs
echo -n "Checking verify-setup.sh... "
if grep -q "claude-oauth-refresh-config.json" "$SCRIPT_DIR/verify-setup.sh" && \
   grep -q "config.json" "$SCRIPT_DIR/verify-setup.sh"; then
    echo -e "${GREEN}✓${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC} Doesn't check both config filenames"
    ((CHECKS_FAILED++))
fi

# Check 12: All scripts executable
echo -n "Checking script permissions... "
ALL_EXECUTABLE=true
for script in install.sh refresh-token.sh verify-setup.sh uninstall.sh detect-notification-config.sh test-detection.sh; do
    if [[ ! -x "$SCRIPT_DIR/$script" ]]; then
        ALL_EXECUTABLE=false
        break
    fi
done
if $ALL_EXECUTABLE; then
    echo -e "${GREEN}✓${NC}"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC} Some scripts not executable"
    ((CHECKS_FAILED++))
fi

# Summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [[ $CHECKS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}✓ All validation checks passed! ($CHECKS_PASSED/${CHECKS_PASSED})${NC}"
    echo ""
    echo -e "${GREEN}Production update is complete and ready to use.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review CHANGES.md for complete change summary"
    echo "  2. Review UPGRADE.md for migration guide"
    echo "  3. Run ./install.sh to install or migrate"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Validation failed: $CHECKS_FAILED check(s) failed${NC}"
    echo -e "${GREEN}  Passed: $CHECKS_PASSED${NC}"
    echo -e "${RED}  Failed: $CHECKS_FAILED${NC}"
    echo ""
    echo "Please review the failed checks above."
    exit 1
fi
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
