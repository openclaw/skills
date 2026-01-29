---
name: auth-checker
description: Audit authentication flows for security vulnerabilities
---

# Auth Checker

Scan your auth implementation for security holes. Catches the stuff that gets you hacked.

## Quick Start

```bash
npx ai-auth-check ./src/auth/
```

## What It Does

- Audits login/signup flows for vulnerabilities
- Checks session management security
- Identifies weak password policies
- Flags insecure token handling

## Usage Examples

```bash
# Audit auth directory
npx ai-auth-check ./src/auth/

# Scan specific auth file
npx ai-auth-check ./src/lib/auth.ts

# Full project scan
npx ai-auth-check ./src --recursive
```

## What It Catches

- Hardcoded credentials
- Missing rate limiting
- Insecure session storage
- JWT vulnerabilities
- Missing CSRF protection
- Weak password validation

## Requirements

Node.js 18+. OPENAI_API_KEY required.

## License

MIT. Free forever.

---

**Built by LXGIC Studios**

- GitHub: [github.com/lxgicstudios/ai-auth-check](https://github.com/lxgicstudios/ai-auth-check)
- Twitter: [@lxgicstudios](https://x.com/lxgicstudios)
