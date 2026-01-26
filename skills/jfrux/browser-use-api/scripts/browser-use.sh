#!/bin/bash
# Browser Use API helper
# Usage: browser-use.sh [--no-wait] "task description"

set -euo pipefail

API_URL="https://api.browser-use.com/api/v2"
POLL_INTERVAL=5
MAX_WAIT=300

if [[ -z "${BROWSER_USE_API_KEY:-}" ]]; then
  echo "Error: BROWSER_USE_API_KEY not set" >&2
  exit 1
fi

NO_WAIT=false
if [[ "${1:-}" == "--no-wait" ]]; then
  NO_WAIT=true
  shift
fi

TASK="${1:-}"
if [[ -z "$TASK" ]]; then
  echo "Usage: browser-use.sh [--no-wait] \"task description\"" >&2
  exit 1
fi

# Submit task
RESPONSE=$(curl -s -X POST "$API_URL/tasks" \
  -H "X-Browser-Use-API-Key: $BROWSER_USE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"task\": $(echo "$TASK" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}")

TASK_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")

if [[ -z "$TASK_ID" ]]; then
  echo "Error submitting task: $RESPONSE" >&2
  exit 1
fi

echo "Task ID: $TASK_ID" >&2

if $NO_WAIT; then
  echo "$TASK_ID"
  exit 0
fi

# Poll for completion
ELAPSED=0
while [[ $ELAPSED -lt $MAX_WAIT ]]; do
  RESULT=$(curl -s "$API_URL/tasks/$TASK_ID" \
    -H "X-Browser-Use-API-Key: $BROWSER_USE_API_KEY")
  
  STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null || echo "")
  
  case "$STATUS" in
    finished)
      echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Status: SUCCESS' if data.get('isSuccess') else 'Status: FAILED')
print(f\"Cost: \${data.get('cost', '?')}\")
print('---')
print(data.get('output', 'No output'))
"
      exit 0
      ;;
    failed)
      echo "Task failed" >&2
      echo "$RESULT"
      exit 1
      ;;
    created|pending|started)
      echo "Status: $STATUS (${ELAPSED}s)" >&2
      sleep $POLL_INTERVAL
      ELAPSED=$((ELAPSED + POLL_INTERVAL))
      ;;
    *)
      echo "Unknown status: $STATUS" >&2
      echo "$RESULT"
      exit 1
      ;;
  esac
done

echo "Timeout after ${MAX_WAIT}s" >&2
exit 1
