---
name: context7
description: Context7 MCP - Intelligent documentation search and context for any library
metadata:
  version: 1.0.3
  tags: ["documentation", "search", "context", "mcp", "llm"]
  clawdbot:
    requires:
      bins: ["node"]
      npm: true
    install:
      - id: "skill-install"
        kind: "skill"
        source: "clawdhub"
        slug: "context7"
        label: "Install Context7 skill"
---

# Context7 MCP

Context7 provides intelligent documentation search and context for any library, powered by LLMs.

## Setup

1. Copy `.env.example` to `.env` and add your Context7 API key:
   ```bash
   cp .env.example .env
   ```

   Add your API key to `.env`:
   ```
   CONTEXT7_API_KEY=your-api-key-here
   ```

   Get your key from [context7.com/dashboard](https://context7.com/dashboard)

2. Install dependencies:
   ```bash
   npm install
   ```

## Usage

Context7 provides two main commands:

### Search Command

Search for libraries by name with intelligent LLM-powered ranking:

```bash
npx tsx query.ts search <library_name> <query>

# Examples:
npx tsx query.ts search "nextjs" "setup ssr"
npx tsx query.ts search "react" "useEffect cleanup"
npx tsx query.ts search "better-auth" "authentication flow"
```

This calls the Context7 Search API:
```
GET https://context7.com/api/v2/libs/search?libraryName=<name>&query=<query>
```

**Response includes:**
- id: Library ID (e.g., `/vercel/next.js`)
- name: Display name
- trustScore: Source reputation (0-100)
- benchmarkScore: Quality indicator (0-100)
- versions: Available version tags

### Context Command

Retrieve intelligent, LLM-reranked documentation context:

```bash
npx tsx query.ts context <owner/repo> <query>

# Examples:
npx tsx query.ts context "vercel/next.js" "setup ssr"
npx tsx query.ts context "facebook/react" "useState hook"
```

This calls the Context7 Context API:
```
GET https://context7.com/api/v2/context?libraryId=<repo>&query=<query>&type=txt
```

**Response includes:**
- title: Documentation section title
- content: Documentation text/snippet
- source: URL to source page

### Quick Reference

```bash
# Search for documentation
npx tsx query.ts search "library-name" "your search query"

# Get context from a specific repo
npx tsx query.ts context "owner/repo" "your question"
```

## Best Practices

Get the most out of the Context7 API with these best practices:

### Optimize Search Relevance

When using the `/libs/search` endpoint, always include the user's original question in the query parameter. This allows the API to use LLM-powered ranking to find the most relevant library for the specific task, rather than relying on a simple name match.

**Example:** If a user asks about SSR in Next.js, search with:
- `libraryName=nextjs`
- `query=setup+ssr`

This ensures the best ranking for the specific task.

### Use Specific Library IDs

For the fastest and most accurate results with the `/context` endpoint, provide the full libraryId (e.g., `/vercel/next.js`). If you already know the library the user is asking about, skipping the search step and calling the context endpoint directly reduces latency.

### Leverage Versioning

To ensure documentation accuracy for older or specific project requirements, include the version in the libraryId using the `/owner/repo/version` format. You can find available version tags in the response from the search endpoint.

### Choose the Right Response Type

Tailor the `/context` response to your needs using the `type` parameter:
- Use `type=json` when you need to programmatically handle titles, content snippets, and source URLs (ideal for UI display).
- Use `type=txt` when you want to pipe the documentation directly into an LLM prompt as plain text.

### Filter by Quality Scores

When programmatically selecting a library from search results, use the `trustScore` and `benchmarkScore` to prioritize high-quality, reputable documentation sources for your users.

### Find Navigation Pages

Find navigation and other pages in this documentation by fetching the `llms.txt` file at:
```
https://context7.com/docs/llms.txt
```

## API Reference

### Context7 REST API

**Search Endpoint:**
```
GET https://context7.com/api/v2/libs/search
  ?libraryName=<library_name>
  &query=<user_query>
```

**Context Endpoint:**
```
GET https://context7.com/api/v2/context
  ?libraryId=<owner/repo>
  &query=<user_query>
  &type=txt|json
```

## Troubleshooting

**No results found?**
- Check your API key is valid
- Verify the library name is correct (e.g., 'react' not 'React')

**Authentication errors?**
- Ensure CONTEXT7_API_KEY is set in `.env`
- Check your key hasn't expired at context7.com/dashboard

## License

MIT
