#!/usr/bin/env bash
# Daily Review Script
# Usage: ./daily-review.sh [YYYY-MM-DD]

set -e

DATE="${1:-$(date +%Y-%m-%d)}"
DATE_NEXT=$(date -d "$DATE + 1 day" +%Y-%m-%d 2>/dev/null || date -v+1d -j -f "%Y-%m-%d" "$DATE" +%Y-%m-%d)

echo "🏆 Daily Performance Review - $DATE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ============ COMMUNICATION ============
echo "📬 COMMUNICATION"

# Emails sent (using Google Workspace skill)
EMAILS=$(cd ~/clawd/skills/google-workspace && node scripts/gmail.js list henry@curacel.ai "after:${DATE//-/\\/} before:${DATE_NEXT//-/\\/} from:me" 2>/dev/null | jq 'length' || echo "?")
echo "  • Emails sent: $EMAILS"

# Slack messages
SLACK_TOKEN=$(cat ~/clawd/secrets/slack-super-ada.json 2>/dev/null | jq -r '.user_token')
SLACK_MSGS=$(curl -s "https://slack.com/api/search.messages" \
  -H "Authorization: Bearer $SLACK_TOKEN" \
  -G --data-urlencode "query=from:<@U0LGU88M8> on:$DATE" \
  --data-urlencode "count=1" 2>/dev/null | jq '.messages.total // 0')
echo "  • Slack messages: $SLACK_MSGS"

# X.com interactions (via bird on Mac)
XCOM=$(ssh -o ConnectTimeout=10 henrymascot@100.86.150.96 "
export PATH=/opt/homebrew/bin:\$PATH
export AUTH_TOKEN='f7aafc8dd93e2f1afc6a0877b2cfc61100ff105a'
export CT0='d3381f602aaf90275500ffd0fda4038d0583e22c7ea5dd4c64091c184b2125329aac54672c511ddeb2cfe74d1d73ac0825f4f187f4782ad8b3fc66a72a077751bd66d8969c26a29132f80ea618de2757'
cd ~/Code/bird
node dist/cli.js mentions -n 50 2>/dev/null | grep -c '@' || echo 0
" 2>/dev/null || echo "?")
echo "  • X.com mentions: $XCOM"

echo ""

# ============ MEETINGS ============
echo "📅 MEETINGS (Fireflies - speaker verified)"

FIREFLIES_KEY=$(cat ~/clawd/secrets/fireflies.key 2>/dev/null)
MEETINGS=$(curl -s -X POST "https://api.fireflies.ai/graphql" \
  -H "Authorization: Bearer $FIREFLIES_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ transcripts(limit: 30) { title dateString duration sentences { speaker_name } } }"}' 2>/dev/null | jq -r "
[.data.transcripts[] | 
  select(.dateString | startswith(\"$DATE\")) |
  select([.sentences[]?.speaker_name // \"\"] | map(ascii_downcase) | any(contains(\"henry\"))) |
  {title: (.title | gsub(\"Meet – \"; \"\")), duration: (.duration | floor)}
] | unique_by(.title)")

echo "$MEETINGS" | jq -r '.[] | "  • \(.title) (\(.duration) min)"' 2>/dev/null || echo "  • No meetings found"

TOTAL_MINS=$(echo "$MEETINGS" | jq '[.[].duration] | add // 0' 2>/dev/null)
TOTAL_HRS=$(echo "scale=1; $TOTAL_MINS / 60" | bc 2>/dev/null || echo "?")
MEETING_COUNT=$(echo "$MEETINGS" | jq 'length' 2>/dev/null)
echo "  Total: $MEETING_COUNT meetings (~$TOTAL_HRS hrs)"

echo ""

# ============ OUTPUT ============
echo "💻 OUTPUT"

# Git commits
GIT_COMMITS=$(cd ~/clawd && git log --oneline --since="$DATE 00:00" --until="$DATE_NEXT 00:00" 2>/dev/null | wc -l | tr -d ' ')
echo "  • Git commits (clawd): $GIT_COMMITS"

# Google Docs edited (using Google Workspace skill)
DOCS=$(cd ~/clawd/skills/google-workspace && node scripts/drive.js list henry@curacel.ai "modifiedTime>='${DATE}T00:00:00'" 2>/dev/null | jq 'length' || echo "?")
echo "  • Docs modified: $DOCS"

# Ada messages (from session)
ADA_MSGS=$(grep -c "Him (@henrino3)" ~/.clawdbot/agents/main/sessions/*.jsonl 2>/dev/null | tail -1 | cut -d: -f2 || echo "?")
echo "  • Messages to Ada: $ADA_MSGS"

echo ""

# ============ FOCUS TIME ============
echo "⏱️ FOCUS TIME"

# ActivityWatch (from Mac)
AW_DATA=$(ssh -o ConnectTimeout=10 henrymascot@100.86.150.96 "
curl -s 'http://localhost:5600/api/0/buckets/aw-watcher-window_MascotM3/events?limit=500' 2>/dev/null | python3 -c '
import json, sys
from collections import defaultdict

data = json.load(sys.stdin)
apps = defaultdict(float)

for event in data:
    app = event.get(\"data\", {}).get(\"app\", \"unknown\")
    duration = event.get(\"duration\", 0)
    apps[app] += duration

sorted_apps = sorted(apps.items(), key=lambda x: x[1], reverse=True)[:5]
total = sum(apps.values())

print(f\"ActivityWatch: {total/3600:.1f} hrs\")
for app, dur in sorted_apps:
    mins = dur / 60
    print(f\"  {app}: {mins:.0f}min\")
' 2>/dev/null
" 2>/dev/null)

if [[ -n "$AW_DATA" ]]; then
  echo "$AW_DATA"
else
  echo "  ActivityWatch: ⚠️ Not running"
fi

# Screen Time (query Mac knowledgeC.db directly - no waiting!)
SCREEN_TIME_DATA=$(ssh -o ConnectTimeout=10 henrymascot@100.86.150.96 "python3 ~/get_screentime.py $DATE" 2>/dev/null)

if [[ -n "$SCREEN_TIME_DATA" && "$SCREEN_TIME_DATA" != "No data found" ]]; then
  echo "⏱️ FOCUS TIME"
  echo "$SCREEN_TIME_DATA" | head -1
  echo "$SCREEN_TIME_DATA" | tail -n +3 | head -8 | sed 's/^/  /'
else
  echo "⏱️ FOCUS TIME: No data available"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Generated: $(date)"
