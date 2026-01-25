#!/bin/bash

# Test Auto-Routing Feature
# Tests various query types to verify routing works correctly

# Load keys from .env file
if [ -f .env ]; then
  source .env
else
  echo "⚠️  No .env file found. Please create one with your API keys."
  echo "   See .env.example for the required format."
  exit 1
fi

# Verify keys are set
if [ -z "$SERPER_API_KEY" ] && [ -z "$TAVILY_API_KEY" ] && [ -z "$EXA_API_KEY" ]; then
  echo "❌ No API keys found. Please set at least one in .env"
  exit 1
fi

echo "🧪 Testing Web Search Plus v2.0.0 - Smart Auto-Routing"
echo "======================================================"
echo

# Test 1: Shopping query
echo "📦 Test 1: Shopping Query"
echo "Query: 'iPhone 16 price best deal'"
python3 scripts/search.py -q "iPhone 16 price best deal" --explain-routing 2>/dev/null | jq -r '.selected_provider // "ERROR"'
echo

# Test 2: Research query
echo "🔬 Test 2: Research Query"
echo "Query: 'how does machine learning work'"
python3 scripts/search.py -q "how does machine learning work" --explain-routing 2>/dev/null | jq -r '.selected_provider // "ERROR"'
echo

# Test 3: Discovery query
echo "🔍 Test 3: Discovery Query"
echo "Query: 'companies similar to Notion'"
python3 scripts/search.py -q "companies similar to Notion" --explain-routing 2>/dev/null | jq -r '.selected_provider // "ERROR"'
echo

# Test 4: Local query
echo "📍 Test 4: Local Query"
echo "Query: 'pizza restaurant near me'"
python3 scripts/search.py -q "pizza restaurant near me" --explain-routing 2>/dev/null | jq -r '.selected_provider // "ERROR"'
echo

# Test 5: Tutorial query
echo "📚 Test 5: Tutorial Query"
echo "Query: 'learn python programming guide'"
python3 scripts/search.py -q "learn python programming guide" --explain-routing 2>/dev/null | jq -r '.selected_provider // "ERROR"'
echo

# Test 6: Startup discovery
echo "🚀 Test 6: Startup Discovery"
echo "Query: 'YC AI startups Series A'"
python3 scripts/search.py -q "YC AI startups Series A" --explain-routing 2>/dev/null | jq -r '.selected_provider // "ERROR"'
echo

# Test 7: Fallback test
echo "⚙️ Test 7: Fallback (Ambiguous)"
echo "Query: 'latest technology trends'"
python3 scripts/search.py -q "latest technology trends" --explain-routing 2>/dev/null | jq -r '.selected_provider // "ERROR"'
echo

echo "✅ All tests completed!"
echo
echo "Expected Results:"
echo "  Test 1: serper (shopping keywords)"
echo "  Test 2: tavily (research keyword)"
echo "  Test 3: exa (similarity keyword)"
echo "  Test 4: serper (local keyword)"
echo "  Test 5: tavily (learning keyword)"
echo "  Test 6: exa (startup keywords)"
echo "  Test 7: serper (fallback)"
