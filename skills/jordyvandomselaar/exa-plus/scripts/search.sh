#!/bin/bash
# Exa neural web search with full options

QUERY="$1"

if [ -z "$QUERY" ]; then
    echo "Usage: bash search.sh \"query\"" >&2
    echo "" >&2
    echo "Options (env vars):" >&2
    echo "  NUM=10          Number of results" >&2
    echo "  TYPE=auto       Search type: auto, neural, fast, deep" >&2
    echo "  CATEGORY=       Category: news, company, people, research paper, github, tweet, pdf" >&2
    echo "  DOMAINS=        Include domains (comma-separated)" >&2
    echo "  EXCLUDE=        Exclude domains (comma-separated)" >&2
    echo "  SINCE=          Published after (YYYY-MM-DD)" >&2
    echo "  UNTIL=          Published before (YYYY-MM-DD)" >&2
    echo "  LOCATION=       User location (country code)" >&2
    exit 1
fi

# Load API key from credentials
CONFIG_FILE="$HOME/.clawdbot/credentials/exa/config.json"
if [ -f "$CONFIG_FILE" ]; then
    EXA_API_KEY=$(jq -r '.apiKey' "$CONFIG_FILE")
fi

if [ -z "${EXA_API_KEY:-}" ]; then
    echo "Error: EXA_API_KEY not found. Create $CONFIG_FILE with {\"apiKey\": \"...\"}" >&2
    exit 1
fi

# Defaults
NUM="${NUM:-10}"
TYPE="${TYPE:-auto}"
LOCATION="${LOCATION:-NL}"

# Build base payload
PAYLOAD=$(jq -n \
    --arg query "$QUERY" \
    --arg type "$TYPE" \
    --argjson numResults "$NUM" \
    --arg location "$LOCATION" \
    '{
        query: $query,
        type: $type,
        numResults: $numResults,
        userLocation: $location,
        contents: {
            text: { maxCharacters: 500 },
            highlights: { numSentences: 2, highlightsPerUrl: 1 },
            summary: {}
        }
    }')

# Add category if set
if [ -n "${CATEGORY:-}" ]; then
    PAYLOAD=$(echo "$PAYLOAD" | jq --arg cat "$CATEGORY" '. + {category: $cat}')
fi

# Add includeDomains if set
if [ -n "${DOMAINS:-}" ]; then
    PAYLOAD=$(echo "$PAYLOAD" | jq --arg domains "$DOMAINS" '. + {includeDomains: ($domains | split(","))}')
fi

# Add excludeDomains if set
if [ -n "${EXCLUDE:-}" ]; then
    PAYLOAD=$(echo "$PAYLOAD" | jq --arg domains "$EXCLUDE" '. + {excludeDomains: ($domains | split(","))}')
fi

# Add date filters if set
if [ -n "${SINCE:-}" ]; then
    PAYLOAD=$(echo "$PAYLOAD" | jq --arg date "${SINCE}T00:00:00.000Z" '. + {startPublishedDate: $date}')
fi

if [ -n "${UNTIL:-}" ]; then
    PAYLOAD=$(echo "$PAYLOAD" | jq --arg date "${UNTIL}T23:59:59.999Z" '. + {endPublishedDate: $date}')
fi

# Call API
curl -s -X POST 'https://api.exa.ai/search' \
    -H "x-api-key: $EXA_API_KEY" \
    -H 'Content-Type: application/json' \
    -d "$PAYLOAD"
