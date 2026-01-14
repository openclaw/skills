---
name: homebrew
description: Homebrew package manager for macOS. Search, install, manage, and troubleshoot packages and casks.
metadata: {"clawdbot":{"emoji":"🍺","requires":{"bins":["brew"]}}}
---

# Homebrew Package Manager

Complete Homebrew command reference and usage guide for installing, managing, and troubleshooting macOS packages.

## When to Use
- Installing packages or applications (`brew install X`)
- Searching for available packages (`brew search X`)
- Updating and upgrading existing packages
- Checking package information and dependencies
- Troubleshooting installation issues
- Managing installed packages

## Command Reference

### Package Search & Information

#### `brew search TEXT|/REGEX/`
**Usage:** Find packages by name or regex pattern
**When to use:** When user asks to find or search for a package
**Examples:**
```bash
brew search python
brew search /^node/
```

#### `brew info [FORMULA|CASK...]`
**Usage:** Display detailed information about one or more packages
**When to use:** Before installing to see dependencies, options, and details
**Examples:**
```bash
brew info python
brew info chrome google-chrome
```

### Installation & Upgrades

#### `brew install FORMULA|CASK...`
**Usage:** Install one or more packages or applications
**When to use:** When user says "install X" or "use brew to install X"
**Notes:**
- FORMULA = command-line tools (installed to /usr/local/bin)
- CASK = GUI applications (installed to /Applications)
- Can install multiple at once: `brew install git python nodejs`
**Examples:**
```bash
brew install python
brew install google-chrome  # installs as cask
brew install git python nodejs
```

#### `brew update`
**Usage:** Fetch the newest version of Homebrew and all formulae
**When to use:** When brew seems outdated or before major operations
**Notes:** Doesn't upgrade packages, just updates the package list
**Examples:**
```bash
brew update
```

#### `brew upgrade [FORMULA|CASK...]`
**Usage:** Upgrade installed packages or specific packages
**When to use:** When user wants to update to newer versions
**Notes:**
- Without args: upgrades all outdated packages
- With args: upgrades only specified packages
**Examples:**
```bash
brew upgrade              # upgrade all outdated packages
brew upgrade python       # upgrade just python
brew upgrade python git   # upgrade multiple
```

### Package Management

#### `brew uninstall FORMULA|CASK...`
**Usage:** Remove installed packages
**When to use:** When user wants to remove/delete a package
**Notes:** Can uninstall multiple at once
**Examples:**
```bash
brew uninstall python
brew uninstall google-chrome
```

#### `brew list [FORMULA|CASK...]`
**Usage:** List installed packages or files from specific packages
**When to use:** When user wants to see what's installed or what files a package contains
**Examples:**
```bash
brew list                 # show all installed packages
brew list python          # show files installed by python
```

### Configuration & Troubleshooting

#### `brew config`
**Usage:** Display Homebrew configuration and environment info
**When to use:** Debugging installation issues or checking system setup
**Shows:**
- Installation path
- Xcode location
- Git version
- CPU architecture
**Examples:**
```bash
brew config
```

#### `brew doctor`
**Usage:** Check for potential problems with Homebrew installation
**When to use:** When experiencing installation issues or errors
**Returns:** Warnings and suggestions for fixing issues
**Examples:**
```bash
brew doctor
```

#### `brew install --verbose --debug FORMULA|CASK`
**Usage:** Install with verbose output and debug information
**When to use:** When standard install fails and you need detailed error messages
**Examples:**
```bash
brew install --verbose --debug python
```

### Advanced Usage

#### `brew create URL [--no-fetch]`
**Usage:** Create a new formula from source code
**When to use:** Creating custom packages (advanced users)
**Options:**
- `--no-fetch` = don't download source immediately
**Examples:**
```bash
brew create https://example.com/package.tar.gz
```

#### `brew edit [FORMULA|CASK...]`
**Usage:** Edit formula or cask definition
**When to use:** Customizing package installation (advanced users)
**Examples:**
```bash
brew edit python
```

#### `brew commands`
**Usage:** Show all available brew commands
**When to use:** Learning about additional brew features
**Examples:**
```bash
brew commands
```

#### `brew help [COMMAND]`
**Usage:** Get help for specific command
**When to use:** Need detailed help for a specific command
**Examples:**
```bash
brew help install
brew help upgrade
```

## Quick Reference

| Task | Command |
|------|---------|
| Search for package | `brew search TEXT` |
| Get package info | `brew info FORMULA` |
| Install package | `brew install FORMULA` |
| Install app | `brew install CASK` |
| Update package list | `brew update` |
| Upgrade all packages | `brew upgrade` |
| Upgrade specific package | `brew upgrade FORMULA` |
| Remove package | `brew uninstall FORMULA` |
| List installed | `brew list` |
| Check config | `brew config` |
| Troubleshoot | `brew doctor` |

## Common Workflows

### Installing a New Package
1. Search: `brew search python`
2. Get info: `brew info python@3.11`
3. Install: `brew install python@3.11`

### Troubleshooting Installation
1. Check config: `brew config`
2. Run doctor: `brew doctor`
3. Retry with debug: `brew install --verbose --debug FORMULA`

### Maintaining Homebrew
1. Update: `brew update`
2. Check what's outdated: `brew upgrade` (shows what would upgrade)
3. Upgrade all: `brew upgrade`

## Key Concepts

**FORMULA:** Command-line tools and libraries (e.g., python, git, node)
**CASK:** GUI applications (e.g., google-chrome, vscode, slack)
**TAP:** Third-party formula repositories (e.g., `brew tap homebrew/cask-versions`)

## Notes
- All brew commands require Homebrew to be installed
- Xcode Command Line Tools are required for building from source
- Some packages may prompt for sudo password
- Different packages have different installation times
- Package names are case-insensitive but shown lowercase by convention

## Resources
- Official docs: https://docs.brew.sh
- Formula documentation: https://github.com/Homebrew/homebrew-core
- Cask documentation: https://github.com/Homebrew/homebrew-cask
