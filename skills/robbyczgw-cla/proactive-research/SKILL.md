---
name: proactive-research
description: Monitor topics of interest and proactively alert when important developments occur. Use when user wants automated monitoring of specific subjects (e.g., product releases, price changes, news topics, technology updates). Supports scheduled web searches, AI-powered importance scoring, smart alerts vs weekly digests, and memory-aware contextual summaries.
---

# Proactive Research

**Monitor what matters. Get notified when it happens.**

Proactive Research transforms your assistant from reactive to proactive by continuously monitoring topics you care about and intelligently alerting you only when something truly matters.

## Core Capabilities

1. **Topic Configuration** - Define subjects with custom parameters
2. **Scheduled Monitoring** - Automated searches at configurable intervals
3. **AI Importance Scoring** - Smart filtering: immediate alert vs digest vs ignore
4. **Contextual Summaries** - Not just links—meaningful summaries with context
5. **Weekly Digest** - Low-priority findings compiled into readable reports
6. **Memory Integration** - References your past conversations and interests

## Quick Start

```bash
# Initialize config
cp config.example.json config.json

# Add a topic
python3 scripts/manage_topics.py add "Dirac Live updates" \
  --keywords "Dirac Live,room correction,audio" \
  --frequency daily \
  --importance medium

# Test monitoring (dry run)
python3 scripts/monitor.py --dry-run

# Set up cron for automatic monitoring
python3 scripts/setup_cron.py
```

## Topic Configuration

Each topic has:

- **name** - Display name (e.g., "ETH Price Tracking")
- **query** - Search query (e.g., "Ethereum price USD")
- **keywords** - Relevance filters (["ETH", "Ethereum", "price"])
- **frequency** - `hourly`, `daily`, `weekly`
- **importance_threshold** - `high` (alert immediately), `medium` (alert if important), `low` (digest only)
- **channels** - Where to send alerts (["telegram", "discord"])
- **context** - Why you care (for AI contextual summaries)

### Example config.json

```json
{
  "topics": [
    {
      "id": "eth-price",
      "name": "ETH Price Alerts",
      "query": "Ethereum price significant change",
      "keywords": ["ETH", "Ethereum", "cryptocurrency"],
      "frequency": "hourly",
      "importance_threshold": "high",
      "channels": ["telegram"],
      "context": "Tracking for investment decisions",
      "alert_on": ["price_change_10pct", "major_news"]
    },
    {
      "id": "fm26-patches",
      "name": "Football Manager 26 Updates",
      "query": "Football Manager 2026 patch update",
      "keywords": ["FM26", "patch", "update", "Sports Interactive"],
      "frequency": "daily",
      "importance_threshold": "medium",
      "channels": ["telegram"],
      "context": "Playing career mode, want bug fixes",
      "alert_on": ["patch_release", "major_bug_fix"]
    },
    {
      "id": "ai-breakthroughs",
      "name": "AI Research Breakthroughs",
      "query": "artificial intelligence breakthrough research",
      "keywords": ["AI", "LLM", "transformer", "AGI"],
      "frequency": "daily",
      "importance_threshold": "medium",
      "channels": ["telegram"],
      "context": "Following AI developments for work",
      "alert_on": ["major_paper", "model_release"]
    }
  ],
  "settings": {
    "digest_day": "sunday",
    "digest_time": "18:00",
    "max_alerts_per_day": 5,
    "deduplication_window_hours": 72,
    "learning_enabled": true
  }
}
```

## Scripts

### manage_topics.py

Manage research topics:

```bash
# Add topic
python3 scripts/manage_topics.py add "Topic Name" \
  --query "search query" \
  --keywords "word1,word2" \
  --frequency daily \
  --importance medium \
  --channels telegram

# List topics
python3 scripts/manage_topics.py list

# Edit topic
python3 scripts/manage_topics.py edit eth-price --frequency hourly

# Remove topic
python3 scripts/manage_topics.py remove eth-price

# Test topic (preview results without saving)
python3 scripts/manage_topics.py test eth-price
```

### monitor.py

Main monitoring script (run via cron):

```bash
# Normal run (alerts + saves state)
python3 scripts/monitor.py

# Dry run (no alerts, shows what would happen)
python3 scripts/monitor.py --dry-run

# Force check specific topic
python3 scripts/monitor.py --topic eth-price

# Verbose logging
python3 scripts/monitor.py --verbose
```

