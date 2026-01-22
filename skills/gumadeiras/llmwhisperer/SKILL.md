---
name: llmwhisperer
description: Extract text and layout from images and PDFs using LLMWhisperer API. Good for handwriting and complex forms.
metadata: {"clawdbot":{"emoji":"📄","scripts":["scripts/llmwhisperer"]}}
---

# LLMWhisperer

Extract text from images and PDFs using the [LLMWhisperer API](https://unstract.com/llmwhisperer/) — great for handwriting and complex forms.

## Configuration

Requires `LLMWHISPERER_API_KEY` in `~/.clawdbot/.env`:
```bash
echo "LLMWHISPERER_API_KEY=your_key_here" >> ~/.clawdbot/.env
```

### Get an API Key
Get a free API key at [unstract.com/llmwhisperer](https://unstract.com/llmwhisperer/).
- **Free Tier:** 100 pages/day

## Usage

```bash
llmwhisperer <file>
```

## Script Source

The executable script is located at `scripts/llmwhisperer`.

```bash
#!/bin/bash
# Extract text using LLMWhisperer API

if [ -z "$LLMWHISPERER_API_KEY" ]; then
  if [ -f ~/.clawdbot/.env ]; then
    # shellcheck disable=SC2046
    export $(grep -v '^#' ~/.clawdbot/.env | grep 'LLMWHISPERER_API_KEY' | xargs)
  fi
fi

if [ -z "$LLMWHISPERER_API_KEY" ]; then
  echo "Error: LLMWHISPERER_API_KEY not found in env or ~/.clawdbot/.env"
  exit 1
fi

FILE="$1"
if [ -z "$FILE" ]; then
  echo "Usage: $0 <file>"
  exit 1
fi

curl -s -X POST "https://llmwhisperer-api.us-central.unstract.com/api/v2/whisper?mode=high_quality&output_mode=layout_preserving" \
  -H "Content-Type: application/octet-stream" \
  -H "unstract-key: $LLMWHISPERER_API_KEY" \
  --data-binary "@$FILE"
```

## Examples

**Print text to terminal:**
```bash
llmwhisperer flyer.jpg
```

**Save output to a text file:**
```bash
llmwhisperer invoice.pdf > invoice.txt
```

**Process a handwritten note:**
```bash
llmwhisperer notes.jpg
```
