---
name: fitbit
description: Query Fitbit health data including sleep, heart rate, activity, SpO2, and breathing rate. Use when user asks about their fitness, sleep quality, steps, or health metrics.
homepage: https://www.fitbit.com
metadata:
  clawdbot:
    emoji: "💪"
    requires:
      bins: ["fitbit-cli"]
---

# Fitbit CLI

Query health and fitness data from Fitbit wearables.

## Commands

### Health Data

```bash
# Sleep logs (deep, light, REM, awake times)
fitbit-cli -s                    # today
fitbit-cli -s yesterday          # yesterday
fitbit-cli -s last-week          # last 7 days
fitbit-cli -s 2026-01-01         # specific date

# Heart rate time series
fitbit-cli -e                    # today
fitbit-cli -e last-week          # last 7 days

# Blood oxygen (SpO2)
fitbit-cli -o                    # today
fitbit-cli -o last-3-days        # last 3 days

# Active Zone Minutes
fitbit-cli -a                    # today
fitbit-cli -a last-month         # last month

# Breathing rate
fitbit-cli -b                    # today

# Daily activity (steps, calories, distance, floors)
fitbit-cli -t                    # today
fitbit-cli -t yesterday          # yesterday
```

### Account & Devices

```bash
# User profile
fitbit-cli -u

# Connected devices (battery, sync status)
fitbit-cli -d
```

### Date Formats

- No parameter: today
- Specific date: `2026-01-05`
- Date range: `2026-01-01,2026-01-05`
- Relative: `yesterday`, `last-week`, `last-month`
- Custom relative: `last-2-days`, `last-3-weeks`, `last-2-months`

## Usage Examples

**User asks "How did I sleep last night?"**
```bash
fitbit-cli -s yesterday
```

**User asks "What's my heart rate been like this week?"**
```bash
fitbit-cli -e last-week
```

**User asks "How many steps today?"**
```bash
fitbit-cli -t
```

**User asks "Show my SpO2 levels"**
```bash
fitbit-cli -o
```

**User asks "Is my Fitbit synced?"**
```bash
fitbit-cli -d
```

**User asks "How active was I last month?"**
```bash
fitbit-cli -a last-month
```

## Notes

- Read-only access to Fitbit data
- Tokens auto-refresh (expire after 8 hours)
- Data may be delayed from device sync
- First-time setup: `fitbit-cli --init-auth`
