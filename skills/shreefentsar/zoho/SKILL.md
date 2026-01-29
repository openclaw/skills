---
name: zoho
description: Interact with Zoho CRM, Projects, and Meeting APIs. Use when managing deals, contacts, leads, tasks, projects, milestones, meeting recordings, or any Zoho workspace data. Triggers on mentions of Zoho, CRM, deals, pipeline, projects, tasks, milestones, meetings, recordings, standups.
author: Zone 99 team
homepage: https://99.zone
repository: https://github.com/shreefentsar/clawdbot-zoho
---

# Zoho Integration (CRM + Projects + Meeting)

Made by [Zone 99](https://99.zone) · [GitHub](https://github.com/shreefentsar/clawdbot-zoho) · [Contribute](https://github.com/shreefentsar/clawdbot-zoho/issues)

## Quick Start

Use the `zoho` CLI wrapper — it handles OAuth token refresh and caching automatically.

```bash
zoho help          # Show all commands
zoho token         # Print current access token (auto-refreshes)
```

## Authentication Setup

### Step 1: Register Your Application

1. Go to [Zoho API Console](https://api-console.zoho.com/)
2. Click **Add Client** → choose **Server-based Applications**
3. Fill in:
   - **Client Name**: your app name (e.g. "Clawdbot Zoho Integration")
   - **Homepage URL**: your domain or `https://localhost`
   - **Redirect URI**: `https://localhost/callback` (or any URL you control — you only need it once to grab the code)
4. Click **Create**
5. Note down the **Client ID** and **Client Secret**

### Step 2: Generate Authorization Code (Grant Token)

Build this URL and open it in your browser (replace the placeholders):

```
https://accounts.zoho.com/oauth/v2/auth
  ?response_type=code
  &client_id=YOUR_CLIENT_ID
  &scope=ZohoCRM.modules.ALL,ZohoCRM.settings.ALL,ZohoProjects.projects.ALL,ZohoProjects.tasks.ALL,ZohoMeeting.recording.READ,ZohoMeeting.meeting.READ,ZohoMeeting.meetinguds.READ,ZohoFiles.files.READ
  &redirect_uri=https://localhost/callback
  &access_type=offline
  &prompt=consent
```

> **Important:** Use the accounts URL matching your datacenter:
> | Region | Accounts URL |
> |--------|-------------|
> | US | `https://accounts.zoho.com` |
> | EU | `https://accounts.zoho.eu` |
> | IN | `https://accounts.zoho.in` |
> | AU | `https://accounts.zoho.com.au` |
> | JP | `https://accounts.zoho.jp` |
> | UK | `https://accounts.zoho.uk` |
> | CA | `https://accounts.zohocloud.ca` |
> | SA | `https://accounts.zoho.sa` |

After granting access, you'll be redirected to something like:
```
https://localhost/callback?code=1000.abc123...&location=us&accounts-server=https://accounts.zoho.com
```

Copy the `code` parameter value. **This code expires in 2 minutes** — move to Step 3 immediately.

### Step 3: Exchange Code for Refresh Token

Run this curl command (replace placeholders):

```bash
curl -X POST "https://accounts.zoho.com/oauth/v2/token" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "grant_type=authorization_code" \
  -d "redirect_uri=https://localhost/callback" \
  -d "code=PASTE_CODE_FROM_STEP_2"
```

Response:
```json
{
  "access_token": "1000.xxxx.yyyy",
  "refresh_token": "1000.xxxx.zzzz",
  "api_domain": "https://www.zohoapis.com",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

Save the **refresh_token** — this is your long-lived credential. The access token expires in 1 hour, but the CLI auto-refreshes it using the refresh token.

### Step 4: Find Your Org IDs

**CRM/Projects Org ID:**
```bash
# After setting up .env with client_id, client_secret, refresh_token:
zoho raw GET /crm/v7/org | jq '.org[0].id'
```

**Meeting Org ID:**
Log into [Zoho Meeting](https://meeting.zoho.com) → Admin Settings → look for the Organization ID in the URL or settings page. It's different from the CRM org ID.

### Step 5: Configure .env

Create `.env` in the skill directory:

```bash
ZOHO_CLIENT_ID=1000.XXXXXXXXXXXXXXXXXXXXXXXXX
ZOHO_CLIENT_SECRET=your_client_secret_here
ZOHO_REFRESH_TOKEN=1000.your_refresh_token_here
ZOHO_ORG_ID=123456789              # CRM/Projects org ID
ZOHO_MEETING_ORG_ID=987654321      # Meeting org ID (different from CRM)
ZOHO_CRM_DOMAIN=https://www.zohoapis.com
ZOHO_PROJECTS_DOMAIN=https://projectsapi.zoho.com/restapi
ZOHO_MEETING_DOMAIN=https://meeting.zoho.com
ZOHO_ACCOUNTS_URL=https://accounts.zoho.com
```

> Adjust the domain URLs if you're on a non-US datacenter (e.g. `.eu`, `.in`, `.com.au`).

### OAuth Scopes Reference

| Scope | Used For |
|-------|----------|
| `ZohoCRM.modules.ALL` | Read/write CRM records (Deals, Contacts, Leads, etc.) |
| `ZohoCRM.settings.ALL` | Read CRM field definitions and org settings |
| `ZohoProjects.projects.ALL` | Read/write projects |
| `ZohoProjects.tasks.ALL` | Read/write tasks, milestones, bugs, timelogs |
| `ZohoMeeting.recording.READ` | List and access meeting recordings |
| `ZohoMeeting.meeting.READ` | List meetings and session details |
| `ZohoMeeting.meetinguds.READ` | Download recording files |
| `ZohoFiles.files.READ` | Download files (recordings, transcripts) |

You can request fewer scopes if you only need CRM or only need Meeting. The authorization URL scope parameter is comma-separated.

### Troubleshooting Auth

- **"invalid_code"** → The authorization code expired (2 min lifetime). Redo Step 2.
- **"invalid_client"** → Wrong Client ID, or wrong accounts-server URL for your datacenter.
- **"invalid_redirect_uri"** → The redirect_uri in the curl must exactly match what you registered in API Console.
- **Token refresh fails** → Refresh tokens can be revoked. Redo Steps 2–3 to get a new one.
- **"Given URL is wrong"** → You're hitting the wrong API domain for your datacenter.

## CRM Commands

```bash
# List records from any module
zoho crm list Deals
zoho crm list Deals "page=1&per_page=5&sort_by=Created_Time&sort_order=desc"
zoho crm list Contacts
zoho crm list Leads

# Get a specific record
zoho crm get Deals 1234567890

# Search with criteria
zoho crm search Deals "(Stage:equals:Closed Won)"
zoho crm search Contacts "(Email:contains:@acme.com)"
zoho crm search Leads "(Lead_Source:equals:Web)"

# Create a record
zoho crm create Contacts '{"data":[{"Last_Name":"Smith","First_Name":"John","Email":"j@co.com"}]}'
zoho crm create Deals '{"data":[{"Deal_Name":"New Project","Stage":"Qualification","Amount":50000}]}'

# Update a record
zoho crm update Deals 1234567890 '{"data":[{"Stage":"Closed Won"}]}'

# Delete a record
zoho crm delete Deals 1234567890
```

### CRM Modules
Leads, Contacts, Accounts, Deals, Tasks, Events, Calls, Notes, Products, Quotes, Sales_Orders, Purchase_Orders, Invoices

### Search Operators
equals, not_equal, starts_with, contains, not_contains, in, not_in, between, greater_than, less_than

## Projects Commands

```bash
# List all projects
zoho proj list

# Get project details
zoho proj get 12345678

# Tasks
zoho proj tasks 12345678
zoho proj create-task 12345678 "name=Fix+login+bug&priority=High&start_date=01-27-2026"
zoho proj update-task 12345678 98765432 "percent_complete=50"

# Other
zoho proj milestones 12345678
zoho proj tasklists 12345678
zoho proj bugs 12345678
zoho proj timelogs 12345678
```

### Task Fields
name, start_date (MM-DD-YYYY), end_date, priority (None/Low/Medium/High), owner, description, tasklist_id, percent_complete

## Meeting Commands

```bash
# List all recordings
zoho meeting recordings
zoho meeting recordings | jq '[.recordings[] | {topic, sDate, sTime, durationInMins, erecordingId}]'

# Download a recording (use downloadUrl from recordings list)
zoho meeting download "https://files-accl.zohopublic.com/public?event-id=..." output.mp4

# List meetings/sessions
zoho meeting list
zoho meeting list "fromDate=2026-01-01T00:00:00Z&toDate=2026-01-31T23:59:59Z"

# Get meeting details
zoho meeting get 1066944216
```

### Recording Response Fields
Key fields from `zoho meeting recordings`:
- `erecordingId` — encrypted recording ID (use for dedup/tracking)
- `topic` — meeting title
- `sDate`, `sTime` — start date/time (human-readable)
- `startTimeinMs` — start time as epoch ms (use for date filtering)
- `durationInMins` — recording duration
- `downloadUrl` / `publicDownloadUrl` — MP4 download URL
- `transcriptionDownloadUrl` — Zoho-generated transcript (if available)
- `summaryDownloadUrl` — Zoho-generated summary (if available)
- `fileSize` / `fileSizeInMB` — recording file size
- `status` — e.g. `UPLOADED`
- `meetingKey` — meeting identifier
- `creatorName` — who started the recording

### Meeting Recording Pipeline
For automated standup/meeting summarization:

```bash
# 1. List recordings, filter by today's date (epoch ms)
zoho meeting recordings | jq --argjson start "$START_MS" --argjson end "$END_MS" \
  '[.recordings[] | select(.startTimeinMs >= $start and .startTimeinMs <= $end)]'

# 2. Download recording
zoho meeting download "$DOWNLOAD_URL" /tmp/recording.mp4

# 3. Extract audio
ffmpeg -i /tmp/recording.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 /tmp/audio.wav -y

# 4. Transcribe via Gemini Flash API (great for Arabic + English mix)
# See scripts/standup-summarizer.sh for full implementation

# 5. Summarize transcript with Claude/GPT
# 6. Clean up temp files
```

A complete standup summarizer script is included at `scripts/standup-summarizer.sh`.

## Raw API Calls

For anything not covered by subcommands:
```bash
# CRM endpoints
zoho raw GET /crm/v7/settings/fields?module=Deals
zoho raw GET /crm/v7/org

# Meeting endpoints
zoho raw GET "https://meeting.zoho.com/meeting/api/v2/{zsoid}/recordings.json"

# Custom modules
zoho raw GET /crm/v7/Custom_Module
```

## Usage Patterns

### When checking deals/pipeline
```bash
zoho crm list Deals "sort_by=Created_Time&sort_order=desc&per_page=10" | jq '.data[] | {Deal_Name, Stage, Amount, Closing_Date}'
```

### When checking project progress
```bash
zoho proj list | jq '.projects[] | {name, status, id: .id_string}'
zoho proj tasks <project_id> | jq '.tasks[] | {name, status: .status.name, percent_complete, priority}'
```

### When creating tasks from conversation
```bash
zoho proj create-task <project_id> "name=Task+description&priority=High&start_date=MM-DD-YYYY&end_date=MM-DD-YYYY"
```

### When summarizing meeting recordings
```bash
# Quick list of recent recordings
zoho meeting recordings | jq '[.recordings[:5] | .[] | {topic, sDate, sTime, durationInMins, fileSize}]'

# Download latest recording
URL=$(zoho meeting recordings | jq -r '.recordings[0].downloadUrl')
zoho meeting download "$URL" /tmp/latest.mp4
```

## Rate Limits
- CRM: 100 requests/min
- Projects: varies by plan
- Meeting: standard API limits
- Token refresh: don't call more than needed (cached automatically)

## References
- [CRM API Fields](references/crm-api.md)
- [Projects API Endpoints](references/projects-api.md)
- [Meeting API Reference](references/meeting-api.md)
