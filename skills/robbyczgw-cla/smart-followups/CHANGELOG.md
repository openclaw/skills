# Changelog

All notable changes to Smart Follow-up Suggestions will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-20

### 🎉 Initial Release

#### Added
- **CLI Tool** (`cli/followups-cli.js`)
  - Standalone command-line interface for generating follow-ups
  - Support for multiple output modes: JSON, Telegram, text, compact
  - Context parsing from various input formats
  - Integration with Claude Haiku API
  - Proper error handling and validation

- **Clawdbot Integration** (`handler.js`)
  - `/followups` command support
  - Auto-trigger mode (optional)
  - Channel detection (inline buttons vs text mode)
  - Support for Telegram, Discord, Slack, Signal, iMessage, SMS

- **Documentation**
  - README.md: Feature overview and quick start
  - SKILL.md: Comprehensive Clawdbot integration guide
  - examples.md: Channel-specific output examples
  - INTERNAL.md: Architecture and design decisions
  - QUICKSTART.md: 5-minute setup guide

- **Features**
  - 3 contextual suggestions per generation (1 per category)
  - 3 categories: Quick (⚡), Deep Dive (🧠), Related (🔗)
  - Mobile-optimized UI (3 buttons = no scrolling on Telegram)
  - Context-aware analysis of last 1-3 exchanges
  - Sub-second latency with Claude Haiku
  - Cost-effective (~$0.0001 per generation)

#### Technical Details
- Uses `@anthropic-ai/sdk` v0.32.0
- Node.js 18+ required
- Temperature: 0.7 for optimal diversity
- Max tokens: 1024
- Context window: Last 3 exchanges

#### Design Decisions
- **3 suggestions (not 6)**: Mobile UX testing showed 3 buttons are cleaner and less cluttered on Telegram mobile, reducing decision fatigue while maintaining category diversity
- **One per category**: Quality over quantity - one well-crafted suggestion per category beats multiple mediocre ones

### Known Issues
- None

### Migration Guide
- N/A (initial release)

---

## [Unreleased]

### Planned for v1.1.0
- [ ] Caching layer for repeated contexts
- [ ] Rate limiting implementation
- [ ] User feedback tracking
- [ ] Personalization based on user profile
- [ ] Multi-language support (i18n)
- [ ] Improved error messages
- [ ] Unit tests
- [ ] Integration tests

### Under Consideration
- Fine-tuned domain-specific models
- Conversation memory (avoid repetitive suggestions)
- Batch processing for high-traffic scenarios
- Webhook support for external integrations
- Analytics dashboard

---

## Version History

- **1.0.0** (2026-01-20): Initial release

---

**Note**: For detailed technical changes, see [INTERNAL.md](./INTERNAL.md)
