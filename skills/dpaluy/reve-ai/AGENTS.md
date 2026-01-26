# reve-ai Skill

Image generation, editing, and remixing via Reve AI API.

## Quick Run

```bash
# Generate
bun scripts/reve.ts create "prompt" -o output.png

# Edit
bun scripts/reve.ts edit "instruction" -i input.png -o output.png

# Remix
bun scripts/reve.ts remix "prompt with <img>0</img>" -i ref1.png -i ref2.png -o output.png
```

## Patterns

### API Request Pattern
See `scripts/reve.ts:22-45` for the standard API request function:
- Bearer token auth
- JSON body
- Error handling with status codes
- Rate limit handling

### Argument Parsing Pattern
See `scripts/reve.ts:72-82` for parseArgs usage:
- Short and long flags
- Defaults
- Help output
- Positional arguments

### Image I/O Pattern
See `scripts/reve.ts:47-59`:
- Base64 encoding for API
- Buffer for file write

## Key Files

| File | Purpose |
|------|---------|
| `SKILL.md` | User documentation, command reference |
| `scripts/reve.ts` | Main CLI script |

## Constraints

- Prompt max: 2560 characters
- Reference images max: 6
- Valid aspect ratios: 16:9, 9:16, 3:2, 2:3, 4:3, 3:4, 1:1

## Environment

Requires one of:
- `REVE_API_KEY`
- `REVE_AI_API_KEY`

## Gotchas

- Remix uses `<img>N</img>` syntax (0-indexed) in prompts
- Edit requires `-i` input, create does not
- Rate limit response includes `retry-after` header
