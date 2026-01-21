---
name: obsidian-conversation-backup
description: Automatic conversation backup system for Obsidian with incremental snapshots, hourly breakdowns, and formatted chat-style markdown. Use when setting up conversation archival, preventing data loss from /new resets, or organizing chat history in Obsidian vault with proper formatting (colored callouts, timestamps, multi-paragraph support).
---

# Obsidian Conversation Backup

Automatically backs up Clawdbot conversations to Obsidian with beautiful chat-style formatting. Prevents data loss from `/new` resets with hourly incremental snapshots.

## Features

- **Incremental backups**: Hourly snapshots of new messages only (no duplication)
- **Chat formatting**: Obsidian callouts with emojis, timestamps, proper multi-paragraph support
- **Hourly breakdowns**: Organize conversations by clock hour for easy reference
- **Zero token cost**: Pure shell scripting, no LLM calls
- **Smart filtering**: Skips empty messages and system notifications

## Quick Setup

### Installation

```bash
# Extract the skill (if downloaded as .skill file)
unzip obsidian-conversation-backup.skill
cd obsidian-conversation-backup

# Run installer (interactive)
chmod +x install.sh
./install.sh
```

The installer will ask for:
- Obsidian vault path
- Session directory location
- Tracking files location

**Or manual setup:**

1. Copy `config.example` to `config`
2. Edit `config` with your paths
3. Make scripts executable: `chmod +x scripts/*.sh`

### Enable Automatic Backups

Add to crontab for hourly backups:

```bash
crontab -e

# Add this line (runs every hour at :00)
0 * * * * /path/to/obsidian-conversation-backup/scripts/monitor_and_save.sh
```

### Customize Chat Appearance (Optional)

Edit `scripts/format_message_v2.jq` to change:
- User emoji (default: 🐉)
- Assistant emoji (default: 🦞)  
- Callout types (default: `[!quote]` for user, `[!check]` for assistant)

## Usage

### Automatic Incremental Backups

Once configured in cron, the system runs automatically:

**Every hour:**
- Checks for new messages (≥10 lines)
- Creates incremental snapshot if found
- Saves to: `YYYY-MM-DD-HHmm-incremental.md`
- Skips if no new conversation

**Example output:**
```
2026-01-20-1500-incremental.md (messages from last save to now)
2026-01-20-1600-incremental.md (new messages since 15:00)
2026-01-20-1700-incremental.md (new messages since 16:00)
```

**Protection:** Max conversation loss = 1 hour

### On-Demand Full Snapshot

Save complete conversation anytime:

```bash
scripts/save_full_snapshot.sh [topic-name]
```

**Examples:**
```bash
scripts/save_full_snapshot.sh important-decisions
scripts/save_full_snapshot.sh bug-fix-discussion
scripts/save_full_snapshot.sh  # uses "full-conversation" as default
```

### Hourly Breakdown (Organization)

Create organized breakdown by clock hour:

```bash
scripts/create_hourly_snapshots.sh YYYY-MM-DD
```

**Example:**
```bash
scripts/create_hourly_snapshots.sh 2026-01-20
```

**Output:**
```
2026-01-20-1500-hourly.md (15:00-15:59 messages)
2026-01-20-1600-hourly.md (16:00-16:59 messages)
2026-01-20-1700-hourly.md (17:00-17:59 messages)
```

**Use case:** End-of-day organization for easy reference

## Chat Format

Messages appear as colored Obsidian callouts:

**User messages** (blue `[!quote]` callout):
```
> [!quote] 🐉 User · 15:30
> This is my message
```

**Assistant messages** (green `[!check]` callout):
```
> [!check] 🦞 Zoidbot · 15:31  
> This is the response
```

**Features:**
- Timestamps (HH:MM format)
- Multi-paragraph support (uses `<br><br>` for paragraph breaks)
- Proper line wrapping (all lines prefixed with `> `)
- Empty messages filtered out
- System notifications excluded

## Token Monitoring

The `monitor_and_save.sh` script also tracks token usage:

