---
name: sound-fx
description: Generate short sound effects via ElevenLabs SFX (text-to-sound). Use when you need SFX clips like applause, canned laughter, whooshes, ambience, or short stingers, and optionally convert to WhatsApp-friendly .ogg/opus.
---

# Sound FX (ElevenLabs)

## Overview
Generate a sound effect from a text prompt using the ElevenLabs SFX API. Output is MP3 by default; convert to .ogg/opus for WhatsApp mobile playback.

## Quick start
1) Set API key:
- `ELEVENLABS_API_KEY` (preferred) or `XI_API_KEY`
- Or set `skills."sound-fx".env.ELEVENLABS_API_KEY` in `~/.clawdbot/clawdbot.json`

2) Generate SFX (MP3):
```bash
scripts/generate_sfx.sh --text "short audience applause" --out "/tmp/applause.mp3" --duration 1.2
```

3) Convert to WhatsApp-friendly .ogg/opus (if needed):
```bash
ffmpeg -y -i /tmp/applause.mp3 -c:a libopus -b:a 48k /tmp/applause.ogg
```

## Script: scripts/generate_sfx.sh
**Usage**
```bash
scripts/generate_sfx.sh --text "canned laughter" --out "/tmp/laugh.mp3" --duration 1.5
```

**Notes**
- Uses `POST https://api.elevenlabs.io/v1/sound-generation`
- Supports optional `--duration` (0.5–30s). When omitted, duration is auto.
- Prints `MEDIA: <path>` on success for auto-attach.

## Examples
- Applause: `"short audience applause"`
- Laughter: `"canned audience laughter"`
- Whoosh: `"fast whoosh"`
- Ambience: `"soft rain ambience"`
