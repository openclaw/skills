---
name: llmwhisperer
description: Extract text and layout from images and PDFs using LLMWhisperer API. Good for handwriting and complex forms.
---

# LLMWhisperer

Use `llmwhisperer <file>` to extract text.

## Configuration
Requires `LLMWHISPERER_API_KEY` in `~/.clawdbot/.env`.

### Get an API Key
Get a free API key at [unstract.com/llmwhisperer](https://unstract.com/llmwhisperer/).
- **Free Tier Limit:** 100 pages/day.

## Usage

```bash
~/.clawdbot/skills/llmwhisperer/llmwhisperer /path/to/image.png
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
