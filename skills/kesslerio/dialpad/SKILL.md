---
name: dialpad
description: Send SMS and make voice calls via Dialpad API. Supports single/batch SMS, voice calls with TTS, and caller ID selection.
homepage: https://developers.dialpad.com/
---

# Dialpad Skill

Send SMS and make voice calls via the Dialpad API.

## Available Phone Numbers

| Number | Purpose | Format |
|--------|---------|--------|
| (415) 520-1316 | Sales Team | Default for sales context |
| (415) 360-2954 | Work/Personal | Default for work context |
| (415) 991-7155 | Support SMS Only | SMS only (no voice) |

Use `--from <number>` to specify which number appears as caller ID.

## Setup

**Required environment variable:**
```
DIALPAD_API_KEY=your_api_key_here
```

**Optional (for ElevenLabs TTS in calls):**
```
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

Get your Dialpad API key from [Dialpad API Settings](https://dialpad.com/api/settings).

## Usage

### Send SMS

```bash
# Basic SMS
python3 send_sms.py --to "+14155551234" --message "Hello from Clawdbot!"

# From specific number (e.g., work phone)
python3 send_sms.py --to "+14155551234" --message "Hello!" --from "+14153602954"

# Batch SMS (up to 10 recipients)
python3 send_sms.py --to "+14155551234" "+14155555678" --message "Group update"
```

### Make Voice Calls

```bash
# Basic call (ring recipient - they'll answer to speak with you)
python3 make_call.py --to "+14155551234"

# Call with Text-to-Speech greeting (Dialpad's robotic TTS)
python3 make_call.py --to "+14155551234" --text "Hello! This is a call from ShapeScale."

# Call from specific number with TTS
python3 make_call.py --to "+14155551234" --from "+14153602954" --text "Meeting reminder"

# With custom voice (requires ELEVENLABS_API_KEY)
python3 make_call.py --to "+14155551234" --voice "Adam" --text "Premium voice test"
```

### From Agent Instructions

**SMS:**
```bash
python3 send_sms.py --to "+14155551234" --message "Your message here"
```

**Voice Call:**
```bash
python3 make_call.py --to "+14155551234" --text "Optional TTS message"
```

## Voice Options

### Low-Cost Voices (Recommended for Budget)
| Voice | Style | Notes |
|-------|-------|-------|
| **Eric** ⭐ | Male, smooth, trustworthy | Low-cost, available! |
| Daniel | Male, British, steady | Budget |
| Sarah | Female, mature | Budget |
| River | Male, neutral | Budget |
| Alice | Female, clear | Budget |
| Brian | Male, deep | Budget |
| Bill | Male, wise | Budget |

### Premium Voices (Higher Quality)
| Voice | Style | Notes |
|-------|-------|-------|
| **Adam** | Male, deep, clear | Best for professional |
| Antoni | Male, warm | Friendly tone |
| Bella | Female, soft | Warm, engaging |

To use a specific voice, add `--voice "VoiceName"`.

## API Capabilities

### SMS
- **Endpoint:** `POST https://dialpad.com/api/v2/sms`
- **Max recipients:** 10 per request
- **Max message length:** 1600 characters
- **Rate limits:** 100-800 requests/minute (tier-dependent)

### Voice Calls
- **Endpoint:** `POST https://dialpad.com/api/v2/call`
- **Requires:** `phone_number` + `user_id`
- **Features:** Outbound calling, Text-to-Speech
- **Caller ID:** Must be assigned to your Dialpad account

### Known Users (Auto-Detected)
| Name | Phone | User ID |
|------|-------|---------|
| Martin | (415) 360-2954 | `5765607478525952` |
| Lilla | (415) 870-1945 | `5625110025338880` |
| Scott | (415) 223-0323 | `5964143916400640` |

## Response

### SMS Response
```json
{
  "id": "4612924117884928",
  "status": "pending",
  "message_delivery_result": "pending",
  "to_numbers": ["+14158235304"],
  "from_number": "+14155201316",
  "direction": "outbound"
}
```

