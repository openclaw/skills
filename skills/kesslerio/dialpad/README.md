# Dialpad Moltbot Skill

Send SMS text messages and make voice calls via the Dialpad API with support for TTS, caller ID selection, and message storage.

## Features

- **Send SMS** - Single or batch SMS messages (up to 10 recipients)
- **Voice Calls** - Outbound voice calls with optional Text-to-Speech
- **Caller ID Selection** - Choose which Dialpad phone number appears as caller ID
- **Message Storage** - SQLite database with full-text search for SMS history
- **Webhooks** - Real-time SMS event notifications
- **Multiple Voices** - Use Dialpad's TTS or premium ElevenLabs voices

## Installation

```bash
# Clone the repository
git clone https://github.com/kesslerio/dialpad-moltbot-skill.git
cd dialpad-moltbot-skill
```

## Configuration

### Required

Set your Dialpad API key:

```bash
export DIALPAD_API_KEY="your-api-key-here"
```

Or add to `~/.moltbot/.env` or `~/.clawdbot/.env`:

```
DIALPAD_API_KEY=your-api-key-here
```

Get your API key from: https://dialpad.com/api/settings

### Optional

For premium voice quality using ElevenLabs TTS:

```bash
export ELEVENLABS_API_KEY="your-elevenlabs-key"
```

## Usage

### Send SMS

```bash
# Basic SMS
python3 send_sms.py --to "+14155551234" --message "Hello from Dialpad!"

# Batch SMS (multiple recipients)
python3 send_sms.py --to "+14155551234" "+14155555678" --message "Group message"

# From specific caller ID
python3 send_sms.py --to "+14155551234" --message "Hello!" --from "+14159901234"
```

### Make Voice Calls

```bash
# Basic outbound call
python3 make_call.py --to "+14155551234"

# Call with TTS greeting
python3 make_call.py --to "+14155551234" --text "Hello! This is a message."

# Call from specific number with TTS
python3 make_call.py --to "+14155551234" --from "+14159901234" --text "Meeting reminder"

# With premium voice (requires ELEVENLABS_API_KEY)
python3 make_call.py --to "+14155551234" --voice "Adam" --text "Premium voice test"
```

## Available Voices

### Dialpad Built-in (Low Cost)

| Voice | Type | Notes |
|-------|------|-------|
| Eric | Male, smooth | Recommended for budget |
| Daniel | Male, British | Professional |
| Sarah | Female, mature | Clear |
| River | Male, neutral | Friendly |
| Alice | Female, clear | Accessible |
| Brian | Male, deep | Authoritative |
| Bill | Male, wise | Experienced |

### ElevenLabs Premium (Higher Quality)

| Voice | Type | Notes |
|-------|------|-------|
| Adam | Male, deep | Best for professional calls |
| Antoni | Male, warm | Friendly tone |
| Bella | Female, soft | Warm, engaging |

Use premium voices by setting `ELEVENLABS_API_KEY` and specifying `--voice "VoiceName"`.

## SMS Storage & History

Messages are stored in SQLite with full-text search capabilities.

### List Conversations

```bash
python3 sms_sqlite.py list
```

### View Specific Thread

```bash
python3 sms_sqlite.py thread "+14155551234"
```

### Full-Text Search

```bash
python3 sms_sqlite.py search "urgent"
```

### Unread Messages

```bash
python3 sms_sqlite.py unread
```

### Statistics

```bash
python3 sms_sqlite.py stats
```

### Mark as Read

```bash
python3 sms_sqlite.py read "+14155551234"
```

## Webhook Integration

Receive SMS events in real-time:

```bash
# Create webhook subscription
python3 create_sms_webhook.py create --url "https://your-server.com/webhook/dialpad" --direction "all"

# List subscriptions
python3 create_sms_webhook.py list
```

Webhook events:
- `sms_sent` - Outgoing SMS
- `sms_received` - Incoming SMS

## Export SMS History

Export past messages as CSV:

```bash
# Export all SMS
python3 export_sms.py --output all_sms.csv

# Export by date range
python3 export_sms.py --start-date 2026-01-01 --end-date 2026-01-31 --output jan_sms.csv
```

## Integration with Moltbot

Add to your Moltbot configuration:

```json
{
  "skills": [
    {
      "name": "dialpad",
      "path": "/path/to/dialpad-moltbot-skill",
      "env": {
        "DIALPAD_API_KEY": "${DIALPAD_API_KEY}"
      }
    }
  ]
}
```

Then reference in workflows:
- "Send a text to..."
- "Call..."
- "What SMS did I get?"
- "Search my messages for..."

## API Reference

### SMS Endpoint

- **URL:** `POST https://dialpad.com/api/v2/sms`
- **Max recipients:** 10 per request
- **Max message length:** 1600 characters
- **Rate limits:** 100-800 requests/minute (varies by plan)

### Voice Call Endpoint

- **URL:** `POST https://dialpad.com/api/v2/call`
- **Requires:** Phone number + User ID
- **Features:** Outbound calling, TTS, Caller ID

### Response Examples

**SMS Response:**
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

**Call Response:**
```json
{
  "call_id": "6342343299702784",
  "status": "ringing"
}
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `invalid_destination` | Invalid phone number | Verify E.164 format (e.g., +14155551234) |
| `invalid_source` | Caller ID not available | Ensure number is assigned to your account |
| `no_route` | Cannot deliver | Check recipient carrier and number validity |
| `unauthorized` | Invalid API key | Verify `DIALPAD_API_KEY` is set correctly |

## Requirements

- Python 3.7+
- No external dependencies (uses Python stdlib)
- Valid Dialpad API key
- For premium voices: ElevenLabs API key

## Project Structure

```
dialpad-moltbot-skill/
├── send_sms.py           # Send SMS messages
├── make_call.py          # Make voice calls
├── sms_sqlite.py         # SQLite storage and search
├── webhook_sqlite.py     # Handle incoming webhooks
├── create_sms_webhook.py # Manage webhook subscriptions
├── export_sms.py         # Export SMS history
├── SKILL.md              # Moltbot manifest
├── README.md             # This file
└── LICENSE               # MIT License
```

## Troubleshooting

### SMS Not Sending

- Verify `DIALPAD_API_KEY` is set: `echo $DIALPAD_API_KEY`
- Check phone number format (must be E.164: +1 country code + number)
- Verify caller ID (--from) is assigned to your Dialpad account

### Calls Not Connecting

- Ensure phone number includes country code
- Verify the Dialpad account has outbound calling enabled
- Check API rate limits haven't been exceeded

### Voice Quality Issues

- Switch to ElevenLabs voices for better quality: `--voice "Adam"`
- Ensure `ELEVENLABS_API_KEY` is set
- Try different voices to find the best fit

### SMS Not Storing

- Check SQLite database permissions at `~/.dialpad/sms.db`
- Run migrate to convert from legacy storage: `python3 sms_sqlite.py migrate`

## License

MIT

## Support

- Dialpad Developer Docs: https://developers.dialpad.com/
- Dialpad API Settings: https://dialpad.com/api/settings
- ElevenLabs Docs: https://elevenlabs.io/docs
- Moltbot: https://moltbot.io/
