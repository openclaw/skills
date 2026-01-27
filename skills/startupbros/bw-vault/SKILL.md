---
name: bitwarden
description: Set up and use Bitwarden CLI (bw). Use when installing the CLI, authenticating (login/unlock), or reading secrets from your vault. Supports email/password, API key, and SSO authentication methods.
homepage: https://bitwarden.com/help/cli/
metadata: {"clawdbot":{"emoji":"🔒","requires":{"bins":["bw"]},"install":[{"id":"npm","kind":"npm","package":"@bitwarden/cli","bins":["bw"],"label":"Install Bitwarden CLI (npm)"},{"id":"brew","kind":"brew","formula":"bitwarden-cli","bins":["bw"],"label":"Install Bitwarden CLI (brew)"},{"id":"choco","kind":"choco","package":"bitwarden-cli","bins":["bw"],"label":"Install Bitwarden CLI (choco)"}]}}
---

# Bitwarden CLI Skill

The Bitwarden command-line interface (CLI) provides full access to your Bitwarden vault for retrieving passwords, secure notes, and other secrets programmatically.

## Workflow Requirements

**CRITICAL:** Always run `bw` commands inside a dedicated tmux session. The CLI requires a session key (`BW_SESSION`) for all vault operations after authentication. A tmux session preserves this environment variable across commands.

### Required Workflow

1. **Verify CLI installation**: Run `bw --version` to confirm the CLI is available
2. **Create a dedicated tmux session**: `tmux new-session -d -s bw-session`
3. **Attach and authenticate**: Run `bw login` or `bw unlock` inside the session
4. **Export session key**: After unlock, export `BW_SESSION` as instructed by the CLI
5. **Execute vault commands**: Use `bw get`, `bw list`, etc. within the same session

### Authentication Methods

| Method | Command | Use Case |
|--------|---------|----------|
| Email/Password | `bw login` | Interactive sessions, first-time setup |
| API Key | `bw login --apikey` | Automation, scripts (requires separate unlock) |
| SSO | `bw login --sso` | Enterprise/organization accounts |

After `bw login` with email/password, your vault is automatically unlocked. For API key or SSO login, you must subsequently run `bw unlock` to decrypt the vault.

### Session Key Management

The unlock command outputs a session key. You **must** export it:

```bash
# Bash/Zsh
export BW_SESSION="<session_key_from_unlock>"

# Or capture automatically
export BW_SESSION=$(bw unlock --raw)
```

Session keys remain valid until you run `bw lock` or `bw logout`. They do **not** persist across terminal windows—hence the tmux requirement.

## Reading Secrets

```bash
# Get password by item name
bw get password "GitHub"

# Get username
bw get username "GitHub"

# Get TOTP code
bw get totp "GitHub"

# Get full item as JSON
bw get item "GitHub"

# Get specific field
bw get item "GitHub" | jq -r '.fields[] | select(.name=="api_key") | .value'

# List all items
bw list items

# Search items
bw list items --search "github"
```

## Security Guardrails

- **NEVER** expose secrets in logs, code, or command output visible to users
- **NEVER** write secrets to disk unless absolutely necessary
- **ALWAYS** use `bw lock` when finished with vault operations
- **PREFER** reading secrets directly into environment variables or piping to commands
- If you receive "Vault is locked" errors, re-authenticate with `bw unlock`
- If you receive "You are not logged in" errors, run `bw login` first
- Stop and request assistance if tmux is unavailable on the system

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `BW_SESSION` | Session key for vault decryption (required for all vault commands) |
| `BW_CLIENTID` | API key client ID (for `--apikey` login) |
| `BW_CLIENTSECRET` | API key client secret (for `--apikey` login) |
| `BITWARDENCLI_APPDATA_DIR` | Custom config directory (enables multi-account setups) |

## Self-Hosted Servers

For Vaultwarden or self-hosted Bitwarden:

```bash
bw config server https://your-bitwarden-server.com
```

## Reference Documentation

- [Get Started Guide](references/get-started.md) - Installation and initial setup
- [CLI Examples](references/cli-examples.md) - Common usage patterns and advanced operations
