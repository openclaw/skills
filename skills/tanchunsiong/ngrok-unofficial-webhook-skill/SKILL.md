---
name: ngrok-unofficial-webhook-skill
description: Start an ngrok tunnel to receive incoming webhooks and process them via the LLM. Use when the user asks to listen for webhooks, set up a webhook endpoint, start ngrok, or when another skill (like Zoom RTMS Meeting Assistant) needs a public webhook URL. Receives webhook payloads and lets the LLM decide how to handle them.
---

# Ngrok Webhook Listener

Start a public webhook endpoint via ngrok. Incoming webhooks are output as JSON lines — read them and decide what to do (e.g. forward to another skill like the Zoom RTMS Meeting Assistant).

## Prerequisites

```bash
cd skills/ngrok-unofficial-webhook-skill
npm install
```

## Environment Variables

Set `NGROK_AUTHTOKEN` in the skill's `.env` file (copy from `.env.example`).

**Required:**
- `NGROK_AUTHTOKEN` — ngrok auth token from https://dashboard.ngrok.com

**Optional:**
- `NGROK_DOMAIN` — stable ngrok domain for consistent URLs
- `WEBHOOK_PORT` — local port (default: `4040`)
- `WEBHOOK_PATH` — webhook path (default: `/webhook`)
- `CLAWDBOT_NOTIFY_CHANNEL` — notification channel (default: `whatsapp`)
- `CLAWDBOT_NOTIFY_TARGET` — phone number / target for notifications

## Usage

### Start the webhook listener

Run as a **background process**:

```bash
cd skills/ngrok-unofficial-webhook-skill
node scripts/webhook-server.js
```

The server prints its public URL to stderr:
```
NGROK_URL=https://xxxx.ngrok-free.app
Webhook endpoint: https://xxxx.ngrok-free.app/webhook
```

Capture the `NGROK_URL` from stderr output to configure external services.

### What happens when a webhook arrives

1. The server immediately responds **200 OK** to the sender
2. It discovers installed skills that declare `webhookEvents` in their `skill.json`
3. It sends a WhatsApp notification to the user with:
   - The event type and payload
   - A numbered list of matching skills (skills whose `webhookEvents` include this event type)
   - Other webhook-capable skills
   - An option to ignore
4. The user replies with their choice

### Skill discovery

Skills opt into webhook handling by adding `webhookEvents` to their `skill.json`:

```json
{
  "clawdbot": {
    "webhookEvents": ["meeting.rtms_started", "meeting.rtms_stopped"]
  }
}
```

The ngrok skill scans all sibling skill folders for `skill.json` files with this field.

### Stdout output

The server also writes each webhook as a JSON line to **stdout** for process polling:

```json
{
  "id": "uuid",
  "timestamp": "ISO-8601",
  "method": "POST",
  "path": "/webhook",
  "query": {},
  "body": {}
}
```

### Health check

```bash
curl http://localhost:4040/health
```

### Stop the listener

Kill the background process when done.

## Integration with Zoom RTMS

Typical flow:
1. Start this webhook listener → get ngrok URL
2. Configure the ngrok URL in your Zoom Marketplace app's webhook settings
3. When a meeting starts, Zoom sends `meeting.rtms_started` to the webhook
4. Read the event, then start the RTMS Meeting Assistant with the payload
