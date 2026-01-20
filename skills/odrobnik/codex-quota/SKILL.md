---
name: codex-quota
description: Check OpenAI Codex CLI rate limit status (daily/weekly quotas) using local session logs. Portable Python script.
---

# Skill: codex-quota

Check OpenAI Codex CLI rate limit status.

## Quick Reference

```bash
# Run the included Python script
./codex-quota.py

# Or if installed to PATH
codex-quota
```

## Options

```bash
codex-quota              # Show current quota (cached from latest session)
codex-quota --fresh      # Ping Codex first for live data
codex-quota --all        # Update all accounts, save to /tmp/codex-quota-all.json
codex-quota --json       # Output as JSON
codex-quota --help       # Show help
```

## What It Shows

- **Primary Window** (5 hours) — Short-term rate limit
- **Secondary Window** (7 days) — Weekly rate limit
- Reset times in local timezone with countdown
- Source session file and age

## Installation

Copy `codex-quota.py` to your path:
```bash
cp skills/codex-quota/codex-quota.py ~/bin/codex-quota
chmod +x ~/bin/codex-quota
```

## How It Works

Codex CLI logs rate limit info in every session file (`~/.codex/sessions/YYYY/MM/DD/*.jsonl`) as part of `token_count` events. This tool:

1. Finds the most recent session file
2. Extracts the last `rate_limits` object
3. Formats and displays it

## When to Use

- Before starting heavy Codex work (check weekly quota)
- When Codex seems slow (might be rate-limited)
- Monitoring quota across multiple accounts
