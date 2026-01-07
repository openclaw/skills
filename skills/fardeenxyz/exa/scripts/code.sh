#!/bin/bash
# Exa code context search

QUERY="$1"
NUM_RESULTS="${2:-10}"

if [ -z "$QUERY" ]; then
    echo "Usage: $0 \"query\" [num_results]" >&2
    exit 1
fi

if [ -z "${EXA_API_KEY:-}" ]; then
    echo "Error: EXA_API_KEY is not set." >&2
    echo "Please set EXA_API_KEY environment variable." >&2
    exit 1
fi

# Optimized settings for code/docs
# No domain restrictions - let Exa's neural search find the best docs/repos
PAYLOAD=$(jq -n \
    --arg query "$QUERY" \
    --argjson numResults "$NUM_RESULTS" \
    '{
        query: $query,
        type: "auto",
        numResults: $numResults,
        text: true,
        highlights: true
    }')

curl -s -X POST 'https://api.exa.ai/search' \
    -H "x-api-key: $EXA_API_KEY" \
    -H 'Content-Type: application/json' \
    -d "$PAYLOAD"
