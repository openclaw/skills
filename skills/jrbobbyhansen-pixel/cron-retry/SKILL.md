---
name: cron-retry
description: Auto-retry failed cron jobs on connection recovery. Use when cron jobs fail due to network errors and should be retried when connectivity is restored. Integrates with heartbeat to detect failed jobs and re-run them automatically.
---

# Cron Retry Skill

Automatically detect and retry cron jobs that failed due to network/connection errors.

## Quick Start (Heartbeat Integration)

Add this to your `HEARTBEAT.md`:

```markdown
## Cron Recovery Check
Check for cron jobs with lastStatus: "error". If the error matches network patterns (connection error, sendMessage failed, fetch failed, ETIMEDOUT, ECONNREFUSED), retry the job using cron tool with action: "run" and the job ID. Report what was recovered.
```

That's it. On each heartbeat, failed network jobs get retried automatically.

## How It Works

1. On heartbeat, check all cron jobs via `cron list`
2. Filter for jobs where `lastStatus = "error"` and `enabled = true`
3. Check if `lastError` matches network-related patterns
4. Re-run eligible jobs via `cron run`
5. Report results

## Network Error Patterns (Retryable)

These errors indicate transient network issues worth retrying:

- `Network request.*failed`
- `Connection error`
- `ECONNREFUSED`
- `ETIMEDOUT`
- `ENOTFOUND`
- `sendMessage.*failed`
- `fetch failed`
- `socket hang up`

## What Gets Retried vs Skipped

**Retried:**
- Network timeouts
- Connection refused
- Message send failures
- DNS lookup failures

**Skipped (not retried):**
- Logic errors (bad config, missing data)
- Auth failures
- Disabled jobs
- Jobs that just ran successfully

## Manual Recovery Check

To check and retry failed jobs manually:

```bash
# List all jobs and their status
clawdbot cron list

# Find failed jobs
clawdbot cron list | jq '.jobs[] | select(.state.lastStatus == "error") | {name, error: .state.lastError}'

# Retry a specific job
clawdbot cron run --id <JOB_ID>
```

## Agent Implementation

When implementing the heartbeat check:

```
1. Call cron tool with action: "list"
2. For each job in response.jobs:
   - Skip if job.enabled !== true
   - Skip if job.state.lastStatus !== "error"
   - Check if job.state.lastError matches network patterns
   - If retryable: call cron tool with action: "run", jobId: job.id
3. Report: "Recovered X jobs" or "No failed jobs to recover"
```

## Example Scenario

1. **7:00 PM** — Evening briefing cron fires
2. **Network hiccup** — Telegram send fails
3. **Job marked** `lastStatus: "error"`, `lastError: "Network request for 'sendMessage' failed!"`
4. **7:15 PM** — Connection restored, heartbeat runs
5. **Skill detects** the failed job, sees it's a network error
6. **Retries** the job → briefing delivered
7. **Reports**: "Recovered 1 job: evening-wrap-briefing"

## Safety

- Only retries transient network errors
- Respects job enabled state
- Won't create retry loops (checks lastRunAtMs)
- Reports all recovery attempts
