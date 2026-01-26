---
name: clawd-docs-v2
description: Smart ClawdBot documentation access with local search index, cached snippets, and on-demand fetch. Token-efficient and freshness-aware.
homepage: https://docs.clawd.bot/
metadata: {"clawdbot":{"emoji":"📚","requires":{"bins":["mcporter"]}}}
version: 2.1.3
---

# Clawd-Docs v2.1 - Smart Documentation Access

This skill provides **intelligent access** to ClawdBot documentation with:
- **Local search index** - instant keyword lookup (0 tokens)
- **Cached snippets** - pre-fetched common answers (~300-500 tokens)
- **On-demand fetch** - full page when needed (~8-12k tokens)
- **Freshness tracking** - TTL per page type

---

## ⚠️ IMPORTANT: This is NOT Auto-Magic!

**Real-world experience shows:**
- Snippets have TTL and **WILL expire**
- You must **manually check** `expires` header before trusting info
- Run `docs-refresh.sh check` **weekly** to see what's outdated
- Manual maintenance is required for fresh content

**Before using ANY snippet, ALWAYS check:**
```bash
head -5 ~/clawd/data/docs-snippets/[snippet].md | grep expires
```

If `expires` date is in the past → **warn user that info may be outdated!**

---

## Quick Start

### Step 0: Check Freshness FIRST!

```bash
# See what's expired
~/clawd/data/docs-refresh.sh check

# See what changed since last refresh
~/clawd/data/docs-refresh.sh changes
```

### Step 1: Check Golden Snippets

Before fetching anything, check if a **Golden Snippet** exists:

```bash
ls ~/clawd/data/docs-snippets/
```

**Available snippets (most used first):**

| Snippet | Query matches | Usage |
|---------|---------------|-------|
| `telegram-allowfrom.md` | "allowFrom", "kto mi môže písať" | ⭐ High |
| `oauth-troubleshoot.md` | "token expired", "oauth error" | ⭐ High |
| `update-procedure.md` | "ako updatnuť", "update clawdbot" | ⭐ High |
| `restart-gateway.md` | "restart", "reštart", "stop/start" | Medium |
| `telegram-setup.md` | "ako nastaviť telegram" | Medium |
| `config-basics.md` | "config", "nastavenie" | Medium |
| `config-providers.md` | "pridať provider", "discord setup" | Low |
| `memory-search.md` | "memory", "vector search", "pamäť" | Low |

**Read snippet (but CHECK EXPIRES FIRST!):**
```bash
# Check if expired
head -10 ~/clawd/data/docs-snippets/telegram-setup.md | grep expires

# Then read
cat ~/clawd/data/docs-snippets/telegram-setup.md
```

### Step 2: Search Index (if snippet doesn't exist)

Check `~/clawd/data/docs-index.json` for page suggestions.

**Keyword matching:**
- "telegram" → channels/telegram
- "oauth" → concepts/oauth, gateway/troubleshooting
- "update" → install/updating
- "config" → gateway/configuration

### Step 3: Check Full Page Cache

**BEFORE fetching via brightdata**, check if the page is already cached:

```bash
# Convert path: concepts/memory → concepts_memory.md
ls ~/clawd/data/docs-cache/ | grep "concepts_memory"
```

**If exists, read locally (0 tokens!):**
```bash
cat ~/clawd/data/docs-cache/concepts_memory.md
```

### Step 4: Fetch Page (only if NOT in cache or expired)

```bash
mcporter call brightdata.scrape_as_markdown url="https://docs.clawd.bot/{path}"
```

**Example:**
```bash
mcporter call brightdata.scrape_as_markdown url="https://docs.clawd.bot/tools/skills"
```

---

## Recommended Workflow (Real-World Tested)

### When answering a documentation question:

```
1. Check if snippet exists for this topic
   ↓
2. If snippet exists:
   a. Check `expires` header
   b. If EXPIRED → warn user "Info may be outdated"
   c. Offer: "Want me to fetch fresh version?"
   ↓
3. If no snippet → check docs-cache
   ↓
4. If not in cache → fetch via brightdata
   ↓
5. Answer the question
```

### Weekly maintenance (recommended):

```bash
# Check what's expired
~/clawd/data/docs-refresh.sh check

# See any content changes
~/clawd/data/docs-refresh.sh changes

# Refresh critical pages (install/updating changes often!)
~/clawd/data/docs-refresh.sh refresh install_updating
mcporter call brightdata.scrape_as_markdown url="https://docs.clawd.bot/install/updating"
# Save output to ~/clawd/data/docs-cache/install_updating.md
~/clawd/data/docs-refresh.sh finalize install_updating
```

---

## Search Index Structure

**Location:** `~/clawd/data/docs-index.json`

```json
{
  "pages": [
    {
      "path": "channels/telegram",
      "ttl_days": 7,
      "keywords": ["telegram", "tg", "bot", "allowfrom"]
    }
  ],
  "synonyms": {
    "telegram": ["tg", "telegrambot"],
    "configuration": ["config", "nastavenie", "settings"]
  }
}
```

**Use synonyms** for fuzzy matching.

---

## TTL Strategy (Freshness)

| Page Category | TTL | Why |
|---------------|-----|-----|
| `install/updating` | 1 day | Always current! |
| `gateway/*` | 7 days | Config changes |
| `channels/*` | 7 days | Provider updates |
| `tools/*` | 7 days | Features added |
| `concepts/*` | 14 days | Rarely changes |
| `reference/*` | 30 days | Stable templates |

