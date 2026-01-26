---
name: oura-ring-data
description: Access Oura Ring health data using the ouracli CLI tool. Use when user asks about "oura data", "sleep stats", "activity data", "heart rate", "readiness score", "stress levels", or wants health metrics from their Oura Ring.
allowed-tools: Bash
---

# Oura Ring Data Access

Retrieves health and fitness data from the Oura Ring using the ouracli command-line interface.

## CRITICAL: Authentication Required

**ALWAYS check for authentication before running ouracli commands.** The tool requires a `PERSONAL_ACCESS_TOKEN` environment variable.

- Token location: `secrets/oura.env` or `~/.secrets/oura.env`
- If commands fail with authentication errors, inform the user to obtain a token from: https://cloud.ouraring.com/personal-access-tokens

## Available Data Types

### Core Health Metrics
- `activity` - Daily activity (steps, MET values, calories)
- `sleep` - Sleep data (stages, efficiency, heart rate)
- `readiness` - Readiness scores and contributors
- `heartrate` - Time-series heart rate data (5-minute resolution)
- `spo2` - Blood oxygen saturation data
- `stress` - Daily stress levels

### Additional Data
- `workout` - Workout sessions
- `session` - Activity sessions
- `tag` - User-added tags
- `rest-mode` - Rest mode periods
- `personal-info` - User profile information
- `all` - All available data types

## Date Range Specification

### ✅ SUPPORTED FORMATS (Use These!)

```bash
# Single date (no quotes needed)
ouracli activity 2025-12-25
ouracli sleep today
ouracli heartrate yesterday

# Relative ranges from today (MUST use quotes)
ouracli activity "7 days"      # Last 7 days including today
ouracli sleep "30 days"        # Last 30 days
ouracli readiness "2 weeks"    # Last 2 weeks
ouracli stress "1 month"       # Last month

# Date + duration (MUST use quotes)
ouracli activity "2025-12-01 28 days"    # 28 days starting Dec 1
ouracli sleep "2025-09-23 7 days"        # Week starting Sept 23
```

**⚠️ CRITICAL: Use quotes when the date range contains spaces!**

### ❌ UNSUPPORTED FORMATS (DO NOT USE)

```bash
# ❌ WRONG - Two separate dates
ouracli activity 2025-09-23 2025-09-30

# ❌ WRONG - "to" syntax
ouracli activity "2025-09-23 to 2025-09-30"

# ❌ WRONG - Range operators
ouracli activity "2025-09-23..2025-09-30"

# ❌ WRONG - Relative past expressions
ouracli activity "3 months ago"
```

### Converting Date Ranges

If user requests data between two specific dates:

**Step 1**: Calculate the number of days (inclusive)
```
Example: Sept 23 to Sept 30 = 7 days
         Dec 1 to Dec 31 = 30 days
```

**Step 2**: Use the "date + duration" format
```bash
# ✅ CORRECT
ouracli activity "2025-09-23 7 days"
ouracli activity "2025-12-01 30 days"
```

## Output Formats

**ALWAYS use `--json` for programmatic data analysis.** This is the most reliable format for parsing.

```bash
# ✅ RECOMMENDED for AI analysis
ouracli activity "7 days" --json

# Other formats (human-readable)
ouracli activity today --tree        # Default: tree structure
ouracli activity "7 days" --markdown # Markdown with charts
ouracli activity "7 days" --html > activity.html  # Interactive HTML charts
ouracli activity "7 days" --dataframe  # Pandas DataFrame format
```

## Common Usage Patterns

### Quick Data Check
```bash
# Today's activity
ouracli activity today --json

# Recent sleep data
ouracli sleep "7 days" --json

# Current readiness
ouracli readiness today --json
```

### Detailed Analysis
```bash
# Weekly health summary
ouracli all "7 days" --json

# Monthly activity report
ouracli activity "30 days" --json

# Heart rate for specific date
ouracli heartrate "2025-12-15 1 days" --json
```

### Multi-Day Reports
```bash
# All data grouped by day (HTML report)
ouracli all "7 days" --by-day --html > weekly-report.html

# All data grouped by type
ouracli all "7 days" --by-method --json
```

## Key Notes

### Readiness Contributors Warning
⚠️ **IMPORTANT**: The `contributors.resting_heart_rate` field in readiness data is a **SCORE (0-100)**, NOT actual BPM:
- Low score (19, 47) = RHR elevated vs. baseline (negative impact)
- High score (95, 100) = RHR optimal vs. baseline (positive impact)
- Actual BPM values are in the `heartrate` command output

**DO NOT interpret contributor scores as actual heart rate measurements.**

### Oura API Quirks
- Single-day queries sometimes return empty results due to timezone issues
- Use date ranges (e.g., "YYYY-MM-DD 2 days") for more reliable results
- When querying specific dates, consider adding a buffer day

### Data Availability
- Ring must be synced recently for current data
- Historical data availability depends on user's Oura subscription
- If no data is returned, suggest broader date range or check sync status

## Troubleshooting

### Error: "Got unexpected extra argument"
**Cause**: Used two separate date arguments instead of one quoted range
```bash
# ❌ WRONG
ouracli activity 2025-09-23 2025-09-30

# ✅ CORRECT
ouracli activity "2025-09-23 7 days"
```

### Error: "Invalid date specification"
**Cause**: Used unsupported syntax like "to", "..", or relative expressions
```bash
# ❌ WRONG
ouracli activity "2025-09-23 to 2025-09-30"

# ✅ CORRECT
ouracli activity "2025-09-23 7 days"
```

### No Data Returned
**Solutions**:
1. Try a broader date range: `ouracli activity "7 days" --json`
2. Add buffer days: `ouracli activity "2025-12-25 2 days" --json`
3. Check if Ring has synced recently
4. Verify date is within available data range

## Example Responses to User Queries

### "Show me my activity for the last week"
```bash
ouracli activity "7 days" --json
```

### "What was my sleep like last night?"
```bash
ouracli sleep today --json
```

### "How was my readiness in December?"
```bash
ouracli readiness "2025-12-01 30 days" --json
```

### "Get all my data from Sept 23 to Sept 30"
```bash
# Calculate: Sept 30 - Sept 23 = 7 days
ouracli all "2025-09-23 7 days" --json
```

### "Show my heart rate from yesterday"
```bash
ouracli heartrate yesterday --json
```

## Quick Reference

| User Intent | Command |
|-------------|---------|
| Today's activity | `ouracli activity today --json` |
| Last week's sleep | `ouracli sleep "7 days" --json` |
| Current readiness | `ouracli readiness today --json` |
| Heart rate today | `ouracli heartrate today --json` |
| Monthly summary | `ouracli all "30 days" --json` |
| Specific date range | `ouracli [TYPE] "YYYY-MM-DD N days" --json` |
| All data types | `ouracli all "7 days" --json` |

## Notes

- Always prefer `--json` format for AI analysis
- Use quotes for all date ranges with spaces
- Calculate day counts for specific date ranges
- Check authentication if commands fail
- Consider timezone quirks when querying specific dates
