---
name: web-search-plus
version: 2.2.1
description: Unified search skill with Intelligent Auto-Routing. Uses multi-signal analysis to automatically select between Serper (Google), Tavily (Research), and Exa (Neural) with confidence scoring.
tags: [search, web-search, serper, tavily, exa, google, research, semantic-search, auto-routing, multi-provider, shopping, free-tier]
---

# Web Search Plus

Multi-provider web search with **Intelligent Auto-Routing**: Serper (Google), Tavily (Research), Exa (Neural).

**NEW in v2.1.0**: Intelligent multi-signal analysis with confidence scoring!

---

## 🔑 API Keys Setup

**NEW in v2.2.0**: The script **auto-loads** API keys from `.env` in the skill directory!

### Quick Setup

**Option A: .env file** (recommended)
```bash
# /path/to/skills/web-search-plus/.env
export SERPER_API_KEY="your-key"   # https://serper.dev
export TAVILY_API_KEY="your-key"   # https://tavily.com  
export EXA_API_KEY="your-key"      # https://exa.ai
```

**Option B: config.json** (NEW in v2.2.1)
```json
{
  "serper": { "api_key": "your-serper-key" },
  "tavily": { "api_key": "your-tavily-key" },
  "exa": { "api_key": "your-exa-key" }
}
```

Just run — keys load automatically:
```bash
python3 scripts/search.py -q "your query"
# No need for 'source .env' anymore! ✨
```

**Priority:** config.json > .env > environment variable

### Get Free API Keys

| Provider | Free Tier | Sign Up |
|----------|-----------|---------|
| Serper | 2,500 queries/mo | https://serper.dev |
| Tavily | 1,000 queries/mo | https://tavily.com |
| Exa | 1,000 queries/mo | https://exa.ai |

---

## ⚠️ Don't Modify Core Clawdbot Config

**Tavily, Serper, and Exa are NOT core Clawdbot providers.**

❌ **DON'T** add to `~/.clawdbot/clawdbot.json`:
```json
"tools": { "web": { "search": { "provider": "tavily" }}}  // WRONG!
```

✅ **DO** use this skill's scripts — keys auto-load from `.env`

Core Clawdbot only supports `brave` as the built-in web search provider. This skill adds Serper, Tavily, and Exa as **additional** options via its own scripts.

---

## 🧠 Intelligent Auto-Routing

No need to choose a provider — just search! The skill uses **multi-signal analysis** to understand your query intent:

```bash
# These queries are intelligently routed with confidence scoring:
python3 scripts/search.py -q "how much does iPhone 16 cost"     # → Serper (68% MEDIUM)
python3 scripts/search.py -q "how does quantum entanglement work"  # → Tavily (86% HIGH)
python3 scripts/search.py -q "startups similar to Notion"       # → Exa (76% HIGH)
python3 scripts/search.py -q "MacBook Pro M3 specs review"      # → Serper (70% HIGH)
python3 scripts/search.py -q "explain pros and cons of React"   # → Tavily (85% HIGH)
python3 scripts/search.py -q "companies like stripe.com"        # → Exa (100% HIGH)
```

### How It Works

The routing engine analyzes multiple signals:

#### 🛒 Shopping Intent → Serper
| Signal Type | Examples | Weight |
|-------------|----------|--------|
| Price patterns | "how much", "price of", "cost of" | HIGH |
| Purchase intent | "buy", "purchase", "order", "where to buy" | HIGH |
| Deal signals | "deal", "discount", "cheap", "best price" | MEDIUM |
| Product + Brand | "iPhone 16", "Sony headphones" + specs/review | HIGH |
| Local business | "near me", "restaurants", "hotels" | HIGH |

#### 📚 Research Intent → Tavily
| Signal Type | Examples | Weight |
|-------------|----------|--------|
| Explanation | "how does", "why does", "explain", "what is" | HIGH |
| Analysis | "compare", "pros and cons", "difference between" | HIGH |
| Learning | "tutorial", "guide", "understand", "learn" | MEDIUM |
| Depth | "in-depth", "comprehensive", "detailed" | MEDIUM |
| Complex queries | Long, multi-clause questions | BONUS |

