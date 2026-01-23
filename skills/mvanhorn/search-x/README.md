# Search X — Real-time Twitter/X Search for Clawdbot

Search X/Twitter in real-time using Grok's `x_search` tool. Get actual tweets with citations.

## Installation

```bash
clawdhub install search-x
```

Or manually:
```bash
cd ~/clawd/skills && git clone https://github.com/mvanhorn/clawdbot-skill-search-x search-x
```

## Setup

Get your API key from [console.x.ai](https://console.x.ai), then:

```bash
clawdbot config set skills.entries.search-x.apiKey "xai-YOUR-KEY"
```

Or set environment variable:
```bash
export XAI_API_KEY="xai-YOUR-KEY"
```

## Usage

### Basic Search
```bash
node scripts/search.js "AI video editing"
```

### Time Filter
```bash
node scripts/search.js --days 7 "breaking news"    # Last 7 days
node scripts/search.js --days 1 "trending today"   # Last 24 hours
```

### Handle Filters
```bash
node scripts/search.js --handles @elonmusk,@OpenAI "AI"
node scripts/search.js --exclude @bots "real discussions"
```

### Output Formats
```bash
node scripts/search.js --compact "topic"      # Just tweets
node scripts/search.js --links-only "topic"   # Just URLs
node scripts/search.js --json "topic"         # Full JSON
```

## Chat Examples

Just tell your Clawdbot:
- "Search X for what people are saying about Claude"
- "Find tweets about Remotion in the last week"
- "What's trending on Twitter about AI today?"

## How It Works

Uses xAI's Responses API with the `x_search` tool:
- **Endpoint:** `/v1/responses`
- **Model:** `grok-4-1-fast` (optimized for search)
- **Features:** Date filtering, handle filtering, real citations

## Output Example

```
🔍 Searching X: "Remotion Claude Code" (last 30 days)...

**@rknkhanna** (Rahul K)
"made a launch video using remotion. the remotion team published a skill
that teaches claude their best practices. fed it my design system.
described 6 scenes. got working animation code."
https://x.com/rknkhanna/status/2014504411981295928

📎 Citations (5):
   https://x.com/i/status/2014504411981295928
   ...
```

## License

MIT
