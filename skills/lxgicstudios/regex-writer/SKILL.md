---
name: regex-writer
description: Generate regex patterns from plain English descriptions. Use when the user needs to create regular expressions without memorizing syntax.
---

# Regex Writer

Turn plain English into working regex patterns. Describe what you want to match and get a tested pattern back with explanation and examples.

## Usage

```bash
npx ai-regex "your description here"
```

## Examples

```bash
# Match email addresses
npx ai-regex "match valid email addresses"

# Extract phone numbers
npx ai-regex "US phone numbers with optional country code"

# Get JSON output
npx ai-regex --json "URLs starting with https"
```

## Notes
- Free, open source, MIT licensed
- Built by LXGIC Studios
- GitHub: https://github.com/LXGIC-Studios/ai-regex
