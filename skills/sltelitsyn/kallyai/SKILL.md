---
name: kallyai
description: Make phone calls via KallyAI API - an AI phone assistant that calls businesses on your behalf. Use when users want to make restaurant reservations, schedule appointments, or inquire at businesses by phone.
metadata: {"clawdbot":{"emoji":"📞","requires":{"bins":["kallyai"]},"install":[{"id":"pip","kind":"pip","package":"kallyai-cli","bins":["kallyai"],"label":"Install via pip"}]}}
---

# KallyAI API Integration

KallyAI is an AI phone assistant that makes calls to businesses on behalf of users.

## Complete Workflow

When a user asks to make a call:

### Step 1: Gather Call Details

Collect from user:
- **Phone number** to call (required)
- **What to accomplish** - the task description (required)
- **Category**: restaurant, clinic, hotel, or general (required)
- For reservations: name, date, time, party size

### Step 2: Authenticate User

Use the CLI OAuth flow:
```
https://api.kallyai.com/v1/auth/cli?redirect_uri=http://localhost:8976/callback
```

This opens a login page. After authentication, the user is redirected to the localhost callback with tokens:
```
http://localhost:8976/callback?access_token=<token>&refresh_token=<refresh>&expires_in=3600
```

Start a local HTTP server to capture the callback and extract the tokens.

### Step 3: Make the Call

Once authenticated, call the API:

```
POST https://api.kallyai.com/v1/calls
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "submission": {
    "task_category": "general",
    "task_description": "Ask about store hours and availability",
    "respondent_phone": "+15551234567",
    "language": "en",
    "call_language": "en"
  },
  "timezone": "America/New_York"
}
```

### Step 4: Report Results

Response contains:
```json
{
  "call_id": "uuid",
  "status": "success",
  "highlights": "They have iPhone 15 for €800, good condition",
  "next_steps": "Call back to arrange pickup"
}
```

**Status values:** `success`, `no_answer`, `busy`, `failed`, `voicemail`, `cancelled`

---

## CLI Commands Reference

### Making Calls

```bash
kallyai -p "+15551234567" -t "Reserve a table for 4 at 8pm" \
  --category restaurant \
  --name "John Smith" \
  --party-size 4 \
  --date "2026-01-28" \
  --time "20:00"
```

| Option | Short | Description |
|--------|-------|-------------|
| `--phone` | `-p` | Phone number (E.164 format) |
| `--task` | `-t` | What the AI should accomplish |
| `--category` | `-c` | restaurant, clinic, hotel, general |
| `--language` | `-l` | en or es |
| `--name` | | Your name (for reservations) |
| `--business` | | Business name |
| `--party-size` | | Party size (restaurants) |
| `--date` | | YYYY-MM-DD |
| `--time` | | HH:MM (24-hour) |

### Account & Usage

```bash
kallyai --usage        # Show minutes/calls remaining
kallyai --subscription # Show subscription status
kallyai --billing      # Open Stripe billing portal
```

### Call History

```bash
kallyai --history              # List recent calls
kallyai --call-info <ID>       # Get call details
kallyai --transcript <ID>      # Get conversation transcript
```

### Authentication

```bash
kallyai --login      # Force re-authentication
kallyai --logout     # Clear saved credentials
kallyai --auth-status # Check if logged in
```

---

## Quick Reference

**Base URL:** `https://api.kallyai.com`

**CLI OAuth URL:** `https://api.kallyai.com/v1/auth/cli?redirect_uri=http://localhost:8976/callback`

**Required fields for calls:**
| Field | Description |
|-------|-------------|
| `task_category` | `restaurant`, `clinic`, `hotel`, `general` |
| `task_description` | What AI should accomplish |
| `respondent_phone` | Phone number in E.164 format (+1234567890) |

**Optional fields:**
| Field | Description |
|-------|-------------|
| `business_name` | Name of business |
| `user_name` | Name for reservation |
| `appointment_date` | YYYY-MM-DD |
| `appointment_time` | HH:MM (24-hour) |
| `party_size` | Number of people (1-50) |
| `language` | `en` or `es` |
| `call_language` | `en` or `es` |

## Example Requests

**Restaurant reservation:**
```json
{
  "submission": {
    "task_category": "restaurant",
    "task_description": "Reserve table for 4 at 8pm",
    "respondent_phone": "+14155551234",
    "business_name": "Italian Bistro",
    "user_name": "John Smith",
    "party_size": 4,
    "appointment_date": "2026-01-28",
    "appointment_time": "20:00"
  },
  "timezone": "America/New_York"
}
```

**Medical appointment:**
```json
{
  "submission": {
    "task_category": "clinic",
    "task_description": "Schedule dental checkup",
    "respondent_phone": "+14155551234",
    "user_name": "Jane Doe",
    "time_preference_text": "morning before 11am"
  },
  "timezone": "America/New_York"
}
```

## Common Errors

| Code | HTTP | Action |
|------|------|--------|
| `quota_exceeded` | 402 | User needs to upgrade at kallyai.com/pricing |
| `missing_phone_number` | 422 | Ask user for phone number |
| `emergency_number` | 422 | Cannot call 911/emergency services |
| `country_restriction` | 403 | Country not supported |

## Security

- **Token storage**: `~/.kallyai_token.json` with 0600 permissions
- **CSRF protection**: State parameter validation
- **Localhost only**: OAuth redirects only to localhost/127.0.0.1
- **Auto-refresh**: Tokens refresh automatically when expired
