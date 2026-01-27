# Bitwarden CLI: Getting Started

## System Requirements

The Bitwarden CLI runs on:
- **macOS**: x64 and ARM64
- **Windows**: x64
- **Linux**: x64 (glibc-based distributions)

For npm installation, Node.js 16+ is required.

## Installation Methods

### NPM (Recommended - Cross-Platform)

```bash
npm install -g @bitwarden/cli
```

This method provides automatic updates via `npm update -g @bitwarden/cli`.

### Homebrew (macOS/Linux)

```bash
brew install bitwarden-cli
```

### Chocolatey (Windows)

```powershell
choco install bitwarden-cli
```

### Snap (Linux)

```bash
sudo snap install bw
```

### Native Executables

Download pre-built binaries from https://bitwarden.com/download/

For Linux/macOS, grant execute permissions:
```bash
chmod +x bw
sudo mv bw /usr/local/bin/
```

## Verify Installation

```bash
bw --version
```

Expected output: Version number like `2024.12.0`

## Initial Configuration

### Connect to Bitwarden Server

For standard Bitwarden cloud (default):
```bash
# No configuration needed - uses https://vault.bitwarden.com by default
```

For self-hosted Bitwarden or Vaultwarden:
```bash
bw config server https://your-server.example.com
```

Verify server configuration:
```bash
bw config server
```

### First-Time Login

**Interactive login (recommended for first setup):**
```bash
bw login
```

You'll be prompted for:
1. Email address
2. Master password
3. Two-step verification code (if enabled)

**Login with API key (for automation):**

First, obtain your API key from the Bitwarden web vault:
1. Go to Settings > Security > Keys
2. View API Key
3. Note your `client_id` and `client_secret`

```bash
# Set environment variables
export BW_CLIENTID="user.xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export BW_CLIENTSECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Login
bw login --apikey

# Unlock vault (required after API key login)
export BW_SESSION=$(bw unlock --raw)
```

### Session Management with tmux

The CLI requires a session key for vault operations. Use tmux to preserve sessions:

```bash
# Create a dedicated session
tmux new-session -d -s bitwarden

# Attach to session
tmux attach -t bitwarden

# Inside tmux: login and export session
bw login
export BW_SESSION=$(bw unlock --raw)

# Now run your commands
bw list items

# When finished
bw lock

# Detach from tmux (Ctrl+B, then D)
```

## Verify Access

After login and unlock:

```bash
# Check authentication status
bw status

# List vaults (should show your email)
bw list organizations

# Sync vault data
bw sync
```

## Troubleshooting

### "You are not logged in"

Run `bw login` to authenticate.

### "Vault is locked"

Run `bw unlock` and export the session key:
```bash
export BW_SESSION=$(bw unlock --raw)
```

### "Session key is invalid"

The session has expired. Re-unlock:
```bash
bw lock
export BW_SESSION=$(bw unlock --raw)
```

### Command hangs or times out

Check network connectivity to Bitwarden server:
```bash
curl -I https://vault.bitwarden.com
```

For self-hosted servers, verify the server URL:
```bash
bw config server
```
