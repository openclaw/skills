#!/bin/bash
# Quick test script for Smart Follow-ups CLI

echo "🧪 Smart Follow-ups CLI Test"
echo "=============================="
echo ""

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY not set"
    echo ""
    echo "Set it with:"
    echo "  export ANTHROPIC_API_KEY='your-key-here'"
    echo ""
    exit 1
fi

echo "✅ API key detected"
echo ""

# Test 1: Help command
echo "Test 1: Help command"
echo "---------------------"
node cli/followups-cli.js --help
echo ""

# Test 2: JSON output mode (with test data)
echo "Test 2: JSON output mode"
echo "------------------------"
cat test-example.json | node cli/followups-cli.js --mode json
echo ""

# Test 3: Text output mode
echo "Test 3: Text output mode"
echo "------------------------"
cat test-example.json | node cli/followups-cli.js --mode text
echo ""

# Test 4: Compact output mode
echo "Test 4: Compact output mode"
echo "---------------------------"
cat test-example.json | node cli/followups-cli.js --mode compact
echo ""

# Test 5: Telegram button format
echo "Test 5: Telegram button format"
echo "-------------------------------"
cat test-example.json | node cli/followups-cli.js --mode telegram
echo ""

echo "✅ All tests completed!"
