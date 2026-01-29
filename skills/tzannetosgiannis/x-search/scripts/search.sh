#!/bin/bash
# X/Twitter search via x402 protocol
# Usage: search.sh "<query>"

set -e

QUERY="$*"

# Check if query is provided
if [ -z "$QUERY" ]; then
    echo "Error: No search query provided"
    echo "Usage: search.sh \"<query>\""
    exit 1
fi

# Try to find config file in multiple locations
CONFIG_LOCATIONS=(
    "./x402-config.json"
    "$HOME/.x402-config.json"
    "$PWD/x402-config.json"
)

# Check each location for config file
for CONFIG_FILE in "${CONFIG_LOCATIONS[@]}"; do
    if [ -f "$CONFIG_FILE" ]; then
        PRIVATE_KEY=$(jq -r '.private_key' "$CONFIG_FILE" 2>/dev/null || echo "")
        if [ -n "$PRIVATE_KEY" ]; then
            export X402_PRIVATE_KEY="$PRIVATE_KEY"
            break
        fi
    fi
done

# Check if private key is available
if [ -z "$X402_PRIVATE_KEY" ]; then
    echo "Error: X402 private key missing"
    echo ""
    echo "Please configure your private key using one of these methods:"
    echo "1. Set environment variable: export X402_PRIVATE_KEY=\"0x...\""
    echo "2. Create x402-config.json in current directory with:"
    echo '   {"private_key": "0x..."}'
    echo "3. Create ~/.x402-config.json in your home directory"
    exit 1
fi

# Execute the search
npx -y @itzannetos/x402-tools-claude x-search "$QUERY"
