#!/usr/bin/env bash
set -euo pipefail

: "${VIKUNJA_URL:?Set VIKUNJA_URL (base URL or include /api/v1)}"

# Normalize VIKUNJA_URL to include /api/v1
VIKUNJA_URL=${VIKUNJA_URL%/}
case "$VIKUNJA_URL" in
  */api/v1) : ;;
  */api/v1/*) VIKUNJA_URL=${VIKUNJA_URL%%/api/v1*}/api/v1 ;;
  *) VIKUNJA_URL="$VIKUNJA_URL/api/v1" ;;
esac

# Auth:
# - Preferred: set VIKUNJA_TOKEN (JWT)
# - Fallback: set VIKUNJA_USERNAME + VIKUNJA_PASSWORD and we'll request a JWT
: "${VIKUNJA_TOKEN:=}"
: "${VIKUNJA_USERNAME:=}"
: "${VIKUNJA_PASSWORD:=}"

usage() {
  cat <<'EOF'
vikunja.sh - small Vikunja CLI helper

Usage:
  vikunja.sh overdue
  vikunja.sh due-today
  vikunja.sh due-week
  vikunja.sh list --filter '<vikunja filter>'
  vikunja.sh show <taskId>
  vikunja.sh done <taskId>

Environment:
  VIKUNJA_URL      e.g. https://vikunja.xyz (or https://vikunja.xyz/api/v1)
  VIKUNJA_TOKEN    JWT bearer token (preferred)
  VIKUNJA_USERNAME Username (fallback)
  VIKUNJA_PASSWORD Password (fallback)

Notes:
  - Uses /tasks/all to fetch tasks across all projects.
  - Filters use Vikunja filter syntax: https://vikunja.io/docs/filters/
EOF
}

ensure_token() {
  if [[ -n "$VIKUNJA_TOKEN" ]]; then
    return 0
  fi

  if [[ -z "$VIKUNJA_USERNAME" || -z "$VIKUNJA_PASSWORD" ]]; then
    echo "Missing auth: set VIKUNJA_TOKEN, or set VIKUNJA_USERNAME + VIKUNJA_PASSWORD" >&2
    exit 2
  fi

  # Request a JWT
  VIKUNJA_TOKEN=$(curl -fsS -X POST "$VIKUNJA_URL/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$VIKUNJA_USERNAME\",\"password\":\"$VIKUNJA_PASSWORD\",\"long_token\":true}" \
    | jq -r '.token // empty')

  if [[ -z "$VIKUNJA_TOKEN" || "$VIKUNJA_TOKEN" == "null" ]]; then
    echo "Login failed: no token returned" >&2
    exit 1
  fi
}

api_get() {
  local path=$1
  ensure_token
  curl -fsS "$VIKUNJA_URL$path" -H "Authorization: Bearer $VIKUNJA_TOKEN"
}

api_post_json() {
  local path=$1
  local json=${2:-}
  ensure_token

  if [[ "$json" == "@-" ]]; then
    curl -fsS -X POST "$VIKUNJA_URL$path" \
      -H "Authorization: Bearer $VIKUNJA_TOKEN" \
      -H "Content-Type: application/json" \
      -d @-
    return 0
  fi

  curl -fsS -X POST "$VIKUNJA_URL$path" \
    -H "Authorization: Bearer $VIKUNJA_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$json"
}

urlencode() {
  # shell-safe: read stdin
  jq -sRr @uri
}

project_map_json() {
  # {"<id>":"Title", ...}
  api_get "/projects" | jq 'map({key:(.id|tostring), value:.title}) | from_entries'
}

format_tasks() {
  local projects_json=$1
  jq -r --argjson projects "$projects_json" '
    def project_icon($name):
      # If the project title starts with an emoji/symbol token (non-alnum), use that token.
      # Example: "💸 Pagos" -> "💸".
      ($name // "") as $n
      | ($n | split(" ")[0]) as $first
      | if ($first | test("^[A-Za-z0-9]")) then "" else $first end;

    def fmt_due($iso):
      if ($iso == null) then "(no due)"
      else ($iso | fromdateiso8601 | strftime("%b/%e") | gsub(" "; ""))
      end;

    .[]
    | ($projects[(.project_id|tostring)] // "") as $pname
    | project_icon($pname) as $icon
    | ($icon | if length>0 then . else "🔨" end) as $glyph
    | "\($glyph) \(fmt_due(.due_date)) - #\(.id) \(.title)"
  '
}

list_tasks() {
  local filter=$1
  local encoded_filter
  encoded_filter=$(printf %s "$filter" | urlencode)

  # Preload projects so output can include project title.
  local projects
  projects=$(project_map_json)

  api_get "/tasks/all?filter=$encoded_filter&sort_by=due_date&order_by=asc" | format_tasks "$projects"
}

cmd=${1:-}
shift || true

case "$cmd" in
  -h|--help|help|"")
    usage
    exit 0
    ;;

  overdue)
    list_tasks 'done = false && due_date < now'
    ;;

  due-today)
    # "today" uses filter_timezone if supplied; we use server default unless overridden.
    # Using relative bounds keeps it compatible.
    list_tasks 'done = false && due_date >= now/d && due_date < now/d + 1d'
    ;;

  list)
    if [[ "${1:-}" != "--filter" || -z "${2:-}" ]]; then
      echo "Missing --filter '<expr>'" >&2
      usage >&2
      exit 2
    fi
    filter=$2
    list_tasks "$filter"
    ;;

  show)
    task_id=${1:-}
    if [[ -z "$task_id" ]]; then
      echo "Missing task id" >&2
      exit 2
    fi
    api_get "/tasks/$task_id" | jq '{id,title,due_date,done,project_id,repeat_after,repeat_mode,priority,created,updated}'
    ;;

  done)
    task_id=${1:-}
    if [[ -z "$task_id" ]]; then
      echo "Missing task id" >&2
      exit 2
    fi

    # Vikunja's recurring-task behavior appears to depend on fields like due_date
    # being present in the update payload (as the web UI sends). To match that,
    # fetch the current task and send it back with done=true.
    api_get "/tasks/$task_id" \
      | jq '.done = true | .done_at = null' \
      | api_post_json "/tasks/$task_id" @- \
      | jq '{id,title,done,done_at,due_date,project_id,updated}'
    ;;

  *)
    echo "Unknown command: $cmd" >&2
    usage >&2
    exit 2
    ;;
esac
