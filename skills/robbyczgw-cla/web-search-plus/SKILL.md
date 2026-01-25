---
name: web-search-plus
version: 2.1.2
description: Unified search skill with Intelligent Auto-Routing. Uses multi-signal analysis to automatically select between Serper (Google), Tavily (Research), and Exa (Neural) with confidence scoring.
---

# Web Search Plus

Multi-provider web search with **Intelligent Auto-Routing**: Serper (Google), Tavily (Research), Exa (Neural).

**NEW in v2.1.0**: Intelligent multi-signal analysis with confidence scoring!

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
  "tavily": {"depth": "basic"},
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

## Environment Setup

```bash
# In your .env file (use 'export' prefix!):
export SERPER_API_KEY="your-key"   # https://serper.dev
export TAVILY_API_KEY="your-key"   # https://tavily.com  
export EXA_API_KEY="your-key"      # https://exa.ai

# Then load with: source .env
```

---

## FAQ

**Q: How does it decide which provider to use?**
> Multi-signal analysis: It detects price patterns, explanation phrases, similarity keywords, URLs, product+brand combos, query complexity, and more. Each signal has a weight, and the provider with the highest total score wins.

**Q: What if it picks the wrong provider?**
> Use `--explain-routing` to see why. You can also use `-p serper/tavily/exa` to override.

**Q: What does "low confidence" mean?**
> The query is ambiguous (e.g., just "Tesla"). The fallback provider (Serper) is used, but results may vary.

**Q: Can I add custom routing rules?**
> Not yet via config, but you can modify the signal patterns in `search.py`.
