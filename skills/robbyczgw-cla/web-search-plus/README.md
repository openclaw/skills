# Web Search Plus

> Unified multi-provider web search with **Intelligent Auto-Routing** — uses multi-signal analysis to automatically select between **Serper**, **Tavily**, and **Exa** with confidence scoring.

[![ClawdHub](https://img.shields.io/badge/ClawdHub-web--search--plus-blue)](https://clawdhub.com)
[![Version](https://img.shields.io/badge/version-2.1.8-green)](https://clawdhub.com)
[![GitHub](https://img.shields.io/badge/GitHub-web--search--plus-blue)](https://github.com/robbyczgw-cla/web-search-plus)

---

## 🧠 Features (v2.1.8)

**Intelligent Multi-Signal Routing** — The skill now uses sophisticated query analysis:

- **Intent Classification**: Shopping vs Research vs Discovery
- **Linguistic Patterns**: "how much" (price) vs "how does" (research)
- **Entity Detection**: Product+brand combos, URLs, domains
- **Complexity Analysis**: Long queries favor research providers
- **Confidence Scoring**: Know how reliable the routing decision is

```bash
python3 scripts/search.py -q "how much does iPhone 16 cost"     # → Serper (68% confidence)
python3 scripts/search.py -q "how does quantum entanglement work"  # → Tavily (86% HIGH)
python3 scripts/search.py -q "startups similar to Notion"       # → Exa (76% HIGH)
python3 scripts/search.py -q "companies like stripe.com"        # → Exa (100% HIGH - URL detected)
```

---

## 🔍 When to Use Which Provider

### Built-in Brave Search (Clawdbot default)
- ✅ General web searches
- ✅ Privacy-focused
- ✅ Quick lookups
- ✅ Default fallback

### Serper (Google Results)
- 🛍️ **Product specs, prices, shopping**
- 📍 **Local businesses, places**
- 🎯 **"Google it" - explicit Google results**
- 📰 **Shopping/images needed**
- 🏆 **Knowledge Graph data**

### Tavily (AI-Optimized Research)
- 📚 **Research questions, deep dives**
- 🔬 **Complex multi-part queries**
- 📄 **Need full page content** (not just snippets)
- 🎓 **Academic/technical research**
- 🔒 **Domain filtering** (trusted sources)

### Exa (Neural Semantic Search)
- 🔗 **Find similar pages**
- 🏢 **Company/startup discovery**
- 📝 **Research papers**
- 💻 **GitHub projects**
- 📅 **Date-specific content**

---

## Table of Contents

- [Quick Start](#quick-start)
- [Smart Auto-Routing](#smart-auto-routing)
- [Configuration Guide](#configuration-guide)
- [Provider Deep Dives](#provider-deep-dives)
- [Usage Examples](#usage-examples)
- [Workflow Examples](#workflow-examples)
- [Optimization Tips](#optimization-tips)
- [FAQ & Troubleshooting](#faq--troubleshooting)
- [API Reference](#api-reference)

---

## Quick Start

```bash
# 1. Set up at least one API key
export SERPER_API_KEY="your-key"   # https://serper.dev
export TAVILY_API_KEY="your-key"   # https://tavily.com
export EXA_API_KEY="your-key"      # https://exa.ai

# 2. Run a search (auto-routed!)
python3 scripts/search.py -q "best laptop 2024"

# 3. Or specify a provider explicitly
python3 scripts/search.py -p serper -q "iPhone 16 specs"
python3 scripts/search.py -p tavily -q "quantum computing explained" --depth advanced
python3 scripts/search.py -p exa -q "AI startups 2024" --category company
```

---

## Smart Auto-Routing

### How It Works

When you don't specify a provider, the skill analyzes your query and routes it to the best provider:

| Query Contains | Routes To | Example |
|---------------|-----------|---------|
| "price", "buy", "shop", "cost" | **Serper** | "iPhone 16 price" |
| "near me", "restaurant", "hotel" | **Serper** | "pizza near me" |
| "weather", "news", "latest" | **Serper** | "weather Vienna" |
| "how does", "explain", "what is" | **Tavily** | "how does TCP work" |
| "research", "study", "analyze" | **Tavily** | "climate research" |
| "tutorial", "guide", "learn" | **Tavily** | "python tutorial" |
| "similar to", "companies like" | **Exa** | "companies like Stripe" |
| "startup", "Series A" | **Exa** | "AI startups Series A" |
| "github", "research paper" | **Exa** | "LLM papers arxiv" |

### Examples

```bash
# These are all auto-routed to the optimal provider:
python3 scripts/search.py -q "MacBook Pro M3 price"           # → Serper
python3 scripts/search.py -q "how does HTTPS work"            # → Tavily
python3 scripts/search.py -q "startups like Notion"           # → Exa
python3 scripts/search.py -q "best sushi restaurant near me"  # → Serper
python3 scripts/search.py -q "explain attention mechanism"    # → Tavily
python3 scripts/search.py -q "alternatives to Figma"          # → Exa
```

### Debug Auto-Routing

See exactly why a provider was selected:

```bash
python3 scripts/search.py --explain-routing -q "best laptop to buy"
```

Output:
```json
{
  "query": "best laptop to buy",
  "selected_provider": "serper",
  "reason": "matched_keywords (score=2)",
  "matched_keywords": ["buy", "best"],
  "available_providers": ["serper", "tavily", "exa"]
}
```

### Routing Info in Results

Every search result includes routing information:

```json
{
  "provider": "serper",
  "query": "iPhone 16 price",
  "results": [...],
  "routing": {
    "auto_routed": true,
    "selected_provider": "serper",
    "reason": "matched_keywords (score=1)",
    "matched_keywords": ["price"]
  }
}
```

---

## Configuration Guide

### Environment Variables

Create a `.env` file or set these in your shell:

```bash
# Required: Set at least one
export SERPER_API_KEY="your-serper-key"
export TAVILY_API_KEY="your-tavily-key"
export EXA_API_KEY="your-exa-key"
```

### Config File (config.json)

The `config.json` file lets you customize auto-routing and provider defaults:

```json
{
  "defaults": {
    "provider": "serper",
    "max_results": 5
  },
  
  "auto_routing": {
    "enabled": true,
    "fallback_provider": "serper",
    "provider_priority": ["serper", "tavily", "exa"],
    "disabled_providers": [],
    "keyword_mappings": {
      "serper": ["price", "buy", "shop", "cost", "deal", "near me", "weather"],
      "tavily": ["how does", "explain", "research", "what is", "tutorial"],
      "exa": ["similar to", "companies like", "alternatives", "startup", "github"]
    }
  },
  
  "serper": {
    "country": "us",
    "language": "en"
  },
  
  "tavily": {
    "depth": "basic",
    "topic": "general"
  },
  
  "exa": {
    "type": "neural"
  }
}
```

### Configuration Examples

#### Example 1: Disable Exa (Only Use Serper + Tavily)

```json
{
  "auto_routing": {
    "disabled_providers": ["exa"]
  }
}
```

#### Example 2: Make Tavily the Default

```json
{
  "auto_routing": {
    "fallback_provider": "tavily"
  }
}
```

#### Example 3: Add Custom Keywords

```json
{
  "auto_routing": {
    "keyword_mappings": {
      "serper": [
        "price", "buy", "shop", "amazon", "ebay", "walmart",
        "deal", "discount", "coupon", "sale", "cheap"
      ],
      "tavily": [
        "how does", "explain", "research", "what is",
        "coursera", "udemy", "learn", "course", "certification"
      ],
      "exa": [
        "similar to", "companies like", "competitors",
        "YC company", "funded startup", "Series A", "Series B"
      ]
    }
  }
}
```

#### Example 4: German Locale for Serper

```json
{
  "serper": {
    "country": "de",
    "language": "de"
  }
}
```

#### Example 5: Disable Auto-Routing

```json
{
  "auto_routing": {
    "enabled": false
  },
  "defaults": {
    "provider": "serper"
  }
}
```

#### Example 6: Research-Heavy Config

```json
{
  "auto_routing": {
    "fallback_provider": "tavily",
    "provider_priority": ["tavily", "serper", "exa"]
  },
  "tavily": {
    "depth": "advanced",
    "include_raw_content": true
  }
}
```

---

## Provider Deep Dives

### Serper (Google Search API)

**What it is:** Direct access to Google Search results via API — the same results you'd see on google.com.

#### Strengths
| Strength | Description |
|----------|-------------|
| 🎯 **Accuracy** | Google's search quality, knowledge graph, featured snippets |
| 🛒 **Shopping** | Product prices, reviews, shopping results |
| 📍 **Local** | Business listings, maps, places |
| 📰 **News** | Real-time news with Google News integration |
| 🖼️ **Images** | Google Images search |
| ⚡ **Speed** | Fastest response times (~200-400ms) |

#### Best Use Cases
- ✅ Product specifications and comparisons
- ✅ Shopping and price lookups
- ✅ Local business searches ("restaurants near me")
- ✅ Quick factual queries (weather, conversions, definitions)
- ✅ News headlines and current events
- ✅ Image searches
- ✅ When you need "what Google shows"

#### Getting Your API Key
1. Go to [serper.dev](https://serper.dev)
2. Sign up with email or Google
3. Copy your API key from the dashboard
4. Set `SERPER_API_KEY` environment variable

---

### Tavily (Research Search)

**What it is:** AI-optimized search engine built for research and RAG applications — returns synthesized answers plus full content.

#### Strengths
| Strength | Description |
|----------|-------------|
| 📚 **Research Quality** | Optimized for comprehensive, accurate research |
| 💬 **AI Answers** | Returns synthesized answers, not just links |
| 📄 **Full Content** | Can return complete page content (raw_content) |
| 🎯 **Domain Filtering** | Include/exclude specific domains |
| 🔬 **Deep Mode** | Advanced search for thorough research |
| 📰 **Topic Modes** | Specialized for general vs news content |

#### Best Use Cases
- ✅ Research questions requiring synthesized answers
- ✅ Academic or technical deep dives
- ✅ When you need actual page content (not just snippets)
- ✅ Multi-source information comparison
- ✅ Domain-specific research (filter to authoritative sources)
- ✅ News research with context
- ✅ RAG/LLM applications

#### Getting Your API Key
1. Go to [tavily.com](https://tavily.com)
2. Sign up and verify email
3. Navigate to API Keys section
4. Generate and copy your key
5. Set `TAVILY_API_KEY` environment variable

---

### Exa (Neural Search)

**What it is:** Neural/semantic search engine that understands meaning, not just keywords — finds conceptually similar content.

#### Strengths
| Strength | Description |
|----------|-------------|
| 🧠 **Semantic Understanding** | Finds results by meaning, not keywords |
| 🔗 **Similar Pages** | Find pages similar to a reference URL |
| 🏢 **Company Discovery** | Excellent for finding startups, companies |
| 📑 **Category Filters** | Filter by type (company, paper, tweet, etc.) |
| 📅 **Date Filtering** | Precise date range searches |
| 🎓 **Academic** | Great for research papers and technical content |

#### Best Use Cases
- ✅ Conceptual queries ("companies building X")
- ✅ Finding similar companies or pages
- ✅ Startup and company discovery
- ✅ Research paper discovery
- ✅ Finding GitHub projects
- ✅ Date-filtered searches for recent content
- ✅ When keyword matching fails

#### Getting Your API Key
1. Go to [exa.ai](https://exa.ai)
2. Sign up with email or Google
3. Navigate to API section in dashboard
4. Copy your API key
5. Set `EXA_API_KEY` environment variable

---

## Usage Examples

### Auto-Routed Searches (Recommended)

```bash
# Just search — the skill picks the best provider
python3 scripts/search.py -q "Tesla Model 3 price"
python3 scripts/search.py -q "how do neural networks learn"
python3 scripts/search.py -q "YC startups like Stripe"
```

### Serper Options

```bash
# Different search types
python3 scripts/search.py -p serper -q "gaming monitor" --type shopping
python3 scripts/search.py -p serper -q "coffee shop" --type places
python3 scripts/search.py -p serper -q "AI news" --type news

# With time filter
python3 scripts/search.py -p serper -q "OpenAI news" --time-range day

# Include images
python3 scripts/search.py -p serper -q "iPhone 16 Pro" --images

# Different locale
python3 scripts/search.py -p serper -q "Wetter Wien" --country at --language de
```

### Tavily Options

```bash
# Deep research mode
python3 scripts/search.py -p tavily -q "quantum computing applications" --depth advanced

# With full page content
python3 scripts/search.py -p tavily -q "transformer architecture" --raw-content

# Domain filtering
python3 scripts/search.py -p tavily -q "AI research" --include-domains arxiv.org nature.com
```

### Exa Options

```bash
# Category filtering
python3 scripts/search.py -p exa -q "AI startups Series A" --category company
python3 scripts/search.py -p exa -q "attention mechanism" --category "research paper"

# Date filtering
python3 scripts/search.py -p exa -q "YC companies" --start-date 2024-01-01

# Find similar pages
python3 scripts/search.py -p exa --similar-url "https://stripe.com" --category company
```

---

## Workflow Examples

### 🛒 Product Research Workflow

```bash
# Step 1: Get product specs (auto-routed to Serper)
python3 scripts/search.py -q "MacBook Pro M3 Max specs"

# Step 2: Check prices (auto-routed to Serper)
python3 scripts/search.py -q "MacBook Pro M3 Max price comparison"

# Step 3: In-depth reviews (auto-routed to Tavily)
python3 scripts/search.py -q "detailed MacBook Pro M3 Max review"
```

### 📚 Academic Research Workflow

```bash
# Step 1: Understand the topic (auto-routed to Tavily)
python3 scripts/search.py -q "explain transformer architecture in deep learning"

# Step 2: Find recent papers (Exa)
python3 scripts/search.py -p exa -q "transformer improvements" --category "research paper" --start-date 2024-01-01

# Step 3: Find implementations (Exa)
python3 scripts/search.py -p exa -q "transformer implementation" --category github
```

### 🏢 Competitive Analysis Workflow

```bash
# Step 1: Find competitors (auto-routed to Exa)
python3 scripts/search.py -q "companies like Notion"

# Step 2: Find similar products (Exa)
python3 scripts/search.py -p exa --similar-url "https://notion.so" --category company

# Step 3: Deep dive comparison (Tavily)
python3 scripts/search.py -p tavily -q "Notion vs Coda comparison" --depth advanced
```

---

## Optimization Tips

### Cost Optimization

| Tip | Savings |
|-----|---------|
| Use auto-routing (defaults to Serper, cheapest) | Best value |
| Use Tavily `basic` before `advanced` | ~50% cost reduction |
| Set appropriate `max_results` | Linear cost savings |
| Use Exa only for semantic queries | Avoid waste |

### Performance Optimization

| Tip | Impact |
|-----|--------|
| Serper is fastest (~200ms) | Use for time-sensitive queries |
| Tavily `basic` faster than `advanced` | ~2x faster |
| Lower `max_results` = faster response | Linear improvement |

---

## FAQ & Troubleshooting

### General Questions

**Q: Do I need API keys for all three providers?**
> No. You only need keys for providers you want to use. Auto-routing skips providers without keys.

**Q: Which provider should I start with?**
> Serper — it's the fastest, cheapest, and has the largest free tier (2,500 queries).

**Q: Can I use multiple providers in one workflow?**
> Yes! That's the recommended approach. See [Workflow Examples](#workflow-examples).

**Q: How do I reduce API costs?**
> Use auto-routing (defaults to cheapest), start with lower `max_results`, use Tavily `basic` before `advanced`.

### Auto-Routing Questions

**Q: Why did my query go to the wrong provider?**
> Use `--explain-routing` to debug. Add custom keywords to config.json if needed.

**Q: Can I add my own keywords?**
> Yes! Edit `config.json` → `auto_routing.keyword_mappings`.

**Q: How does keyword scoring work?**
> Multi-word phrases get higher weights. "companies like" (2 words) scores higher than "like" (1 word).

**Q: What if no keywords match?**
> Uses the fallback provider (default: Serper).

**Q: Can I force a specific provider?**
> Yes, use `-p serper`, `-p tavily`, or `-p exa`.

### Troubleshooting

**Error: "Missing API key"**
```bash
# Check if key is set
echo $SERPER_API_KEY

# Set it
export SERPER_API_KEY="your-key"
```

**Error: "API Error (401)"**
> Your API key is invalid or expired. Generate a new one.

**Error: "API Error (429)"**
> Rate limited. Wait and retry, or upgrade your plan.

**Empty results?**
> Try a different provider, broaden your query, or remove restrictive filters.

**Slow responses?**
> Reduce `max_results`, use Tavily `basic`, or use Serper (fastest).

---

## API Reference

### Output Format

All providers return unified JSON:

```json
{
  "provider": "serper|tavily|exa",
  "query": "original search query",
  "results": [
    {
      "title": "Page Title",
      "url": "https://example.com/page",
      "snippet": "Content excerpt...",
      "score": 0.95,
      "date": "2024-01-15",
      "raw_content": "Full page content (Tavily only)"
    }
  ],
  "images": ["url1", "url2"],
  "answer": "Synthesized answer",
  "knowledge_graph": { },
  "routing": {
    "auto_routed": true,
    "selected_provider": "serper",
    "reason": "matched_keywords (score=1)",
    "matched_keywords": ["price"]
  }
}
```

### CLI Options Reference

| Option | Providers | Description |
|--------|-----------|-------------|
| `-q, --query` | All | Search query |
| `-p, --provider` | All | Provider: auto, serper, tavily, exa |
| `-n, --max-results` | All | Max results (default: 5) |
| `--auto` | All | Force auto-routing |
| `--explain-routing` | All | Debug auto-routing |
| `--images` | Serper, Tavily | Include images |
| `--country` | Serper | Country code (default: us) |
| `--language` | Serper | Language code (default: en) |
| `--type` | Serper | search/news/images/videos/places/shopping |
| `--time-range` | Serper | hour/day/week/month/year |
| `--depth` | Tavily | basic/advanced |
| `--topic` | Tavily | general/news |
| `--raw-content` | Tavily | Include full page content |
| `--exa-type` | Exa | neural/keyword |
| `--category` | Exa | company/research paper/news/pdf/github/tweet |
| `--start-date` | Exa | Start date (YYYY-MM-DD) |
| `--end-date` | Exa | End date (YYYY-MM-DD) |
| `--similar-url` | Exa | Find similar pages |
| `--include-domains` | Tavily, Exa | Only these domains |
| `--exclude-domains` | Tavily, Exa | Exclude these domains |
| `--compact` | All | Compact JSON output |

---

## License

MIT

---

## Links

- [Serper](https://serper.dev) — Google Search API
- [Tavily](https://tavily.com) — AI Research Search
- [Exa](https://exa.ai) — Neural Search
- [ClawdHub](https://clawdhub.com) — Clawdbot Skills