**How it works:**
1. Reads topics due for checking (based on frequency)
2. Searches using web-search-plus or built-in web_search
3. Scores each result with AI importance scorer
4. High-importance → immediate alert
5. Medium-importance → saved for digest
6. Low-importance → ignored
7. Updates state to prevent duplicate alerts

### digest.py

Generate weekly digest:

```bash
# Generate digest for current week
python3 scripts/digest.py

# Generate and send
python3 scripts/digest.py --send

# Preview without sending
python3 scripts/digest.py --preview
```

Output format:
```markdown
# Weekly Research Digest - [Date Range]

## 🔥 Highlights

- **ETH Price**: Jumped 15% following SEC approval news
- **FM26**: Patch 26.3.1 released fixing transfer bug you reported

## 📊 By Topic

### ETH Price Tracking
- [3 findings this week]

### Football Manager 26 Updates
- [1 finding this week]

## 💡 Recommendations

Based on your interests, you might want to monitor:
- "SEC crypto regulation" (mentioned 3x this week)
```

### setup_cron.py

Configure automated monitoring:

```bash
# Interactive setup
python3 scripts/setup_cron.py

# Auto-setup with defaults
python3 scripts/setup_cron.py --auto

# Remove cron jobs
python3 scripts/setup_cron.py --remove
```

Creates cron entries:
```cron
# Proactive Research - Hourly topics
0 * * * * cd /path/to/skills/proactive-research && python3 scripts/monitor.py --frequency hourly

# Proactive Research - Daily topics  
0 9 * * * cd /path/to/skills/proactive-research && python3 scripts/monitor.py --frequency daily

# Proactive Research - Weekly digest
0 18 * * 0 cd /path/to/skills/proactive-research && python3 scripts/digest.py --send
```

## AI Importance Scoring

The scorer uses multiple signals to decide alert priority:

### Scoring Signals

**HIGH priority (immediate alert):**
- Major breaking news (detected via freshness + keyword density)
- Price changes >10% (for finance topics)
- Product releases matching your exact keywords
- Security vulnerabilities in tools you use
- Direct answers to specific questions you asked

**MEDIUM priority (digest-worthy):**
- Related news but not urgent
- Minor updates to tracked products
- Interesting developments in your topics
- Tutorial/guide releases
- Community discussions with high engagement

**LOW priority (ignore):**
- Duplicate news (already alerted)
- Tangentially related content
- Low-quality sources
- Outdated information
- Spam/promotional content

### Learning Mode

When enabled (`learning_enabled: true`), the system:
1. Tracks which alerts you interact with
2. Adjusts scoring weights based on your behavior
3. Suggests topic refinements
4. Auto-adjusts importance thresholds

Learning data stored in `.learning_data.json` (privacy-safe, never shared).

## Memory Integration

Proactive Research connects to your conversation history:

**Example alert:**
> 🔔 **Dirac Live Update**
> 
> Version 3.8 released with the room correction improvements you asked about last week.
> 
> **Context:** You mentioned struggling with bass response in your studio. This update includes new low-frequency optimization.
> 
> [Link] | [Full details]

**How it works:**
1. Reads references/memory_hints.md (create this file)
2. Scans recent conversation logs (if available)
3. Matches findings to past context
4. Generates personalized summaries

### memory_hints.md (optional)

Help the AI connect dots:

```markdown
# Memory Hints for Proactive Research

## ETH Price
- Tracking for potential investment
- Interested in regulatory news (SEC, EU)
- Sold at $2800, watching for re-entry

## FM26
- Playing career mode with custom tactics
- Frustrated by transfer bug (should be fixed now)
- Interested in editor updates

## Dirac Live
- Setting up home studio
- Using with miniDSP
- Struggling with bass management below 80Hz
```

## Alert Channels

### Telegram

Requires Moltbot message tool:

```json
{
  "channels": ["telegram"],
  "telegram_config": {
    "chat_id": "@your_username",
    "silent": false,
    "effects": {
      "high_importance": "🔥",
      "medium_importance": "📌"
    }
  }
}
```

### Discord

Webhook-based:

```json
{
  "channels": ["discord"],
  "discord_config": {
    "webhook_url": "https://discord.com/api/webhooks/...",
    "username": "Research Bot",
    "avatar_url": "https://..."
  }
}
```

### Email

SMTP or API:

```json
{
  "channels": ["email"],
  "email_config": {
    "to": "you@example.com",
    "from": "research@yourdomain.com",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
  }
}
```

## Advanced Features

### Alert Conditions