**Check snippet expiry:**
```bash
head -10 ~/clawd/data/docs-snippets/telegram-setup.md | grep expires
```

---

## Hash-Based Change Detection

The refresh script tracks content changes via MD5 hashes:

```bash
# Check current hash of a page
~/clawd/data/docs-refresh.sh hash install_updating

# Output shows:
# - Current file hash
# - Stats hash (from last known state)
# - Previous hash (before last refresh)
# - Changed: true/false
```

**⚠️ IMPORTANT: `check` vs actual changes**

| Command | What it shows |
|---------|---------------|
| `check` | Pages where **TTL expired** (doesn't mean content changed!) |
| `changes` | Pages that **actually changed** during last refresh |
| `refresh` | Fetches new content and **compares hashes** |

**To verify if a page ACTUALLY changed on the web:**
1. Run `refresh <page>` → fetches fresh content
2. Script compares MD5 hash (old vs new)
3. If different → `changed: true`
4. See all changes with `docs-refresh.sh changes`

**Common mistake:** Running `check`, seeing "155 expired" and assuming content changed. 
**Reality:** TTL expiry is just a **trigger to verify** — actual changes are detected only after refresh!

**How it works:**
1. When you refresh a page, script calculates MD5 of new content
2. Compares with stored hash in `docs-stats.json`
3. If different → marks page as `changed: true`
4. You can see all changed pages with `docs-refresh.sh changes`

---

## Common Scenarios

### "Ako nastaviť Telegram?"
1. Check expires: `head -5 ~/clawd/data/docs-snippets/telegram-setup.md`
2. ✅ If fresh → Read snippet
3. ⚠️ If expired → Warn user, offer fresh fetch

### "allowFrom nefunguje"
1. ✅ Read `~/clawd/data/docs-snippets/telegram-allowfrom.md`
2. This is a HIGH-USE snippet - keep it fresh!

### "Token expired / oauth error"
1. ✅ Read `~/clawd/data/docs-snippets/oauth-troubleshoot.md`
2. This is a HIGH-USE snippet - keep it fresh!

### "Ako updatnúť ClawdBot?"
1. ⚠️ **ALWAYS fetch fresh!** Update info changes frequently
2. `mcporter call brightdata.scrape_as_markdown url="https://docs.clawd.bot/install/updating"`

### "Ako pridať nový skill?" (nie je snippet)
1. Search index → tools/skills
2. Fetch: `mcporter call brightdata.scrape_as_markdown url="https://docs.clawd.bot/tools/skills"`

---

## Fallback: Full Index Refresh

If you can't find what you need:

```bash
mcporter call brightdata.scrape_as_markdown url="https://docs.clawd.bot/llms.txt"
```

Returns **complete list** of all documentation pages.

---

## Token Efficiency Guide

| Method | Tokens | When to use |
|--------|--------|-------------|
| Golden Snippet | ~300-500 | ✅ First choice (if fresh!) |
| Search Index | 0 | Keyword lookup |
| Full Page Fetch | ~8-12k | When snippet expired or missing |
| Batch Fetch | ~20-30k | Multiple related topics |

**Realistic expectation:** 60-70% of common queries from snippets (if maintained)

---

## Data Locations

```
~/clawd/data/
├── docs-index.json       # Search index (99 pages)
├── docs-stats.json       # Usage + hash tracking
├── docs-refresh.sh       # Maintenance script
├── docs-snippets/        # Golden Snippets (8 files)
│   ├── telegram-setup.md
│   ├── telegram-allowfrom.md
│   ├── oauth-troubleshoot.md
│   ├── update-procedure.md
│   ├── restart-gateway.md
│   ├── config-basics.md
│   ├── config-providers.md
│   └── memory-search.md
└── docs-cache/           # Full page cache
```

---

## Version Info

| Item | Value |
|------|-------|
| **Skill version** | 2.1.0 |
| **Created** | 2026-01-14 |
| **Updated** | 2026-01-25 |
| **Authors** | Claude Code + Clawd (Synteza collaborative) |
| **Source** | https://docs.clawd.bot/ |
| **Dependencies** | brightdata skill (mcporter) |
| **Index pages** | 99 pages |
| **Golden snippets** | 8 pre-cached |

---

## Changelog

### v2.1.3 (2026-01-25)
- Clarified difference between TTL expiry (`check`) and actual content changes (`refresh`)
- Added warning table about common mistake (expired ≠ changed)

### v2.1.0 (2026-01-25)
- Added real-world usage warnings
- Documented hash-based change detection
- Added maintenance workflow
- Marked high-use vs low-use snippets
- Realistic token efficiency expectations

### v2.0.0 (2026-01-14)
- 3-layer architecture: Search Index → Snippets → On-demand Fetch
- Golden Snippets pre-cached for common queries
- TTL-based freshness tracking
- Synonym support for fuzzy matching
- 80-90% token reduction for common queries

### v1.0.0 (2026-01-08)
- Initial release with brightdata fetch only

---

## Honest Assessment

**What works well:**
- Token savings when snippets are fresh
- Search index for finding relevant pages
- Hash detection for tracking content changes

**What requires attention:**
- Manual maintenance needed
- Snippets expire and need refresh
- Not "set and forget" - requires weekly check

**Recommended for:** Users who will commit to occasional maintenance

---

*This skill provides smart documentation access with honest expectations about maintenance requirements.*
