#!/bin/bash
# Vinculum installer
set -e
echo "Installing Vinculum dependencies..."
npm install --production
echo "✅ Vinculum installed successfully!"
echo ""
echo "Quick start:"
echo "  /link relay start  - Start the Vinculum relay"
echo "  /link init         - Create a new collective"
echo "  /link help         - Show all commands"
