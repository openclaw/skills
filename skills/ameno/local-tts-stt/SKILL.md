---
name: local-tts-stt
description: >
  Use the local-tts-stt CLI to call the WSL STT/TTS service over Tailscale.
  Use for health checks, STT transcription, TTS synthesis, and fetching the OpenAPI schema.
argument-hint: "<audio-path | text>"
allowed-tools: Bash(local-tts-stt:*), Bash(curl:*), Bash(jq:*), Bash(base64:*), Read, Write
---

# Local TTS/STT (WSL over Tailscale)

Single entrypoint: `local-tts-stt` CLI.

## VPS Quick Start

```bash
cd ~/dev
git clone https://github.com/ameno-/local-tts-stt
cd local-tts-stt

python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .

export STT_TTS_BASE_URL="https://donatello.tail98db32.ts.net"
# Optional if the service is protected:
# export STT_TTS_TOKEN="..."
```

## Core Commands

Health:

```bash
local-tts-stt health --json | jq
```

OpenAPI:

```bash
local-tts-stt openapi --out /tmp/local-tts-stt-openapi.json --json
```

STT (preferred: write JSON, then read):

```bash
local-tts-stt stt /path/to/audio.wav \
  --out /tmp/stt.json \
  --verbose \
  --json
jq -r '.text' /tmp/stt.json
```

TTS (file output):

```bash
local-tts-stt tts \
  --text "Local TTS STT is ready." \
  --out /tmp/tts.wav \
  --json
```

TTS (JSON/base64 response -> wav):

```bash
local-tts-stt tts --text "Health check." --json \
  | jq -r '.audio_base64' \
  | base64 --decode > /tmp/tts.wav
```

## Notes and Pitfalls

- Tailnet HTTPS goes through Tailscale Serve on the WSL node.
- If `health` hangs or times out, check tailnet ACL grants for the caller and port 443.
- If STT returns 500 with faster-whisper, ensure temperature defaults are set server-side.
- If TTS returns 500, the XTTS upstream is likely down; check WSL logs.

## Direct Debug Commands

Bypass the CLI (useful for isolating auth/serve issues):

```bash
curl -sS "$STT_TTS_BASE_URL/health" | jq
```

