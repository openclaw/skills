# Bitwarden CLI Examples

## Prerequisites

All commands assume you are:
1. Inside a tmux session: `tmux attach -t bitwarden` or `tmux new -s bitwarden`
2. Logged in: `bw login`
3. Unlocked with session exported: `export BW_SESSION=$(bw unlock --raw)`

## Reading Credentials

### Get Password by Name

```bash
# Simple lookup (requires unique name)
bw get password "GitHub"

# If multiple items match, use item ID
bw get password 12345678-1234-1234-1234-123456789012
```

### Get Username

```bash
bw get username "GitHub"
```

### Get TOTP Code

```bash
# Returns current 6-digit code
bw get totp "GitHub"
```

### Get Full Item (JSON)

```bash
bw get item "GitHub"

# Pretty print
bw get item "GitHub" | jq .

# Extract specific login fields
bw get item "GitHub" | jq -r '.login.username'
bw get item "GitHub" | jq -r '.login.password'
bw get item "GitHub" | jq -r '.login.totp'
```

### Get Custom Fields

```bash
# List all custom fields
bw get item "AWS Credentials" | jq '.fields'

# Get specific custom field by name
bw get item "AWS Credentials" | jq -r '.fields[] | select(.name=="access_key") | .value'

# Get hidden field
bw get item "AWS Credentials" | jq -r '.fields[] | select(.name=="secret_key") | .value'
```

### Get Secure Notes

```bash
# Get note content
bw get notes "My Secure Note"

# Full item with metadata
bw get item "My Secure Note" | jq -r '.notes'
```

## Listing and Searching

### List All Items

```bash
# All items
bw list items

# Count items
bw list items | jq 'length'

# Item names only
bw list items | jq -r '.[].name'
```

### Search Items

```bash
# Search by name (case-insensitive)
bw list items --search "github"

# Search in specific folder
bw list items --folderid 12345678-1234-1234-1234-123456789012 --search "api"

# Items without folder
bw list items --folderid null
```

### List Folders

```bash
bw list folders
bw list folders | jq -r '.[].name'
```

### List Organizations

```bash
bw list organizations
```

### List Collections

```bash
bw list collections
bw list org-collections --organizationid <org-id>
```

## Environment Variable Injection

### Export to Environment

```bash
# Single credential
export GITHUB_TOKEN=$(bw get password "GitHub Token")

# Multiple credentials
export AWS_ACCESS_KEY_ID=$(bw get item "AWS" | jq -r '.fields[] | select(.name=="access_key") | .value')
export AWS_SECRET_ACCESS_KEY=$(bw get item "AWS" | jq -r '.fields[] | select(.name=="secret_key") | .value')
```

### Run Command with Injected Secrets

```bash
# Using shell substitution
DATABASE_URL="postgres://user:$(bw get password 'DB Prod')@host/db" ./my-app

# Using environment export
export DATABASE_PASSWORD=$(bw get password "DB Prod")
./my-app
```

## Vault Synchronization

### Sync from Server

```bash
# Full sync
bw sync

# Force sync (ignore cache)
bw sync --force
```

### Check Sync Status

```bash
bw status | jq '.lastSync'
```

## Account Management

### Check Current Session

```bash
# Full status
bw status

# Just logged-in state
bw status | jq -r '.status'

# Current user
bw status | jq -r '.userEmail'
```

### Lock Vault

```bash
# Lock (keeps session, requires unlock)
bw lock
```

### Logout

```bash
# Full logout (clears all session data)
bw logout
```

## Working with Attachments

### Download Attachment

```bash
# List attachments on an item
bw get item "SSL Certificate" | jq '.attachments'

# Download by attachment ID
bw get attachment <attachment-id> --itemid <item-id> --output ./cert.pem
```

## Advanced: Creating and Editing Items

### Get Templates

```bash
# Login item template
bw get template item

# Folder template
bw get template folder
```

### Create New Item

```bash
# Create from template
bw get template item | jq '.name="New Item" | .login.username="user" | .login.password="pass"' | bw encode | bw create item
```

### Edit Existing Item

```bash
# Get item, modify, update
bw get item <item-id> | jq '.login.password="newpassword"' | bw encode | bw edit item <item-id>
```

## Error Handling Patterns

### Check Authentication Before Operations

```bash
# Verify unlocked state
if [ "$(bw status | jq -r '.status')" != "unlocked" ]; then
    echo "Vault is locked. Run: export BW_SESSION=\$(bw unlock --raw)"
    exit 1
fi
```

### Handle Missing Items

```bash
# Check if item exists
if ! bw get item "GitHub" >/dev/null 2>&1; then
    echo "Item 'GitHub' not found in vault"
    exit 1
fi
```

## Multi-Account Setup

### Use Different Config Directories

```bash
# Personal account
export BITWARDENCLI_APPDATA_DIR=~/.bitwarden-personal
bw login personal@example.com

# Work account (different terminal)
export BITWARDENCLI_APPDATA_DIR=~/.bitwarden-work
bw login work@company.com
```

## Self-Hosted / Vaultwarden

### Configure Custom Server

```bash
# Set server URL
bw config server https://vault.example.com

# Verify configuration
bw config server

# Reset to default Bitwarden cloud
bw config server https://vault.bitwarden.com
```
