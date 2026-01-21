#!/bin/bash
# Generate a WhatsApp-style video
# Usage: ./generate.sh [output-name]

OUTPUT_NAME=${1:-"whatsapp-video"}
PROJECT_DIR="$HOME/Projects/remotion-test"

cd "$PROJECT_DIR" || exit 1

echo "🎬 Rendering WhatsApp video..."
npx remotion render WhatsAppDemo "out/${OUTPUT_NAME}.mp4" --concurrency=4

if [ $? -eq 0 ]; then
    echo "✅ Video saved to: $PROJECT_DIR/out/${OUTPUT_NAME}.mp4"
    open "$PROJECT_DIR/out/${OUTPUT_NAME}.mp4"
else
    echo "❌ Render failed"
    exit 1
fi
