---
name: imsg-autoresponder
description: Monitor iMessage/SMS conversations and auto-respond based on configurable rules, AI prompts, and rate-limiting conditions. Use when you need to automatically reply to specific contacts with AI-generated responses based on conversation context. Also use when the user asks to manage auto-responder settings, contacts, prompts, or view status/history.
---

# iMessage Auto-Responder

Automatically respond to iMessages/SMS from specific contacts using AI-generated replies that match your voice and conversation context.

## ⚠️ Requirements Checklist

Before using this skill, ensure you have:

- [ ] **macOS** with Messages.app signed in to iMessage
- [ ] **imsg CLI** installed: `brew install steipete/tap/imsg`
- [ ] **OpenAI API key** configured in Clawdbot config
- [ ] **Full Disk Access** granted to Terminal/iTerm
- [ ] **Messages automation permission** (macOS will prompt on first use)

## Features

- 🤖 **AI-powered responses** using OpenAI GPT-4
- 📱 **Contact-based prompts** - different AI personality per contact
- ⏱️ **Rate limiting** - configurable delays between auto-responses
- 💬 **Context-aware** - AI sees recent conversation history
- 📊 **Telegram management** - slash commands + natural language
- 🔄 **Background monitoring** - continuous polling for new messages
- 🔧 **Auto-cleanup** - clears stale locks on restart (prevents stuck contacts)
- 🧪 **Test mode** - generate real AI responses without sending
- ⏰ **Time windows** - only respond during specific hours (e.g., 9 AM - 10 PM)
- 🔑 **Keyword triggers** - only respond if message contains specific keywords (e.g., "urgent", "help")
- 📊 **Statistics tracking** - track total responses, daily counts, and averages per contact
- 🚦 **Daily cap** - limit max replies per day per contact (safety feature)

## Quick Start

### 1. Add contacts to watch list

```bash
cd ~/clawd/imsg-autoresponder/scripts
node manage.js add "+15551234567" "Reply with a middle finger emoji" "Best Friend"
node manage.js add "+15559876543" "You are my helpful assistant. Reply warmly and briefly, as if I'm responding myself. Keep it under 160 characters." "Mom"
```

### 2. Start the watcher

```bash
node watcher.js
```

The watcher runs in the foreground and logs to `~/clawd/logs/imsg-autoresponder.log`.

### 3. Run in background (recommended)

```bash
# Start in background
nohup node ~/clawd/imsg-autoresponder/scripts/watcher.js > /dev/null 2>&1 &

# Or use screen/tmux
screen -S imsg-watcher
node ~/clawd/imsg-autoresponder/scripts/watcher.js
# Ctrl+A, D to detach
```

## Configuration

Config file: `~/clawd/imsg-autoresponder.json`

```json
{
  "enabled": true,
  "defaultMinMinutesBetweenReplies": 15,
  "watchList": [
    {
      "identifier": "+15551234567",
      "name": "Best Friend",
      "prompt": "Reply with a middle finger emoji",
      "minMinutesBetweenReplies": 10,
      "enabled": true
    }
  ]
}
```

## Management via Telegram (Recommended)

The auto-responder can be managed directly through Telegram using **slash commands** or **natural language**.

### Slash Commands

Both space and underscore formats are supported:

```
/autorespond list              OR  /autorespond_list
/autorespond status            OR  /autorespond_status
/autorespond add               OR  /autorespond_add <number> <name> <prompt>
/autorespond remove            OR  /autorespond_remove <number>
/autorespond edit              OR  /autorespond_edit <number> <prompt>
/autorespond delay             OR  /autorespond_delay <number> <minutes>
/autorespond history           OR  /autorespond_history <number>
/autorespond test              OR  /autorespond_test <number> <message>
/autorespond toggle            OR  /autorespond_toggle
/autorespond restart           OR  /autorespond_restart

Bulk Operations:
/autorespond set-all-delays    OR  /autorespond_set_all_delays <minutes>
/autorespond enable-all        OR  /autorespond_enable_all
/autorespond disable-all       OR  /autorespond_disable_all

Time Windows:
/autorespond set-time-window   OR  /autorespond_set_time_window <number> <start> <end>
/autorespond clear-time-windows OR  /autorespond_clear_time_windows <number>

Keyword Triggers:
/autorespond add-keyword       OR  /autorespond_add_keyword <number> <keyword>
/autorespond remove-keyword    OR  /autorespond_remove_keyword <number> <keyword>
/autorespond clear-keywords    OR  /autorespond_clear_keywords <number>

Statistics & Limits:
/autorespond stats             OR  /autorespond_stats [<number>]
/autorespond set-daily-cap     OR  /autorespond_set_daily_cap <number> <max>
```

