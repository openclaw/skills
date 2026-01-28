#!/bin/bash
#
# Twitter Search Wrapper Script
# This script handles environment variable loading and provides a convenient interface
# for running the Twitter search analysis.
#

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print error and exit
error_exit() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

# Function to print warning
warn() {
    echo -e "${YELLOW}Warning: $1${NC}" >&2
}

# Check if TWITTER_API_KEY is set
if [[ -z "$TWITTER_API_KEY" ]]; then
    # Try to source .bashrc to get the API key
    if [[ -f "$HOME/.bashrc" ]]; then
        # Source .bashrc and extract TWITTER_API_KEY
        eval "$(grep -E '^export TWITTER_API_KEY=' "$HOME/.bashrc" 2>/dev/null || true)"
    fi

    # Still not set? Try .zshrc
    if [[ -z "$TWITTER_API_KEY" && -f "$HOME/.zshrc" ]]; then
        eval "$(grep -E '^export TWITTER_API_KEY=' "$HOME/.zshrc" 2>/dev/null || true)"
    fi

    # If still not set, show error
    if [[ -z "$TWITTER_API_KEY" ]]; then
        error_exit "TWITTER_API_KEY is not set. Please set it in your shell config or pass as --api-key argument.

Get your API key from: https://twitterapi.io

To set it permanently:
  echo 'export TWITTER_API_KEY=\"your_key_here\"' >> ~/.bashrc
  source ~/.bashrc"
    fi

    warn "TWITTER_API_KEY loaded from shell config file"
fi

# Check Python is available
if ! command -v python3 &> /dev/null; then
    error_exit "python3 is not installed. Please install Python 3."
fi

# Check if requests module is available
if ! python3 -c "import requests" 2>/dev/null; then
    warn "requests module not found. Attempting to install..."
    pip3 install requests --user
fi

# Default values
MAX_RESULTS=${MAX_RESULTS:-1000}
QUERY_TYPE=${QUERY_TYPE:-Top}
FORMAT=${FORMAT:-json}

# Parse command line arguments
QUERY=""
API_KEY=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --api-key)
            API_KEY="$2"
            shift 2
            ;;
        --max-results)
            MAX_RESULTS="$2"
            shift 2
            ;;
        --query-type)
            QUERY_TYPE="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        -*)
            error_exit "Unknown option: $1"
            ;;
        *)
            if [[ -z "$QUERY" ]]; then
                QUERY="$1"
            else
                error_exit "Too many arguments. Only one query is allowed."
            fi
            shift
            ;;
    esac
done

# Use provided API key or environment variable
if [[ -n "$API_KEY" ]]; then
    TWITTER_API_KEY="$API_KEY"
fi

# Validate query
if [[ -z "$QUERY" ]]; then
    error_exit "No query specified. Usage: $0 \"your search query\" [options]

Examples:
  $0 \"AI\"
  $0 \"from:elonmusk\"
  $0 \"Claude OR ChatGPT\" --max-results 100
  $0 \"Bitcoin\" --query-type Latest --format summary"
fi

# Display mask for API key (show only first 8 chars)
API_KEY_MASK="${TWITTER_API_KEY:0:8}..."

echo -e "${GREEN}Twitter Search Analysis${NC}" >&2
echo "Query: $QUERY" >&2
echo "Max Results: $MAX_RESULTS" >&2
echo "Query Type: $QUERY_TYPE" >&2
echo "API Key: $API_KEY_MASK" >&2
echo "---" >&2

# Run the Python script
python3 "$SCRIPT_DIR/twitter_search.py" "$TWITTER_API_KEY" "$QUERY" \
    --max-results "$MAX_RESULTS" \
    --query-type "$QUERY_TYPE" \
    --format "$FORMAT"
