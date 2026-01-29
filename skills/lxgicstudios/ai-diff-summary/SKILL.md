---
name: diff-summary
description: Summarize git diffs in plain English
---

# Diff Summary

Turn messy git diffs into human-readable summaries. Perfect for PR descriptions and code reviews.

## Quick Start

```bash
npx ai-diff-summary
```

## What It Does

- Summarizes staged changes
- Explains what code does, not just what changed
- Groups related changes
- Identifies breaking changes

## Usage Examples

```bash
# Summarize staged changes
npx ai-diff-summary

# Summarize specific commit
npx ai-diff-summary --commit abc123

# Compare branches
npx ai-diff-summary --from main --to feature/auth

# Output as PR description
npx ai-diff-summary --format pr
```

## Output Example

```markdown
## Summary
Added user authentication with JWT tokens

## Changes
- New login/logout endpoints in auth.ts
- JWT middleware for protected routes
- User model with password hashing
- Updated API docs

## Breaking Changes
- /api/users now requires authentication
```

## Requirements

Node.js 18+. OPENAI_API_KEY required. Must be in a git repo.

## License

MIT. Free forever.

---

**Built by LXGIC Studios**

- GitHub: [github.com/lxgicstudios/ai-diff-summary](https://github.com/lxgicstudios/ai-diff-summary)
- Twitter: [@lxgicstudios](https://x.com/lxgicstudios)
