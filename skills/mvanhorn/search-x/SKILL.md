---
name: search-x
description: Search X/Twitter in real-time using Grok. Find tweets, trends, and discussions with citations.
homepage: https://docs.x.ai
triggers:
  - search x
  - search twitter
  - find tweets
  - what's on x about
  - x search
  - twitter search
metadata:
  clawdbot:
    emoji: "🔍"
---

# Search X

Real-time X/Twitter search powered by Grok's x_search tool. Get actual tweets with citations.

## Setup

Set your xAI API key:

```bash
clawdbot config set skills.entries.search-x.apiKey "xai-YOUR-KEY"
```

Or use environment variable:
```bash
export XAI_API_KEY="xai-YOUR-KEY"
```

Get your API key at: https://console.x.ai

## Commands

### Basic Search
```bash
node {baseDir}/scripts/search.js "AI video editing"
```

### Filter by Time
```bash
node {baseDir}/scripts/search.js --days 7 "breaking news"
node {baseDir}/scripts/search.js --days 1 "trending today"
```

### Filter by Handles
```bash
node {baseDir}/scripts/search.js --handles @elonmusk,@OpenAI "AI announcements"
node {baseDir}/scripts/search.js --exclude @bots "real discussions"
```

### Output Options
```bash
node {baseDir}/scripts/search.js --json "topic"        # Full JSON response
node {baseDir}/scripts/search.js --compact "topic"     # Just tweets, no fluff
node {baseDir}/scripts/search.js --links-only "topic"  # Just X links
```

## Example Usage in Chat

**User:** "Search X for what people are saying about Claude Code"
**Action:** Run search with query "Claude Code"

**User:** "Find tweets from @remotion_dev in the last week"
**Action:** Run search with --handles @remotion_dev --days 7

**User:** "What's trending about AI on Twitter today?"
**Action:** Run search with --days 1 "AI trending"

**User:** "Search X for Remotion best practices, last 30 days"
**Action:** Run search with --days 30 "Remotion best practices"

## How It Works

Uses xAI's Responses API (`/v1/responses`) with the `x_search` tool:
- Model: `grok-4-1-fast` (optimized for agentic search)
- Returns real tweets with URLs
- Includes citations for verification
- Supports date and handle filtering

## Response Format

Each result includes:
- **@username** (display name)
- Tweet content
- Date/time
- Direct link to tweet

## Environment Variables

- `XAI_API_KEY` - Your xAI API key (required)
- `SEARCH_X_MODEL` - Model override (default: grok-4-1-fast)
- `SEARCH_X_DAYS` - Default days to search (default: 30)
