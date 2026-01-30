#!/bin/bash
# Setup script for voice-note-to-midi skill
# This automates the installation of the melody-to-MIDI pipeline

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${INSTALL_DIR:-$HOME/melody-pipeline}"
VENV_DIR="$INSTALL_DIR/venv-bp"

echo "=================================="
echo "Voice Note to MIDI - Setup Script"
echo "=================================="
echo ""
echo "This will install the melody-to-MIDI pipeline to:"
echo "  $INSTALL_DIR"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo "❌ Error: Python 3.11+ is required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✓ Python version: $PYTHON_VERSION"

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is required but not installed."
    exit 1
fi

echo "✓ pip3 available"

# Check for FFmpeg (optional but recommended)
if command -v ffmpeg &> /dev/null; then
    echo "✓ FFmpeg available (for extended audio format support)"
else
    echo "⚠ FFmpeg not found. Install for broader audio format support."
fi

echo ""
echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Create virtual environment
echo "Creating Python virtual environment..."
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists. Update? [y/N]"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        rm -rf "$VENV_DIR"
        python3 -m venv "$VENV_DIR"
    fi
else
    python3 -m venv "$VENV_DIR"
fi

echo "✓ Virtual environment ready"

# Install dependencies
echo ""
echo "Installing dependencies (this may take a few minutes)..."
source "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install basic-pitch librosa soundfile mido

# Install optional music21 for advanced key detection
echo ""
echo "Install music21 for enhanced key detection? [Y/n]"
read -r response
if [[ ! "$response" =~ ^([nN][oO]|[nN])$ ]]; then
    pip install music21
    echo "✓ music21 installed"
fi

echo "✓ Core dependencies installed"

# Download or create hum2midi script
echo ""
echo "Setting up hum2midi script..."

if [ -f "$SCRIPT_DIR/hum2midi" ]; then
    cp "$SCRIPT_DIR/hum2midi" "$INSTALL_DIR/hum2midi"
    chmod +x "$INSTALL_DIR/hum2midi"
    echo "✓ hum2midi script copied from skill directory"
elif [ -f "$INSTALL_DIR/hum2midi" ]; then
    echo "✓ hum2midi script already exists"
else
    echo "⚠ Please download the hum2midi script manually:"
    echo "  wget https://raw.githubusercontent.com/basic-pitch/basic-pitch/main/hum2midi -O $INSTALL_DIR/hum2midi"
    echo "  chmod +x $INSTALL_DIR/hum2midi"
fi

# Create .stems directory for temporary files
mkdir -p "$INSTALL_DIR/.stems"

# Optionally add to PATH
echo ""
echo "Add $INSTALL_DIR to your PATH? [y/N]"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    SHELL_RC="$HOME/.bashrc"
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    fi
    
    if ! grep -q "$INSTALL_DIR" "$SHELL_RC"; then
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_RC"
        echo "✓ Added to $SHELL_RC"
        echo "  Run 'source $SHELL_RC' to apply changes"
    else
        echo "✓ Already in PATH"
    fi
fi

echo ""
echo "=================================="
echo "Installation complete!"
echo "=================================="
echo ""
echo "Test your installation:"
echo "  cd $INSTALL_DIR"
echo "  ./hum2midi --help"
echo ""
echo "Quick start:"
echo "  ./hum2midi your_voice_memo.wav"
echo ""
