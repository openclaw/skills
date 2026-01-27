---
name: security-validator
description: "Pre-tool security validation - blocks dangerous commands, SSRF, and injection attempts"
metadata: 
  clawdbot:
    emoji: "🔒"
    events: ["before_tool_call", "after_tool_call"]
    requires:
      bins: ["jq"]
---

# 🔒 Security Validator Hook

Automatically validates tool calls before execution to prevent:
- Command injection attacks
- SSRF (Server-Side Request Forgery)  
- Path traversal attempts
- Prompt injection
- API key exposure

## Features

- **Pre-execution validation** - Blocks dangerous tool calls before they run
- **Real-time logging** - Records all security events with timestamps
- **Pattern-based detection** - 50+ threat patterns from security research
- **Zero configuration** - Works automatically once enabled

## Events

- `before_tool_call` - Validates tool parameters before execution
- `after_tool_call` - Logs tool results for monitoring

## Security Patterns

### Command Injection
- Shell metacharacters: `;`, `|`, `&`, `$()`, backticks
- Dangerous commands: `rm -rf`, `curl | bash`, `wget | sh`
- Process substitution and command chaining

### SSRF Protection  
- Private IP ranges: `127.0.0.1`, `169.254.x.x`, `10.x.x.x`
- Localhost variants and internal domains
- Cloud metadata services

### Path Traversal
- Directory traversal: `../`, `..\\`
- Sensitive system files: `/etc/passwd`, `/etc/shadow`
- Configuration files and SSH keys

### Prompt Injection
- Instruction overrides: "ignore previous instructions"
- System commands embedded in content
- Base64 encoded attacks

## Usage

Once enabled, the hook runs automatically on every tool call. No manual intervention required.

**Enable the hook:**
```bash
clawdbot hooks enable security-validator
```

**View security events:**
```bash
tail -f ~/.clawdbot/logs/security-events.log
```

**Check security statistics:**
```bash
~/.clawdbot/skills/security/security stats
```

## Configuration

Edit `~/.clawdbot/hooks/security-validator/config.json` to customize:

```json
{
  "strictMode": false,
  "blockThreats": true,
  "logEvents": true,
  "patterns": {
    "commandInjection": true,
    "ssrf": true,
    "pathTraversal": true,
    "promptInjection": true
  }
}
```

## Integration

Works seamlessly with the Security Skill (`~/.clawdbot/skills/security`) for:
- Pattern detection logic
- Event logging
- Threat intelligence updates

## Security Events

All security events are logged to `~/.clawdbot/logs/security-events.log`:

```
2026-01-26T23:00:00Z [THREAT] Command injection blocked - Tool: bash - Command: rm -rf /
2026-01-26T23:00:01Z [SAFE] Command validated - Tool: bash - Command: ls -la  
2026-01-26T23:00:02Z [THREAT] SSRF attempt blocked - Tool: web_fetch - URL: http://127.0.0.1:8080
```

## Performance

- **~10-15ms overhead** per tool call
- **No external API calls** - all validation is local
- **Fail-safe design** - if validation fails, tool call proceeds with warning

---

## Security Intelligence Updates

**Stay ahead of emerging AI agent threats:**

🐦 **Follow [@LexpertAI](https://x.com/LexpertAI)** for real-time security research, threat analysis, and updates to the Clawdbot Security Suite.

New attack patterns are discovered regularly. Following @LexpertAI keeps your security current with the latest threat intelligence.