# Zoho Skill for Clawdbot

Talk to your Zoho workspace like a human. CRM deals, project tasks, meeting recordings — all through natural conversation with your AI agent.

No more tab-switching between Zoho CRM, Projects, and Meeting. Just ask.

## What it does

This skill gives your Clawdbot agent direct access to three Zoho products:

**CRM** — Search, create, and update deals, contacts, leads, and any other module. Your agent reads your pipeline and acts on it.

**Projects** — List projects, create tasks, track milestones, log time. Your agent becomes your project manager's best friend.

**Meeting** — Pull recording lists, download MP4s, and feed them into transcription pipelines. The included standup summarizer script handles the full loop: download → transcribe (Gemini Flash) → summarize.

## Real use cases

- "What deals closed this month?" → Agent queries CRM, gives you a summary
- "Create a task in Project X: fix the login bug, high priority, due Friday" → Done
- "Summarize today's standup recording" → Downloads from Zoho Meeting, transcribes via Gemini, gives you bullet points
- "Show me all leads from web signups" → Searches CRM with the right filters
- "How's Project Alpha going?" → Pulls task completion stats, flags overdue items
- "Log 2 hours on the API integration task" → Posts a timelog entry

## What's included

```
zoho/
├── SKILL.md              # Agent instructions (how to use the CLI)
├── bin/zoho              # CLI wrapper — handles OAuth, token refresh, caching
├── scripts/
│   └── standup-summarizer.sh   # Full meeting recording → summary pipeline
└── references/
    ├── crm-api.md        # CRM field definitions
    ├── projects-api.md   # Projects endpoint reference
    └── meeting-api.md    # Meeting API reference
```

## Quick start

### 1. Install via ClawdHub

```bash
clawdhub install zoho
```

### 2. Register a Zoho API app

Go to [Zoho API Console](https://api-console.zoho.com/) → Add Client → Server-based Application.

Set the redirect URI to `https://localhost/callback`.

### 3. Get your refresh token

The SKILL.md has step-by-step instructions for the OAuth flow. It takes about 3 minutes — you generate an auth code, exchange it for a refresh token, and you're set. The CLI handles token refresh automatically after that.

### 4. Configure `.env`

Create a `.env` file in the skill directory:

```bash
ZOHO_CLIENT_ID=1000.XXXXX
ZOHO_CLIENT_SECRET=your_secret
ZOHO_REFRESH_TOKEN=1000.your_refresh_token
ZOHO_ORG_ID=123456789
ZOHO_MEETING_ORG_ID=987654321
ZOHO_CRM_DOMAIN=https://www.zohoapis.com
ZOHO_PROJECTS_DOMAIN=https://projectsapi.zoho.com/restapi
ZOHO_MEETING_DOMAIN=https://meeting.zoho.com
ZOHO_ACCOUNTS_URL=https://accounts.zoho.com
```

Adjust domains for your datacenter (EU, IN, AU, etc.). See SKILL.md for the full region table.

## CLI usage

The `zoho` CLI works standalone too — you don't need Clawdbot to use it.

```bash
zoho help                          # All commands
zoho crm list Deals                # List CRM deals
zoho crm search Deals "(Stage:equals:Qualification)"
zoho crm create Contacts '{"data":[{"Last_Name":"Smith","Email":"j@co.com"}]}'
zoho proj list                     # List projects
zoho proj tasks <project-id>       # List tasks
zoho meeting recordings            # List meeting recordings
zoho raw GET /crm/v7/org           # Raw API calls
```

## Standup summarizer

The included `standup-summarizer.sh` automates daily meeting summaries:

1. Pulls today's recordings from Zoho Meeting
2. Downloads the MP4
3. Extracts audio and transcribes via Gemini Flash API (handles Arabic + English mix)
4. Outputs a structured summary

```bash
./scripts/standup-summarizer.sh                    # Today's recordings
./scripts/standup-summarizer.sh --date 2026-01-28  # Specific date
```

Works great as a cron job for automated daily standups.

## Supported Zoho regions

US, EU, IN, AU, JP, UK, CA, SA — just swap the domain URLs in your `.env`.

## Rate limits

- CRM: 100 requests/min
- Projects: varies by plan
- Meeting: standard API limits
- Token refresh is cached — no wasted calls

## Contributing

Found a bug? Want to add Zoho Books, Desk, or another product? PRs welcome.

1. Fork the repo
2. Create a feature branch
3. Submit a PR with a clear description

Open an issue if you're unsure about something — happy to discuss before you write code.

GitHub: [github.com/shreefentsar/clawdbot-zoho](https://github.com/shreefentsar/clawdbot-zoho)

## License

MIT

---

Made by the **Zone 99** team · [99.zone](https://99.zone)