### Call Response
```json
{
  "call_id": "6342343299702784",
  "status": "ringing"
}
```

## Error Handling

| Error | Meaning | Action |
|-------|---------|--------|
| `invalid_destination` | Invalid phone number | Verify E.164 format |
| `invalid_source` | Caller ID not available | Check `--from` number assignment |
| `no_route` | Cannot deliver | Check carrier/recipient |
| `user_id required` | Missing user ID | Use `--from` with known number |

## SMS Storage (SQLite with FTS5)

Messages are stored in a single SQLite database with full-text search.

### Storage

```
~/.dialpad/sms.db  # Single file with messages + FTS5 index
```

### Commands

```bash
# List all SMS conversations
python3 sms_sqlite.py list

# View specific conversation thread
python3 sms_sqlite.py thread "+14155551234"

# Full-text search across all messages
python3 sms_sqlite.py search "demo"

# Show unread message summary
python3 sms_sqlite.py unread

# Statistics
python3 sms_sqlite.py stats

# Mark messages as read
python3 sms_sqlite.py read "+14155551234"

# Migrate from legacy storage
python3 sms_sqlite.py migrate
```

### Features

- **Full-text search** via FTS5 (`search "keyword"`)
- **Fast queries** with indexes on contact, timestamp, direction
- **ACID transactions** — no corruption on concurrent writes
- **Unread tracking** with per-contact counts
- **Denormalized contact stats** for instant list views

### Webhook Integration

```python
from webhook_sqlite import handle_sms_webhook, format_notification, get_inbox_summary

# Store incoming message
result = handle_sms_webhook(dialpad_payload)
notification = format_notification(result)

# Get inbox summary
summary = get_inbox_summary()
```

### Legacy JSON Storage (Deprecated)

The original JSON-based storage is still available but not recommended:

```bash
python3 sms_storage.py [list|thread|search|unread]
```

## Requirements

- Python 3.7+
- No external dependencies (uses stdlib only)
- Valid `DIALPAD_API_KEY` environment variable
- For ElevenLabs TTS: `ELEVENLABS_API_KEY` + webhook setup for audio playback

## Reading SMS Messages

Dialpad doesn't provide a direct "GET /sms" endpoint. Instead, use:

### 1. Real-Time: SMS Webhooks

Receive SMS events in real-time when messages are sent/received.

```bash
# Create a webhook subscription
python3 create_sms_webhook.py create --url "https://your-server.com/webhook/dialpad" --direction "all"

# List existing subscriptions
python3 create_sms_webhook.py list
```

**Webhook Events:**
- `sms_sent` — Outgoing SMS
- `sms_received` — Incoming SMS

**Note:** Add `message_content_export` scope to receive message text in events.

### 2. Historical: Stats Export API

Export past SMS messages as CSV.

```bash
# Export all SMS
python3 export_sms.py --output all_sms.csv

# Export by date range
python3 export_sms.py --start-date 2026-01-01 --end-date 2026-01-31 --output jan_sms.csv

# Export for specific office
python3 export_sms.py --office-id 6194013244489728 --output office_sms.csv
```

**Output:** CSV file with columns:
- `date` — Timestamp
- `from_number` — Sender
- `to_number` — Recipient
- `text` — Message content
- `status` — Delivery status

## Architecture

```
Dialpad SMS Skill
├── send_sms.py           # Send SMS (working)
├── make_call.py          # Make voice calls (working)
├── create_sms_webhook.py # Create webhook subscriptions (new)
├── export_sms.py         # Export historical SMS (new)
├── sms_sqlite.py         # SQLite storage with FTS5 (RECOMMENDED)
├── webhook_sqlite.py     # Webhook handler for SQLite
├── sms_storage.py        # Legacy JSON storage (deprecated)
└── webhook_receiver.py   # Legacy webhook handler
```
