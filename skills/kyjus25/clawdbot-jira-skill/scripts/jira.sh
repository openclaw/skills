
#!/usr/bin/env bash
set -euo pipefail

# Jira CLI wrapper
# Mirrors the helper tools defined in jira.ts
# Requires: curl, jq, bc, python3, env vars JIRA_EMAIL and JIRA_API_TOKEN

JIRA_URL="${JIRA_URL:-}"
JIRA_BOARD="${JIRA_BOARD:-}"

for bin in curl jq bc python3; do
  if ! command -v "$bin" >/dev/null 2>&1; then
    echo "Error: $bin is required" >&2
    exit 1
  fi
done

if [[ -z "${JIRA_EMAIL:-}" || -z "${JIRA_API_TOKEN:-}" || -z "${JIRA_URL:-}" ]]; then
  cat >&2 <<'EOF'
Error: JIRA_EMAIL, JIRA_API_TOKEN, and JIRA_URL must be set.
Create a token at https://id.atlassian.com/manage-profile/security/api-tokens
Then export, for example:
  export JIRA_URL="https://your-domain.atlassian.net"
  export JIRA_EMAIL="you@example.com"
  export JIRA_API_TOKEN="token-value"
EOF
  exit 1
fi

AUTH_HEADER="Authorization: Basic $(printf '%s:%s' "$JIRA_EMAIL" "$JIRA_API_TOKEN" | base64)"
JSON_HEADER="Content-Type: application/json"

