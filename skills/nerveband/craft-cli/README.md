# Craft CLI Skill for Clawdbot

Fast, token-efficient Craft Documents integration via CLI.

## Files

- **SKILL.md** - Complete skill documentation for Clawdbot
- **craft** - Craft CLI binary (v1.0.0, macOS ARM64)
- **craft-helper.sh** - Quick space switching script

## Quick Reference

### Switch Spaces
```bash
# Business (wavedepth)
~/clawd/skills/craft-cli/craft-helper.sh wavedepth

# Personal
~/clawd/skills/craft-cli/craft-helper.sh personal
```

### Common Operations
```bash
# List documents
~/clawd/skills/craft-cli/craft list --format table

# Search
~/clawd/skills/craft-cli/craft search "query"

# Get document
~/clawd/skills/craft-cli/craft get <doc-id>
```

## Source

GitHub: https://github.com/nerveband/craft-cli
