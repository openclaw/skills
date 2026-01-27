# Contributing to Clawdbot Security Suite

Thank you for your interest in contributing! Security is a community effort, and we welcome contributions from security researchers, developers, and AI safety advocates.

## Ways to Contribute

### 🔍 Report New Threats
Found a new attack pattern that evades detection?

1. **Check existing patterns** in `skills/security/patterns.json`
2. **Create an issue** with:
   - Attack description
   - Example payload
   - Expected vs actual behavior
   - Impact assessment

### 🛡️ Submit Detection Patterns
Add new security patterns:

1. **Fork the repository**
2. **Add pattern** to `skills/security/patterns.json`
3. **Test the pattern** with both malicious and benign inputs
4. **Update documentation** if needed
5. **Submit PR** with clear description

### 📚 Improve Documentation
Help make security more accessible:

- Fix typos or unclear instructions
- Add usage examples
- Translate documentation
- Create video tutorials or blog posts

### 🧪 Testing & QA
- Test on different platforms
- Performance benchmarking
- Edge case discovery
- Integration testing with various Clawdbot setups

### 💡 Feature Requests
- Additional threat detection categories
- New integration methods
- Performance improvements
- Monitoring enhancements

## Development Setup

### Prerequisites
```bash
# Required tools
git, bash, jq, node/npm

# Clawdbot installation
# See: https://docs.clawd.bot/install
```

### Local Setup
```bash
# Clone repository
git clone https://github.com/gtrusler/clawdbot-security-suite.git
cd clawdbot-security-suite

# Install development dependencies
npm install

# Install security skill locally
cp -r skills/security ~/.clawdbot/skills/

# Test installation
~/.clawdbot/skills/security/security help
```

## Adding Security Patterns

### Pattern Categories
Security patterns are organized by threat type:

```json
{
  "command_injection": ["pattern1", "pattern2"],
  "ssrf": ["pattern1", "pattern2"],
  "path_traversal": ["pattern1", "pattern2"], 
  "prompt_injection": ["pattern1", "pattern2"],
  "api_keys": ["pattern1", "pattern2"],
  "sensitive_files": ["pattern1", "pattern2"],
  "data_exfiltration": ["pattern1", "pattern2"]
}
```

### Pattern Guidelines

**Good patterns:**
- ✅ Specific enough to avoid false positives
- ✅ General enough to catch variations
- ✅ Based on real attack examples
- ✅ Tested with both malicious and benign inputs

**Avoid:**
- ❌ Overly broad patterns (high false positive rate)
- ❌ Patterns that break legitimate use cases
- ❌ Untested regex (can cause performance issues)

### Testing Patterns

Test new patterns thoroughly:

```bash
# Test malicious input (should detect)
~/.clawdbot/skills/security/security validate-command "your_malicious_example"

# Test benign input (should allow)  
~/.clawdbot/skills/security/security validate-command "your_benign_example"

# Performance test
time ~/.clawdbot/skills/security/security validate-command "test_command"
```

## Code Style

### Shell Scripts
- Use `set -euo pipefail`
- Quote variables: `"$variable"`
- Use descriptive function names
- Add comments for complex logic

### JSON Files
- Proper indentation (2 spaces)
- Validate JSON syntax: `jq . file.json`
- Sort arrays alphabetically when possible

### Documentation
- Use clear, concise language
- Include examples
- Follow existing format/style
- Test all example commands

## Pull Request Process

1. **Fork & clone** the repository
2. **Create feature branch**: `git checkout -b feature/add-php-injection-patterns`
3. **Make changes** following contribution guidelines
4. **Test thoroughly** - see testing section above
5. **Update documentation** if needed
6. **Commit with clear message**:
   ```
   Add PHP injection detection patterns
   
   - Add 5 new patterns for PHP code injection
   - Cover eval(), system(), exec() variations
   - Include base64 and hex encoding bypasses
   - Tested with WordPress and Laravel examples
   ```
7. **Push branch** and create pull request
8. **Address review feedback**

### PR Requirements
- [ ] All tests pass
- [ ] No false positives on common legitimate commands
- [ ] Documentation updated
- [ ] Performance impact minimal (<5ms additional overhead)
- [ ] Follows existing code style

## Security Guidelines

### Responsible Development
- **Test in isolated environment** - Don't test on production systems
- **Validate all inputs** - Security tools are high-value targets
- **Follow least privilege** - Don't require unnecessary permissions
- **Document security implications** - Help users understand trade-offs

### Security Review
All security-related changes undergo additional review:

1. **Pattern effectiveness** - Does it catch the intended threats?
2. **Bypass potential** - Are there obvious evasion techniques?  
3. **Performance impact** - Does it slow down validation significantly?
4. **False positive rate** - Will it block legitimate operations?

## Community

### Getting Help
- **GitHub Discussions** - General questions and ideas
- **GitHub Issues** - Bug reports and feature requests
- **[@LexpertAI](https://x.com/LexpertAI)** - Security updates and community discussion

### Code of Conduct
Be respectful and constructive:
- Focus on the security merit of contributions
- Assume good intentions
- Help newcomers learn
- Keep discussions technical and factual

### Recognition
Contributors are recognized in:
- Release notes
- `CONTRIBUTORS.md` file
- Security advisories (for vulnerability reports)
- Social media acknowledgments

## Release Process

### Version Numbering
- **Major** (1.0.0): Breaking changes, major new features
- **Minor** (1.1.0): New patterns, features, backwards-compatible
- **Patch** (1.0.1): Bug fixes, pattern updates

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated  
- [ ] Version bumped in package.json
- [ ] Git tag created
- [ ] GitHub release published
- [ ] ClawdHub package updated
- [ ] Community notification via [@LexpertAI](https://x.com/LexpertAI)

## Questions?

**Technical questions**: [GitHub Discussions](https://github.com/gtrusler/clawdbot-security-suite/discussions)  
**Security concerns**: [gt@lexpertai.com](mailto:gt@lexpertai.com)  
**General updates**: [@LexpertAI](https://x.com/LexpertAI)  

Thank you for helping secure the AI agent ecosystem! 🔒