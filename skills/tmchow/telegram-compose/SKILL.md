---
name: telegram-compose
description: |
  Compose rich, readable Telegram messages using HTML formatting via direct Telegram API.
  Use when: (1) Sending any Telegram message beyond a simple one-line reply,
  (2) Creating structured messages with sections, lists, or status updates,
  (3) Need formatting unavailable via Clawdbot's Markdown conversion (underline, spoilers, expandable blockquotes, user mentions by ID),
  (4) Sending alerts, reports, summaries, or notifications to Telegram,
  (5) Want professional, scannable message formatting with visual hierarchy.
  Default to this skill for substantive Telegram communication.
---

# Telegram Compose

Rich, scannable Telegram messages via direct API with HTML formatting.

## Credentials

**Bot tokens:** Stored in Clawdbot config at `channels.telegram.accounts.<name>.botToken`

```bash
# Get token from config
BOT_TOKEN=$(jq -r '.channels.telegram.accounts.alerts.botToken' ~/.clawdbot/clawdbot.json)
# Or for main bot:
BOT_TOKEN=$(jq -r '.channels.telegram.accounts.main.botToken' ~/.clawdbot/clawdbot.json)
```

**Chat IDs:** See TOOLS.md → Telegram section for configured chat IDs.

---

## Direct API Call

```bash
# Get token and send
BOT_TOKEN=$(jq -r '.channels.telegram.accounts.alerts.botToken' ~/.clawdbot/clawdbot.json)
CHAT_ID="TARGET_CHAT_ID"  # See TOOLS.md

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg chat "$CHAT_ID" --arg text "$MESSAGE" '{
    chat_id: $chat,
    text: $text,
    parse_mode: "HTML"
  }')"
```

---

## HTML Tags

```
<b>bold</b>  <i>italic</i>  <u>underline</u>  <s>strike</s>
<code>mono</code>  <pre>code block</pre>
<tg-spoiler>hidden until tapped</tg-spoiler>
<blockquote>quote</blockquote>
<blockquote expandable>collapsed by default</blockquote>
<a href="url">link</a>
<a href="tg://user?id=123">mention by ID</a>
```

**Escape in text:** `<` → `&lt;`  `>` → `&gt;`  `&` → `&amp;`

---

## Structure Pattern

```
EMOJI <b>HEADING IN CAPS</b>

<b>Label:</b> Value
<b>Label:</b> Value

<b>SECTION</b>

• Bullet point
• Another point

<blockquote>Key quote or summary</blockquote>

<blockquote expandable><b>Details</b>

Hidden content here...
Long details go in expandable blocks.</blockquote>

<a href="https://...">Action Link →</a>
```

---

## Examples

**Status update:**
```
📋 <b>TASK COMPLETE</b>

<b>Task:</b> Deploy v2.3
<b>Status:</b> ✅ Done
<b>Duration:</b> 12 min

<blockquote>All health checks passing.</blockquote>
```

**Alert:**
```
⚠️ <b>ATTENTION NEEDED</b>

<b>Issue:</b> API rate limit at 90%
<b>Action:</b> Review usage

<a href="https://dashboard.example.com">View Dashboard →</a>
```

**List:**
```
✅ <b>PRIORITIES</b>

• <s>Review PR #234</s> — done
• <b>Finish docs</b> — in progress
• Deploy staging

<i>2 of 3 complete</i>
```

---

## Style Rules

1. **Faux headings:** `EMOJI <b>CAPS TITLE</b>` with blank line after
2. **Emojis:** 1-3 per message as visual anchors, not decoration
3. **Whitespace:** Blank lines between sections
4. **Long content:** Use `<blockquote expandable>` 
5. **Links:** Own line, with arrow: `Link Text →`

---

## Limits

- Message: 4,096 chars
- Caption: 1,024 chars

---

## When to Use Direct API vs Clawdbot

| Direct API | Clawdbot message tool |
|------------|----------------------|
| Structured messages | Quick acknowledgments |
| Status/alerts/reports | Simple replies |
| Need underline/spoiler/expandable | Basic formatting sufficient |
| Visual hierarchy matters | Throwaway messages |
