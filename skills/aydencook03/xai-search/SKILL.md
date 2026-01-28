---
name: xai-search
description: Search X/Twitter and the web in real-time using xAI's Grok API with agentic search tools.
metadata: {"clawdbot":{"emoji":"🔍"}}
---

# xAI Search (Grok API)

Use xAI's agentic search to query X/Twitter and the web in real-time. This leverages Grok's `web_search` and `x_search` tools.

**Docs:** https://docs.x.ai/docs/

## Requirements

- `XAI_API_KEY` environment variable
- Python 3 + xai-sdk: `pip install xai-sdk`

## Quick Usage (curl)

### Web Search
```bash
curl -s https://api.x.ai/v1/chat/completions \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-3-fast",
    "messages": [{"role": "user", "content": "YOUR QUERY HERE"}],
    "tools": [{"type": "function", "function": {"name": "web_search"}}]
  }' | jq -r '.choices[0].message.content'
```

### X/Twitter Search
```bash
curl -s https://api.x.ai/v1/chat/completions \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-3-fast",
    "messages": [{"role": "user", "content": "YOUR QUERY HERE"}],
    "tools": [{"type": "function", "function": {"name": "x_search"}}]
  }' | jq -r '.choices[0].message.content'
```

### Combined (Web + X)
```bash
curl -s https://api.x.ai/v1/chat/completions \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "grok-3-fast",
    "messages": [{"role": "user", "content": "YOUR QUERY HERE"}],
    "tools": [
      {"type": "function", "function": {"name": "web_search"}},
      {"type": "function", "function": {"name": "x_search"}}
    ]
  }' | jq -r '.choices[0].message.content'
```

## Helper Script

For convenience, use the `xai-search.py` script in the `scripts/` folder:

```bash
# Web search (adjust path to your skill location)
python ~/.clawdbot/skills/xai-search/scripts/xai-search.py web "latest news about AI"

# X/Twitter search  
python ~/.clawdbot/skills/xai-search/scripts/xai-search.py x "what are people saying about Clawdbot"

# Both
python ~/.clawdbot/skills/xai-search/scripts/xai-search.py both "current events today"
```

## Models

- `grok-3-fast` — fast, good for quick searches
- `grok-4-1-fast` — reasoning model, better for complex queries

## X Search Filters

You can filter X searches by:
- `allowed_x_handles` / `excluded_x_handles` — limit to specific accounts
- `from_date` / `to_date` — date range (ISO8601 format)
- `enable_image_understanding` — analyze images in posts
- `enable_video_understanding` — analyze videos in posts

## Web Search Filters

- `allowed_domains` / `excluded_domains` — limit to specific sites
- `enable_image_understanding` — analyze images on pages

## Tips

- For breaking news: use X search
- For factual/research queries: use web search or both
- For sentiment/opinions: use X search
- The model will make multiple search calls if needed (agentic)
