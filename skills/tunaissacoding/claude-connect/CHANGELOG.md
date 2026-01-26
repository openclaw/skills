# Changelog

## v1.1.0 - 2026-01-26

### Fixed
- **OAuth auth-profiles.json format bug**: Script now writes proper OAuth format (`type: oauth` with `access`/`refresh`/`expires` fields) instead of forcing `type: token`
- Removed code that deleted `anthropic:claude-cli` profile
- Properly sets profile order and lastGood for OAuth

### Changed
- Default profile name changed from `anthropic:default` to `anthropic:claude-cli` (proper OAuth profile)
- SKILL.md updated to reflect current functionality (removed deprecation notice)

### Why This Matters
The original version fought against OAuth by converting it to token mode. This caused issues for users where `clawdbot onboard --auth-choice claude-cli` wouldn't properly save OAuth credentials. This version fixes that and ensures OAuth works correctly.

---

## v1.0.12 - 2026-01-25

- Initial archived version (deprecated)
