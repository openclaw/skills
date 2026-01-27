#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"

mkdir -p "$BIN_DIR"
mkdir -p "$HOME/.config/findmy-location"

# Link the script
ln -sf "$SCRIPT_DIR/findmy-location.py" "$BIN_DIR/findmy-location"

# Create default config if not exists
if [ ! -f "$HOME/.config/findmy-location/config.json" ]; then
    cat > "$HOME/.config/findmy-location/config.json" << 'CONFIG'
{
  "target": null,
  "known_locations": []
}
CONFIG
    echo "Created default config at ~/.config/findmy-location/config.json"
    echo "Edit it to add your target contact and known locations."
fi

echo "Installed findmy-location to $BIN_DIR"
echo "Make sure $BIN_DIR is in your PATH"
