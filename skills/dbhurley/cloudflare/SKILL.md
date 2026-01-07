---
name: cloudflare
description: Cloudflare CLI - manage DNS records, purge cache, and control Workers routes.
version: 1.0.0
author: dbhurley
homepage: https://cloudflare.com
metadata:
  clawdis:
    emoji: "🔶"
    requires:
      bins: ["python3", "uv"]
      env:
        - CLOUDFLARE_API_TOKEN
    primaryEnv: CLOUDFLARE_API_TOKEN
---

# Cloudflare CLI

Manage Cloudflare DNS, cache, and Workers via the API.

## 🔑 Required Secrets

| Variable | Description | How to Get |
|----------|-------------|------------|
| `CLOUDFLARE_API_TOKEN` | Scoped API token | Cloudflare → My Profile → API Tokens |

**Recommended token permissions:**
- DNS:Read, DNS:Edit
- Cache Purge:Purge
- Workers Routes:Edit

## ⚙️ Setup

Configure in `~/.clawdis/clawdis.json`:
```json
{
  "skills": {
    "cloudflare": {
      "env": {
        "CLOUDFLARE_API_TOKEN": "your-token"
      }
    }
  }
}
```

## 📋 Commands

### Verify Token

```bash
# Test that your token works
uv run {baseDir}/scripts/cloudflare.py verify
```

### Zones (Domains)

```bash
# List all zones
uv run {baseDir}/scripts/cloudflare.py zones

# Get zone details
uv run {baseDir}/scripts/cloudflare.py zone <zone_id_or_domain>
```

### DNS Records

```bash
# List DNS records for a zone
uv run {baseDir}/scripts/cloudflare.py dns list <domain>

# Add DNS record
uv run {baseDir}/scripts/cloudflare.py dns add <domain> --type A --name www --content 1.2.3.4
uv run {baseDir}/scripts/cloudflare.py dns add <domain> --type CNAME --name blog --content example.com

# Update DNS record
uv run {baseDir}/scripts/cloudflare.py dns update <domain> <record_id> --content 5.6.7.8

# Delete DNS record (asks for confirmation)
uv run {baseDir}/scripts/cloudflare.py dns delete <domain> <record_id>

# Delete without confirmation
uv run {baseDir}/scripts/cloudflare.py dns delete <domain> <record_id> --yes
```

### Cache

```bash
# Purge everything
uv run {baseDir}/scripts/cloudflare.py cache purge <domain> --all

# Purge specific URLs
uv run {baseDir}/scripts/cloudflare.py cache purge <domain> --urls "https://example.com/page1,https://example.com/page2"

# Purge by prefix
uv run {baseDir}/scripts/cloudflare.py cache purge <domain> --prefix "/blog/"
```

### Workers Routes

```bash
# List routes
uv run {baseDir}/scripts/cloudflare.py routes list <domain>

# Add route
uv run {baseDir}/scripts/cloudflare.py routes add <domain> --pattern "*.example.com/*" --worker my-worker
```

## 📤 Output Formats

All commands support `--json` for machine-readable output:
```bash
uv run {baseDir}/scripts/cloudflare.py dns list example.com --json
```

## 🔗 Common Workflows

### Point domain to Vercel
```bash
# Add CNAME for apex
cloudflare dns add example.com --type CNAME --name @ --content cname.vercel-dns.com --proxied false

# Add CNAME for www
cloudflare dns add example.com --type CNAME --name www --content cname.vercel-dns.com --proxied false
```

### Clear cache after deploy
```bash
cloudflare cache purge example.com --all
```

## 📦 Installation

```bash
clawdhub install cloudflare
```
