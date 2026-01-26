---
name: remember-all-prompts-daily
description: Preserve conversation continuity across token compaction cycles by extracting and archiving all prompts with date-wise entries. Automatically triggers at 95% token usage (pre-compaction) and 1% (new sprint start) to export session history, then ingests archived summaries on session restart to restore context.
---

# Remember All Prompts Daily

This skill maintains conversation continuity across token budget cycles by automatically archiving your session history before compaction and restoring it when a new session begins.

## How It Works

### 1. **Extraction Trigger (95% Token Usage)**
When token usage approaches 95%:
- Run `export_prompts.py` to extract current session history
- Format all prompts/responses with timestamps
- Append to `memory/remember-all-prompts-daily.md` with date-wise entry
- Marks the archive point so compaction can proceed

### 2. **Fresh Session Trigger (1% Token Usage)**
When a new session starts (fresh 1% token usage):
- Check if `memory/remember-all-prompts-daily.md` exists
- Read the most recent entry
- Ingest it as "past conversation summary" to restore context
- Continues naturally from where the previous session ended

### 3. **Daily File Structure**
```
# Remember All Prompts Daily

## [DATE: 2026-01-26]

### Session 1 (09:00 - 09:47)
[All prompts and responses from session]

### Session 2 (10:15 - 11:30)
[All prompts and responses from session]
```

## Scripts

### `scripts/export_prompts.py`
Extracts all prompts/responses from current session and archives them.

**Usage:**
```bash
python scripts/export_prompts.py
```

**What it does:**
- Uses `sessions_history()` to fetch all messages from current session
- Formats with timestamps and message IDs
- Appends to `memory/remember-all-prompts-daily.md`
- Includes metadata (token count, duration, etc.)

### `scripts/ingest_prompts.py`
Reads the daily archive and injects it as context on session start.

**Usage:**
```bash
python scripts/ingest_prompts.py
```

**What it does:**
- Reads `memory/remember-all-prompts-daily.md` (if exists)
- Extracts most recent session
- Returns formatted summary for ingestion into new session

## Integration

### Heartbeat Check
Add to `HEARTBEAT.md` to monitor token usage:
```
Check token usage - if >95%, export session history
```

### Cron Job (Optional)
For automatic triggers:
```bash
# Check token at regular intervals
clawdbot cron add --text "Check token usage and export if needed" --schedule "*/15 * * * *"
```

## Example Flow

**Session 1:**
1. Chat normally
2. Token reaches 95%
3. export_prompts.py runs automatically
4. All prompts archived to daily file
5. Session compacts

**Session 2 (New Sprint):**
1. Fresh 1% token budget
2. ingest_prompts.py reads archive
3. "Here's what we discussed yesterday..."
4. Context restored, conversation continues seamlessly

## Manual Usage

### Export Right Now
```bash
python skills/remember-all-prompts-daily/scripts/export_prompts.py
```

### View Today's Archive
```bash
cat memory/remember-all-prompts-daily.md | tail -100
```

### Ingest Previous Session
```bash
python skills/remember-all-prompts-daily/scripts/ingest_prompts.py
```

## Token Monitoring

Monitor token usage via:
```bash
session_status  # Shows current token usage %
```

When you see token usage approaching 95%, the skill can auto-trigger, or you can manually export.

## Notes

- Runs only in main session (direct chat with Ateeb)
- Respects privacy — only stores your actual prompts and responses
- Daily file auto-rotates at midnight (one entry per date)
- Can be manually triggered anytime