**Examples:**
```
/autorespond_list
/autorespond_status
/autorespond_edit +15551234567 Be more sarcastic
/autorespond_delay +15551234567 30
/autorespond_history +15551234567
/autorespond_set_time_window +15551234567 09:00 22:00
/autorespond_clear_time_windows +15551234567
/autorespond_add_keyword +15551234567 urgent
/autorespond_add_keyword +15551234567 help
/autorespond_clear_keywords +15551234567
/autorespond_stats
/autorespond_stats +15551234567
/autorespond_set_daily_cap +15551234567 10
/autorespond_set_all_delays 30
/autorespond_disable_all
/autorespond_restart
```

### Natural Language

You can also just ask naturally:

- "Show me the auto-responder status"
- "Add +15551234567 to the watch list with prompt: be sarcastic"
- "Change Scott's prompt to be nicer"
- "Disable auto-replies for Mom"
- "What has the auto-responder sent to Foxy recently?"
- "Restart the auto-responder"

The agent will understand and execute the command using the `telegram-handler.js` script.

## Command-Line Management (Advanced)

```bash
cd ~/clawd/imsg-autoresponder/scripts

# List all contacts
node manage.js list

# Add contact
node manage.js add "+15551234567" "Your custom prompt here" "Optional Name"

# Remove contact
node manage.js remove "+15551234567"

# Enable/disable contact
node manage.js enable "+15551234567"
node manage.js disable "+15551234567"

# Set custom delay for contact (in minutes)
node manage.js set-delay "+15551234567" 30

# Toggle entire system on/off
node manage.js toggle
```

## How It Works

1. **Watcher** monitors all incoming messages via `imsg watch`
2. **Checks watch list** to see if sender is configured for auto-response
3. **Rate limiting** ensures we don't spam (configurable minutes between replies)
4. **Fetches message history** for the conversation (last 20 messages)
5. **Generates AI response** using Clawdbot + the contact's configured prompt
6. **Sends reply** via `imsg send`
7. **Logs everything** to `~/clawd/logs/imsg-autoresponder.log`

## State Tracking

Response times are tracked in `~/clawd/data/imsg-autoresponder-state.json`:

```json
{
  "lastResponses": {
    "+15551234567": 1706453280000
  }
}
```

This ensures rate limiting works correctly across restarts.

## Prompts

Prompts define how the AI should respond to each contact. Be specific!

**Examples:**

```
"Reply with a middle finger emoji"

"You are my helpful assistant. Reply warmly and briefly, as if I'm responding myself. Keep it under 160 characters."

"You are my sarcastic friend. Reply with witty, slightly snarky responses. Keep it short."

"Politely decline any requests and say I'm busy. Be brief but friendly."
```

The AI will see:
- The contact's custom prompt
- Recent message history (last 5 messages)
- The latest incoming message

## Requirements

- macOS with Messages.app signed in
- `imsg` CLI installed (`brew install steipete/tap/imsg`)
- Full Disk Access for Terminal
- Clawdbot installed and configured
- Anthropic API key (configured in `~/.clawdbot/clawdbot.json` or `ANTHROPIC_API_KEY` env var)
- `curl` (pre-installed on macOS)

## Safety

- **Rate limiting** prevents spam (default: 15 minutes between replies per contact)
- **Manual override** via `enabled: false` in config or `node manage.js disable <number>`
- **System toggle** to disable all auto-responses: `node manage.js toggle`
- **Logs** track all activity for review

## Troubleshooting

**Watcher not responding:**
- Check `~/clawd/logs/imsg-autoresponder.log` for errors
- Verify `imsg watch` works manually: `imsg watch --json`
- Ensure contact is in watch list: `node manage.js list`

**Rate limited too aggressively:**
- Adjust delay: `node manage.js set-delay "+15551234567" 5`
- Or edit `defaultMinMinutesBetweenReplies` in config

**AI responses are off:**
- Refine the prompt for that contact
- Check message history is being captured correctly (see logs)

## Agent Command Handling

When the user uses slash commands or natural language about the auto-responder, use the `telegram-handler.js` script.

### Command Mapping (Both Formats Supported)

