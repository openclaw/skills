# Architecture & Design Decisions

**Version:** 1.0  
**Date:** 2026-01-27  
**Author:** Research & audit by Clawd 🦊

---

## Why This Document Exists

This document explains why `crypto-price` does **not** use template generation for wrapper skills, and why the current architecture is optimal.

**TL;DR:** No refactoring needed. System already DRY.

---

## System Overview

### What We Have

**1 Core Script:**
- `scripts/get_price_chart.py` (~800 lines)
- All logic: API calls, caching, chart generation, error handling

**30 Wrapper Skills:**
- `../btc/SKILL.md`, `../eth/SKILL.md`, `../hype/SKILL.md`, ... (28 token wrappers)
- `../cryptochart/SKILL.md` (universal fallback)
- `../token/SKILL.md` (universal `/token ANY` command)
- Each wrapper = 35 lines: metadata + symbol + "call core script"

**Total duplication:** Zero. All wrappers call same script.

---

## Why No Template Generation?

### The Proposal (Rejected)

**Idea:** Generate wrappers from template to reduce duplication.

**Reality:** No duplication exists.

**Current wrapper:**
```yaml
---
name: BTC
description: Slash command for Bitcoin token price + chart.
metadata: {"clawdbot":{"emoji":"📈","requires":{"bins":["python3"]}}}
---

# Bitcoin Price

## Usage
/BTC
/BTC 12h

## Execution
python3 {baseDir}/../crypto-price/scripts/get_price_chart.py BTC

Return JSON output. Attach chart_path PNG.
Return text_plain with no markdown.
```

**Lines:** 35  
**Logic:** 0 (just metadata + symbol)

### Comparison: Manual vs Template

**Current (no template):**
```bash
# Add new token
cp btc/SKILL.md pepe/SKILL.md
vim pepe/SKILL.md  # Edit 3 places: name, description, symbol
# Done (2 minutes)
```

**With template:**
```bash
# Maintain template file
vim crypto-price/templates/token_wrapper.md
# Maintain generator script
vim crypto-price/scripts/generate_wrapper.sh
# Generate wrapper
./generate_wrapper.sh PEPE "Pepe Coin" pepe
# Debug if generator fails
# Done (5 minutes + maintenance overhead)
```

**Winner:** Current approach (simpler, fewer files, easier to understand)

---

## Maintenance Model

### Bug Fix Scenario

**Bug:** Chart generation broken

**Fix location:** `scripts/get_price_chart.py` (1 file)

**Impact:** All 30 wrapper skills fixed instantly

**Wrapper changes:** 0 files

**Time:** 10 minutes (edit core script only)

### Adding New Token

**Process:**
1. `cp ../btc/SKILL.md ../pepe/SKILL.md`
2. Edit 3 lines: `name: PEPE`, description, symbol
3. Done

**Time:** 2 minutes

**No template needed.**

---

## Architecture Principles

### 1. Single Source of Truth

**Core script** = all logic  
**Wrappers** = metadata only

**Result:** Bug fix in 1 place affects all 30 skills.

### 2. Minimal Wrappers

**Current:** 35 lines per wrapper  
**Can't reduce further** without losing readability

**Template would add complexity** (template file + generator script + docs) without reducing wrapper size.

### 3. Clear Separation of Concerns

**Core script:**
- API calls (Hyperliquid, CoinGecko)
- Caching (300s TTL)
- Chart generation (matplotlib)
- Error handling (retries, fallbacks)

**Wrappers:**
- Clawdbot metadata (name, description, emoji)
- Trigger conditions (slash command, keywords)
- Symbol mapping (e.g., `gld` → `GOLD-USDC`)

**Clawdbot:**
- Skill matching (user input → skill)
- Execution (run core script)
- Reply formatting (text + image)

### 4. Easy to Extend

**New token:** Copy wrapper + edit 3 lines

**No script maintenance needed.**

---

## Data Flow

```
User: /hype 12h
  ↓
Clawdbot: Match skill hype/SKILL.md
  ↓
Execute: python3 .../get_price_chart.py HYPE 12h
  ↓
Core Script:
  1. Parse duration
  2. Try Hyperliquid API
  3. Fallback to CoinGecko
  4. Check cache (5 min TTL)
  5. Generate chart (matplotlib)
  6. Return JSON
  ↓
Clawdbot: Send text + attach image
  ↓
User sees: Text + Chart
```

**Single entry point:** Core script  
**Single maintenance location:** Core script

---

## Testing Results

**Test 1: HYPE (Hyperliquid)**
```bash
$ python3 get_price_chart.py HYPE
{"symbol": "HYPE", "price": 27.31, "text_plain": "HYPE: $27.31 USD ⬆️ +22.60% over 24h"}
```
✅ Works

**Test 2: BTC 12h**
```bash
$ python3 get_price_chart.py BTC 12h
{"symbol": "BTC", "price": 88263.00, "text_plain": "BTC: $88263.00 USD ⬆️ +0.53% over 12h"}
```
✅ Works

**Test 3: Rate Limit**
```bash
$ python3 get_price_chart.py PEPE
{"error": "price lookup failed", "details": "HTTP Error 429: Too Many Requests"}
```
✅ Graceful error

**Test 4: Wrapper Consistency**
```bash
$ diff -u btc/SKILL.md eth/SKILL.md
-name: BTC
+name: ETH
-# Bitcoin Price
+# Ethereum Price
-get_price_chart.py BTC
+get_price_chart.py ETH
```
✅ Identical structure (only symbol differs)

