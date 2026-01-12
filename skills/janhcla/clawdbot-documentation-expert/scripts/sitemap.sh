#!/bin/bash
# Fetch and display Clawdbot documentation sitemap organized by category

SITEMAP_URL="https://docs.clawd.bot/sitemap.xml"

echo "📚 Clawdbot Documentation Structure"
echo "===================================="
echo ""

# Fetch sitemap and extract URLs (macOS compatible)
URLS=$(curl -s "$SITEMAP_URL" | sed -n 's/.*<loc>\([^<]*\)<\/loc>.*/\1/p' | sort)

# Function to print category
print_category() {
    local category="$1"
    local emoji="$2"
    local pattern="$3"
    
    local matches=$(echo "$URLS" | grep -E "$pattern" | sed 's|https://docs.clawd.bot/||')
    if [ -n "$matches" ]; then
        echo "$emoji $category"
        echo "$matches" | sed 's/^/  - /'
        echo ""
    fi
}

# Print each category
print_category "Getting Started" "🚀" "/start/"
print_category "Gateway & Operations" "🔧" "/gateway/"
print_category "Providers" "💬" "/providers/"
print_category "Core Concepts" "🧠" "/concepts/"
print_category "Tools" "🛠️" "/tools/"
print_category "Automation" "⚡" "/automation/"
print_category "CLI" "💻" "/cli/"
print_category "Platforms" "📱" "/platforms/"
print_category "Nodes" "📡" "/nodes/"
print_category "Web" "🌐" "/web/"
print_category "Install" "📦" "/install/"
print_category "Reference" "📚" "/reference/"
print_category "Experiments" "🧪" "/experiments/"

# Count total docs
TOTAL=$(echo "$URLS" | wc -l | tr -d ' ')
echo "📊 Total documentation pages: $TOTAL"