| User Input | Normalize To | Handler Call |
|------------|--------------|--------------|
| `/autorespond list` or `/autorespond_list` | list | `node telegram-handler.js list` |
| `/autorespond status` or `/autorespond_status` | status | `node telegram-handler.js status` |
| `/autorespond add` or `/autorespond_add <args>` | add | `node telegram-handler.js add <number> <name> <prompt>` |
| `/autorespond remove` or `/autorespond_remove <num>` | remove | `node telegram-handler.js remove <number>` |
| `/autorespond edit` or `/autorespond_edit <args>` | edit | `node telegram-handler.js edit <number> <prompt>` |
| `/autorespond delay` or `/autorespond_delay <args>` | delay | `node telegram-handler.js delay <number> <minutes>` |
| `/autorespond history` or `/autorespond_history <num>` | history | `node telegram-handler.js history <number> [limit]` |
| `/autorespond test` or `/autorespond_test <num> <msg>` | test | `node telegram-handler.js test <number> <message>` |
| `/autorespond toggle` or `/autorespond_toggle` | toggle | `node telegram-handler.js toggle` |
| `/autorespond restart` or `/autorespond_restart` | restart | `node telegram-handler.js restart` |
| `/autorespond set-all-delays` or `/autorespond_set_all_delays <min>` | set-all-delays | `node telegram-handler.js set-all-delays <minutes>` |
| `/autorespond enable-all` or `/autorespond_enable_all` | enable-all | `node telegram-handler.js enable-all` |
| `/autorespond disable-all` or `/autorespond_disable_all` | disable-all | `node telegram-handler.js disable-all` |
| `/autorespond set-time-window` or `/autorespond_set_time_window <num> <s> <e>` | set-time-window | `node telegram-handler.js set-time-window <number> <start> <end>` |
| `/autorespond clear-time-windows` or `/autorespond_clear_time_windows <num>` | clear-time-windows | `node telegram-handler.js clear-time-windows <number>` |
| `/autorespond add-keyword` or `/autorespond_add_keyword <num> <word>` | add-keyword | `node telegram-handler.js add-keyword <number> <keyword>` |
| `/autorespond remove-keyword` or `/autorespond_remove_keyword <num> <word>` | remove-keyword | `node telegram-handler.js remove-keyword <number> <keyword>` |
| `/autorespond clear-keywords` or `/autorespond_clear_keywords <num>` | clear-keywords | `node telegram-handler.js clear-keywords <number>` |
| `/autorespond stats` or `/autorespond_stats [<num>]` | stats | `node telegram-handler.js stats [<number>]` |
| `/autorespond set-daily-cap` or `/autorespond_set_daily_cap <num> <max>` | set-daily-cap | `node telegram-handler.js set-daily-cap <number> <max>` |

**Processing steps:**
1. Detect `/autorespond` or `/autorespond_` prefix
2. Extract subcommand (normalize underscores to spaces)
3. Parse remaining arguments
4. Call telegram-handler.js with appropriate parameters

### Natural Language Pattern Matching

- "show/list/view auto-responder" → `node telegram-handler.js list`
- "add [contact] to auto-responder" → `node telegram-handler.js add <number> <name> <prompt>`
- "change/edit/update [contact]'s prompt" → `node telegram-handler.js edit <number> <prompt>`
- "set delay for [contact]" → `node telegram-handler.js delay <number> <minutes>`
- "disable/remove [contact] from auto-responder" → `node telegram-handler.js remove <number>`
- "auto-responder status" → `node telegram-handler.js status`
- "what has auto-responder sent to [contact]" → `node telegram-handler.js history <number>`
- "restart auto-responder" → `node telegram-handler.js restart`
- "enable/disable auto-responder" → `node telegram-handler.js toggle`

**Contact resolution:**
- When user refers to contact names, look up their phone number from the config
- Always use the full E.164 format (e.g., `+15551234567`)

**After config changes:**
Always remind the user to restart the watcher if the command output mentions it.

## Troubleshooting

### Watcher Not Responding

**Check status:**
```
/autorespond_status
```

**View logs:**
```bash
tail -f ~/clawd/logs/imsg-autoresponder.log
```

**Restart:**
```
/autorespond_restart
```

### Common Issues

**"OPENAI_API_KEY not found"**
- Add API key to `~/.clawdbot/clawdbot.json`:
  ```json
  {
    "skills": {
      "openai-whisper-api": {
        "apiKey": "sk-proj-YOUR_KEY_HERE"
      }
    }
  }
  ```
- Restart watcher after adding key

**Permission errors**
- Grant Full Disk Access to Terminal in System Settings
- Restart Terminal after granting access
- Verify `imsg chats --json` works manually

**Messages not detected**
- Check Messages.app is signed in
- Verify contact is in watch list: `/autorespond_list`
- Ensure watcher is running: `/autorespond_status`

**Duplicate responses**
- Fixed in current version via processing locks
- Restart watcher to apply fix: `/autorespond_restart`

### Testing

Generate actual AI responses without sending (preview mode):
```
/autorespond_test +15551234567 Hey what's up?
```

This will:
- Use the contact's actual prompt
- Generate a real AI response via OpenAI
- Show exactly what would be sent
- **NOT actually send** the message

Perfect for testing new prompts before going live!

## Privacy & Safety

⚠️ **Important:** This tool sends messages on your behalf automatically.

- Only add contacts who know they're texting an AI or won't mind
- Review responses regularly via `/autorespond_history`
- Use rate limiting to avoid spam
- Be transparent when appropriate
- Disable instantly if needed: `/autorespond_toggle`

## Future Enhancements

- Smart rate limiting based on conversation patterns
- Group chat support
- Web dashboard
- Voice message transcription
