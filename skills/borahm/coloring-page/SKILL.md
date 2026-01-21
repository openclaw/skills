---
name: coloring-page
description: Turn an uploaded photo into a printable black-and-white coloring page.
metadata:
  clawdbot:
    config:
      requiredEnv:
        - GEMINI_API_KEY
---

# coloring-page

Create a printable black-and-white outline coloring page from a photo.

This skill is designed to be used conversationally:
- You upload an image
- You say: “create a coloring page”
- The assistant runs this skill and sends back the generated PNG

Under the hood, this uses the Nano Banana Pro (Gemini 3 Pro Image) image model.

## Requirements

- `GEMINI_API_KEY` set (recommended in `~/.clawdbot/.env`)
- `uv` available (used by the underlying nano-banana-pro skill)

## How the assistant should use this

When a user message includes:
- an attached image (jpg/png/webp)
- and the user asks for a “coloring page”

Run:
- `bin/coloring-page --in <path-to-uploaded-image> [--out <output.png>] [--resolution 1K|2K|4K]`

Then send the output image back to the user.

## CLI

### Basic

```bash
coloring-page --in photo.jpg
```

### Choose output name

```bash
coloring-page --in photo.jpg --out coloring.png
```

### Resolution

```bash
coloring-page --in photo.jpg --resolution 2K
```

## Notes

- Input must be a raster image (`.jpg`, `.png`, `.webp`).
- Output is a PNG coloring page on a white background.