#### 🔍 Discovery Intent → Exa
| Signal Type | Examples | Weight |
|-------------|----------|--------|
| Similarity | "similar to", "alternatives to", "competitors" | VERY HIGH |
| Company discovery | "companies like", "startups doing", "who else" | HIGH |
| URL detection | Any URL or domain (stripe.com) | VERY HIGH |
| Academic | "arxiv", "research papers", "github projects" | HIGH |
| Funding | "Series A", "YC", "funded startup" | HIGH |

### Confidence Scoring

Every routing decision includes a confidence level:

| Confidence | Level | Meaning |
|------------|-------|---------|
| 70-100% | **HIGH** | Strong signal match, very reliable |
| 40-69% | **MEDIUM** | Good match, should work well |
| 0-39% | **LOW** | Ambiguous query, using fallback |

### Debug Routing Decisions

See the full analysis:

```bash
python3 scripts/search.py --explain-routing -q "how much does iPhone 16 Pro cost"
```

Output:
```json
{
  "query": "how much does iPhone 16 Pro cost",
  "routing_decision": {
    "provider": "serper",
    "confidence": 0.68,
    "confidence_level": "medium",
    "reason": "moderate_confidence_match"
  },
  "scores": {"serper": 7.0, "tavily": 0.0, "exa": 0.0},
  "top_signals": [
    {"matched": "how much", "weight": 4.0},
    {"matched": "brand + product detected", "weight": 3.0}
  ],
  "query_analysis": {
    "word_count": 7,
    "is_complex": false,
    "has_url": null,
    "recency_focused": false
  }
}
```

---

## 🔍 When to Use This Skill vs Built-in Brave Search

### Use **Built-in Brave Search** when:
- ✅ General web searches (news, info, questions)
- ✅ Privacy is important
- ✅ Quick lookups without specific requirements

### Use **web-search-plus** when:

#### → **Serper** (Google results):
- 🛍️ **Product specs, prices, shopping** - "Compare iPhone 16 vs Samsung S24"
- 📍 **Local businesses, places** - "Best pizza in Vienna"
- 🎯 **"Google it"** - Explicitly wants Google results
- 📰 **Shopping/images/news** - `--type shopping/images/news`
- 🏆 **Knowledge Graph** - Structured info (prices, ratings, etc.)

#### → **Tavily** (AI-optimized research):
- 📚 **Research questions** - "How does quantum computing work?"
- 🔬 **Deep dives** - Complex multi-part questions
- 📄 **Full page content** - Not just snippets (`--raw-content`)
- 🎓 **Academic research** - Synthesized answers
- 🔒 **Domain filtering** - `--include-domains` for trusted sources

#### → **Exa** (Neural semantic search):
- 🔗 **Similar pages** - "Sites like OpenAI.com" (`--similar-url`)
- 🏢 **Company discovery** - "AI companies like Anthropic"
- 📝 **Research papers** - `--category "research paper"`
- 💻 **GitHub projects** - `--category github`
- 📅 **Date-specific** - `--start-date` / `--end-date`

---

## Provider Comparison

| Feature | Serper | Tavily | Exa |
|---------|:------:|:------:|:---:|
| Speed | ⚡⚡⚡ | ⚡⚡ | ⚡⚡ |
| Factual Accuracy | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Semantic Understanding | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| Research Quality | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Full Page Content | ✗ | ✓ | ✓ |
| Shopping/Local | ✓ | ✗ | ✗ |
| Similar Pages | ✗ | ✗ | ✓ |
| Knowledge Graph | ✓ | ✗ | ✗ |

---

## Usage Examples

### Auto-Routed (Recommended)

```bash
python3 scripts/search.py -q "iPhone 16 Pro Max price"          # → Serper
python3 scripts/search.py -q "how does HTTPS encryption work"   # → Tavily
python3 scripts/search.py -q "startups similar to Notion"       # → Exa
```

