---
name: browser-cash
description: Spin up unblocked browser sessions via Browser.cash for web automation. Sessions bypass anti-bot protections (Cloudflare, DataDome, etc.) making them ideal for scraping and automation.
homepage: https://browser.cash
metadata: {"clawdbot":{"emoji":"🌐","requires":{"bins":["curl","jq"]}}}
---

# browser-cash

Spin up unblocked browser sessions via Browser.cash for web automation. These sessions bypass common anti-bot protections (Cloudflare, DataDome, etc.), making them ideal for scraping, testing, and automation tasks that would otherwise get blocked.

**When to use:** Any browser automation task—scraping, form filling, testing, screenshots. Browser.cash sessions appear as real browsers and handle bot detection automatically.

## Setup

**API Key** is stored in clawdbot config at `skills.entries.browser-cash.apiKey`.

If not configured, prompt the user:
> Get your API key from https://dash.browser.cash and run:
> ```bash
> clawdbot config set skills.entries.browser-cash.apiKey "your_key_here"
> ```

**Reading the key:**
```bash
BROWSER_CASH_KEY=$(clawdbot config get skills.entries.browser-cash.apiKey)
```

**Before first use**, check and install Playwright if needed:
```bash
if [ ! -d ~/clawd/node_modules/playwright ]; then
  cd ~/clawd && npm install playwright puppeteer-core
fi
```

## API Basics

```bash
curl -X POST "https://api.browser.cash/v1/..." \
  -H "Authorization: Bearer $BROWSER_CASH_KEY" \
  -H "Content-Type: application/json"
```

## Create a Browser Session

**Basic session:**
```bash
curl -X POST "https://api.browser.cash/v1/browser/session" \
  -H "Authorization: Bearer $BROWSER_CASH_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "sessionId": "abc123...",
  "status": "active",
  "servedBy": "node-id",
  "createdAt": "2025-01-20T01:51:25.000Z",
  "stoppedAt": null,
  "cdpUrl": "wss://gcp-usc1-1.browser.cash/v1/consumer/abc123.../devtools/browser/uuid"
}
```

**With options:**
```bash
curl -X POST "https://api.browser.cash/v1/browser/session" \
  -H "Authorization: Bearer $BROWSER_CASH_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "country": "US",
    "windowSize": "1920x1080",
    "profile": {
      "name": "my-profile",
      "persist": true
    }
  }'
```

### Session Options

| Option | Type | Description |
|--------|------|-------------|
| `country` | string | 2-letter ISO code (e.g., "US", "DE", "GB") |
| `windowSize` | string | Browser dimensions, e.g., "1920x1080" |
| `proxyUrl` | string | SOCKS5 proxy URL (optional) |
| `profile.name` | string | Named browser profile for session persistence |
| `profile.persist` | boolean | Save cookies/storage after session ends |

## Using Browser.cash with Clawdbot

Browser.cash returns a WebSocket CDP URL (`wss://...`). Use one of these approaches:

### Option 1: Direct CDP via exec (Recommended)

**Important:** Before running Playwright/Puppeteer scripts, ensure dependencies are installed:
```bash
[ -d ~/clawd/node_modules/playwright ] || (cd ~/clawd && npm install playwright puppeteer-core)
```

Use Playwright or Puppeteer in an exec block to connect directly to the CDP URL:

```bash
# 1. Create session
BROWSER_CASH_KEY=$(clawdbot config get skills.entries.browser-cash.apiKey)
SESSION=$(curl -s -X POST "https://api.browser.cash/v1/browser/session" \
  -H "Authorization: Bearer $BROWSER_CASH_KEY" \
  -H "Content-Type: application/json" \
  -d '{"country": "US", "windowSize": "1920x1080"}')

SESSION_ID=$(echo $SESSION | jq -r '.sessionId')
CDP_URL=$(echo $SESSION | jq -r '.cdpUrl')

# 2. Use via Node.js exec (Playwright)
node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.connectOverCDP('$CDP_URL');
  const context = browser.contexts()[0];
  const page = context.pages()[0] || await context.newPage();
  await page.goto('https://example.com');
  console.log('Title:', await page.title());
  await browser.close();
})();
"

# 3. Stop session when done
curl -X DELETE "https://api.browser.cash/v1/browser/session?sessionId=$SESSION_ID" \
  -H "Authorization: Bearer $BROWSER_CASH_KEY"
```

### Option 2: Curl-based automation

For simple tasks, use curl to interact with pages via CDP commands:

```bash
# Navigate and extract content using the CDP URL
# (See CDP protocol docs for available methods)
```

### Note on Clawdbot browser tool

