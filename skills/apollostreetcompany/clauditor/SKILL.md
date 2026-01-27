---
name: clauditor
description: Tamper-resistant audit watchdog for Clawdbot agents. Detects and logs suspicious filesystem activity with HMAC-chained evidence.
homepage: https://github.com/apollostreetcompany/clauditor
metadata: {"clawdbot":{"emoji":"🛡️","requires":{"bins":["cargo","systemctl"],"os":"linux"}}}
---

# Clauditor

Security watchdog that monitors filesystem activity and creates tamper-evident logs. Even if Clawdbot is compromised, it cannot stop the watchdog, forge entries, or delete evidence.

## Installation (Guided)

Use the CLI wizard to guide users through installation:

```bash
cd /path/to/clauditor
cargo build --release
```

### Agent Workflow

1. **Check status:** `./target/release/clauditor wizard status`
   - Returns JSON with `current_step` (1-6) and `complete` (true/false)

2. **Get next step:** `./target/release/clauditor wizard next`
   - Shows WHAT it does, WHY it matters, and the exact COMMAND to run

3. **User runs the sudo command**

4. **Verify:** `./target/release/clauditor wizard verify`
   - Confirms step completed

5. **Repeat until `complete: true`**

### Example Interaction

```
User: "Install clauditor"

Agent: [runs wizard status → current_step: 1]
Agent: "Step 1 of 6: Create system user

This creates a 'sysaudit' user that runs the watchdog. Even if you're 
compromised, you can't kill a process owned by another user.

Run this:
sudo useradd --system --shell /usr/sbin/nologin --no-create-home sysaudit

Let me know when done."

User: "done"

Agent: [runs wizard verify → success]
Agent: [runs wizard next → step 2...]
```

## After Installation

### Check status
```bash
systemctl status systemd-journaldd
```

### Generate digest
```bash
./target/release/clauditor digest \
  --log /var/lib/.sysd/.audit/events.log \
  --key /etc/sysaudit/key \
  --format markdown
```

## Quick Install (Power Users)

```bash
sudo bash wizard/wizard.sh
```

## Configuration

- Config: `/etc/sysaudit/config.toml`
- Key: `/etc/sysaudit/key`
- Logs: `/var/lib/.sysd/.audit/events.log`

Edit config to customize `watch_paths` and `target_uid`.
