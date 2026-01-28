#!/bin/bash
# Linear API Helper Script
# Part of linear-autopilot skill

set -e

# Load API key
if [ -f ~/.clawdbot/linear.env ]; then
  source ~/.clawdbot/linear.env
elif [ -n "$LINEAR_API_KEY" ]; then
  : # Already set
else
  echo "Error: LINEAR_API_KEY not found"
  echo "Run: echo 'LINEAR_API_KEY=lin_api_xxx' > ~/.clawdbot/linear.env"
  exit 1
fi

# Load config if exists
CONFIG_FILE=~/.clawdbot/linear-config.json
if [ -f "$CONFIG_FILE" ]; then
  TEAM_ID=$(jq -r '.teamId // empty' "$CONFIG_FILE" 2>/dev/null)
  STATE_TODO=$(jq -r '.states.todo // empty' "$CONFIG_FILE" 2>/dev/null)
  STATE_IN_PROGRESS=$(jq -r '.states.inProgress // empty' "$CONFIG_FILE" 2>/dev/null)
  STATE_DONE=$(jq -r '.states.done // empty' "$CONFIG_FILE" 2>/dev/null)
fi

graphql() {
  local query="$1"
  curl -s -X POST https://api.linear.app/graphql \
    -H "Content-Type: application/json" \
    -H "Authorization: $LINEAR_API_KEY" \
    -d "{\"query\": \"$query\"}"
}

list_teams() {
  graphql "{ teams { nodes { id name } } }" | jq '.data.teams.nodes'
}

list_states() {
  if [ -z "$TEAM_ID" ]; then
    echo "Error: teamId not set in config"
    exit 1
  fi
  graphql "{ team(id: \\\"$TEAM_ID\\\") { states { nodes { id name type } } } }" | jq '.data.team.states.nodes'
}

get_task() {
  local task_id="$1"
  graphql "{ issue(id: \\\"$task_id\\\") { id identifier title description state { name } priority labels { nodes { name } } } }"
}

get_task_by_identifier() {
  local identifier="$1"
  graphql "{ issueSearch(query: \\\"$identifier\\\", first: 1) { nodes { id identifier title description state { name } } } }" | jq '.data.issueSearch.nodes[0]'
}

get_pending() {
  if [ -z "$TEAM_ID" ]; then
    echo "Error: teamId not set in config"
    exit 1
  fi
  graphql "{ team(id: \\\"$TEAM_ID\\\") { issues(filter: { state: { type: { in: [\\\"backlog\\\", \\\"unstarted\\\"] } } }, first: 50) { nodes { id identifier title state { name } } } } }" | jq '.data.team.issues.nodes'
}

update_status() {
  local task_id="$1"
  local state_id="$2"
  graphql "mutation { issueUpdate(id: \\\"$task_id\\\", input: { stateId: \\\"$state_id\\\" }) { success issue { identifier state { name } } } }"
}

start_task() {
  local task_id="$1"
  if [ -z "$STATE_IN_PROGRESS" ]; then
    echo "Error: states.inProgress not set in config"
    exit 1
  fi
  # Handle BAG-XX format
  if [[ "$task_id" == *-* ]]; then
    task_id=$(get_task_by_identifier "$task_id" | jq -r '.id')
  fi
  update_status "$task_id" "$STATE_IN_PROGRESS"
}

complete_task() {
  local task_id="$1"
  if [ -z "$STATE_DONE" ]; then
    echo "Error: states.done not set in config"
    exit 1
  fi
  if [[ "$task_id" == *-* ]]; then
    task_id=$(get_task_by_identifier "$task_id" | jq -r '.id')
  fi
  update_status "$task_id" "$STATE_DONE"
}

add_comment() {
  local task_id="$1"
  local comment="$2"
  if [[ "$task_id" == *-* ]]; then
    task_id=$(get_task_by_identifier "$task_id" | jq -r '.id')
  fi
  local escaped=$(echo "$comment" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')
  graphql "mutation { commentCreate(input: { issueId: \\\"$task_id\\\", body: \\\"$escaped\\\" }) { success } }"
}

case "$1" in
  teams) list_teams ;;
  states) list_states ;;
  get) get_task "$2" ;;
  find) get_task_by_identifier "$2" ;;
  pending) get_pending ;;
  start) start_task "$2" ;;
  done) complete_task "$2" ;;
  comment) add_comment "$2" "$3" ;;
  help|--help|-h|"")
    echo "Linear API Helper - linear-autopilot skill"
    echo ""
    echo "Setup:"
    echo "  echo 'LINEAR_API_KEY=lin_api_xxx' > ~/.clawdbot/linear.env"
    echo ""
    echo "Commands:"
    echo "  teams              List teams and IDs"
    echo "  states             List workflow states for configured team"
    echo "  get <id>           Get task by Linear ID"
    echo "  find <identifier>  Get task by identifier (e.g., BAG-12)"
    echo "  pending            List pending tasks"
    echo "  start <id>         Mark task as In Progress"
    echo "  done <id>          Mark task as Done"
    echo "  comment <id> <text> Add comment to task"
    ;;
  *)
    echo "Unknown command: $1"
    echo "Run '$0 help' for usage"
    exit 1
    ;;
esac
