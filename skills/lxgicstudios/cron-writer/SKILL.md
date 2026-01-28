---
name: cron-writer
description: Convert natural language to cron expressions. Use when you need to schedule tasks.
---

# Cron Writer

Cron syntax is one of those things that looks simple until you actually need to write one. Five asterisks staring back at you and you can't remember which field is the day of week. This tool converts plain English like "every Tuesday at 3pm" into the exact cron expression. It even shows you the next few run times so you can verify it's right.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-cron-gen "every day at midnight"
```

## What It Does

- Converts plain English schedule descriptions to cron expressions
- Shows the human-readable meaning of the generated expression
- Lists the next scheduled run times for verification
- Handles complex schedules like "every other Friday" or "first Monday of each month"
- Works instantly with zero configuration

## Usage Examples

```bash
# Simple schedule
npx ai-cron-gen "every day at midnight"

# Complex schedule
npx ai-cron-gen "every weekday at 9am and 5pm"

# Specific pattern
npx ai-cron-gen "first Monday of every month at 10:30am"
```

## Best Practices

- **Verify with the next runs output** - Always check the preview to make sure the schedule is what you wanted
- **Be specific about time zones** - Cron expressions don't include timezone info. Know what zone your server runs in
- **Test edge cases** - Schedules like "every other week" can be tricky. Double-check with the preview
- **Copy directly into crontab** - The output is ready to paste straight into your crontab or scheduler

## When to Use This

- Setting up a new cron job and can't remember the syntax
- Configuring CI/CD scheduled pipelines
- Building a task scheduler and need to validate cron expressions
- Documenting existing cron jobs in human-readable format

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgic.dev

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended.

```bash
npx ai-cron-gen --help
```

## How It Works

The tool sends your schedule description to an AI model that understands cron syntax and time patterns. It generates the cron expression, explains what it means in plain English, and calculates the next several run times so you can verify the schedule is correct.

## License

MIT. Free forever. Use it however you want.