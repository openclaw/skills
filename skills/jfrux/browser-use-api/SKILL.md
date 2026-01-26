---
name: browser-use
version: 1.0.0
description: Cloud browser automation via Browser Use API. Use when you need AI-driven web browsing, scraping, form filling, or multi-step web tasks without local browser control. Triggers on "browser use", "cloud browser", "scrape website", "automate web task", or when local browser isn't available/suitable.
metadata: {"clawdbot":{"emoji":"🌐","requires":{"env":["BROWSER_USE_API_KEY"]}}}
---

# Browser Use

Cloud-based AI browser automation. Send a task in plain English, get structured results.

## Quick Start

```bash
# Submit task
curl -s -X POST https://api.browser-use.com/api/v2/tasks \
  -H "X-Browser-Use-API-Key: $BROWSER_USE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"task": "Go to example.com and extract the main heading"}'

# Poll for result (replace TASK_ID)
curl -s "https://api.browser-use.com/api/v2/tasks/TASK_ID" \
  -H "X-Browser-Use-API-Key: $BROWSER_USE_API_KEY"
```

## Helper Script

Use `scripts/browser-use.sh` for simpler execution:

```bash
# Run task and wait for result
./scripts/browser-use.sh "Go to hacker news and get the top 3 stories"

# Just submit (don't wait)
./scripts/browser-use.sh --no-wait "Search Google for AI news"
```

## API Reference

### Create Task
```
POST https://api.browser-use.com/api/v2/tasks
```

Body:
```json
{
  "task": "Plain English description of what to do",
  "llm": "gemini-3-flash-preview"  // optional, default is fast model
}
```

Response:
```json
{
  "id": "task-uuid",
  "sessionId": "session-uuid"
}
```

### Get Task Status
```
GET https://api.browser-use.com/api/v2/tasks/{taskId}
```

Response fields:
- `status`: `pending` | `started` | `finished` | `failed`
- `output`: Result text when finished
- `steps`: Array of actions taken (with screenshots)
- `cost`: Cost in dollars (e.g., "0.02")
- `isSuccess`: Boolean result

### Stop Task
```
POST https://api.browser-use.com/api/v2/tasks/{taskId}/stop
```

## Pricing

~$0.01-0.05 per task depending on complexity. Check balance:
```bash
curl -s https://api.browser-use.com/api/v2/credits \
  -H "X-Browser-Use-API-Key: $BROWSER_USE_API_KEY"
```

## When to Use

- Complex multi-step web workflows
- Sites that block simple scraping
- Form filling and submissions
- When you need screenshots of steps
- When local browser control isn't available

## When NOT to Use

- Simple page fetches (use `web_fetch` instead)
- When you have local browser access (use `browser` tool)
- Rapid/high-volume scraping (use Code Use or local scraping)
