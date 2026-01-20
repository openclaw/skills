# 📱 Channel Support Guide

> Complete documentation for Smart Follow-ups across all Clawdbot channels

---

## Overview

Smart Follow-ups works on **every Clawdbot channel**, with adaptive formatting:

| Channel | Mode | Format | Interaction |
|---------|------|--------|-------------|
| **Telegram** | Interactive | Inline buttons | Tap to ask |
| **Discord** | Interactive | Inline buttons | Click to ask |
| **Slack** | Interactive | Inline buttons | Click to ask |
| **Signal** | Text | Numbered list | Reply with 1-3 |
| **WhatsApp** | Text | Numbered list | Reply with 1-3 |
| **iMessage** | Text | Numbered list | Reply with 1-3 |
| **SMS** | Text | Numbered list | Reply with 1-3 |
| **Matrix** | Text | Numbered list | Reply with 1-3 |
| **Email** | Text | Numbered list | Reply with number |

---

## Interactive Mode (Buttons)

### Telegram

**Best experience** — full inline button support with callbacks.

```
💡 What would you like to explore next?

[⚡ How do I install Docker?        ] ← tap
[🧠 Explain Docker's architecture   ] ← tap
[🔗 Compare Docker to Kubernetes    ] ← tap
```

**Requirements:**
- `capabilities: ["inlineButtons"]` in channel config
- Bot must have inline button permissions

**Callback handling:**
When user taps a button, the question is sent as a new message automatically.

---

### Discord

Full button component support.

```
💡 What would you like to explore next?

[⚡ How do I install Docker?]
[🧠 Explain Docker's architecture]
[🔗 Compare Docker to Kubernetes]
```

**Requirements:**
- Bot must have `Send Messages` and `Use Buttons` permissions
- Application commands enabled

---

### Slack

Block Kit button support.

```
💡 What would you like to explore next?

[⚡ How do I install Docker?]
[🧠 Explain Docker's architecture]  
[🔗 Compare Docker to Kubernetes]
```

**Requirements:**
- Slack app with `chat:write` scope
- Interactive components enabled

---

## Text Mode (Fallback)

For channels without button support, a numbered list is displayed:

### Signal

```
💡 Smart Follow-up Suggestions

⚡ Quick
1. How do I install Docker?

🧠 Deep Dive
2. Explain Docker's architecture

🔗 Related
3. Compare Docker to Kubernetes

Reply with 1, 2, or 3 to ask that question.
```

**How to use:** Simply reply with the number (1, 2, or 3).

---

### WhatsApp

```
💡 Smart Follow-up Suggestions

⚡ Quick
1. How do I install Docker?

🧠 Deep Dive
2. Explain Docker's architecture

🔗 Related
3. Compare Docker to Kubernetes

Reply 1, 2, or 3
```

**How to use:** Reply with the number.

**Note:** WhatsApp has limited button support for business accounts. The skill uses text mode for reliability.

---

### iMessage

```
💡 Smart Follow-up Suggestions

⚡ Quick
1. How do I install Docker?

🧠 Deep Dive
2. Explain Docker's architecture

🔗 Related
3. Compare Docker to Kubernetes

Reply with 1, 2, or 3
```

**How to use:** Reply with the number.

---

### SMS

```
Smart Follow-ups

1. How do I install Docker?
2. Explain Docker's architecture
3. Compare Docker to Kubernetes

Reply 1, 2, or 3
```

**Note:** Simplified formatting for SMS character limits. Emojis may be stripped depending on carrier.

---

### Matrix

```
💡 Smart Follow-up Suggestions

⚡ Quick
1. How do I install Docker?

🧠 Deep Dive
2. Explain Docker's architecture

🔗 Related
3. Compare Docker to Kubernetes

Reply with 1, 2, or 3
```

---

### Email

```
Subject: Re: Your conversation

💡 Smart Follow-up Suggestions

⚡ Quick
1. How do I install Docker?

🧠 Deep Dive
2. Explain Docker's architecture

🔗 Related
3. Compare Docker to Kubernetes

Reply with the number of your choice (1, 2, or 3).
```

---

## Channel Detection Logic

The handler automatically detects the channel and formats appropriately:

```javascript
// Channels with button support
const BUTTON_CHANNELS = ['telegram', 'discord', 'slack'];

// Check channel capability
function supportsButtons(channel, capabilities) {
  return BUTTON_CHANNELS.includes(channel) && 
         capabilities?.includes('inlineButtons');
}
```

**Priority:**
1. Check if channel is in `BUTTON_CHANNELS` list
2. Verify `inlineButtons` capability is enabled
3. Fall back to text mode if either check fails

---

## Configuration Per Channel

You can override settings per channel in `clawdbot.json`:

```json
{
  "skills": {
    "smart-followups": {
      "channels": {
        "telegram": {
          "mode": "buttons",
          "showCategory": true
        },
        "signal": {
          "mode": "text",
          "compact": false
        },
        "sms": {
          "mode": "text",
          "compact": true,
          "stripEmoji": true
        }
      }
    }
  }
}
```

| Option | Default | Description |
|--------|---------|-------------|
| `mode` | auto | `buttons`, `text`, or `auto` |
| `compact` | false | Use compact formatting |
| `showCategory` | true | Show category labels (⚡🧠🔗) |
| `stripEmoji` | false | Remove emojis (for SMS) |

---

## Reply Handling

### Button Channels

When a user clicks a button:
1. Button sends `callback_data` containing the question
2. Clawdbot receives it as a new user message
3. Clawdbot answers the question normally

### Text Channels

When a user replies with a number:
1. Clawdbot receives "1", "2", or "3"
2. Handler maps number to the corresponding question
3. Clawdbot processes as if user typed the full question

**Implementation Note:** The handler stores recent suggestions in session context to map numbers back to questions.

---

## Troubleshooting

### Buttons not appearing on Telegram

1. Check channel config has `capabilities: ["inlineButtons"]`
2. Verify bot has inline button permissions
3. Try restarting Clawdbot

### Numbers not working on Signal

1. Make sure you're replying with just the number (1, 2, or 3)
2. Don't include other text
3. Check Clawdbot logs for errors

### Wrong formatting on WhatsApp

WhatsApp formatting is limited. If buttons don't work:
1. Check if you have a WhatsApp Business account
2. The skill defaults to text mode for reliability

### Emojis broken on SMS

Some carriers strip emojis. Enable `stripEmoji: true` in SMS channel config:

```json
{
  "skills": {
    "smart-followups": {
      "channels": {
        "sms": {
          "stripEmoji": true
        }
      }
    }
  }
}
```

---

## Adding New Channels

To add support for a new channel:

1. **Check button support** — Does the platform support interactive buttons?
2. **Add to handler** — Update `BUTTON_CHANNELS` array if supported
3. **Test formatting** — Verify text/button output looks correct
4. **Document** — Add section to this file

Pull requests welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Channel Feature Matrix

| Feature | Telegram | Discord | Slack | Signal | WhatsApp | iMessage | SMS |
|---------|:--------:|:-------:|:-----:|:------:|:--------:|:--------:|:---:|
| Inline buttons | ✅ | ✅ | ✅ | ❌ | ⚠️ | ❌ | ❌ |
| Emoji support | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Markdown | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Number replies | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Rich formatting | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | ❌ |

**Legend:** ✅ Full support | ⚠️ Partial/limited | ❌ Not supported

---

**Last updated:** January 20, 2026
