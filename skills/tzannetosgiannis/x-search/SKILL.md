---
name: x-search
description: AI-powered X/Twitter search for real-time trends, breaking news, sentiment analysis, and social media insights. Use when users want to search Twitter/X for topics, hashtags, viral content, or public opinion. Costs $0.05 USDC per request via x402 protocol on Base network.
---

# X Search

Search X/Twitter using an AI-powered agent for real-time insights and social media intelligence.

## Configuration

The private key must be available via one of these methods:

**Option 1: Environment variable**
```bash
export X402_PRIVATE_KEY="0x..."
```

**Option 2: Config file (Recommended)**

The script checks for `x402-config.json` in these locations (in order):
1. Current directory: `./x402-config.json`
2. Home directory: `~/.x402-config.json` ← **Recommended**
3. Working directory: `$PWD/x402-config.json`

Create the config file:
```json
{
  "private_key": "0x1234567890abcdef..."
}
```

**Example (home directory - works for any user):**
```bash
echo '{"private_key": "0x..."}' > ~/.x402-config.json
```

## Usage

Run the search script with a query:

```bash
scripts/search.sh "<search query>"
```

The script:
- Executes the npx CLI tool with payment handling
- Costs $0.05 USDC per request (Base network)
- Returns AI-processed search results

## Examples

**User:** "What are people saying about AI agents on Twitter?"
```bash
scripts/search.sh "AI agents discussions and opinions"
```

**User:** "Find trending topics about cryptocurrency"
```bash
scripts/search.sh "cryptocurrency trends today"
```

**User:** "Show me viral content about climate change"
```bash
scripts/search.sh "viral climate change posts"
```

## Capabilities
- Real-time trends and breaking news
- Social media sentiment analysis
- Viral content tracking
- Public opinion research
- Hashtag and topic analysis

## Error Handling
- **"Payment failed: Not enough USDC"** → Inform user to top up Base wallet with USDC
- **"X402 private key missing"** → Guide user to configure private key (see Configuration above)
- **Timeout errors** → The API has a 5-minute timeout; complex queries may take time
