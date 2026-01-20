# 🔧 Internal Development Notes

> This document captures the development history, design decisions, and architecture of the Smart Follow-ups skill.

**Created:** January 20, 2026  
**Author:** Cami (Clawdbot) with Robby  
**Status:** v1.0.0 - Ready for testing

---

## 📜 Development History

### Origin

The Smart Follow-ups skill was inspired by [Chameleon AI Chat](https://github.com/robbyczgw-cla/Chameleon-AI-Chat), Robby's open-source AI chat application. Chameleon features a "Smart Follow-up Suggestions" system that generates contextual follow-up questions after every AI response.

Robby wanted to bring this feature to Clawdbot as a standalone skill that could work across multiple messaging channels.

### Initial Specification (from Chameleon)

Chameleon's original implementation:
- 6 suggestions total (2 per category)
- Three categories: Quick (green), Deep Dive (purple), Related (blue)
- Mobile-optimized with clickable suggestions
- AI-generated based on conversation context

### Design Decisions

#### 1. Reduced to 3 suggestions (from 6)

**Decision:** 1 suggestion per category instead of 2

**Rationale (from Robby):**
> "Make 3 instead of 6 for here makes more sense, 6 is too much"

**Benefits:**
- Cleaner mobile UX
- Less overwhelming
- Faster to scan and decide
- Each suggestion is more focused/high-quality

#### 2. Clawdbot Native Auth as Default

**Decision:** Use Clawdbot's existing authentication by default, not separate API keys

**Robby's requirement:**
> "Follow ups skill should use the exact same login and model and authentication... we use as auth anthropic Claude CLI token NOT Openrouter"

**Implementation:**
- Default `provider: "clawdbot"` uses current session's model and auth
- OpenRouter and direct Anthropic are optional fallbacks
- No separate API key required for default mode

#### 3. Model Inheritance

**Decision:** Follow-ups use the same model as the current chat session

**Robby's requirement:**
> "Default should use the model the user is using for chat"

**Implementation:**
- If chatting with Opus → follow-ups use Opus
- If chatting with Sonnet → follow-ups use Sonnet
- If chatting with Haiku → follow-ups use Haiku
- Configurable override available

#### 4. Manual Trigger (not auto)

**Decision:** Use `/followups` command, not automatic after every response

**Rationale:**
- User controls when they want suggestions
- No spam/clutter
- Lower API costs
- Can add auto-trigger as optional feature later

---

## 🏗️ Architecture

### Handler-Based Integration

The skill works by returning a prompt to Clawdbot's agent system:

```
User types /followups
    ↓
Handler receives command
    ↓
Handler returns agent-prompt type response
    ↓
Clawdbot agent generates follow-ups using current model/auth
    ↓
Handler transforms response to buttons/text
    ↓
Sent to user
```

**Why this approach:**
- No separate API calls from the skill
- Uses Clawdbot's existing infrastructure
- Inherits session model and authentication
- Consistent with Clawdbot's architecture

### CLI Tool (Fallback/Testing)

The CLI exists for:
- Standalone testing
- Users who want to use OpenRouter/Anthropic directly
- Scripting/automation use cases

```
CLI receives context JSON
    ↓
Makes API call (OpenRouter or Anthropic)
    ↓
Parses response
    ↓
Formats output (json/telegram/text/compact)
```

---

## 🔧 Technical Notes

### OpenRouter Model IDs

OpenRouter uses different model ID format:
- ✅ `anthropic/claude-sonnet-4.5` (dot)
- ❌ `anthropic/claude-sonnet-4-5` (dash)

Discovered during testing when `claude-sonnet-4-5` returned "not a valid model ID" error.

### Telegram Callback Data Limit

Telegram inline buttons have a 64-byte limit for `callback_data`. Questions are truncated if needed:

```javascript
callback_data: suggestions.quick.substring(0, 50)
```

### readme.md Domain Issue

During development, we discovered that typing "readme.md" in messages caused Telegram to show spam link previews. This is because `readme.md` is an actual registered domain (Moldova TLD) that redirects to a spam site:

```
readme.md → 302 redirect → dealsbe.com (spam)
```

**Not a security issue** — just unfortunate domain squatting. Telegram auto-generates link previews for text that looks like URLs.

---

## 📁 File Structure

| File | Purpose | Audience |
|------|---------|----------|
| `README.md` | Public documentation | Users, ClawdHub |
| `SKILL.md` | Clawdbot skill manifest | Clawdbot |
| `FAQ.md` | Common questions | Users |
| `INTERNAL.md` | This file - dev notes | Developers |
| `handler.js` | Command handler | Clawdbot |
| `cli/followups-cli.js` | Standalone CLI | Power users |
| `CHANGELOG.md` | Version history | Users, devs |
| `CONTRIBUTING.md` | Contribution guide | Contributors |
| `LICENSE` | MIT License | Legal |

---

## 🔮 Future Improvements

### Short-term
- [ ] Add auto-trigger mode (configurable)
- [ ] Support custom prompts/categories
- [ ] Add `/followups 5` to specify number
- [ ] Cache recent suggestions to avoid regeneration

### Medium-term
- [ ] Support for follow-up chains (click suggestion → new suggestions)
- [ ] Category customization (add/remove categories)
- [ ] Integration with Clawdbot memory (suggest based on past conversations)

### Long-term
- [ ] Multi-language support
- [ ] Learning from user preferences (which categories they click most)
- [ ] Context-aware auto-trigger (only suggest when conversation seems stuck)

---

## 🧪 Testing Checklist

- [x] CLI help command works
- [x] CLI generates valid JSON output
- [x] CLI generates valid Telegram buttons
- [x] CLI text mode formatting correct
- [x] OpenRouter API integration works
- [x] Model ID format correct for OpenRouter
- [ ] Handler integration with Clawdbot
- [ ] `/followups` command registered
- [ ] Telegram buttons clickable and functional
- [ ] Signal/iMessage text fallback works

---

## 📊 Cost Analysis

| Model | Cost per Generation | Notes |
|-------|---------------------|-------|
| Claude 3 Haiku | ~$0.0002 | Cheapest, good quality |
| Claude Sonnet 4.5 | ~$0.003 | Default for Clawdbot |
| Claude Opus 4.5 | ~$0.015 | Highest quality |

**Recommendation:** For cost-conscious users, configure OpenRouter with Haiku specifically for follow-ups while keeping main chat on Sonnet/Opus.

---

## 🗣️ Key Quotes from Development

**On button count:**
> "Make 3 instead of 6 for here makes more sense 6 is too much" — Robby

**On authentication:**
> "Follow ups skill should use the exact same login and model and authentication... NOT Openrouter but yeah make Openrouter a configurable option if you want" — Robby

**On model consistency:**
> "Default should use the model the user is using for chat" — Robby

---

## 📝 Changelog Summary

### v1.0.0 (2026-01-20)
- Initial release
- 3 suggestions (Quick, Deep, Related)
- Clawdbot native auth as default
- OpenRouter and Anthropic as optional providers
- CLI tool for standalone use
- Multi-channel support (buttons + text fallback)

---

**Last updated:** January 20, 2026
