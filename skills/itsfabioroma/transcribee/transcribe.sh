#!/usr/bin/env bash

# Transcribe YouTube videos with intelligent organization
# Usage: transcribe "https://www.youtube.com/watch?v=..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# If no arguments provided, show usage
if [ $# -eq 0 ]; then
    echo "Usage: transcribe \"<youtube-url>\""
    echo ""
    echo "Examples:"
    echo "  transcribe \"https://www.youtube.com/watch?v=MW3t6jP9AOs\""
    echo "  transcribe \"https://www.youtube.com/watch?v=MW3t6jP9AOs&t=107s\""
    echo ""
    echo "Note: Use quotes if the URL contains & or other special characters"
    exit 1
fi

# Check if URL looks like a YouTube URL
if [[ ! "$1" =~ youtube\.com|youtu\.be ]]; then
    echo "⚠️  Warning: This doesn't look like a YouTube URL"
    echo "   Got: $1"
    echo ""
fi

# Pass the first argument (URL) to the script
pnpm exec tsx index.ts "$1"
