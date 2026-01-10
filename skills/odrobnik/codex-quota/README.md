# codex-quota

A portable Python tool to check OpenAI Codex rate limit status.

## Installation

```bash
cp codex-quota.py ~/bin/codex-quota
chmod +x ~/bin/codex-quota
```

## Usage

```bash
codex-quota              # Cached data from latest session
codex-quota --fresh      # Ping Codex for live data
codex-quota --json       # JSON output
```

## Example Output

```
═══════════════════════════════════════════
           CODEX RATE LIMIT STATUS         
═══════════════════════════════════════════

📊 Primary (5 hours window)
   [░░░░░░░░░░░░░░░░░░░░] 0.0%
   Resets: 2026-01-10 19:20 (in 4h 23m)

📈 Secondary (7 days window)
   [█████████████████░░░] 89.0%
   Resets: 2026-01-14 14:14 (in 95h 18m)

═══════════════════════════════════════════
   Updated: 2026-01-10 14:20
═══════════════════════════════════════════
```

## How It Works

Reads rate limit data from Codex session files (`~/.codex/sessions/`). Every Codex API response includes rate limit headers, which get logged as `token_count` events in the session JSONL files.

## License

MIT
