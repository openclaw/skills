---
name: jira
description: Manage Jira issues, transitions, and worklogs via the Jira Cloud REST API.
homepage: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
metadata:
  {
    "clawdbot":
      {
        "emoji": "🧭",
        "requires":
          {
            "bins": ["curl", "jq", "bc", "python3"],
            "env": ["JIRA_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"],
            "optional_env": ["JIRA_BOARD"],
          },
      },
  }
---

# Jira Skill

Work with Jira issues and worklogs from Clawdbot (search, status, create, log work, worklog summaries).

## Setup

1. Get your API key: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API Token"
3. Set environment variables:
   ```bash
   export JIRA_EMAIL="you@example.com"
   export JIRA_API_TOKEN="your-api-token"
   export JIRA_URL="https://your-domain.atlassian.net"
   # Optional project scope (comma-separated). Empty = search all.
   export JIRA_BOARD="ABC"
   ```

Requires `curl`, `jq`, `bc`, and `python3`.

## Quick Commands

All commands live in `{baseDir}/scripts/jira.sh`.

- `{baseDir}/scripts/jira.sh search "timeout" [max]` — fuzzy search by summary or key inside `JIRA_BOARD`
- `{baseDir}/scripts/jira.sh link ABC-123` — browser link for an issue
- `{baseDir}/scripts/jira.sh issue ABC-123` — quick issue details
- `{baseDir}/scripts/jira.sh status ABC-123 "In Progress"` — move an issue (validates available transitions)
- `{baseDir}/scripts/jira.sh transitions ABC-123` — list allowed transitions
- `{baseDir}/scripts/jira.sh assign ABC-123 "name or email"` — assign by user search
- `{baseDir}/scripts/jira.sh assign-me ABC-123` — assign to yourself
- `{baseDir}/scripts/jira.sh comment ABC-123 "text"` — add a comment
- `{baseDir}/scripts/jira.sh create "Title" ["Description"]` — create a Task in `JIRA_BOARD`
- `{baseDir}/scripts/jira.sh log ABC-123 2.5 [YYYY-MM-DD]` — log hours (defaults to today UTC)
- `{baseDir}/scripts/jira.sh my [max]` — open issues assigned to you
- `{baseDir}/scripts/jira.sh hours 2025-01-01 2025-01-07` — your logged hours by issue (JSON)
- `{baseDir}/scripts/jira.sh hours-day 2025-01-07 [name|email]` — logged hours for a day grouped by user/issue; optional filter (name/email; also resolves to accountId)
- `{baseDir}/scripts/jira.sh hours-issue ABC-123 [name|email]` — logged hours for an issue; optional filter (name/email; also resolves to accountId)

## Command Reference

- **Search issues**

  ```bash
  {baseDir}/scripts/jira.sh search "payment failure" [maxResults]
  ```

- **Issue link**

  ```bash
  {baseDir}/scripts/jira.sh link ABC-321
  ```

- **Issue details**

  ```bash
  {baseDir}/scripts/jira.sh issue ABC-321
  ```

- **Update status**

  ```bash
  {baseDir}/scripts/jira.sh status ABC-321 "Done"
  ```

- **List transitions**

  ```bash
  {baseDir}/scripts/jira.sh transitions ABC-321
  ```

- **Assign issue**

  ```bash
  {baseDir}/scripts/jira.sh assign ABC-321 "Jane Doe"
  ```

- **Assign to yourself**

  ```bash
  {baseDir}/scripts/jira.sh assign-me ABC-321
  ```

- **Add comment**

  ```bash
  {baseDir}/scripts/jira.sh comment ABC-321 "Deployed to staging"
  ```

- **Create issue**

  ```bash
  {baseDir}/scripts/jira.sh create "Fix auth timeout" "Users being logged out after 5m"
  ```

- **Log hours**

  ```bash
  {baseDir}/scripts/jira.sh log PB-321 1.5 2025-01-18
  ```

- **My open issues**

  ```bash
  {baseDir}/scripts/jira.sh my [maxResults]
  ```

- **Logged hours by issue (me)**

  ```bash
  {baseDir}/scripts/jira.sh hours 2025-01-01 2025-01-05
  ```

- **Logged hours for a day (everyone)**

  ```bash
  {baseDir}/scripts/jira.sh hours-day 2025-01-05
  ```

- **Logged hours for a day (user filter)**

  ```bash
  {baseDir}/scripts/jira.sh hours-day 2025-01-05 "jane"
  ```

- **Logged hours for an issue**
  ```bash
  {baseDir}/scripts/jira.sh hours-issue ABC-321 "jane"
  ```

## Notes

- Worklog commands use Jira's worklog/updated + worklog/list combo and may take a few seconds on large projects.
- `hours` filters by `JIRA_EMAIL`; `hours-day` returns all users with totals per issue and user.
- Outputs for hours commands are JSON for reuse in other tools.
- Status transitions are validated against the server-provided transition list before applying.
