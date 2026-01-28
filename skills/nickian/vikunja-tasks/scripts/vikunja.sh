#!/bin/bash
# Vikunja CLI - Manage tasks and projects
# Uses Vikunja REST API v1
#
# Requires environment variables:
#   VIKUNJA_URL - Your Vikunja instance URL (e.g., https://todo.example.com)
#   VIKUNJA_TOKEN - Your Vikunja API token
#
# Usage:
#   vikunja.sh tasks [--project NAME] [--search TEXT] [--filter EXPR] [--count N] [--sort FIELD] [--order asc|desc]
#   vikunja.sh overdue
#   vikunja.sh due [--hours N]
#   vikunja.sh create-task --project NAME --title TEXT [--description TEXT] [--due DATE] [--priority 1-5]
#   vikunja.sh complete --id ID
#   vikunja.sh projects
#   vikunja.sh create-project --title TEXT [--description TEXT] [--parent ID]
#   vikunja.sh notifications
#   vikunja.sh task --id ID

set -e

# --- Config ---
if [ -z "$VIKUNJA_URL" ] || [ -z "$VIKUNJA_TOKEN" ]; then
  echo "Error: VIKUNJA_URL and VIKUNJA_TOKEN must be set" >&2
  exit 1
fi

API="${VIKUNJA_URL}/api/v1"
AUTH="Authorization: Bearer ${VIKUNJA_TOKEN}"

# --- Helpers ---
api_get() {
  curl -s -H "$AUTH" "${API}/$1"
}

api_put() {
  curl -s -X PUT -H "$AUTH" -H "Content-Type: application/json" "${API}/$1" -d "$2"
}

api_post() {
  curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" "${API}/$1" -d "$2"
}

api_delete() {
  curl -s -X DELETE -H "$AUTH" "${API}/$1"
}

get_project_id() {
  local NAME="$1"
  api_get "projects" | jq -r --arg name "$NAME" '.[] | select(.title | ascii_downcase == ($name | ascii_downcase)) | .id' | head -1
}

format_tasks() {
  jq -r '
    if length == 0 then "No tasks found."
    else
      .[] |
      "[\(if .done then "✅" else "⬜" end)] \(.title)" +
      (if .due_date != null and .due_date != "0001-01-01T00:00:00Z" then "\n    Due: \(.due_date[0:10])" else "" end) +
      (if .priority > 0 then "\n    Priority: \(.priority)/5" else "" end) +
      "\n    ID: \(.id)\n"
    end
  ' 2>/dev/null || echo "Error parsing tasks" >&2
}

# --- Commands ---

cmd_tasks() {
  local COUNT=20
  local SEARCH=""
  local FILTER=""
  local PROJECT=""
  local SORT="due_date"
  local ORDER="asc"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --count) COUNT="$2"; shift 2 ;;
      --search) SEARCH="$2"; shift 2 ;;
      --filter) FILTER="$2"; shift 2 ;;
      --project) PROJECT="$2"; shift 2 ;;
      --sort) SORT="$2"; shift 2 ;;
      --order) ORDER="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  local URL="tasks/all?per_page=${COUNT}&sort_by=${SORT}&order_by=${ORDER}&filter_timezone=America/Denver"

  if [ -n "$SEARCH" ]; then
    URL="${URL}&s=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$SEARCH'))")"
  fi

  if [ -n "$FILTER" ]; then
    URL="${URL}&filter=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$FILTER'))")"
  fi

  if [ -n "$PROJECT" ]; then
    local PID
    PID=$(get_project_id "$PROJECT")
    if [ -z "$PID" ]; then
      echo "Error: Project '$PROJECT' not found" >&2
      exit 1
    fi
    URL="${URL}&filter=$(python3 -c "import urllib.parse; print(urllib.parse.quote('project = $PID'))")"
  fi

  api_get "$URL" | format_tasks
}

