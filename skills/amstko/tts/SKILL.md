---
name: tts
description: Convert text to speech using Hume AI (or OpenAI) API. Use when the user asks for an audio message, a voice reply, or to hear something "of vive voix".
---

# Text-to-Speech (TTS)

Convert text to speech and generate audio files (MP3).

## Hume AI (Preferred)

- **Preferred Voice**: `9e1f9e4f-691a-4bb0-b87c-e306a4c838ef`
- **Keys**: Stored in environment as `HUME_API_KEY` and `HUME_SECRET_KEY`.

### Usage

```bash
HUME_API_KEY="..." HUME_SECRET_KEY="..." node {baseDir}/scripts/generate_hume_speech.js --text "Hello Jonathan" --output "output.mp3"
```

## OpenAI (Legacy)

- **Preferred Voice**: `nova`
- **Usage**: `OPENAI_API_KEY="..." node {baseDir}/scripts/generate_speech.js --text "..." --output "..."`

## General Notes

- The scripts print a `MEDIA:` line with the absolute path to the generated file.
- Use the `message` tool to send the resulting file to the user.
