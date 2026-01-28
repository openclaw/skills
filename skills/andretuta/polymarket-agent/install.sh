#!/bin/bash
# Polymarket Agent - Installation Script
# Works with Ubuntu 24.04+ (PEP 668 compliant)

set -e

echo "🎰 Polymarket Agent - Installing..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Check for python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install with: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate venv and install
echo "📦 Installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip --quiet
pip install -r "$SCRIPT_DIR/requirements.txt" --quiet
pip install -e "$SCRIPT_DIR" --quiet

echo ""
echo "✅ Installation complete!"
echo ""
echo "To use the 'poly' command, activate the environment first:"
echo ""
echo "  source $VENV_DIR/bin/activate"
echo "  poly --help"
echo ""
echo "Or run directly:"
echo ""
echo "  $VENV_DIR/bin/poly --help"
echo ""
echo "💡 Tip: Add this to your ~/.bashrc for easy access:"
echo "  alias poly='$VENV_DIR/bin/poly'"
