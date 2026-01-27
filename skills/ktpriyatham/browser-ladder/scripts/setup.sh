#!/bin/bash
# Browser Ladder Setup Script
# Prompts for optional API keys and adds them to .env

set -e

ENV_FILE="${CLAWDBOT_WORKSPACE:-.}/.env"

echo "🪜 Browser Ladder Setup"
echo "========================"
echo ""
echo "This skill works without any API keys (Rungs 1-2)."
echo "Add keys below to enable cloud browsers (Rungs 3-4)."
echo ""

# Rung 3: BrowserCat (free)
echo "--- Rung 3: BrowserCat (FREE) ---"
echo "Get a free API key at: https://browsercat.com"
read -p "BrowserCat API Key (or press Enter to skip): " BROWSERCAT_KEY

if [ -n "$BROWSERCAT_KEY" ]; then
  # Remove existing key if present
  grep -v "^BROWSERCAT_API_KEY=" "$ENV_FILE" > "$ENV_FILE.tmp" 2>/dev/null || true
  mv "$ENV_FILE.tmp" "$ENV_FILE" 2>/dev/null || true
  echo "BROWSERCAT_API_KEY=$BROWSERCAT_KEY" >> "$ENV_FILE"
  echo "✅ BrowserCat key saved"
else
  echo "⏭️  Skipped (Rung 3 disabled)"
fi

echo ""

# Rung 4: Browserless.io (paid)
echo "--- Rung 4: Browserless.io (\$10+/mo) ---"
echo "Get a token at: https://browserless.io"
echo "Enables: CAPTCHA solving, bot detection bypass"
read -p "Browserless Token (or press Enter to skip): " BROWSERLESS_KEY

if [ -n "$BROWSERLESS_KEY" ]; then
  grep -v "^BROWSERLESS_TOKEN=" "$ENV_FILE" > "$ENV_FILE.tmp" 2>/dev/null || true
  mv "$ENV_FILE.tmp" "$ENV_FILE" 2>/dev/null || true
  echo "BROWSERLESS_TOKEN=$BROWSERLESS_KEY" >> "$ENV_FILE"
  echo "✅ Browserless token saved"
else
  echo "⏭️  Skipped (Rung 4 disabled)"
fi

echo ""
echo "🪜 Setup complete!"
echo ""
echo "Available rungs:"
echo "  ✅ Rung 1: web_fetch (always available)"
echo "  ✅ Rung 2: Playwright Docker (requires: docker)"
[ -n "$BROWSERCAT_KEY" ] && echo "  ✅ Rung 3: BrowserCat" || echo "  ⬜ Rung 3: BrowserCat (no key)"
[ -n "$BROWSERLESS_KEY" ] && echo "  ✅ Rung 4: Browserless.io" || echo "  ⬜ Rung 4: Browserless.io (no key)"
