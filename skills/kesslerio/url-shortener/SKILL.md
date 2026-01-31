---
name: shorten
description: Shorten URLs using is.gd (no auth required). Returns a permanent short link.
---

# Shorten

Quickly shorten URLs using the [is.gd](https://is.gd) service. No API key or account required.

## Usage

```bash
shorten "https://example.com/very/long/url"
```

## Examples

**Standard usage:**
```bash
shorten "https://google.com"
# Output: https://is.gd/O5d2Xq
```

## Notes
- Links are permanent.
- No analytics dashboard (simple redirect).
- Rate limits apply (be reasonable).
