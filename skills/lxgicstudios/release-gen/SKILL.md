---
name: release-gen
description: Generate semantic version bumps and git tags from commit history. Use when preparing a release.
---

# Release Gen

Figuring out whether to bump major, minor, or patch is tedious. This tool analyzes your commits since the last tag and determines the right version bump. Then creates the tag and updates your changelog.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-release
```

## What It Does

- Analyzes commits since last tag to determine version bump
- Follows semantic versioning (major.minor.patch)
- Creates annotated git tags
- Generates changelog entries
- Supports conventional commits but works with any commit style

## Usage Examples

```bash
# Analyze and suggest version bump
npx ai-release

# Create the release (tag + changelog)
npx ai-release --create

# Force a specific bump type
npx ai-release --bump major

# Preview without making changes
npx ai-release --dry-run

# Include pre-release tag
npx ai-release --prerelease beta
```

## Best Practices

- **Use conventional commits** - feat:, fix:, BREAKING CHANGE: make analysis more accurate
- **Always dry-run first** - See what would happen before creating tags
- **Review the changelog** - AI groups things well but you might want to edit
- **Tag on main only** - Keep releases off feature branches

## When to Use This

- Ready to ship a new version and need to figure out the version number
- Want to automate your release process
- Generating changelogs manually is eating your time
- Need consistent tagging across team members

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgic.dev

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended. Requires OPENAI_API_KEY environment variable.

```bash
export OPENAI_API_KEY=sk-...
npx ai-release --help
```

## How It Works

Reads git log since the last tag (or first commit if no tags). Classifies commits by impact: breaking changes trigger major bumps, new features trigger minor, fixes trigger patch. Creates an annotated tag and appends to your changelog file.

## License

MIT. Free forever. Use it however you want.
