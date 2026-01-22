---
name: vikunja-fast
description: Manage Vikunja projects and tasks (overdue/due/today), mark done, and get quick summaries via the Vikunja API.
homepage: https://vikunja.io/
metadata: {"clawdbot":{"emoji":"📋","requires":{"bins":["curl","jq"],"env":["VIKUNJA_URL"],"optionalEnv":["VIKUNJA_TOKEN","VIKUNJA_USERNAME","VIKUNJA_PASSWORD"]},"primaryEnv":"VIKUNJA_TOKEN"}}
---

# ✅ Vikunja Fast Skill

Use Vikunja as the source of truth for tasks and completions, and interact with it from Clawdbot.

## Setup

You can provide credentials either via environment variables **or** via Clawdbot’s skills config.

### Option A: Environment variables

Set these environment variables **in the same environment where the gateway runs**:

```bash
export VIKUNJA_URL="https://vikunja.xyz"

# Recommended: use a JWT (starts with "eyJ")
export VIKUNJA_TOKEN="<jwt>"

# Alternative: login with username/password (the helper CLI will request a JWT)
export VIKUNJA_USERNAME="<username>"
export VIKUNJA_PASSWORD="<password>"
```

### Option B: Clawdbot skills config (recommended for the agent)

Edit `~/.clawdbot/clawdbot.json`:

```json5
{
  skills: {
    entries: {
      "vikunja-fast": {
        enabled: true,
        env: {
          VIKUNJA_URL: "https://vikunja.xyz",
          VIKUNJA_TOKEN: "<jwt>"
        }
      }
    }
  }
}
```

Notes:
- `VIKUNJA_URL` can be the base URL; the helper normalizes to `/api/v1`.
- Vikunja auth expects a JWT bearer token for most API calls (`Authorization: Bearer <jwt>`).
- If you only have a non-JWT token (often starts with `tk_...`), use `/login` to obtain a JWT.

## Quick checks

### Login (get a JWT)
```bash
curl -fsS -X POST "$VIKUNJA_URL/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"YOUR_USERNAME","password":"YOUR_PASSWORD","long_token":true}' | jq
```

### Who am I? (requires JWT)
```bash
curl -fsS "$VIKUNJA_URL/user" \
  -H "Authorization: Bearer $VIKUNJA_TOKEN" | jq
```

### List projects
```bash
curl -fsS "$VIKUNJA_URL/projects" \
  -H "Authorization: Bearer $VIKUNJA_TOKEN" | jq '.[] | {id, title}'
```

## Commands

This skill ships with a tiny helper CLI:

- `{baseDir}/vikunja.sh`

Examples:

```bash
# Overdue across all projects
{baseDir}/vikunja.sh overdue

# Due today
{baseDir}/vikunja.sh due-today

# Arbitrary filter (Vikunja filter syntax)
{baseDir}/vikunja.sh list --filter 'done = false && due_date < now'

# Show / complete a task
{baseDir}/vikunja.sh show 123
{baseDir}/vikunja.sh done 123
```

Notes:
- Output formatting:
  - Each task should be formated as: `<EMOJI> <DUE_DATE> - #<ID> <TASK>`
  - Emoji comes from the project title when it starts with one; otherwise uses `🔨`
  - Due dates are rendered as `Mon/D` (time + year removed)
- This skill uses `GET /tasks/all` to fetch tasks across all projects

## Mark task done

```bash
TASK_ID=123

curl -fsS -X POST "$VIKUNJA_URL/tasks/$TASK_ID" \
  -H "Authorization: Bearer $VIKUNJA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"done": true}' | jq
```