---

## Risks Assessment

### Risk 1: Core Script Failure
**Scenario:** Bug in `get_price_chart.py` → all 30 skills break

**Likelihood:** LOW (stable for months)

**Mitigation:**
- Error handling in script
- Caching reduces API dependency
- Graceful degradation (price without chart if matplotlib fails)

**Impact:** HIGH (all token commands broken)

**Note:** Same risk exists regardless of wrapper structure. Not a refactoring issue.

### Risk 2: API Rate Limits
**Scenario:** CoinGecko 50 calls/min exceeded

**Likelihood:** MEDIUM (confirmed during testing)

**Mitigation:**
- 5-minute cache (TTL 300s)
- Hyperliquid fallback
- Retry logic with backoff

**Impact:** LOW (temporary failure, user retries in 5 min)

### Risk 3: Template Maintenance
**Scenario:** Template generator breaks

**Likelihood:** ZERO (no template exists)

**Current approach:** Manual copy-paste (simpler, no generator to maintain)

---

## Comparison: Current vs Template System

| Aspect | Current | With Template |
|--------|---------|---------------|
| Core logic files | 1 | 1 |
| Template files | 0 | 1 |
| Generator scripts | 0 | 1 |
| Wrapper files | 30 | 30 |
| Lines per wrapper | 35 | 35 (same) |
| Add new token | 2 min (copy + edit) | 5 min (run generator) |
| Maintenance overhead | Low (1 file) | Medium (3 files) |
| Debugging complexity | Low | Medium (script + template) |
| Learning curve | Low | Medium |

**Winner:** Current approach

---

## Alternatives Considered

### Alternative 1: Full Template Generation
**Idea:** Template file + generator script

**Pros:**
- Slightly more "automated"

**Cons:**
- More files to maintain (template + script + docs)
- More complexity (scripting, error handling)
- No reduction in wrapper size (still 35 lines)
- Slower than copy-paste

**Decision:** Rejected (adds complexity without benefit)

### Alternative 2: Single Universal Skill
**Idea:** Remove all wrappers, use only `/token ANY`

**Pros:**
- Fewer files

**Cons:**
- Worse UX (users must remember symbols)
- No autocomplete for popular tokens
- Loses slash command convenience (`/btc` vs `/token BTC`)

**Decision:** Rejected (UX downgrade)

### Alternative 3: Current System (Winner)
**Idea:** 1 core script + minimal wrappers (copy-paste to add tokens)

**Pros:**
- Simple (no template complexity)
- Fast (copy + edit 3 lines = 2 min)
- Easy to understand (no hidden generation logic)
- Zero duplication (all use same script)

**Cons:**
- None

**Decision:** Keep current system

---

## Common Misconceptions

### Misconception 1: "25 duplicate skills"
**Reality:** 28 wrappers + 2 utility skills, **zero logic duplication**

All wrappers call same script. No duplicated code.

### Misconception 2: "Maintenance nightmare"
**Reality:** Bug fix in 1 place (core script) = instant fix for all 30 skills

Wrappers never need maintenance (only core script).

### Misconception 3: "Template would reduce duplication"
**Reality:** No duplication exists to reduce

Wrappers are metadata-only (35 lines). Template wouldn't make them smaller.

### Misconception 4: "Hard to add new tokens"
**Reality:** 2 minutes to copy + edit 3 lines

Simpler than maintaining template + generator.

---

## Optional Improvements

**None required, but if desired:**

### 1. Add Unit Tests
**File:** `tests/test_get_price_chart.py`

**Why:**
- Catch bugs before deployment
- Validate API changes

**Effort:** 2-3 hours

### 2. Add Helper Script
**File:** `scripts/add_token.sh`

**Usage:**
```bash
./add_token.sh PEPE "Pepe Coin" pepe
# Creates ../pepe/SKILL.md from btc template
```

**Why:**
- Slightly faster than manual copy-paste
- Reduces typos

**Effort:** 30 minutes

**Note:** Still simpler than full template system.

### 3. Documentation
**File:** This document (`ARCHITECTURE.md`)

**Why:**
- Explain design decisions
- Prevent future "refactoring" attempts

**Effort:** Done

---

## Conclusion

### Summary

**System is optimal as-is:**

✅ 1 core script (all logic)  
✅ 30 minimal wrappers (metadata only)  
✅ Zero duplication  
✅ Easy maintenance (bug fix in 1 place)  
✅ Easy to extend (copy + edit 3 lines)

**Template generation would:**

❌ Add complexity (more files to maintain)  
❌ Slow down token addition (scripting overhead)  
❌ Not reduce wrapper size (still 35 lines)  
❌ Not improve maintenance (already 1 bug fix location)

### Recommendation

**Action:** Keep current system. No refactoring needed.

**Rationale:** Current approach is simpler, faster, and easier to understand than template generation.

---

## References

**Core Script:**
- `scripts/get_price_chart.py` (~800 lines)
- Git repo: `git@github.com:evgyur/crypto-price.git`

**Wrapper Example:**
- `../btc/SKILL.md` (35 lines)

**Documentation:**
- `README.md` (user guide)
- `ARCHITECTURE.md` (this document)

**Research:**
- `/home/eyurc/clawd/memory/2026-01-27-crypto-refactor-research.md` (full analysis)

---

**Last Updated:** 2026-01-27  
**Status:** Stable, no changes planned
