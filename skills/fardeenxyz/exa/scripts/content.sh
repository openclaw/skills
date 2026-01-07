#!/bin/bash
# Get content from URLs

if [ $# -eq 0 ]; then
    echo "Usage: $0 url1 [url2 ...]" >&2
    exit 1
fi

if [ -z "${EXA_API_KEY:-}" ]; then
    echo "Error: EXA_API_KEY is not set." >&2
    echo "Please set EXA_API_KEY environment variable." >&2
    exit 1
fi

URLS=$(printf '%s\n' "$@" | jq -R . | jq -s .)

PAYLOAD=$(jq -n \
    --argjson ids "$URLS" \
    '{
        ids: $ids,
        text: true,
        highlights: true,
        summary: true
    }')

curl -s -X POST 'https://api.exa.ai/contents' \
    -H "x-api-key: $EXA_API_KEY" \
    -H 'Content-Type: application/json' \
    -d "$PAYLOAD"
