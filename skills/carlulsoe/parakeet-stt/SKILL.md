---
name: parakeet-stt
description: >-
  Local speech-to-text with NVIDIA Parakeet TDT 0.6B v3 (ONNX on CPU).
  30x faster than Whisper, 25 languages, auto-detection, OpenAI-compatible API.
  Use when transcribing audio files, converting speech to text, or processing
  voice recordings locally without cloud APIs.
homepage: https://github.com/groxaxo/parakeet-tdt-0.6b-v3-fastapi-openai
metadata: {"clawdbot":{"emoji":"🦜","env":["PARAKEET_URL"]}}
---

# Parakeet TDT (Speech-to-Text)

Local transcription using NVIDIA Parakeet TDT 0.6B v3 with ONNX Runtime.
Runs on CPU — no GPU required. ~30x faster than realtime.

## Installation

```bash
# Clone the repo
git clone https://github.com/groxaxo/parakeet-tdt-0.6b-v3-fastapi-openai.git
cd parakeet-tdt-0.6b-v3-fastapi-openai

# Run with Docker (recommended)
docker compose up -d parakeet-cpu

# Or run directly with Python
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 5000
```

Default port is `5000`. Set `PARAKEET_URL` to override (e.g., `http://localhost:5092`).

## API Endpoint

OpenAI-compatible API at `$PARAKEET_URL` (default: `http://localhost:5000`).

## Quick Start

```bash
# Transcribe audio file (plain text)
curl -X POST $PARAKEET_URL/v1/audio/transcriptions \
  -F "file=@/path/to/audio.mp3" \
  -F "response_format=text"

# Get timestamps and segments
curl -X POST $PARAKEET_URL/v1/audio/transcriptions \
  -F "file=@/path/to/audio.mp3" \
  -F "response_format=verbose_json"

# Generate subtitles (SRT)
curl -X POST $PARAKEET_URL/v1/audio/transcriptions \
  -F "file=@/path/to/audio.mp3" \
  -F "response_format=srt"
```

## Python / OpenAI SDK

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url=os.getenv("PARAKEET_URL", "http://localhost:5000") + "/v1",
    api_key="not-needed"
)

with open("audio.mp3", "rb") as f:
    transcript = client.audio.transcriptions.create(
        model="parakeet-tdt-0.6b-v3",
        file=f,
        response_format="text"
    )
print(transcript)
```

## Response Formats

| Format | Output |
|--------|--------|
| `text` | Plain text |
| `json` | `{"text": "..."}` |
| `verbose_json` | Segments with timestamps and words |
| `srt` | SRT subtitles |
| `vtt` | WebVTT subtitles |

## Supported Languages (25)

English, Spanish, French, German, Italian, Portuguese, Polish, Russian,
Ukrainian, Dutch, Swedish, Danish, Finnish, Norwegian, Greek, Czech,
Romanian, Hungarian, Bulgarian, Slovak, Croatian, Lithuanian, Latvian,
Estonian, Slovenian

Language is auto-detected — no configuration needed.

## Web Interface

Open `$PARAKEET_URL` in a browser for drag-and-drop transcription UI.

## Docker Management

```bash
# Check status
docker ps --filter "name=parakeet"

# View logs
docker logs -f <container-name>

# Restart
docker compose restart

# Stop
docker compose down
```

## Why Parakeet over Whisper?

- **Speed**: ~30x faster than realtime on CPU
- **Accuracy**: Comparable to Whisper large-v3
- **Privacy**: Runs 100% locally, no cloud calls
- **Compatibility**: Drop-in replacement for OpenAI's transcription API
