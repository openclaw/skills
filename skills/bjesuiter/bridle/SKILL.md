---
name: bridle
description: "Unified configuration manager for AI coding assistants. Manage profiles, install skills/agents/commands, and switch configurations across Claude Code, OpenCode, Goose, and Amp."
metadata: {"version":"1.0.0","homepage":"https://github.com/neiii/bridle","clawdbot":{"emoji":"🐴","os":["darwin","linux"],"requires":{"bins":["bridle"]},"install":[{"id":"brew","kind":"brew","formula":"neiii/bridle/bridle","bins":["bridle"],"label":"Install bridle via Homebrew"},{"id":"cargo","kind":"shell","command":"cargo install bridle","bins":["bridle"],"label":"Install bridle via Cargo"}]}}
---

# Bridle Skill

Unified configuration manager for AI coding assistants. Manage profiles, install skills/agents/commands, and switch configurations across Claude Code, OpenCode, Goose, and Amp.

## Installation

```bash
# Homebrew (macOS/Linux)
brew install neiii/bridle/bridle

# Cargo (Rust)
cargo install bridle

# From source
git clone https://github.com/neiii/bridle && cd bridle && cargo install --path .
```

## Core Concepts

- **Harnesses**: AI coding assistants (`claude`, `opencode`, `goose`, `amp`)
- **Profiles**: Saved configurations per harness (e.g., `work`, `personal`, `minimal`)

## Quick Commands

```bash
# Launch interactive TUI
bridle

# Show active profiles across all harnesses
bridle status

# Initialize bridle config and default profiles
bridle init
```

## Profile Management

```bash
# List all profiles for a harness
bridle profile list <harness>

# Show profile details (model, MCPs, plugins)
bridle profile show <harness> <name>

# Create empty profile
bridle profile create <harness> <name>

# Create profile from current config
bridle profile create <harness> <name> --from-current

# Switch/activate a profile
bridle profile switch <harness> <name>

# Open profile in editor
bridle profile edit <harness> <name>

# Compare profiles
bridle profile diff <harness> <name> [other]

# Delete a profile
bridle profile delete <harness> <name>
```

## Installing Components

Bridle can install skills, agents, commands, and MCPs from GitHub repos and auto-translates paths/configs for each harness.

```bash
# Install from GitHub (owner/repo or full URL)
bridle install owner/repo

# Overwrite existing installations
bridle install owner/repo --force

# Interactively remove components [experimental]
bridle uninstall <harness> <profile>
```

## Configuration

Config location: `~/.config/bridle/config.toml`

```bash
# Get a config value
bridle config get <key>

# Set a config value
bridle config set <key> <value>
```

**Config keys:** `profile_marker`, `editor`, `tui.view`, `default_harness`

## Output Formats

All commands support `-o, --output <format>`:
- `text` (default) — Human-readable
- `json` — Machine-readable
- `auto` — Text for TTY, JSON for pipes

## Supported Harnesses & Config Locations

| Harness     | Config Location         | Status       |
| ----------- | ----------------------- | ------------ |
| Claude Code | `~/.claude/`            | Full support |
| OpenCode    | `~/.config/opencode/`   | Full support |
| Goose       | `~/.config/goose/`      | Full support |
| Amp         | `~/.amp/`               | Experimental |

## Component Paths by Harness

| Component | Claude Code | OpenCode | Goose |
| --------- | ----------- | -------- | ----- |
| Skills    | `~/.claude/skills/` | `~/.config/opencode/skill/` | `~/.config/goose/skills/` |
| Agents    | `~/.claude/plugins/*/agents/` | `~/.config/opencode/agent/` | — |
| Commands  | `~/.claude/plugins/*/commands/` | `~/.config/opencode/command/` | — |
| MCPs      | `~/.claude/.mcp.json` | `opencode.jsonc` | `config.yaml` |

## Common Workflows

### Create a work profile from current config
```bash
bridle profile create claude work --from-current
```

### Create profile from existing profile (duplicate & modify)
```bash
# 1. Switch to the source profile
bridle profile switch opencode default

# 2. Create new profile from current (now the source profile)
bridle profile create opencode minimal --from-current

# 3. Edit the new profile to remove/modify as needed
bridle profile edit opencode minimal
```

### Switch between profiles
```bash
bridle profile switch claude personal
bridle profile switch opencode minimal
```

### Check status across all harnesses
```bash
bridle status
```