project_clause() {
  local board="${JIRA_BOARD:-}"
  if [[ -z "$board" ]]; then
    echo ""
    return
  fi
  IFS=',' read -ra parts <<<"$board"
  if ((${#parts[@]} == 1)); then
    echo "project = \"${parts[0]}\""
  else
    local quoted=""
    for p in "${parts[@]}"; do
      [[ -n "$quoted" ]] && quoted+=", "
      quoted+="\"$p\""
    done
    echo "project in (${quoted})"
  fi
}

api() {
  local method="$1"
  local url="$2"
  local data="${3:-}"
  if [[ "$url" != http* ]]; then
    url="${JIRA_URL}${url}"
  fi
  curl -sS -X "$method" "$url" \
    -H "$AUTH_HEADER" \
    -H "$JSON_HEADER" \
    ${data:+-d "$data"}
}

search_api() {
  local jql="$1"
  local fields="$2"
  local max="${3:-50}"
  curl -sS -G "${JIRA_URL}/rest/api/3/search/jql" \
    -H "$AUTH_HEADER" \
    -H "$JSON_HEADER" \
    --data-urlencode "jql=$jql" \
    --data-urlencode "fields=$fields" \
    --data-urlencode "maxResults=$max"
}

to_epoch_ms() {
  local iso="$1"
  if command -v gdate >/dev/null 2>&1; then
    gdate -u -d "$iso" +%s%3N
  else
    local secs
    secs=$(date -j -u -f "%Y-%m-%dT%H:%M:%SZ" "$iso" +%s 2>/dev/null || date -u -d "$iso" +%s 2>/dev/null)
    if [[ -z "$secs" ]]; then
      echo "Error: unable to parse date $iso" >&2
      exit 1
    fi
    printf '%s000' "$secs"
  fi
}

fetch_worklog_ids() {
  local since_ms="$1"
  local out_file="$2"
  : >"$out_file"
  local next="${JIRA_URL}/rest/api/3/worklog/updated?since=${since_ms}"
  while [[ -n "$next" ]]; do
    local resp
    resp=$(api GET "$next")
    echo "$resp" | jq -r '.values[].worklogId' >>"$out_file"
    local last
    last=$(echo "$resp" | jq -r '.lastPage')
    if [[ "$last" == "true" ]]; then
      next=""
    else
      next=$(echo "$resp" | jq -r '.nextPage // ""')
    fi
  done
}

post_worklog_chunk() {
  local chunk="$1"
  local out_file="$2"
  local resp
  resp=$(api POST "/rest/api/3/worklog/list" "{\"ids\":[${chunk}]}")
  echo "$resp" | jq -c '.[]' >>"$out_file"
}

fetch_worklogs() {
  local ids_file="$1"
  local out_file="$2"
  : >"$out_file"
  local chunk=""
  local count=0
  while IFS= read -r id; do
    [[ -z "$id" ]] && continue
    if [[ $count -gt 0 ]]; then
      chunk+=","
    fi
    chunk+="$id"
    count=$((count + 1))
    if [[ $count -ge 200 ]]; then
      post_worklog_chunk "$chunk" "$out_file"
      chunk=""
      count=0
    fi
  done <"$ids_file"
  if [[ -n "$chunk" ]]; then
    post_worklog_chunk "$chunk" "$out_file"
  fi
}

search_by_issue_ids() {
  local ids_csv="$1"
  curl -sS -G "${JIRA_URL}/rest/api/3/search/jql" \
    -H "$AUTH_HEADER" \
    -H "$JSON_HEADER" \
    --data-urlencode "jql=id in (${ids_csv})" \
    --data-urlencode "fields=key,summary" \
    --data-urlencode "maxResults=200"
}

fetch_issue_details() {
  local ids_file="$1"
  local out_file="$2"
  : >"$out_file"
  [[ ! -s "$ids_file" ]] && return 0
  local chunk=""
  local count=0
  while IFS= read -r id; do
    [[ -z "$id" ]] && continue
    if [[ $count -gt 0 ]]; then
      chunk+=","
    fi
    chunk+="$id"
    count=$((count + 1))
    if [[ $count -ge 50 ]]; then
      search_by_issue_ids "$chunk" | jq -c '.issues[]? | {id: .id, key: .key, summary: .fields.summary}' >>"$out_file"
      chunk=""
      count=0
    fi
  done <"$ids_file"
  if [[ -n "$chunk" ]]; then
    search_by_issue_ids "$chunk" | jq -c '.issues[]? | {id: .id, key: .key, summary: .fields.summary}' >>"$out_file"
  fi
}

print_search() {
  local query="$1"
  local max="${2:-10}"
  local scope
  scope=$(project_clause)
  local jql=""
  if [[ -n "$scope" ]]; then
    jql="${scope} AND "
  fi
  jql+="(text ~ \"${query}\" OR key = \"${query}\") ORDER BY updated DESC"
  local resp
  resp=$(search_api "$jql" "key,summary" "$max")
  if echo "$resp" | jq -e '.errorMessages? // [] | length > 0' >/dev/null 2>&1; then
    echo "$resp" | jq -r '.errorMessages[]' >&2
    exit 1
  fi
  echo "$resp" | jq -r '.issues[]? | "\(.key)\t\(.fields.summary)"'
}

print_my_open() {
  local max="${1:-50}"
  local scope
  scope=$(project_clause)
  local jql="assignee = currentUser() AND status != \"Done\" ORDER BY updated DESC"
  if [[ -n "$scope" ]]; then
    jql="${scope} AND ${jql}"
  fi
  local resp
  resp=$(search_api "$jql" "key,summary,status,priority,updated" "$max")
  if echo "$resp" | jq -e '.errorMessages? // [] | length > 0' >/dev/null 2>&1; then
    echo "$resp" | jq -r '.errorMessages[]' >&2
    exit 1
  fi
  echo "$resp" | jq -r '.issues[]? | "\(.key) [\(.fields.status.name // "Status") / \(.fields.priority.name // "Priority")]\t\(.fields.summary)"'
}

create_issue() {
  local summary="$1"
  local description="${2:-}"
  local payload
  payload=$(jq -n --arg project "$JIRA_BOARD" --arg summary "$summary" --arg desc "$description" '
    {
      fields: {
        project: { key: $project },
        summary: $summary,
        issuetype: { name: "Task" }
      }
    } + ( ($desc | length) > 0
      ? { fields: { description: { type: "doc", version: 1, content: [ { type: "paragraph", content: [ { type: "text", text: $desc } ] } ] } } }
      : {} )
  ')
  local resp
  resp=$(api POST "/rest/api/3/issue" "$payload")
  echo "$resp" | jq -r 'if .key then "Created: \(.key) -> '"${JIRA_URL}"'/browse/\(.key)" else "Error: \(.errors // .errorMessages // .)" end'
}

transition_issue() {
  local issue="$1"
  local target="$2"
  local transitions
  transitions=$(api GET "/rest/api/3/issue/${issue}/transitions")
  local id
  id=$(echo "$transitions" | jq -r --arg t "$target" '.transitions[]? | select((.name|ascii_downcase)==($t|ascii_downcase)) | .id' | head -n1)
  if [[ -z "$id" ]]; then
    echo "Transition not available. Options: $(echo "$transitions" | jq -r '.transitions[]?.name' | paste -sd, -)" >&2
    exit 1
  fi
  local resp
  resp=$(api POST "/rest/api/3/issue/${issue}/transitions" "{\"transition\": {\"id\": \"${id}\"}}")
  if [[ -z "$resp" ]]; then
    echo "${issue} moved to ${target}"
    return
  fi
  if echo "$resp" | jq -e .errors >/dev/null 2>&1; then
    echo "$resp" | jq -r '.errors'
  else
    echo "${issue} moved to ${target}"
  fi
}

log_work() {
  local issue="$1"
  local hours="$2"
  local date="${3:-$(date -u +%Y-%m-%d)}"
  local seconds
  seconds=$(printf "%.0f" "$(echo "$hours * 3600" | bc -l)")
  local started="${date}T12:00:00.000+0000"
  local resp
  resp=$(api POST "/rest/api/3/issue/${issue}/worklog" "{\"timeSpentSeconds\": ${seconds}, \"started\": \"${started}\"}")
  if echo "$resp" | jq -e '.errors // .errorMessages' >/dev/null 2>&1; then
    echo "$resp" | jq -r '.errors // .errorMessages'
  else
    echo "Logged ${hours}h to ${issue} on ${date}"
  fi
}

find_account_id() {
  local query="$1"
  local resp
  resp=$(curl -sS -G "${JIRA_URL}/rest/api/3/user/search" \
    -H "$AUTH_HEADER" \
    -H "$JSON_HEADER" \
    --data-urlencode "query=${query}")
  echo "$resp" | jq -r '.[0].accountId // empty'
}

assign_issue() {
  local issue="$1"
  local user_query="$2"
  local acct
  acct=$(find_account_id "$user_query")
  if [[ -z "$acct" ]]; then
    echo "User not found for query: $user_query" >&2
    exit 1
  fi
  local resp
  resp=$(api PUT "/rest/api/3/issue/${issue}/assignee" "{\"accountId\":\"${acct}\"}")
  if echo "$resp" | jq -e '.errors // .errorMessages' >/dev/null 2>&1; then
    echo "$resp" | jq -r '.errors // .errorMessages'
  else
    echo "Assigned ${issue} -> ${user_query}"
  fi
}

my_account_id() {
  local resp
  resp=$(api GET "/rest/api/3/myself")
  echo "$resp" | jq -r '.accountId // empty'
}

assign_me() {
  local issue="$1"
  local acct
  acct=$(my_account_id)
  if [[ -z "$acct" ]]; then
    echo "Could not resolve current user account id" >&2
    exit 1
  fi
  local resp
  resp=$(api PUT "/rest/api/3/issue/${issue}/assignee" "{\"accountId\":\"${acct}\"}")
  if echo "$resp" | jq -e '.errors // .errorMessages' >/dev/null 2>&1; then
    echo "$resp" | jq -r '.errors // .errorMessages'
  else
    echo "Assigned ${issue} -> me (${JIRA_EMAIL})"
  fi
}

issue_details() {
  local issue="$1"
  local resp
  resp=$(api GET "/rest/api/3/issue/${issue}?fields=key,summary,status,assignee,priority,reporter,components,fixVersions")
  if echo "$resp" | jq -e '.errorMessages? // [] | length > 0' >/dev/null 2>&1; then
    echo "$resp" | jq -r '.errorMessages[]'
    return
  fi
  local line
  line=$(echo "$resp" | jq -r '[
    .key,
    (.fields.summary // "Unknown"),
    (.fields.status.name // "Unknown"),
    (.fields.priority.name // "None"),
    (.fields.assignee.displayName // "Unassigned"),
    (.fields.reporter.displayName // "Unknown"),
    (((.fields.components // []) | map(.name) | join(", ")) // "-"),
    (((.fields.fixVersions // []) | map(.name) | join(", ")) // "-")
  ] | @tsv')
  IFS=$'\t' read -r key summary status priority assignee reporter components fix <<<"$line"
  printf "%s: %s\n" "$key" "$summary"
  printf "Status: %s | Priority: %s\n" "$status" "$priority"
  printf "Assignee: %s | Reporter: %s\n" "$assignee" "$reporter"
  printf "Components: %s | FixVersions: %s\n" "$components" "$fix"
}

fetch_issue_worklogs() {
  local issue="$1"
  local out_file="$2"
  : >"$out_file"
  local start=0
  local total=0
  local max=100
  while :; do
    local resp
    resp=$(api GET "/rest/api/3/issue/${issue}/worklog?startAt=${start}&maxResults=${max}")
    echo "$resp" | jq -c '.worklogs[]?' >>"$out_file"
    total=$(echo "$resp" | jq -r '.total // 0')
    local fetched
    fetched=$(echo "$resp" | jq -r '(.worklogs | length) // 0')
    if [[ $fetched -eq 0 ]]; then
      break
    fi
    start=$((start + fetched))
    if [[ $start -ge $total ]]; then
      break
    fi
  done
}

hours_for_issue() {
  local issue="$1"
  local user_filter="${2:-}"
  local account=""
  if [[ -n "$user_filter" ]]; then
    account=$(find_account_id "$user_filter" || true)
  fi

  local tmp_logs tmp_issue_details tmp_issue_map
  tmp_logs=$(mktemp)
  tmp_issue_details=$(mktemp)
  tmp_issue_map=$(mktemp)

  fetch_issue_worklogs "$issue" "$tmp_logs"
  if [[ ! -s "$tmp_logs" ]]; then
    echo "{\"issue\":\"${issue}\",\"totalHours\":0,\"users\":[]}"
    rm -f "$tmp_logs" "$tmp_issue_details" "$tmp_issue_map"
    return 0
  fi

  # ensure we can map issue id to key (handles case-insensitive key input)
  api GET "/rest/api/3/issue/${issue}?fields=key,summary" \
    | jq -c '{key, summary: .fields.summary}' >"$tmp_issue_details"
  jq -s 'map({key, summary}) | (.[0] // {})' "$tmp_issue_details" >"$tmp_issue_map"

  local issue_meta
  issue_meta=$(cat "$tmp_issue_map")
  local issue_key issue_summary
  issue_key=$(echo "$issue_meta" | jq -r '.key // "'"$issue"'"')
  issue_summary=$(echo "$issue_meta" | jq -r '.summary // "Unknown"')

  python3 - "$issue_key" "$issue_summary" "$user_filter" "$account" "$tmp_logs" <<'PY'
import json, re, sys
from datetime import datetime

issue_key, issue_summary, user_filter, account_filter, path = sys.argv[1:]
user_filter = (user_filter or "").lower()
account_filter = account_filter or ""

users = {}
total_seconds = 0

with open(path) as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        log = json.loads(line)
        author = log.get("author") or {}
        email = author.get("emailAddress") or "unknown"
        display = author.get("displayName") or email
        account_id = author.get("accountId") or ""
        if user_filter or account_filter:
            matches_text = False
            if user_filter:
                if user_filter in email.lower() or user_filter in display.lower():
                    matches_text = True
            matches_acct = account_filter and account_id == account_filter
            if not (matches_text or matches_acct):
                continue
        seconds = int(log.get("timeSpentSeconds") or 0)
        total_seconds += seconds
        if email not in users:
            users[email] = {"email": email, "displayName": display, "seconds": 0}
        users[email]["seconds"] += seconds

result = {
    "issue": issue_key,
    "summary": issue_summary,
    "totalHours": round(total_seconds / 3600, 2),
    "users": sorted(
        [
            {
                "email": v["email"],
                "displayName": v["displayName"],
                "hours": round(v["seconds"] / 3600, 2),
            }
            for v in users.values()
        ],
        key=lambda x: x["hours"],
        reverse=True,
    ),
}

print(json.dumps(result))
PY

  rm -f "$tmp_logs" "$tmp_issue_details" "$tmp_issue_map"
}

comment_issue() {
  local issue="$1"
  local body="$2"
  local payload
  payload=$(jq -n --arg text "$body" '{body:{type:"doc",version:1,content:[{type:"paragraph",content:[{type:"text",text:$text}]}]}}')
  local resp
  resp=$(api POST "/rest/api/3/issue/${issue}/comment" "$payload")
  if echo "$resp" | jq -e '.errors // .errorMessages' >/dev/null 2>&1; then
    echo "$resp" | jq -r '.errors // .errorMessages'
  else
    echo "Comment added to ${issue}"
  fi
}

list_transitions() {
  local issue="$1"
  api GET "/rest/api/3/issue/${issue}/transitions" | jq -r '.transitions[]? | "\(.id)\t\(.name)"'
}

hours_by_issue() {
  local start_date="$1"
  local end_date="$2"
  local start_iso="${start_date}T00:00:00Z"
  local end_iso="${end_date}T23:59:59Z"
  local start_ms
  start_ms=$(to_epoch_ms "$start_iso")
  local self_account=""
  self_account=$(my_account_id || true)
  if [[ -z "$self_account" && -n "${JIRA_EMAIL:-}" ]]; then
    self_account=$(find_account_id "$JIRA_EMAIL" || true)
  fi

  local tmp_ids tmp_logs tmp_hours tmp_issue_ids tmp_issue_details tmp_issue_map
  tmp_ids=$(mktemp)
  tmp_logs=$(mktemp)
  tmp_hours=$(mktemp)
  tmp_issue_ids=$(mktemp)
  tmp_issue_details=$(mktemp)
  tmp_issue_map=$(mktemp)

  fetch_worklog_ids "$start_ms" "$tmp_ids"
  if [[ ! -s "$tmp_ids" ]]; then
    echo "[]"
    rm -f "$tmp_ids" "$tmp_logs" "$tmp_hours" "$tmp_issue_ids" "$tmp_issue_details" "$tmp_issue_map"
    return 0
  fi

  fetch_worklogs "$tmp_ids" "$tmp_logs"
  python3 - "$start_iso" "$end_iso" "$JIRA_EMAIL" "$self_account" "$tmp_logs" >"$tmp_hours" <<'PY'
import json, re, sys
from datetime import datetime

start_iso, end_iso, email, account, path = sys.argv[1:]
fix_tz = re.compile(r"([+-]\d{2})(\d{2})$")
start = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
end = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
totals = {}
email_l = (email or "").lower()
account = account or ""

with open(path) as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        log = json.loads(line)
        author = log.get("author") or {}
        log_email = (author.get("emailAddress") or "").lower()
        log_account = author.get("accountId") or ""
        if email_l and log_email == email_l:
            pass
        elif account and log_account == account:
            pass
        else:
            continue
        started = log.get("started")
        if not started:
            continue
        started_fixed = fix_tz.sub(r"\1:\2", started)
        try:
            ts = datetime.fromisoformat(started_fixed)
        except ValueError:
            continue
        if ts < start or ts > end:
            continue
        issue_id = str(log.get("issueId"))
        totals[issue_id] = totals.get(issue_id, 0) + int(log.get("timeSpentSeconds") or 0)

json.dump([{"issueId": k, "seconds": v} for k, v in totals.items()], sys.stdout)
PY

  if [[ ! -s "$tmp_hours" || "$(cat "$tmp_hours")" == "[]" ]]; then
    echo "[]"
    rm -f "$tmp_ids" "$tmp_logs" "$tmp_hours" "$tmp_issue_ids" "$tmp_issue_details" "$tmp_issue_map"
    return 0
  fi

  jq -r '.[].issueId' "$tmp_hours" >"$tmp_issue_ids"
  fetch_issue_details "$tmp_issue_ids" "$tmp_issue_details"
  jq -s 'map({(.id): {key, summary}}) | add' "$tmp_issue_details" >"$tmp_issue_map"

  local issue_map_json
  issue_map_json=$(cat "$tmp_issue_map")
  if [[ -z "$issue_map_json" ]]; then
    issue_map_json="{}"
  fi

  jq --argjson m "$issue_map_json" '
    map({
      issue: ($m[(.issueId|tostring)].key // (.issueId | tostring)),
      name: ($m[(.issueId|tostring)].summary // "Unknown"),
      hours: ((.seconds / 3600 * 100) | round / 100)
    })
  ' "$tmp_hours"

  rm -f "$tmp_ids" "$tmp_logs" "$tmp_hours" "$tmp_issue_ids" "$tmp_issue_details" "$tmp_issue_map"
}

hours_for_day() {
  local day="$1"
  local user_filter="${2:-}"
  local start_iso="${day}T00:00:00Z"
  local end_iso="${day}T23:59:59Z"
  local start_ms
  start_ms=$(to_epoch_ms "$start_iso")
  local user_account=""
  if [[ -n "$user_filter" ]]; then
    user_account=$(find_account_id "$user_filter" || true)
  fi

  local tmp_ids tmp_logs tmp_filtered tmp_issue_ids tmp_issue_details tmp_issue_map
  tmp_ids=$(mktemp)
  tmp_logs=$(mktemp)
  tmp_filtered=$(mktemp)
  tmp_issue_ids=$(mktemp)
  tmp_issue_details=$(mktemp)
  tmp_issue_map=$(mktemp)

  fetch_worklog_ids "$start_ms" "$tmp_ids"
  if [[ ! -s "$tmp_ids" ]]; then
    echo "{\"date\":\"${day}\",\"users\":[]}"
    rm -f "$tmp_ids" "$tmp_logs" "$tmp_filtered" "$tmp_issue_ids" "$tmp_issue_details" "$tmp_issue_map"
    return 0
  fi

  fetch_worklogs "$tmp_ids" "$tmp_logs"
  python3 - "$start_iso" "$end_iso" "$user_filter" "$user_account" "$tmp_logs" >"$tmp_filtered" <<'PY'
import json, re, sys
from datetime import datetime

start_iso, end_iso, user_filter, account_filter, path = sys.argv[1:]
fix_tz = re.compile(r"([+-]\d{2})(\d{2})$")
start = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
end = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
aggregate = {}
user_filter = (user_filter or "").lower()
account_filter = account_filter or ""

with open(path) as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        log = json.loads(line)
        started = log.get("started")
        if not started:
            continue
        started_fixed = fix_tz.sub(r"\1:\2", started)
        try:
            ts = datetime.fromisoformat(started_fixed)
        except ValueError:
            continue
        if ts < start or ts > end:
            continue
        author = log.get("author") or {}
        email = author.get("emailAddress") or "unknown"
        display = author.get("displayName") or email
        account_id = author.get("accountId") or ""

        if user_filter or account_filter:
            matches_text = False
            if user_filter:
                email_l = email.lower()
                display_l = display.lower()
                if user_filter in email_l or user_filter in display_l:
                    matches_text = True
            matches_acct = account_filter and account_id == account_filter
            if not (matches_text or matches_acct):
                continue
        issue_id = str(log.get("issueId"))
        seconds = int(log.get("timeSpentSeconds") or 0)
        key = (email, issue_id)
        if key not in aggregate:
            aggregate[key] = {"email": email, "displayName": display, "issueId": issue_id, "seconds": 0}
        aggregate[key]["seconds"] += seconds

json.dump(list(aggregate.values()), sys.stdout)
PY

  if [[ ! -s "$tmp_filtered" || "$(cat "$tmp_filtered")" == "[]" ]]; then
    echo "{\"date\":\"${day}\",\"users\":[]}"
    rm -f "$tmp_ids" "$tmp_logs" "$tmp_filtered" "$tmp_issue_ids" "$tmp_issue_details" "$tmp_issue_map"
    return 0
  fi

  jq -r '.[].issueId' "$tmp_filtered" | sort -u >"$tmp_issue_ids"
  fetch_issue_details "$tmp_issue_ids" "$tmp_issue_details"
  jq -s 'map({(.id): {key, summary}}) | add' "$tmp_issue_details" >"$tmp_issue_map"

  local issue_map_json
  issue_map_json=$(cat "$tmp_issue_map")
  if [[ -z "$issue_map_json" ]]; then
    issue_map_json="{}"
  fi

  jq --argjson m "$issue_map_json" --arg day "$day" '
    {
      date: $day,
      users:
        (sort_by(.email) |
         group_by(.email) |
         map({
           email: .[0].email,
           displayName: .[0].displayName,
           issues:
             (map({issueId, seconds}) |
              sort_by(.issueId) |
              map({
                key: ($m[(.issueId|tostring)].key // (.issueId | tostring)),
                summary: ($m[(.issueId|tostring)].summary // "Unknown"),
                hours: ((.seconds / 3600 * 100) | round / 100)
              })),
           totalHours: ((map(.seconds) | add) / 3600 * 100 | round / 100)
         }) | sort_by(.totalHours) | reverse)
    }
  ' "$tmp_filtered"

  rm -f "$tmp_ids" "$tmp_logs" "$tmp_filtered" "$tmp_issue_ids" "$tmp_issue_details" "$tmp_issue_map"
}

cmd="${1:-help}"
shift || true

case "$cmd" in
  search)
    q="${1:-}"
    max="${2:-10}"
    if [[ -z "$q" ]]; then
      echo "Usage: jira.sh search \"query\" [maxResults]" >&2
      exit 1
    fi
    print_search "$q" "$max"
    ;;
  issue-link|link)
    issue="${1:-}"
    if [[ -z "$issue" ]]; then
      echo "Usage: jira.sh link ABC-123" >&2
      exit 1
    fi
    echo "${JIRA_URL}/browse/${issue}"
    ;;
  status)
    issue="${1:-}"
    status_to="${2:-}"
    if [[ -z "$issue" || -z "$status_to" ]]; then
      echo "Usage: jira.sh status ABC-123 \"In Progress\"" >&2
      exit 1
    fi
    transition_issue "$issue" "$status_to"
    ;;
  transitions)
    issue="${1:-}"
    if [[ -z "$issue" ]]; then
      echo "Usage: jira.sh transitions ABC-123" >&2
      exit 1
    fi
    list_transitions "$issue"
    ;;
  issue)
    issue="${1:-}"
    if [[ -z "$issue" ]]; then
      echo "Usage: jira.sh issue ABC-123" >&2
      exit 1
    fi
    issue_details "$issue"
    ;;
  assign)
    issue="${1:-}"
    user="${2:-}"
    if [[ -z "$issue" || -z "$user" ]]; then
      echo "Usage: jira.sh assign ABC-123 \"name or email\"" >&2
      exit 1
    fi
    assign_issue "$issue" "$user"
    ;;
  assign-me)
    issue="${1:-}"
    if [[ -z "$issue" ]]; then
      echo "Usage: jira.sh assign-me ABC-123" >&2
      exit 1
    fi
    assign_me "$issue"
    ;;
  comment)
    issue="${1:-}"
    text="${2:-}"
    if [[ -z "$issue" || -z "$text" ]]; then
      echo "Usage: jira.sh comment ABC-123 \"Comment text\"" >&2
      exit 1
    fi
    comment_issue "$issue" "$text"
    ;;
  create)
    summary="${1:-}"
    description="${2:-}"
    if [[ -z "$summary" ]]; then
      echo "Usage: jira.sh create \"Summary\" [\"Description\"]" >&2
      exit 1
    fi
    create_issue "$summary" "$description"
    ;;
  log|log-hours)
    issue="${1:-}"
    hours="${2:-}"
    day="${3:-}"
    if [[ -z "$issue" || -z "$hours" ]]; then
      echo "Usage: jira.sh log ABC-123 2.5 [YYYY-MM-DD]" >&2
      exit 1
    fi
    log_work "$issue" "$hours" "$day"
    ;;
  my|my-open)
    max="${1:-50}"
    print_my_open "$max"
    ;;
  hours)
    start="${1:-}"
    end="${2:-}"
    if [[ -z "$start" || -z "$end" ]]; then
      echo "Usage: jira.sh hours YYYY-MM-DD YYYY-MM-DD" >&2
      exit 1
    fi
    hours_by_issue "$start" "$end"
    ;;
  hours-day|day)
    day="${1:-}"
    user_filter="${2:-}"
    if [[ -z "$day" ]]; then
      echo "Usage: jira.sh hours-day YYYY-MM-DD [name|email]" >&2
      exit 1
    fi
    hours_for_day "$day" "$user_filter"
    ;;
  hours-issue|issue-hours|hours-task|task-hours)
    issue="${1:-}"
    user_filter="${2:-}"
    if [[ -z "$issue" ]]; then
      echo "Usage: jira.sh hours-issue ABC-123 [name|email]" >&2
      exit 1
    fi
    hours_for_issue "$issue" "$user_filter"
    ;;
  help|*)
    cat <<'EOF'
Jira CLI - worklogs and issues

Commands:
  search "query" [max]        Search by summary or key (project scoped)
  link <ABC-123>              Get browser link
  issue <ABC-123>             Issue details
  status <ABC-123> <status>   Move issue (To Do, In Progress, Done)
  transitions <ABC-123>       List available transitions
  assign <ABC-123> <user>     Assign issue by name/email lookup
  assign-me <ABC-123>         Assign issue to yourself
  comment <ABC-123> "text"    Add a comment
  create "Summary" ["Desc"]   Create Task in JIRA_BOARD
  log <ABC-123> <hours> [day] Log work (defaults to today UTC)
  my [max]                    Open issues assigned to you
  hours <start> <end>         Your logged hours by issue (JSON)
  hours-day <day> [user]      Logged hours for a day (JSON, optional name/email filter)
  hours-issue <ABC-123> [user] Logged hours for an issue (JSON, optional name/email filter)
EOF
    ;;
esac
