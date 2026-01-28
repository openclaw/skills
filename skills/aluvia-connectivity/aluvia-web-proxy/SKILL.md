---
name: aluvia-web-proxy
description: Unblock websites and bypass CAPTCHAs and 403 errors using Aluvia mobile proxies. Enables web search and content extraction without browser automation.
---

# Aluvia Web Proxy

Provides unblockable web access for agents using Aluvia mobile proxies.
Use this skill to search the web or fetch page content from sites that block bots, scrapers, or datacenter IPs.

## Capabilities

- Web search with unblockable access
- Fetch and extract page content as Markdown
- Bypass CAPTCHAs and anti-bot challenges
- Avoid 403 and IP-based blocking
- Route requests through Aluvia mobile IPs
- Reuse proxy connections

## Requirements

- Aluvia API key
- Brave Search API key
- Optional Aluvia connection ID for connection reuse

## Setup

```bash
cd ~/Projects/agent-scripts/skills/aluvia-web-proxy
npm ci
```

```bash
export ALUVIA_API_KEY=your_aluvia_key
export BRAVE_API_KEY=your_brave_key
```

Optional:

```bash
export ALUVIA_CONNECTION_ID=your_connection_id
```

## Usage

### Web Search

```bash
./search.js "query"
./search.js "query" -n 10
./search.js "query" --content
```

### Fetch Page Content

```bash
./content.js https://example.com/article
```

## Output

Returns structured search results and extracted page content in Markdown format.

## Use Cases

- Agents blocked by CAPTCHAs or 403 errors
- Web retrieval without headless browsers
- Scraping sites that block cloud IPs
- Search + fetch workflows requiring stable IPs

## Keywords

unblock, bypass captcha, 403 errors, website block, mobile proxy, web scraping, agent retrieval, anti-bot
