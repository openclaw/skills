---
name: github-pat
description: Interact with GitHub using Personal Access Tokens. Secure, user-controlled access - no OAuth, no full account access. Clone, push, branch, PR, issues. Use when user wants to work with GitHub repos.
---

# GitHub PAT

Interact with GitHub using Personal Access Tokens. User controls access via PAT scopes.

## Setup

User provides their PAT:
```
1. Create PAT at github.com/settings/tokens
2. Select scopes (repo for full, public_repo for public only)
3. Provide token to agent
```

Store in TOOLS.md or pass via `--token`.

## Commands

```bash
# List repos you have access to
python3 scripts/gh.py repos [--token TOKEN]

# Clone a repo
python3 scripts/gh.py clone owner/repo [--token TOKEN]

# Create branch
python3 scripts/gh.py branch <branch-name> [--repo owner/repo]

# Commit and push
python3 scripts/gh.py push "<message>" [--branch branch] [--repo owner/repo]

# Open a pull request
python3 scripts/gh.py pr "<title>" [--body "description"] [--base main] [--head branch]

# Create an issue
python3 scripts/gh.py issue "<title>" [--body "description"] [--repo owner/repo]

# View repo info
python3 scripts/gh.py info owner/repo
```

## Security Model

- **User controls access** via PAT scopes
- **No OAuth** - no "allow full access" prompts
- **Least privilege** - user creates PAT with minimal needed scopes
- **Fine-grained PATs** supported for specific repo access

## Token Storage

Agent stores token in TOOLS.md under `### GitHub` section. Never expose in logs or messages.
