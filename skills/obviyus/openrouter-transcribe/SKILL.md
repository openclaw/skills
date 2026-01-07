---
name: openrouter-transcribe
description: Transcribe audio files via OpenRouter using audio-capable models (Gemini, GPT-4o-audio, etc).
homepage: https://openrouter.ai/docs
metadata: {"clawdbot":{"emoji":"🎙️","requires":{"bins":["curl","ffmpeg","base64","jq"],"env":["OPENROUTER_API_KEY"]},"primaryEnv":"OPENROUTER_API_KEY"}}
---

# OpenRouter Audio Transcription

Transcribe audio files using OpenRouter's chat completions API with `input_audio` content type. Works with any audio-capable model.

## Quick start

```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a
```

Output goes to stdout.

## Useful flags

```bash
# Custom model (default: google/gemini-2.5-flash)
{baseDir}/scripts/transcribe.sh audio.ogg --model openai/gpt-4o-audio-preview

# Custom instructions
{baseDir}/scripts/transcribe.sh audio.m4a --prompt "Transcribe with speaker labels"

# Save to file
{baseDir}/scripts/transcribe.sh audio.m4a --out /tmp/transcript.txt

# Custom caller identifier (for OpenRouter dashboard)
{baseDir}/scripts/transcribe.sh audio.m4a --title "MyApp"
```

## How it works

1. Converts audio to WAV (mono, 16kHz) using ffmpeg
2. Base64 encodes the audio
3. Sends to OpenRouter chat completions with `input_audio` content
4. Extracts transcript from response

## API key

Set `OPENROUTER_API_KEY` env var, or configure in `~/.clawdbot/clawdbot.json`:

```json5
{
  skills: {
    "openrouter-transcribe": {
      apiKey: "YOUR_OPENROUTER_KEY"
    }
  }
}
```

## Headers

The script sends identification headers to OpenRouter:
- `X-Title`: Caller name (default: "Peanut/Clawdbot")
- `HTTP-Referer`: Reference URL (default: "https://clawdbot.com")

These show up in your OpenRouter dashboard for tracking.

## Troubleshooting

**ffmpeg format errors**: The script uses a temp directory (not `mktemp -t file.wav`) because macOS's mktemp adds random suffixes after the extension, breaking format detection.

**Argument list too long**: Large audio files produce huge base64 strings that exceed shell argument limits. The script writes to temp files (`--rawfile` for jq, `@file` for curl) instead of passing data as arguments.

**Empty response**: If you get "Empty response from API", the script will dump the raw response for debugging. Common causes:
- Invalid API key
- Model doesn't support audio input
- Audio file too large or corrupted
