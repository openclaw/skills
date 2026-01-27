---
name: whoop
description: Access WHOOP fitness tracker data via API, including recovery scores, sleep metrics, workout stats, daily strain, and body measurements. Use when the user asks about their WHOOP data, fitness metrics, recovery status, sleep quality, workout performance, or wants to track health trends.
---

# WHOOP API

Retrieve and analyze fitness data from WHOOP wearables via the official REST API.

## Usage Snippet
```bash
# Install (if using Clawdhub)
clawdhub install whoop-tracker

# From the skill root:
python3 scripts/get_recovery.py --today
python3 scripts/get_sleep.py --last
python3 scripts/get_workouts.py --days 7
python3 scripts/get_profile.py
```

## Prerequisites

- Python 3.7+
- `requests` library: `pip3 install requests`  
  (or run `bash scripts/install.sh`)

## Quick Start

### 1. Register Application
- Go to https://developer.whoop.com
- Create a new app and note your `client_id` and `client_secret`
- Set redirect URI (e.g., `http://localhost:8080/callback`)

### 2. Save Credentials
```bash
mkdir -p ~/.whoop
cat > ~/.whoop/credentials.json <<EOF
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET"
}
EOF
chmod 600 ~/.whoop/credentials.json
```

### 3. Authorize (see [references/oauth.md](references/oauth.md) for full guide)
- Open the authorization URL in browser
- User grants permissions → redirected with code
- Exchange code for tokens via `WhoopClient.authenticate(code, redirect_uri)`

### 4. Fetch Data
All scripts are run from the skill root directory:

```bash
# Today's recovery
python3 scripts/get_recovery.py --today

# Last night's sleep
python3 scripts/get_sleep.py --last

# Recent workouts
python3 scripts/get_workouts.py --days 7

# User profile
python3 scripts/get_profile.py
```

## Core Data Types

### Recovery
- **Recovery Score** (0-100): Readiness for strain
- **HRV (RMSSD)**: Heart rate variability in milliseconds
- **Resting Heart Rate**: Morning baseline HR
- **SPO2**: Blood oxygen percentage
- **Skin Temperature**: Deviation from baseline in °C

### Sleep
- **Performance %**: How well you slept vs. your sleep need
- **Duration**: Total time in bed and per stage (REM, SWS, light, awake)
- **Efficiency %**: Time asleep / time in bed
- **Consistency %**: How consistent your sleep schedule is
- **Respiratory Rate**: Breaths per minute
- **Sleep Needed/Debt**: Baseline need and accumulated debt

### Cycle (Daily Strain)
- **Strain Score**: Cardiovascular load (0-21 scale)
- **Kilojoules**: Energy expenditure
- **Average/Max Heart Rate**: Daily HR metrics

### Workout
- **Strain**: Activity-specific strain score
- **Sport**: Activity type (running, cycling, etc.)
- **Heart Rate Zones**: Time spent in each of 6 zones
- **Distance/Altitude**: GPS metrics (if available)

## API Endpoints

Base URL: `https://api.prod.whoop.com`

See [references/api-reference.md](references/api-reference.md) for full endpoint documentation with response schemas.

**User Profile:**
- `GET /v1/user/profile/basic` — Name, email
- `GET /v1/user/body_measurement` — Height, weight, max HR

**Recovery:**
- `GET /v1/recovery` — All recovery data (paginated)
- `GET /v1/cycle/{cycleId}/recovery` — Recovery for specific cycle

**Sleep:**
- `GET /v1/sleep` — All sleep records (paginated)
- `GET /v1/sleep/{sleepId}` — Specific sleep by ID
- `GET /v1/cycle/{cycleId}/sleep` — Sleep for specific cycle

**Cycle:**
- `GET /v1/cycle` — All physiological cycles (paginated)
- `GET /v1/cycle/{cycleId}` — Specific cycle by ID

**Workout:**
- `GET /v1/workout` — All workouts (paginated)
- `GET /v1/workout/{workoutId}` — Specific workout by ID

All collection endpoints support `start`, `end` (ISO 8601), `limit` (max 25), and `nextToken` (pagination cursor).

## Required OAuth Scopes

- `read:profile` — User name and email
- `read:body_measurement` — Height, weight, max HR
- `read:recovery` — Recovery scores and HRV
- `read:sleep` — Sleep metrics and stages
- `read:cycles` — Daily strain data
- `read:workout` — Activity and workout data

## Scripts

### `scripts/whoop_client.py`
Core API client. Features:
- OAuth token storage and auto-refresh
- Token expiry tracking (proactive refresh)
- Rate limit handling (429 with retry)
- Automatic pagination iterators (`iter_recovery`, `iter_sleep`, `iter_cycles`, `iter_workouts`)

### `scripts/get_recovery.py`
```bash
python3 scripts/get_recovery.py --today              # Today's recovery
python3 scripts/get_recovery.py --days 7             # Past week
python3 scripts/get_recovery.py --start 2026-01-20   # From date
python3 scripts/get_recovery.py --json               # Raw JSON output
```

### `scripts/get_sleep.py`
```bash
python3 scripts/get_sleep.py --last       # Last night
python3 scripts/get_sleep.py --days 7     # Past week
python3 scripts/get_sleep.py --json       # Raw JSON output
```

### `scripts/get_workouts.py`
```bash
python3 scripts/get_workouts.py --days 7             # Past week
python3 scripts/get_workouts.py --sport running       # Filter by sport
python3 scripts/get_workouts.py --json                # Raw JSON output
```

### `scripts/get_profile.py`
```bash
python3 scripts/get_profile.py            # Profile + body measurements
python3 scripts/get_profile.py --json     # Raw JSON output
```

### `scripts/install.sh`
```bash
bash scripts/install.sh                   # Install pip dependencies + setup guide
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'requests'"
Install dependencies: `pip3 install requests` or `bash scripts/install.sh`

### "Credentials not found at ~/.whoop/credentials.json"
Create the file with your OAuth client_id and client_secret (see Quick Start step 2).

### "Not authenticated"
Complete the OAuth authorization flow (see [references/oauth.md](references/oauth.md)).

### "401 Unauthorized" after token refresh fails
Your refresh token has expired. Re-authorize from the authorization URL.

### "429 Too Many Requests"
Rate limit hit. The client automatically retries after the `Retry-After` period.

### Empty results
Check your date range — use `--days 7` or wider range. Ensure your OAuth scopes include the data type you're requesting.

## References

- [references/oauth.md](references/oauth.md) — OAuth setup, token management, authorization flow
- [references/api-reference.md](references/api-reference.md) — Complete API endpoint documentation with response schemas