### Explicit Provider

```bash
python3 scripts/search.py -p serper -q "weather Vienna" --type weather
python3 scripts/search.py -p tavily -q "quantum computing" --depth advanced
python3 scripts/search.py -p exa --similar-url "https://stripe.com" --category company
```

---

## Configuration

### config.json

```json
{
  "auto_routing": {
    "enabled": true,
    "fallback_provider": "serper",
    "confidence_threshold": 0.3,
    "disabled_providers": []
  },
  "serper": {"country": "us", "language": "en"},
  "tavily": {"depth": "advanced"},
  "exa": {"type": "neural"}
}
```

---

## Output Format

```json
{
  "provider": "serper",
  "query": "iPhone 16 price",
  "results": [{"title": "...", "url": "...", "snippet": "...", "score": 0.95}],
  "answer": "Synthesized answer...",
  "routing": {
    "auto_routed": true,
    "provider": "serper",
    "confidence": 0.78,
    "confidence_level": "high",
    "reason": "high_confidence_match",
    "top_signals": [{"matched": "price", "weight": 3.0}]
  }
}
```

---

## FAQ

### General

**Q: How does auto-routing decide which provider to use?**
> Multi-signal analysis scores each provider based on: price patterns, explanation phrases, similarity keywords, URLs, product+brand combos, and query complexity. Highest score wins. Use `--explain-routing` to see the decision breakdown.

**Q: What if it picks the wrong provider?**
> Override with `-p serper/tavily/exa`. Check `--explain-routing` to understand why it chose differently.

**Q: What does "low confidence" mean?**
> Query is ambiguous (e.g., "Tesla" could be cars, stock, or company). Falls back to Serper. Results may vary.

**Q: Can I disable a provider?**
> Yes! In config.json: `"disabled_providers": ["exa"]`

### API Keys

**Q: Which API keys do I need?**
> At minimum ONE key. You can use just Serper, just Tavily, or all three. Missing keys = that provider is skipped.

**Q: Where do I get API keys?**
> - Serper: https://serper.dev (2,500 free queries, no credit card)
> - Tavily: https://tavily.com (1,000 free searches/month)
> - Exa: https://exa.ai (1,000 free searches/month)

**Q: How do I set API keys?**
> Two options (both auto-load):
> 
> **Option A: .env file**
> ```bash
> export SERPER_API_KEY="your-key"
> ```
> 
> **Option B: config.json** (v2.2.1+)
> ```json
> { "serper": { "api_key": "your-key" } }
> ```

### Routing Details

**Q: How do I know which provider handled my search?**
> Check `routing.provider` in JSON output, or `[🔍 Searched with: Provider]` in chat responses.

**Q: Why does it sometimes choose Serper for research questions?**
> If the query has brand/product signals (e.g., "how does Tesla FSD work"), shopping intent may outweigh research intent. Override with `-p tavily`.

**Q: What's the confidence threshold?**
> Default: 0.3 (30%). Below this = low confidence, uses fallback. Adjustable in config.json.

### Troubleshooting

**Q: "No API key found" error?**
> 1. Check `.env` exists in skill folder with `export VAR=value` format
> 2. Keys auto-load from skill's `.env` since v2.2.0
> 3. Or set in system environment: `export SERPER_API_KEY="..."`

**Q: Getting empty results?**
> 1. Check API key is valid
> 2. Try a different provider with `-p`
> 3. Some queries have no results (very niche topics)

**Q: Rate limited?**
> Each provider has limits. Spread queries across providers or wait. Serper: 2,500 free total, Tavily: 1,000/month free.

### For Clawdbot Users

**Q: How do I use this in chat?**
> Just ask! Clawdbot auto-detects search intent. Or explicitly: "search with web-search-plus for..."

**Q: Does it replace built-in Brave Search?**
> No, it's complementary. Use Brave for quick lookups, web-search-plus for research/shopping/discovery.

**Q: Can I see which provider was used?**
> Yes! SOUL.md can include attribution: `[🔍 Searched with: Serper/Tavily/Exa]`
