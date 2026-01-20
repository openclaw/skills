# Contributing to Smart Follow-up Suggestions

Thank you for considering contributing to this project! 🎉

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Testing Guidelines](#testing-guidelines)

---

## 🤝 Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/). Please be respectful and constructive in all interactions.

**TL;DR**: Be kind, inclusive, and professional.

---

## 💡 How Can I Contribute?

### Reporting Bugs

Found a bug? Help us fix it!

1. **Check existing issues** first to avoid duplicates
2. **Create a new issue** with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Node version, OS, Clawdbot version)
   - Sample input/output if applicable

**Example**:
```
Title: JSON parsing fails for markdown-wrapped responses

Steps to reproduce:
1. Run: cat test.json | node cli/followups-cli.js --mode json
2. API returns response wrapped in ```json...```
3. CLI crashes with SyntaxError

Expected: CLI should extract JSON from markdown
Actual: SyntaxError thrown

Environment: Node v18.16.0, Ubuntu 22.04, @anthropic-ai/sdk v0.32.0
```

### Suggesting Enhancements

Have an idea? We'd love to hear it!

1. **Open an issue** with tag `enhancement`
2. Describe the feature and use case
3. Explain why it's valuable
4. (Optional) Suggest implementation approach

### Adding Channel Support

Want to add a new messaging platform?

1. Update `supportsInlineButtons()` in `handler.js`
2. Add channel-specific formatting if needed
3. Create examples in `examples.md`
4. Test with real account on that platform
5. Update `package.json` clawdbot.channels
6. Submit PR with screenshots/recordings

### Improving Documentation

Documentation improvements are always welcome!

- Fix typos or unclear explanations
- Add missing examples
- Improve code comments
- Translate to other languages (future)

---

## 🛠️ Development Setup

### Prerequisites

- Node.js 18+
- npm or yarn
- Anthropic API key
- Git

### Setup Steps

1. **Fork and clone**:
   ```bash
   git clone https://github.com/your-username/clawdbot-smart-followups.git
   cd clawdbot-smart-followups
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set API key**:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-your-key-here"
   ```

4. **Test your setup**:
   ```bash
   ./test.sh
   ```

5. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## 📏 Coding Standards

### Style Guide

- **Language**: JavaScript (ES2020+)
- **Formatting**: Standard JS style (2-space indent)
- **Line length**: Max 100 characters
- **Naming**:
  - `camelCase` for functions and variables
  - `UPPER_CASE` for constants
  - Descriptive names (no single-letter except loop counters)

### Code Principles

1. **Readability over cleverness**
   ```javascript
   // ✅ Good
   const isInteractiveChannel = buttonChannels.includes(channel);
   
   // ❌ Bad (too clever)
   const isInteractiveChannel = ~buttonChannels.indexOf(channel);
   ```

2. **Error handling**
   ```javascript
   // ✅ Always handle errors
   try {
     const result = await apiCall();
     return result;
   } catch (error) {
     console.error('API call failed:', error.message);
     throw new Error(`Failed to generate: ${error.message}`);
   }
   ```

3. **Comments for "why", not "what"**
   ```javascript
   // ✅ Good
   // Truncate to 40 chars to stay under Telegram's 64-byte callback_data limit
   const callbackData = `ask:${question.substring(0, 40)}`;
   
   // ❌ Bad (obvious)
   // Substring the question to 40 characters
   const callbackData = `ask:${question.substring(0, 40)}`;
   ```

4. **Small, focused functions**
   - One function = one responsibility
   - Max ~50 lines per function
   - Extract complex logic into helpers

### File Organization

```
smart-followups/
├── cli/                  # CLI tool (standalone)
│   └── followups-cli.js
├── handler.js            # Clawdbot integration
├── test/                 # Tests (future)
│   ├── cli.test.js
│   └── handler.test.js
├── docs/                 # Documentation
│   ├── README.md
│   ├── SKILL.md
│   ├── examples.md
│   └── INTERNAL.md
└── package.json
```

---

## 🚀 Submitting Changes

### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features (when test framework added)
3. **Ensure tests pass**: `npm test`
4. **Update CHANGELOG.md** under `[Unreleased]`
5. **Create PR** with clear description

### PR Template

```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes
- Added X
- Modified Y
- Fixed Z

## Testing
How was this tested?

## Screenshots (if applicable)
[Attach images/videos]

## Checklist
- [ ] Documentation updated
- [ ] Tests added/passing
- [ ] CHANGELOG.md updated
- [ ] No breaking changes (or documented)
```

### Review Process

- Maintainers will review within 3-5 days
- Address feedback promptly
- Be open to suggestions
- Once approved, maintainer will merge

---

## 🧪 Testing Guidelines

### Manual Testing Checklist

Before submitting PR, verify:

- [ ] CLI runs without errors: `./test.sh`
- [ ] All output modes work (json, telegram, text, compact)
- [ ] Error handling works (invalid input, missing API key)
- [ ] Different conversation lengths (1, 3, 10 exchanges)
- [ ] Various topics (technical, casual, creative)

### Testing Channels (if applicable)

- [ ] Telegram inline buttons
- [ ] Signal numbered list
- [ ] Discord (if you have access)

### Future: Unit Tests

When test framework is added:

```javascript
// Example test structure
describe('generateFollowups', () => {
  it('should return 6 suggestions across 3 categories', async () => {
    const exchanges = [{ user: 'test', assistant: 'response' }];
    const result = await generateFollowups(exchanges);
    
    expect(result.quick).toHaveLength(2);
    expect(result.deep).toHaveLength(2);
    expect(result.related).toHaveLength(2);
  });
});
```

---

## 🎯 Priority Areas

Current focus areas for contributions:

1. **High Priority**
   - Unit tests (Jest/Mocha)
   - Integration tests
   - Rate limiting implementation
   - Error message improvements

2. **Medium Priority**
   - Multi-language support
   - Caching layer
   - User feedback tracking
   - Performance optimizations

3. **Nice to Have**
   - Additional channels (WhatsApp, Teams, etc.)
   - Custom category definitions
   - Prompt engineering experiments
   - Analytics/metrics

---

## 📞 Questions?

- **General questions**: Open a GitHub Discussion
- **Bug reports**: GitHub Issues
- **Security issues**: Email robby@chameleon.ai (do not open public issue)
- **Direct contact**: @robbyczgw-cla

---

## 🏆 Recognition

Contributors will be:
- Listed in README.md
- Mentioned in release notes
- Credited in CHANGELOG.md

Thank you for making Smart Follow-ups better! 🙏

---

**Last Updated**: January 20, 2026