cmd_overdue() {
  local NOW
  NOW=$(date -u +"%Y-%m-%dT%H:%M:%S")
  local FILTER="due_date < '${NOW}' && done = false"
  local URL="tasks/all?per_page=50&sort_by=due_date&order_by=asc&filter_timezone=America/Denver"
  URL="${URL}&filter=$(python3 -c "import urllib.parse; print(urllib.parse.quote(\"$FILTER\"))")"
  api_get "$URL" | format_tasks
}

cmd_due() {
  local HOURS=24
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --hours) HOURS="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  local NOW
  local FUTURE
  NOW=$(date -u +"%Y-%m-%dT%H:%M:%S")
  FUTURE=$(date -u -v+${HOURS}H +"%Y-%m-%dT%H:%M:%S" 2>/dev/null || date -u -d "+${HOURS} hours" +"%Y-%m-%dT%H:%M:%S" 2>/dev/null)

  local FILTER="due_date > '${NOW}' && due_date < '${FUTURE}' && done = false"
  local URL="tasks/all?per_page=50&sort_by=due_date&order_by=asc&filter_timezone=America/Denver"
  URL="${URL}&filter=$(python3 -c "import urllib.parse; print(urllib.parse.quote(\"$FILTER\"))")"
  api_get "$URL" | format_tasks
}

cmd_create_task() {
  local TITLE=""
  local DESCRIPTION=""
  local DUE=""
  local PRIORITY=0
  local PROJECT=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --title) TITLE="$2"; shift 2 ;;
      --description) DESCRIPTION="$2"; shift 2 ;;
      --due) DUE="$2"; shift 2 ;;
      --priority) PRIORITY="$2"; shift 2 ;;
      --project) PROJECT="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  if [ -z "$TITLE" ] || [ -z "$PROJECT" ]; then
    echo "Error: --title and --project are required" >&2
    exit 1
  fi

  local PID
  PID=$(get_project_id "$PROJECT")
  if [ -z "$PID" ]; then
    echo "Error: Project '$PROJECT' not found" >&2
    exit 1
  fi

  local BODY
  BODY=$(jq -n \
    --arg title "$TITLE" \
    --arg desc "$DESCRIPTION" \
    --arg due "$DUE" \
    --argjson priority "$PRIORITY" \
    '{title: $title, description: $desc, priority: $priority} + (if $due != "" then {due_date: ($due + "T00:00:00Z")} else {} end)')

  local RESPONSE
  RESPONSE=$(api_put "projects/${PID}/tasks" "$BODY")

  if echo "$RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    local ID
    ID=$(echo "$RESPONSE" | jq -r '.id')
    echo "Created task: $TITLE (id: $ID) in project: $PROJECT"
  else
    echo "Error creating task:" >&2
    echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE" >&2
    exit 1
  fi
}

cmd_complete() {
  local ID=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) ID="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  if [ -z "$ID" ]; then
    echo "Error: --id is required" >&2
    exit 1
  fi

  local RESPONSE
  RESPONSE=$(api_post "tasks/${ID}" '{"done": true}')

  if echo "$RESPONSE" | jq -e '.done' > /dev/null 2>&1; then
    local TITLE
    TITLE=$(echo "$RESPONSE" | jq -r '.title')
    echo "Completed: $TITLE (id: $ID) ✅"
  else
    echo "Error completing task:" >&2
    echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE" >&2
    exit 1
  fi
}

cmd_task() {
  local ID=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) ID="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  if [ -z "$ID" ]; then
    echo "Error: --id is required" >&2
    exit 1
  fi

  api_get "tasks/${ID}" | jq '{
    id: .id,
    title: .title,
    description: .description,
    done: .done,
    due_date: .due_date,
    priority: .priority,
    percent_done: .percent_done,
    project: .project.title,
    labels: [.labels[]?.title],
    created: .created,
    updated: .updated
  }'
}

cmd_projects() {
  api_get "projects" | jq -r '.[] | "\(.title) (id: \(.id))" + (if .description != "" then "\n    \(.description)" else "" end)'
}

cmd_create_project() {
  local TITLE=""
  local DESCRIPTION=""
  local PARENT=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --title) TITLE="$2"; shift 2 ;;
      --description) DESCRIPTION="$2"; shift 2 ;;
      --parent) PARENT="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  if [ -z "$TITLE" ]; then
    echo "Error: --title is required" >&2
    exit 1
  fi

  local BODY
  BODY=$(jq -n \
    --arg title "$TITLE" \
    --arg desc "$DESCRIPTION" \
    --arg parent "$PARENT" \
    '{title: $title, description: $desc} + (if $parent != "" then {parent_project_id: ($parent | tonumber)} else {} end)')

  local RESPONSE
  RESPONSE=$(api_put "projects" "$BODY")

  if echo "$RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    local ID
    ID=$(echo "$RESPONSE" | jq -r '.id')
    echo "Created project: $TITLE (id: $ID)"
  else
    echo "Error creating project:" >&2
    echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE" >&2
    exit 1
  fi
}

cmd_notifications() {
  api_get "notifications" | jq -r '
    if length == 0 then "No notifications."
    else
      .[] | "\(.created | split("T")[0]) - \(.name // "Notification")\n  \(.notification.subject // .notification // "No details")\n"
    end
  '
}

# --- Main ---
COMMAND="${1:-tasks}"
shift 2>/dev/null || true

case "$COMMAND" in
  tasks|list) cmd_tasks "$@" ;;
  overdue) cmd_overdue ;;
  due|upcoming) cmd_due "$@" ;;
  create-task|add) cmd_create_task "$@" ;;
  complete|done) cmd_complete "$@" ;;
  task|get) cmd_task "$@" ;;
  projects) cmd_projects ;;
  create-project) cmd_create_project "$@" ;;
  notifications|notifs) cmd_notifications ;;
  *)
    echo "Usage: $0 {tasks|overdue|due|create-task|complete|task|projects|create-project|notifications}" >&2
    exit 1
    ;;
esac
