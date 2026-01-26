---
name: george
description: "Automate George online banking (Erste Bank / Sparkasse Austria) using Playwright: login/session (phone approval), list accounts + balances, and download statements/exports/transactions (CAMT53, MT940, CSV/JSON/OFX/XLSX). Use when the user mentions George, Erste/Sparkasse, account statements, CAMT53/MT940, or transaction exports."
summary: "George (Erste/Sparkasse Austria) banking automation: login, accounts/balances, statements and transaction exports."
version: 1.0.7
homepage: https://github.com/odrobnik/george-skill
metadata: {"clawdbot":{"emoji":"🏦","requires":{"bins":["python3","playwright"]}}}
---

# George Banking Automation

Modular automation for **George (Erste Bank / Sparkasse Austria)**.

**Entry point:** `{baseDir}/scripts/george.py`

## Setup

### Quick setup (recommended)

```bash
python3 {baseDir}/scripts/george.py setup

# First account sync (auto-fetches if config has none):
python3 {baseDir}/scripts/george.py accounts
```

What `setup` does:
- Prompts for your **George user number / username** (`user_id`)
- Writes `~/.clawdbot/george/config.json` (accounts stored as an array)
- Ensures Playwright is installed and installs Chromium

### Manual setup (alternative)

```bash
pipx install playwright
playwright install chromium

mkdir -p ~/.clawdbot/george
cat > ~/.clawdbot/george/config.json <<EOF
{
  "user_id": "YOUR_USER_ID",
  "accounts": {}
}
EOF

python3 {baseDir}/scripts/george.py accounts
```

## Commands

### Session management

```bash
python3 {baseDir}/scripts/george.py login
python3 {baseDir}/scripts/george.py logout
```

Session is persisted in `~/.clawdbot/george/.pw-profile/` (or `--dir`).

### Accounts

```bash
python3 {baseDir}/scripts/george.py accounts          # list from config; if empty, fetch + save into config.json
python3 {baseDir}/scripts/george.py accounts --fetch  # refresh from George and update config.json
```

### Balances

```bash
python3 {baseDir}/scripts/george.py balances
```

### Statements (PDF)

```bash
python3 {baseDir}/scripts/george.py statements -a main -y 2025 -q 4
```

Note: currently only the **Q4 statement ID mapping** is validated.

### Data exports (bookkeeping)

```bash
python3 {baseDir}/scripts/george.py export              # CAMT53 (default)
python3 {baseDir}/scripts/george.py export --type mt940
```

### Transactions

```bash
python3 {baseDir}/scripts/george.py transactions -a main                  # CSV (default)
python3 {baseDir}/scripts/george.py transactions -a main -f json
python3 {baseDir}/scripts/george.py transactions -a main -f ofx
python3 {baseDir}/scripts/george.py transactions -a main -f xlsx

python3 {baseDir}/scripts/george.py transactions -a main --from 01.01.2025 --to 31.01.2025
```

Supported formats: `csv` (default), `json`, `ofx`, `xlsx`

## Global options

```
--visible          Show browser window (debugging)
--dir DIR          State directory (default: ~/.clawdbot/george; override via GEORGE_DIR)
--login-timeout N  Seconds to wait for phone approval (default: 60)
--user-id ID       Override user number/username (or set GEORGE_USER_ID)
```

You can also put `GEORGE_USER_ID=...` in `~/.clawdbot/george/.env`.

## Output / state locations

- **Config:** `~/.clawdbot/george/config.json` (or `--dir`)
- **Session:** `~/.clawdbot/george/.pw-profile/` (or `--dir`)
- **Downloads:** `~/.clawdbot/george/data/` (or `--dir`)

## Security notes

- This skill downloads **banking documents and transaction exports** to disk. Treat the state dir as sensitive.
- Login requires **phone approval** in the George app; credentials are **not** stored in the skill folder.
- Never log OAuth tokens (George sometimes returns tokens in URL fragments).
