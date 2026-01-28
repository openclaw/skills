#!/usr/bin/env bash
# Featurebase API CLI
# Usage: featurebase.sh <resource> <action> [options]

set -e

# Load config
if [[ -z "$FEATUREBASE_API_KEY" ]]; then
  CONFIG_FILE="${HOME}/.clawdbot/clawdbot.json"
  if [[ -f "$CONFIG_FILE" ]]; then
    FEATUREBASE_API_KEY=$(grep -A5 '"featurebase"' "$CONFIG_FILE" | grep '"apiKey"' | cut -d'"' -f4)
  fi
fi

if [[ -z "$FEATUREBASE_API_KEY" ]]; then
  echo "Error: FEATUREBASE_API_KEY not set"
  exit 1
fi

API_BASE="https://do.featurebase.app"
API_VERSION="2026-01-01.nova"

# API request helper
api() {
  local method="$1"
  local endpoint="$2"
  shift 2
  
  curl -s -X "$method" "${API_BASE}${endpoint}" \
    -H "Authorization: Bearer $FEATUREBASE_API_KEY" \
    -H "Featurebase-Version: $API_VERSION" \
    -H "Content-Type: application/json" \
    "$@"
}

# Format posts output
format_posts() {
  python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    posts = data.get('data', [])
    for p in posts:
        status = p.get('status', {}).get('name', 'unknown')
        status_type = p.get('status', {}).get('type', '')
        emoji = {'reviewing': '🟡', 'unstarted': '⚪', 'active': '🔵', 'completed': '✅', 'canceled': '⚫'}.get(status_type, '⚪')
        upvotes = p.get('upvotes', 0)
        title = p.get('title', 'Untitled')[:50]
        pid = p.get('id', 'N/A')[:8]
        print(f'{emoji} {pid}\t{title}\t{upvotes} votes\t{status}')
    if not posts:
        print('No posts found')
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
"
}

# Format conversations output
format_conversations() {
  python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    convos = data.get('data', [])
    for c in convos:
        state = c.get('state', 'unknown')
        emoji = {'open': '🔴', 'closed': '✅', 'snoozed': '💤'}.get(state, '⚪')
        title = c.get('title', 'No subject')[:40] if c.get('title') else 'No subject'
        cid = c.get('id', 'N/A')
        priority = '⭐' if c.get('priority') else ''
        waiting = '⏳' if c.get('awaitingCustomerReply') else ''
        print(f'{emoji}{priority}{waiting} {cid}\t{title}\t{state}')
    if not convos:
        print('No conversations found')
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
"
}

# Commands
cmd_posts() {
  local action="${1:-list}"
  shift || true
  
  case "$action" in
    list)
      echo "📋 Listing posts..."
      local params="limit=20"
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --board) params="${params}&boardId=$2"; shift 2 ;;
          --status) params="${params}&statusId=$2"; shift 2 ;;
          --sort) params="${params}&sortBy=$2"; shift 2 ;;
          --limit) params="limit=$2"; shift 2 ;;
          --search) params="${params}&q=$2"; shift 2 ;;
          *) shift ;;
        esac
      done
      api GET "/v2/posts?${params}" | format_posts
      ;;
    show)
      local id="$1"
      api GET "/v2/posts/${id}"
      ;;
    update)
      local id="$1"; shift
      local data="{}"
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --status) data="{\"statusId\":\"$2\"}"; shift 2 ;;
          *) shift ;;
        esac
      done
      api PATCH "/v2/posts/${id}" -d "$data"
      ;;
    *)
      echo "Usage: posts [list|show|update]"
      echo "  list [--board ID] [--status ID] [--sort upvotes|createdAt] [--search query]"
      echo "  show <id>"
      echo "  update <id> --status <statusId>"
      ;;
  esac
}

cmd_conversations() {
  local action="${1:-list}"
  shift || true
  
  case "$action" in
    list)
      echo "💬 Listing conversations..."
      local params="limit=20"
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --limit) params="limit=$2"; shift 2 ;;
          *) shift ;;
        esac
      done
      api GET "/v2/conversations?${params}" | format_conversations
      ;;
    show)
      local id="$1"
      api GET "/v2/conversations/${id}"
      ;;
    reply)
      local id="$1"; shift
      local content=""
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --content) content="$2"; shift 2 ;;
          *) shift ;;
        esac
      done
      echo "Creating reply..."
      api POST "/v2/conversations/${id}/parts" -d "{\"bodyMarkdown\":\"$content\"}"
      ;;
    close)
      local id="$1"
      api PATCH "/v2/conversations/${id}" -d '{"state":"closed"}'
      ;;
    *)
      echo "Usage: conversations [list|show|reply|close]"
      echo "  list [--limit N]"
      echo "  show <id>"
      echo "  reply <id> --content 'message'"
      echo "  close <id>"
      ;;
  esac
}

cmd_boards() {
  echo "📊 Listing boards..."
  api GET "/v2/boards?limit=50" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for b in data.get('data', []):
    print(f\"{b.get('id')}\t{b.get('name')}\t{b.get('postCount', 0)} posts\")
"
}

cmd_statuses() {
  echo "🏷️ Listing post statuses..."
  api GET "/v2/post-statuses?limit=50" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for s in data.get('data', []):
    emoji = {'reviewing': '🟡', 'unstarted': '⚪', 'active': '🔵', 'completed': '✅', 'canceled': '⚫'}.get(s.get('type', ''), '⚪')
    print(f\"{emoji} {s.get('id')}\t{s.get('name')}\t{s.get('type')}\")
"
}

cmd_changelog() {
  local action="${1:-list}"
  shift || true
  
  case "$action" in
    list)
      echo "📝 Listing changelog entries..."
      api GET "/v2/changelogs?limit=20" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for c in data.get('data', []):
    status = '✅' if c.get('isPublished') else '📝'
    print(f\"{status} {c.get('id')[:8]}\t{c.get('title', 'Untitled')[:50]}\t{c.get('publishedAt', 'draft')[:10]}\")
"
      ;;
    *)
      echo "Usage: changelog [list]"
      ;;
  esac
}

# Main
resource="${1:-help}"
shift || true

case "$resource" in
  posts|p) cmd_posts "$@" ;;
  conversations|c|inbox) cmd_conversations "$@" ;;
  boards|b) cmd_boards "$@" ;;
  statuses|s) cmd_statuses "$@" ;;
  changelog|cl) cmd_changelog "$@" ;;
  help|--help|-h)
    echo "Featurebase CLI"
    echo ""
    echo "Usage: featurebase.sh <resource> <action> [options]"
    echo ""
    echo "Resources:"
    echo "  posts (p)          - Feature requests & feedback"
    echo "  conversations (c)  - Support inbox / messenger"
    echo "  boards (b)         - Feedback boards"
    echo "  statuses (s)       - Post statuses"
    echo "  changelog (cl)     - Release notes"
    echo ""
    echo "Examples:"
    echo "  featurebase.sh posts list --sort upvotes"
    echo "  featurebase.sh conversations list"
    echo "  featurebase.sh c reply 12345 --content 'Thanks for reaching out!'"
    ;;
  *)
    echo "Unknown resource: $resource"
    echo "Run 'featurebase.sh help' for usage"
    exit 1
    ;;
esac
