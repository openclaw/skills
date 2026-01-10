#!/bin/bash
# Quick install script for Homey CLI skill

set -e

LINK=0
for arg in "$@"; do
  case "$arg" in
    --link)
      LINK=1
      ;;
    --no-link)
      LINK=0
      ;;
  esac
done

echo "🦞 Installing Homey CLI Skill..."
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
  echo "❌ Error: package.json not found. Run this from the homey skill directory."
  exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Make CLI executable
echo "🔧 Making CLI executable..."
chmod +x bin/homeycli.js

# Check for token
if [ -z "$HOMEY_TOKEN" ] && [ ! -f "$HOME/.homey/config.json" ]; then
  echo ""
  echo "⚠️  No Homey token found (HOMEY_TOKEN or ~/.homey/config.json)."
  echo ""
  echo "To get a token:"
  echo "  1. Visit: https://tools.developer.homey.app/api/clients"
  echo "  2. Create a Personal Access Token"
  echo ""
  echo "Then set it (recommended):"
  echo "  ./bin/homeycli.js auth set-token \"your-token-here\""
  echo ""
  echo "Or set env var:"
  echo "  export HOMEY_TOKEN=\"your-token-here\""
  echo ""
else
  echo "✅ Token found (env var or config file)"
fi

# Test CLI
echo ""
echo "🧪 Testing CLI..."
if ./bin/homeycli.js --help > /dev/null 2>&1; then
  echo "✅ CLI works!"
else
  echo "❌ CLI test failed"
  exit 1
fi

# Link globally (optional, non-interactive)
if [ "$LINK" -eq 1 ]; then
  echo ""
  echo "🔗 Linking globally with npm link..."
  npm link
  echo "✅ Installed globally as 'homeycli'"
else
  echo ""
  echo "Skipped global install. Use ./bin/homeycli.js to run, or pass --link."
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Set your token: ./bin/homeycli.js auth set-token \"...\""
echo "  2. Test: ./bin/homeycli.js status"
echo "  3. List devices: ./bin/homeycli.js devices --json"
echo ""
