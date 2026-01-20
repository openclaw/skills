#!/bin/bash
# Verification script - Check if skill package is complete and ready

echo "🔍 Smart Follow-ups Skill Verification"
echo "======================================="
echo ""

ERRORS=0
WARNINGS=0

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to check file existence
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1 (MISSING)"
        ((ERRORS++))
    fi
}

# Function to check directory
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
    else
        echo -e "${RED}✗${NC} $1/ (MISSING)"
        ((ERRORS++))
    fi
}

# Function to check executable
check_exec() {
    if [ -x "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 (executable)"
    else
        echo -e "${YELLOW}⚠${NC} $1 (not executable)"
        ((WARNINGS++))
    fi
}

echo "📁 File Structure"
echo "-----------------"
check_dir "cli"
check_file "cli/followups-cli.js"
check_file "handler.js"
check_file "package.json"
check_file "README.md"
check_file "SKILL.md"
check_file "examples.md"
check_file "INTERNAL.md"
check_file "QUICKSTART.md"
check_file "CHANGELOG.md"
check_file "CONTRIBUTING.md"
check_file "LICENSE"
check_file ".gitignore"
check_file "test.sh"
check_file "test-example.json"
check_file "PROJECT_INDEX.md"
echo ""

echo "🔒 Permissions"
echo "--------------"
check_exec "cli/followups-cli.js"
check_exec "test.sh"
echo ""

echo "📦 Dependencies"
echo "---------------"
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✓${NC} node_modules/ exists"
    
    if [ -d "node_modules/@anthropic-ai" ]; then
        echo -e "${GREEN}✓${NC} @anthropic-ai/sdk installed"
    else
        echo -e "${RED}✗${NC} @anthropic-ai/sdk NOT installed"
        echo "  Run: npm install"
        ((ERRORS++))
    fi
else
    echo -e "${RED}✗${NC} node_modules/ missing"
    echo "  Run: npm install"
    ((ERRORS++))
fi
echo ""

echo "🔑 Environment"
echo "--------------"
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}⚠${NC} ANTHROPIC_API_KEY not set"
    echo "  This is required to run the skill"
    echo "  Set with: export ANTHROPIC_API_KEY='sk-ant-...'"
    ((WARNINGS++))
else
    echo -e "${GREEN}✓${NC} ANTHROPIC_API_KEY is set"
fi
echo ""

echo "📊 Documentation"
echo "----------------"
# Check README has key sections
if grep -q "## Features" README.md && grep -q "## Quick Start" README.md; then
    echo -e "${GREEN}✓${NC} README.md has key sections"
else
    echo -e "${YELLOW}⚠${NC} README.md may be incomplete"
    ((WARNINGS++))
fi

# Check package.json has required fields
if grep -q '"name"' package.json && grep -q '"version"' package.json; then
    echo -e "${GREEN}✓${NC} package.json has name and version"
else
    echo -e "${RED}✗${NC} package.json is malformed"
    ((ERRORS++))
fi

echo -e "${GREEN}✓${NC} All documentation files present"
echo ""

echo "🧪 Basic Syntax Check"
echo "---------------------"
if node -c cli/followups-cli.js 2>/dev/null; then
    echo -e "${GREEN}✓${NC} cli/followups-cli.js syntax OK"
else
    echo -e "${RED}✗${NC} cli/followups-cli.js has syntax errors"
    ((ERRORS++))
fi

if node -c handler.js 2>/dev/null; then
    echo -e "${GREEN}✓${NC} handler.js syntax OK"
else
    echo -e "${RED}✗${NC} handler.js has syntax errors"
    ((ERRORS++))
fi
echo ""

echo "📈 Statistics"
echo "-------------"
TOTAL_FILES=$(find . -type f -not -path './node_modules/*' | wc -l)
JS_FILES=$(find . -name '*.js' -not -path './node_modules/*' | wc -l)
MD_FILES=$(find . -name '*.md' | wc -l)
TOTAL_LINES=$(find . -name '*.js' -not -path './node_modules/*' -exec wc -l {} + | tail -1 | awk '{print $1}')

echo "  Total files: $TOTAL_FILES"
echo "  JavaScript files: $JS_FILES"
echo "  Documentation files: $MD_FILES"
echo "  Lines of code: $TOTAL_LINES"
echo ""

echo "======================================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo "   The skill package is ready for testing."
    echo ""
    echo "Next steps:"
    echo "  1. Test CLI: ./test.sh"
    echo "  2. Integrate with Clawdbot (see SKILL.md)"
    echo "  3. Test on Telegram"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Passed with $WARNINGS warning(s)${NC}"
    echo "   Review warnings above."
    exit 0
else
    echo -e "${RED}❌ Failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo "   Fix errors above before proceeding."
    exit 1
fi
