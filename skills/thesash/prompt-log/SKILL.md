---
name: prompt-log
description: Extract conversation transcripts from AI coding session logs (Clawdbot, Claude Code, Codex). Use when asked to export prompt history, session logs, or transcripts from .jsonl session files.
---

# Prompt Log

## Quick start

Run the bundled script on a session file:

```bash
scripts/extract.sh <session-file>
```

## Inputs

- **Session file**: A `.jsonl` session log from Clawdbot, Claude Code, or Codex.
- **Optional filters**: `--after` and `--before` ISO timestamps.
- **Optional output**: `--output` path for the markdown transcript.

## Outputs

- Writes a markdown transcript. Defaults to `.prompt-log/YYYY-MM-DD-HHMMSS.md` in the current project.

## Examples

```bash
scripts/extract.sh ~/.codex/sessions/2026/01/12/abcdef.jsonl
scripts/extract.sh ~/.claude/projects/my-proj/xyz.jsonl --after "2026-01-12T10:00:00" --before "2026-01-12T12:00:00"
scripts/extract.sh ~/.clawdbot/agents/main/sessions/123.jsonl --output my-transcript.md
```

## Dependencies

- Requires `jq` in PATH.
- Uses `gdate` if available on macOS; otherwise falls back to `date`.