Fine-tune when to alert:

```json
{
  "alert_on": [
    "price_change_10pct",
    "keyword_exact_match",
    "source_tier_1",
    "high_engagement"
  ],
  "ignore_sources": [
    "spam-site.com",
    "clickbait-news.io"
  ],
  "boost_sources": [
    "github.com",
    "arxiv.org",
    "official-site.com"
  ]
}
```

### Regex Patterns

Match specific patterns:

```json
{
  "patterns": [
    "version \\d+\\.\\d+\\.\\d+",
    "\\$\\d{1,3}(,\\d{3})*",
    "CVE-\\d{4}-\\d+"
  ]
}
```

### Rate Limiting

Prevent alert fatigue:

```json
{
  "settings": {
    "max_alerts_per_day": 5,
    "max_alerts_per_topic_per_day": 2,
    "quiet_hours": {
      "start": "22:00",
      "end": "08:00"
    }
  }
}
```

## State Management

### .research_state.json

Tracks:
- Last check time per topic
- Alerted URLs (deduplication)
- Importance scores history
- Learning data (if enabled)

Example:
```json
{
  "topics": {
    "eth-price": {
      "last_check": "2026-01-28T22:00:00Z",
      "last_alert": "2026-01-28T15:30:00Z",
      "alerted_urls": [
        "https://example.com/eth-news-1"
      ],
      "findings_count": 3,
      "alerts_today": 1
    }
  },
  "deduplication": {
    "url_hash_map": {
      "abc123": "2026-01-28T15:30:00Z"
    }
  }
}
```

### .findings/ directory

Stores digest-worthy findings:

```
.findings/
├── 2026-01-22_eth-price.json
├── 2026-01-24_fm26-patches.json
└── 2026-01-27_ai-breakthroughs.json
```

## Best Practices

1. **Start conservative** - Set `importance_threshold: medium` initially, adjust based on alert quality
2. **Use context field** - Helps AI generate better summaries
3. **Refine keywords** - Add negative keywords to filter noise: `"keywords": ["ETH", "-scam", "-airdrop"]`
4. **Enable learning** - Improves over time based on your behavior
5. **Review digest weekly** - Don't ignore the digest—it surfaces patterns
6. **Combine with personal-analytics** - Get topic recommendations based on your chat patterns

## Integration with Other Skills

### web-search-plus

Automatically uses intelligent routing:
- Product/price topics → Serper
- Research topics → Tavily  
- Company/startup discovery → Exa

### personal-analytics

Suggests topics based on conversation patterns:
> "You've asked about Rust 12 times this month. Want me to monitor 'Rust language updates'?"

## Privacy & Security

- **All data local** - No external services except search APIs
- **State files gitignored** - Safe to use in version-controlled workspace
- **Memory hints optional** - You control what context is shared
- **Learning data stays local** - Never sent to APIs

## Troubleshooting

**No alerts being sent:**
- Check cron is running: `crontab -l`
- Verify channel config (Telegram chat ID, Discord webhook)
- Run with `--dry-run --verbose` to see scoring

**Too many alerts:**
- Increase `importance_threshold`
- Add rate limiting
- Refine keywords (add negative filters)
- Enable learning mode

**Missing important news:**
- Decrease `importance_threshold`
- Increase check frequency
- Broaden keywords
- Check `.research_state.json` for deduplication issues

**Digest not generating:**
- Verify `.findings/` directory exists and has content
- Check digest cron schedule
- Run manually: `python3 scripts/digest.py --preview`

## Example Workflows

### Track Product Release

```bash
python3 scripts/manage_topics.py add "iPhone 17 Release" \
  --query "iPhone 17 announcement release date" \
  --keywords "iPhone 17,Apple event,September" \
  --frequency daily \
  --importance high \
  --channels telegram \
  --context "Planning to upgrade from iPhone 13"
```

### Monitor Competitor

```bash
python3 scripts/manage_topics.py add "Competitor Analysis" \
  --query "CompetitorCo product launch funding" \
  --keywords "CompetitorCo,product,launch,Series,funding" \
  --frequency weekly \
  --importance medium \
  --channels discord,email
```

### Research Topic

```bash
python3 scripts/manage_topics.py add "Quantum Computing Papers" \
  --query "quantum computing arxiv" \
  --keywords "quantum,qubit,arxiv" \
  --frequency weekly \
  --importance low \
  --channels email
```

## Credits

Built for ClawdHub. Uses web-search-plus skill for intelligent search routing.
