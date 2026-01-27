#!/bin/bash
# Polymarket Agent - Post-Install Script
# This script is automatically executed after `clawdhub install polymarket-agent`

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

echo "🎰 Polymarket Agent - Installing Dependencies..."

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip not found. Please install Python and pip first."
    exit 1
fi

# Check if uv is available (faster), fallback to pip
if command -v uv &> /dev/null; then
    echo "✨ Using uv for fast installation..."
    uv pip install -r "$REQUIREMENTS_FILE"
else
    echo "📦 Using pip..."
    pip install -r "$REQUIREMENTS_FILE" --quiet
fi

echo "✅ Dependencies installed successfully!"
echo ""
echo "📦 Installing 'poly' command globally..."
pip install -e "$SCRIPT_DIR" --quiet
echo "✅ 'poly' command is now available!"
echo ""
echo "🔧 Next step: Run the setup wizard to configure your API keys:"
echo "   poly setup"
