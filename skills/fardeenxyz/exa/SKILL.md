---
name: exa
description: Neural web search and code context via Exa AI API. Requires EXA_API_KEY. Use for finding documentation, code examples, research papers, or company info.
metadata: {"clawdbot":{"emoji":"🧠","requires":{"env":["EXA_API_KEY"]}}}
---

# Exa - Neural Web Search

Direct API access to Exa's neural search engine.

## Setup

**1. Get your API Key:**
Get a key from [Exa Dashboard](https://dashboard.exa.ai/api-keys).

**2. Set it in your environment:**
```bash
export EXA_API_KEY="your-key-here"
```

## Usage

### Web Search
```bash
bash scripts/search.sh "query" [num_results] [type]
```
*   `type`: auto (default), neural, fast, deep
*   `category`: company, research-paper, news, github, tweet, personal-site, pdf

### Code Context
Finds relevant code snippets and documentation.
```bash
bash scripts/code.sh "query" [num_results]
```

### Get Content
Extract full text from URLs.
```bash
bash scripts/content.sh "url1" "url2"
```
