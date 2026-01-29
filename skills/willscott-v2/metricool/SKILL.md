---
name: metricool
description: Schedule and manage social media posts via Metricool API. Use when posting to multiple platforms (LinkedIn, X, Bluesky, Threads, Instagram), checking scheduled posts, or analyzing social metrics.
---

# Metricool Integration

Schedule posts to multiple social platforms through Metricool's API.

## Setup

Get your Metricool API token from the Metricool dashboard.

Add environment variables in `~/.moltbot/moltbot.json`:
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

Or in your workspace `.env`:
```
METRICOOL_USER_TOKEN=your-api-token
METRICOOL_USER_ID=your@email.com
```

## Scripts

### Get Brands

List connected brands and their blog IDs:

```bash
node skills/metricool/scripts/get-brands.js
node skills/metricool/scripts/get-brands.js --json
```

### Schedule a Post

```bash
node skills/metricool/scripts/schedule-post.js '{
  "platforms": ["linkedin", "x", "bluesky", "threads", "instagram"],
  "text": "Your post text here",
  "datetime": "2026-01-30T09:00:00",
  "timezone": "America/New_York",
  "blogId": "YOUR_BLOG_ID"
}'
```

**Parameters:**
- `platforms`: Array — linkedin, x, bluesky, threads, instagram, facebook
- `text`: String or object with per-platform text (see below)
- `datetime`: ISO datetime for scheduling
- `timezone`: Timezone (default: America/Chicago)
- `imageUrl`: Optional publicly accessible image URL
- `blogId`: Brand ID from get-brands.js

**Per-platform text:**
```json
{
  "text": {
    "linkedin": "Full LinkedIn post with more detail...",
    "x": "Short X post under 280 chars",
    "bluesky": "Bluesky version under 300 chars",
    "threads": "Threads version under 500 chars",
    "instagram": "Instagram with #hashtags"
  }
}
```

### List Scheduled Posts

```bash
node skills/metricool/scripts/list-scheduled.js
node skills/metricool/scripts/list-scheduled.js --start 2026-01-30 --end 2026-02-05
```

### Get Best Time to Post

```bash
node skills/metricool/scripts/best-time.js linkedin
node skills/metricool/scripts/best-time.js x
```

## Character Limits

| Platform | Limit |
|----------|-------|
| LinkedIn | 3,000 |
| X/Twitter | 280 |
| Bluesky | 300 |
| Threads | 500 |
| Instagram | 2,200 |

## Image Requirements

- Must be publicly accessible URL (S3, GCS, etc.)
- Recommended formats: PNG, JPG
- Square images work best for Instagram/Threads
- Wide images (1.91:1) work best for X/LinkedIn
