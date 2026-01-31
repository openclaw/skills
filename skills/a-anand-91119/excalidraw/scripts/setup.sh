#!/bin/bash
# Setup script for Excalidraw renderer
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FONT_DIR="$SCRIPT_DIR/fonts"

echo "=== Excalidraw Renderer Setup ==="

# 1. Install npm dependencies
echo "→ Installing npm packages..."
cd "$SCRIPT_DIR"
npm install

# 2. Create fonts directory
mkdir -p "$FONT_DIR"

# 3. Download Virgil font (Excalidraw's handwritten font)
if [ ! -f "$FONT_DIR/Virgil.ttf" ]; then
  echo "→ Downloading Virgil font..."
  curl -sL "https://cdn.jsdelivr.net/npm/@excalidraw/excalidraw@0.17.6/dist/excalidraw-assets/Virgil.woff2" \
    -o "$FONT_DIR/Virgil.woff2"
  # Convert woff2 → ttf using fonttools (needed for resvg)
  if command -v python3 &>/dev/null && python3 -c "import fontTools" 2>/dev/null; then
    python3 -c "
from fontTools.ttLib import TTFont
font = TTFont('$FONT_DIR/Virgil.woff2')
font.flavor = None
font.save('$FONT_DIR/Virgil.ttf')
print('  Converted Virgil.woff2 → Virgil.ttf')
"
  else
    echo "  ⚠ fonttools not available. Install with: pip3 install --user fonttools brotli"
    echo "  Then run: python3 -c \"from fontTools.ttLib import TTFont; f=TTFont('$FONT_DIR/Virgil.woff2'); f.flavor=None; f.save('$FONT_DIR/Virgil.ttf')\""
  fi
fi

# 4. Download Cascadia Code (for code font)
if [ ! -f "$FONT_DIR/CascadiaCode.ttf" ]; then
  echo "→ Downloading Cascadia Code font..."
  CASCADIA_VERSION="2404.23"
  curl -sL "https://github.com/microsoft/cascadia-code/releases/download/v${CASCADIA_VERSION}/CascadiaCode-${CASCADIA_VERSION}.zip" \
    -o /tmp/cascadia.zip
  cd /tmp
  unzip -qo cascadia.zip -d cascadia_extract 2>/dev/null || true
  find cascadia_extract -name "CascadiaCode*.woff2" -not -path "*/static/*" | head -1 | xargs -I{} cp {} "$FONT_DIR/CascadiaCode.woff2" 2>/dev/null || true
  find cascadia_extract -name "CascadiaCode-Regular.ttf" | head -1 | xargs -I{} cp {} "$FONT_DIR/CascadiaCode.ttf" 2>/dev/null || true
  rm -rf cascadia.zip cascadia_extract
  cd "$SCRIPT_DIR"
fi

# 5. Make render.js executable
chmod +x "$SCRIPT_DIR/render.js"

echo "=== Setup complete ==="
echo "Usage: node $SCRIPT_DIR/render.js input.excalidraw [output.png]"
