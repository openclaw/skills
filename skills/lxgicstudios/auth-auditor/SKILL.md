---
name: auth-auditor
description: Audit your authentication implementation for security flaws. Use when you need to verify your auth is actually secure.
---

# Auth Auditor

You implemented auth. But did you do it right? This tool audits your authentication code for common security mistakes. Missing CSRF tokens, weak password hashing, insecure session management, JWT misuse. It checks all of it and tells you what needs fixing.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-auth-check src/
```

## What It Does

- Scans your auth implementation for security vulnerabilities
- Checks password hashing algorithms and salt usage
- Detects missing CSRF protection on state changing endpoints
- Finds insecure session configuration and JWT problems
- Reports issues with severity levels and specific fix instructions

## Usage Examples

```bash
# Audit your entire auth system
npx ai-auth-check src/

# Check specific auth files
npx ai-auth-check src/auth/

# Scan middleware and route handlers
npx ai-auth-check src/middleware/ src/routes/
```

## Best Practices

- **Use bcrypt or argon2 for passwords** - MD5 and SHA are not password hashing algorithms, no matter what that tutorial said
- **Set httpOnly and secure flags on cookies** - Missing these is one of the most common auth mistakes
- **Rotate JWT secrets** - Hardcoded secrets that never change are a ticking time bomb
- **Rate limit login attempts** - Without rate limiting, brute force attacks are trivial

## When to Use This

- Before launching any app that handles user accounts
- After implementing a custom auth flow instead of using a library
- When migrating from one auth provider to another
- During security review of authentication related code

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgic.dev

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended.

```bash
npx ai-auth-check --help
```

## How It Works

The tool scans your source code for authentication patterns including login handlers, session management, password storage, and token generation. It analyzes these against security best practices and common vulnerability patterns, then uses AI to generate context-specific fix recommendations.

## License

MIT. Free forever. Use it however you want.