Clawdbot's native `browser` tool expects HTTP control server URLs, not raw WebSocket CDP. The `gateway config.patch` approach works when Clawdbot's browser control server proxies the connection. For direct Browser.cash CDP, use the exec approach above.

## Get Session Status

```bash
curl "https://api.browser.cash/v1/browser/session?sessionId=YOUR_SESSION_ID" \
  -H "Authorization: Bearer $BROWSER_CASH_KEY"
```

Statuses: `starting`, `active`, `completed`, `error`

## Stop a Session

```bash
curl -X DELETE "https://api.browser.cash/v1/browser/session?sessionId=YOUR_SESSION_ID" \
  -H "Authorization: Bearer $BROWSER_CASH_KEY"
```

## List Sessions

```bash
curl "https://api.browser.cash/v1/browser/sessions?page=1&pageSize=20" \
  -H "Authorization: Bearer $BROWSER_CASH_KEY"
```

## Browser Profiles

Profiles persist cookies, localStorage, and session data across sessions—useful for staying logged in or maintaining state.

**List profiles:**
```bash
curl "https://api.browser.cash/v1/browser/profiles" \
  -H "Authorization: Bearer $BROWSER_CASH_KEY"
```

**Delete profile:**
```bash
curl -X DELETE "https://api.browser.cash/v1/browser/profile?profileName=my-profile" \
  -H "Authorization: Bearer $BROWSER_CASH_KEY"
```

## Connecting via CDP

The `cdpUrl` is a WebSocket endpoint for Chrome DevTools Protocol. Use it with any CDP-compatible library.

**Playwright:**
```javascript
const { chromium } = require('playwright');
const browser = await chromium.connectOverCDP(cdpUrl);
const context = browser.contexts()[0];
const page = context.pages()[0] || await context.newPage();
await page.goto('https://example.com');
```

**Puppeteer:**
```javascript
const puppeteer = require('puppeteer-core');
const browser = await puppeteer.connect({ browserWSEndpoint: cdpUrl });
const pages = await browser.pages();
const page = pages[0] || await browser.newPage();
await page.goto('https://example.com');
```

## Full Workflow Example

```bash
# 0. Ensure Playwright is installed
[ -d ~/clawd/node_modules/playwright ] || (cd ~/clawd && npm install playwright puppeteer-core)

# 1. Create session
BROWSER_CASH_KEY=$(clawdbot config get skills.entries.browser-cash.apiKey)
SESSION=$(curl -s -X POST "https://api.browser.cash/v1/browser/session" \
  -H "Authorization: Bearer $BROWSER_CASH_KEY" \
  -H "Content-Type: application/json" \
  -d '{"country": "US", "windowSize": "1920x1080"}')

SESSION_ID=$(echo $SESSION | jq -r '.sessionId')
CDP_URL=$(echo $SESSION | jq -r '.cdpUrl')

# 2. Connect with Playwright/Puppeteer using $CDP_URL...

# 3. Stop session when done
curl -X DELETE "https://api.browser.cash/v1/browser/session?sessionId=$SESSION_ID" \
  -H "Authorization: Bearer $BROWSER_CASH_KEY"
```

## Scraping Tips

When extracting data from pages with lazy-loading or infinite scroll:

```javascript
// Scroll to load all products
async function scrollToBottom(page) {
  let previousHeight = 0;
  while (true) {
    const currentHeight = await page.evaluate(() => document.body.scrollHeight);
    if (currentHeight === previousHeight) break;
    previousHeight = currentHeight;
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(1500); // Wait for content to load
  }
}

// Wait for specific elements
await page.waitForSelector('.product-card', { timeout: 10000 });

// Handle "Load More" buttons
const loadMore = await page.$('button.load-more');
if (loadMore) {
  await loadMore.click();
  await page.waitForTimeout(2000);
}
```

**Common patterns:**
- Always scroll to trigger lazy-loaded content
- Wait for network idle: `await page.waitForLoadState('networkidle')`
- Use `page.waitForSelector()` before extracting elements
- Add delays between actions to avoid rate limiting

## Why Browser.cash for Automation

- **Unblocked**: Sessions bypass Cloudflare, DataDome, PerimeterX, and other bot protections
- **Real browser fingerprint**: Appears as a genuine Chrome browser, not headless
- **CDP native**: Direct WebSocket connection for Playwright, Puppeteer, or raw CDP
- **Geographic targeting**: Spin up sessions in specific countries
- **Persistent profiles**: Maintain login state across sessions

## Notes

- Sessions auto-terminate after extended inactivity
- Always stop sessions when done to avoid unnecessary usage
- Use profiles when you need to maintain logged-in state
- SOCKS5 is the only supported proxy type
- Clawdbot runs scripts from `~/clawd/` - install npm dependencies there
- For full page scraping, always scroll to trigger lazy-loaded content
