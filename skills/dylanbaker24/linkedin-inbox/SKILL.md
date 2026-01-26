---
name: linkedin-inbox
description: LinkedIn inbox management with scheduled scanning, auto-draft responses following user's communication style, and approval workflows. Use when monitoring LinkedIn messages, drafting replies, managing inbox during off-hours, or setting up morning ping summaries of LinkedIn activity.
---

# LinkedIn Inbox Manager

Automated LinkedIn inbox monitoring with human-in-the-loop approval for responses. Uses Peekaboo for UI automation (no API rate limits, works with any LinkedIn account).

## Requirements

- macOS with Peekaboo CLI installed (`brew install steipete/tap/peekaboo`)
- Screen Recording + Accessibility permissions granted
- LinkedIn logged in via browser (Chrome recommended)
- Clawdbot with browser capability

## Quick Start

### 1. One-time Setup
```bash
# Grant Peekaboo permissions
peekaboo permissions

# Verify LinkedIn is accessible
peekaboo app launch "Google Chrome"
peekaboo see --app "Google Chrome" --annotate --path /tmp/linkedin-check.png
```

### 2. Configure User Style
Create `linkedin-inbox-config.json` in your workspace:
```json
{
  "scan": {
    "intervalMinutes": 60,
    "activeHours": { "start": 9, "end": 18, "timezone": "America/Los_Angeles" },
    "skipWeekends": true
  },
  "drafting": {
    "styleProfile": "USER.md",
    "templates": {
      "decline": "Thanks for reaching out. Not a fit for us right now, but best of luck.",
      "interested": "This looks interesting. Happy to chat more. What's your availability?",
      "referral": "I might know someone. Let me check and get back to you."
    }
  },
  "notifications": {
    "channel": "discord",
    "target": "#linkedin"
  }
}
```

### 3. Start Monitoring
Tell your agent: "Start LinkedIn inbox monitoring" or add to HEARTBEAT.md:
```markdown
- Check LinkedIn inbox if last scan >1 hour ago
```

## Core Workflow

### Scan Inbox
```bash
# Navigate to LinkedIn messaging
peekaboo app launch "Google Chrome"
peekaboo menu click --app "Google Chrome" --item "New Tab"
peekaboo type "https://www.linkedin.com/messaging/" --return
sleep 3

# Capture inbox state
peekaboo see --app "Google Chrome" --window-title "Messaging" --annotate --path /tmp/linkedin-inbox.png
```

The agent reads the annotated screenshot to identify:
- Unread messages (bold names, blue dots)
- Message previews
- Sender names and titles

### Draft Responses
For each unread message:
1. Agent reads the conversation
2. Classifies intent (pitch, networking, job inquiry, spam)
3. Drafts response matching user's communication style
4. Posts draft to notification channel for approval

Example notification:
```
💼 LinkedIn: New message from **Alex M.** (Founder @ SomeCompany)

Preview: "Hi, I noticed you're growing and wondered if..."

**My read:** Services pitch. Doesn't fit current needs.

**Draft reply:**
> Thanks for reaching out. We're set on that side for now, but I'll keep you in mind if that changes.

React ✅ to send, ❌ to skip, or reply with edits.
```

### Send Approved Messages
On approval:
```bash
# Click into conversation
peekaboo click --on [message-element-id] --app "Google Chrome"
sleep 1

# Type response
peekaboo type "Your approved message here" --app "Google Chrome"

# Send (Enter or click Send button)
peekaboo press return --app "Google Chrome"
```

## Communication Style Matching

The skill reads `USER.md` (or configured style file) to match the user's tone:

**Extract these signals:**
- Formality level (casual vs professional)
- Typical greeting style
- Sign-off patterns
- Sentence length preference
- Banned words/phrases
- Response length norms

**Apply to drafts:**
- Mirror detected patterns
- Use user's vocabulary
- Match their directness level
- Respect their guardrails (no "excited", no hype, etc.)

See `references/style-extraction.md` for detailed guidance.

## Morning Ping Integration

Add LinkedIn summary to your morning ping:
```markdown
📣 The Morning Ping — Monday, Jan 27

**LinkedIn:**
• 💚 Sarah Chen replied — "That sounds great, let's do Thursday" → Draft ready
• 💚 Mike R. replied — "Not interested right now" → No action needed
• 📩 3 new connection requests (2 sales pitches, 1 relevant)
• 📩 1 unread message from Alex (job inquiry) → Draft ready

Reply "send sarah" to approve, "skip mike" to archive.
```

## Approval Commands

Users can respond with:
- `send [name]` - Send the drafted reply
- `send all` - Send all pending drafts
- `skip [name]` - Archive without replying
- `edit [name]: [new message]` - Replace draft and send
- `show [name]` - Show full conversation

## Scheduled Scanning

### Via Cron (Recommended)
```json
{
  "schedule": "0 */2 9-18 * * 1-5",
  "text": "Scan LinkedIn inbox and post any new messages to #linkedin with draft replies"
}
```

### Via Heartbeat
In HEARTBEAT.md:
```markdown
- If 9am-6pm PT and last LinkedIn scan >60min: scan inbox, draft replies, post to #linkedin
```

## Safety Rules

1. **Never send without explicit approval** - Always wait for user confirmation
2. **Rate limit actions** - Max 20 LinkedIn actions per hour
3. **Respect quiet hours** - Don't scan outside configured activeHours
4. **Log everything** - Record all actions in daily memory file
5. **Preserve originals** - Never delete messages, only archive

## Troubleshooting

### "Can't find messaging UI"
- Ensure Chrome is open with LinkedIn logged in
- Check window title matches (may vary by language)
- Use `peekaboo list windows --app "Google Chrome" --json` to debug

### "Session expired"
- LinkedIn sessions expire periodically
- Re-authenticate manually in browser
- Skill will detect login page and notify user

### "Peekaboo permissions denied"
```bash
peekaboo permissions  # Check status
# Grant via System Preferences > Privacy & Security > Screen Recording + Accessibility
```

## Files

- `scripts/scan_inbox.sh` - Peekaboo commands for inbox capture
- `scripts/send_message.sh` - Peekaboo commands for sending
- `references/style-extraction.md` - Guide for communication style matching
