---
name: vikunja
description: Manage tasks and projects on a self-hosted Vikunja instance. Use when the user wants to create, view, complete, or manage tasks, check what's due or overdue, list projects, or get task notifications. Also use for to-do lists, reminders, and task tracking.
---

# Vikunja Task Manager

Manage tasks and projects on a self-hosted Vikunja instance via REST API.

## Setup

Set these environment variables:

```bash
export VIKUNJA_URL="https://your-vikunja-instance.com"
export VIKUNJA_TOKEN="your-api-token"
```

Get your API token: Vikunja → Settings → API Tokens → Create token.

## Commands

### List tasks

```bash
{baseDir}/scripts/vikunja.sh tasks --count 10
{baseDir}/scripts/vikunja.sh tasks --project "Shopping" --count 5
{baseDir}/scripts/vikunja.sh tasks --search "groceries"
{baseDir}/scripts/vikunja.sh tasks --sort priority --order desc
```

### Overdue tasks

```bash
{baseDir}/scripts/vikunja.sh overdue
```

### Tasks due soon (next N hours)

```bash
{baseDir}/scripts/vikunja.sh due --hours 24
{baseDir}/scripts/vikunja.sh due --hours 48
```

### Create a task

```bash
{baseDir}/scripts/vikunja.sh create-task --project "Tasks" --title "Buy milk" --due "2026-02-01" --priority 3
```

Priority: 1 (low) to 5 (urgent). Due date format: YYYY-MM-DD.

### Complete a task

```bash
{baseDir}/scripts/vikunja.sh complete --id 123
```

### Get task details

```bash
{baseDir}/scripts/vikunja.sh task --id 123
```

### List projects

```bash
{baseDir}/scripts/vikunja.sh projects
```

### Create a project

```bash
{baseDir}/scripts/vikunja.sh create-project --title "New Project" --description "Optional description"
```

### Get notifications

```bash
{baseDir}/scripts/vikunja.sh notifications
```

## Due Date Monitoring

To get proactive notifications about due/overdue tasks, set up a cron job:

```bash
clawdbot cron add \
  --name "Task due check" \
  --cron "0 9,14 * * *" \
  --tz "America/Denver" \
  --session isolated \
  --message "Check Vikunja for overdue and upcoming tasks (next 24 hours). If any are found, notify me with the list." \
  --deliver \
  --channel telegram
```

## Notes

- Project names in `--project` are case-insensitive
- Filter expressions follow Vikunja filter syntax (see https://vikunja.io/docs/filters)
- All times are handled in America/Denver timezone