**Warnings via Telegram:**
- **800k tokens (80%)**: "Consider /new soon"
- **900k tokens (90%)**: "Run /new NOW"

**Implementation:**
```bash
# Sends warning only when crossing threshold (one-time)
# No repeated warnings
# Resets when back under 800k
```

## File Structure

```
scripts/
├── monitor_and_save.sh           # Hourly incremental backup + token monitoring
├── save_full_snapshot.sh         # On-demand full conversation save
├── create_hourly_snapshots.sh    # Organize by clock hour
└── format_message_v2.jq          # Chat formatting logic
```

## Configuration

### Tracking Files

The system uses hidden files to track state:

```bash
/root/clawd/.last_save_line_count       # For token monitoring
/root/clawd/.last_snapshot_timestamp    # For incremental saves
/root/clawd/.token_warning_sent         # For warning deduplication
```

**Note:** Do not delete these files or incremental backups may duplicate content

### Session File Location

Default: `/root/.clawdbot/agents/main/sessions/*.jsonl`

If your session files are elsewhere, update the `SESSION_FILE` path in each script.

## Troubleshooting

### No snapshots being created

1. Check cron is running: `crontab -l`
2. Verify script has execute permission: `chmod +x scripts/*.sh`
3. Check logs: Run manually to see errors

### Messages breaking out of callouts

- Ensure `format_message_v2.jq` has the `gsub("\n\n"; "<br><br>")` line
- Check that all lines have `> ` prefix
- Verify jq is installed: `jq --version`

### Duplicated content in snapshots

- Delete tracking files and let system reset:
  ```bash
  rm /root/clawd/.last_snapshot_timestamp
  ```

### Empty callout boxes appearing

- Update `format_message_v2.jq` to filter empty messages
- Check for the `if ($text_content | length) > 0` condition

## Requirements

- **jq**: JSON parsing (`apt-get install jq`)
- **cron**: For automatic backups
- **Obsidian vault**: Target directory for markdown files

## Advanced Customization

### Change Backup Frequency

Edit crontab:
```bash
# Every 2 hours
0 */2 * * * /path/to/monitor_and_save.sh

# Every 30 minutes
*/30 * * * * /path/to/monitor_and_save.sh

# Specific times only (9am, 12pm, 6pm, 9pm)
0 9,12,18,21 * * * /path/to/monitor_and_save.sh
```

### Change Minimum Message Threshold

Edit `monitor_and_save.sh`:
```bash
# Change from 10 to 5 messages minimum
if [[ $new_lines -lt 5 ]]; then
```

### Add More Callout Styles

Obsidian callout types:
- `[!quote]` - Blue
- `[!check]` - Green
- `[!note]` - Cyan
- `[!tip]` - Purple
- `[!warning]` - Orange
- `[!danger]` - Red

### Customize Telegram Notifications

Edit `monitor_and_save.sh` to change warning text or add custom notifications.

## Best Practices

1. **Run hourly breakdown at end of day** - Use as organizational tool, not backup
2. **Keep incremental backups running** - This is your safety net
3. **Test scripts after setup** - Run manually first to verify output
4. **Backup tracking files** - Include `.last_snapshot_timestamp` in vault backups
5. **Use descriptive topic names** - For full snapshots, use meaningful names

## Example Workflow

**Daily routine:**
1. Automatic incremental backups run hourly (no action needed)
2. At end of day: `scripts/create_hourly_snapshots.sh 2026-01-20`
3. Review organized hourly files in Obsidian
4. Delete old incrementals if desired (hourly breakdown covers them)

**Before /new reset:**
1. Optional: `scripts/save_full_snapshot.sh before-reset`
2. Run `/new` safely - conversation is backed up
3. Continue chatting - incrementals resume automatically

## Integration with Clawdbot

This skill works with:
- **HEARTBEAT.md**: Automatic token monitoring
- **MEMORY.md**: Conversation archival system
- **Telegram integration**: Warning notifications
- **Any Obsidian vault**: Works with existing vaults

## Credits

Created by the Clawdbot community for reliable conversation backup and beautiful Obsidian formatting.
