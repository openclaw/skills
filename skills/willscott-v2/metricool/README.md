# Metricool Skill for Moltbot

Schedule and manage social media posts via [Metricool](https://metricool.com) API.

## Platforms Supported

- LinkedIn
- X (Twitter)
- Bluesky
- Threads
- Instagram
- Facebook

## Installation

Copy the `metricool` folder to your Moltbot skills directory, or download `metricool.skill` from releases.

## Setup

1. Get your API token from Metricool dashboard
2. Add credentials to `~/.moltbot/moltbot.json`:

```json
{
  "env": {
    "vars": {
      "METRICOOL_USER_TOKEN": "your-api-token",
      "METRICOOL_USER_ID": "your@email.com"
    }
  }
}
```

Or add to your workspace `.env` file.

## Scripts

| Script | Purpose |
|--------|---------|
| `get-brands.js` | List connected accounts/brands |
| `schedule-post.js` | Schedule posts to multiple platforms |
| `list-scheduled.js` | View queued posts |
| `best-time.js` | Get optimal posting times |

## Usage Examples

```bash
# List your brands
node scripts/get-brands.js

# Schedule a post
node scripts/schedule-post.js '{
  "platforms": ["linkedin", "x", "bluesky"],
  "text": "Hello world!",
  "datetime": "2026-01-30T09:00:00",
  "timezone": "America/New_York"
}'

# Check scheduled posts
node scripts/list-scheduled.js --start 2026-01-30 --end 2026-02-05
```

## License

MIT
