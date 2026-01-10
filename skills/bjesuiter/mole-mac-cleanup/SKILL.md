---
name: mole-mac-cleanup
version: 1.0.0
description: Mac cleanup & optimization tool combining CleanMyMac, AppCleaner, DaisyDisk features. Deep cleaning, smart uninstaller, disk insights, and project artifact purge.
homepage: https://github.com/tw93/Mole
metadata: {"clawdbot":{"emoji":"🧹","os":["darwin"],"requires":{"bins":["mo"]},"install":[{"id":"brew","kind":"brew","formula":"mole","bins":["mo"],"label":"Install Mole via Homebrew"}]}}
---

# Mole - Mac Cleanup & Optimization Tool

**Repo:** https://github.com/tw93/Mole
**Command:** `mo` (not `mole`!)
**Install:** `brew install mole`

> **Note for humans:** `mo` without params opens an interactive TUI mode. Not useful for agents, but you might wanna try it manually! 😉

## What It Does

All-in-one toolkit combining CleanMyMac, AppCleaner, DaisyDisk, and iStat Menus:
- **Deep cleaning** — removes caches, logs, browser leftovers
- **Smart uninstaller** — removes apps + hidden remnants
- **Disk insights** — visualizes usage, manages large files
- **Live monitoring** — real-time system stats
- **Project artifact purge** — cleans `node_modules`, `target`, `build`, etc.

---

## Non-Interactive Commands (Clawd-friendly)

### Preview / Dry Run (ALWAYS USE FIRST)
```bash
mo clean --dry-run              # Preview cleanup plan
mo clean --dry-run --debug      # Detailed preview with risk levels & file info
mo optimize --dry-run           # Preview optimization actions
mo optimize --dry-run --debug   # Detailed optimization preview
```

### Execute Cleanup
```bash
mo clean                        # Run deep cleanup (caches, logs, browser data, trash)
mo clean --debug                # Cleanup with detailed logs
```

### System Optimization
```bash
mo optimize                     # Rebuild caches, reset services, refresh Finder/Dock
mo optimize --debug             # With detailed operation logs
```

**What `mo optimize` does:**
- Rebuild system databases and clear caches
- Reset network services
- Refresh Finder and Dock
- Clean diagnostic and crash logs
- Remove swap files and restart dynamic pager
- Rebuild launch services and Spotlight index

### Whitelist Management
```bash
mo clean --whitelist            # Manage protected cache paths
mo optimize --whitelist         # Manage protected optimization rules
```

### Project Artifact Purge
```bash
mo purge                        # Clean old build artifacts (node_modules, target, venv, etc.)
mo purge --paths                # Configure which directories to scan
```

Config file: `~/.config/mole/purge_paths`

### Installer Cleanup
```bash
mo installer                    # Find/remove .dmg, .pkg, .zip installers
```

Scans: Downloads, Desktop, Homebrew caches, iCloud, Mail attachments

### Setup & Maintenance
```bash
mo touchid                      # Configure Touch ID for sudo
mo completion                   # Set up shell tab completion
mo update                       # Update Mole itself
mo remove                       # Uninstall Mole from system
mo --version                    # Show installed version
mo --help                       # Show help
```

---

## Typical Workflow

1. **Check what would be cleaned:**
   ```bash
   mo clean --dry-run --debug
   ```

2. **If looks good, run cleanup:**
   ```bash
   mo clean
   ```

3. **Optimize system (after cleanup):**
   ```bash
   mo optimize --dry-run
   mo optimize
   ```

4. **Clean dev project artifacts:**
   ```bash
   mo purge
   ```

---

## What Gets Cleaned (`mo clean`)

- User app cache
- Browser cache (Chrome, Safari, Firefox)
- Developer tools (Xcode, Node.js, npm)
- System logs and temp files
- App-specific cache (Spotify, Dropbox, Slack)
- Trash

## Notes

- **Terminal:** Best with Ghostty, Alacritty, kitty, WezTerm. iTerm2 has issues.
- **Safety:** Use `--dry-run` first. Built with strict protections.
- **Debug:** Add `--debug` for detailed logs.
