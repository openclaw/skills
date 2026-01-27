# ElevenLabs Voice Personas v2.0.0

High-quality voice synthesis with 18 personas, 32 languages, sound effects, and voice design.

## Quick Start

```bash
# Set your API key
export ELEVEN_API_KEY="your-key-here"

# Basic TTS
python3 scripts/tts.py --text "Hello world" --voice rachel

# Multi-language
python3 scripts/tts.py --text "Bonjour!" --voice rachel --lang fr

# Sound effects
python3 scripts/sfx.py --prompt "Thunder rumbling"

# Batch processing
python3 scripts/tts.py --batch texts.txt --voice adam --output-dir ./audio

# Usage stats
python3 scripts/tts.py --stats
```

## Features

| Feature | Command |
|---------|---------|
| TTS | `python3 scripts/tts.py --text "..." --voice NAME` |
| Languages (32) | `--lang de` (German), `--lang fr` (French), etc. |
| Streaming | `--stream` |
| Batch | `--batch file.txt --output-dir ./out` |
| Sound Effects | `python3 scripts/sfx.py --prompt "..."` |
| Voice Design | `python3 scripts/voice-design.py --gender female --age young` |
| Cost Stats | `--stats` |

## Voice Presets

- `narrator` - Documentary style
- `storyteller` - Audiobooks
- `professional` - Corporate
- `educator` - Tutorials
- `calm` - Meditation
- `energetic` - Social media
- `broadcaster` - News

## Documentation

- [SKILL.md](SKILL.md) - Full documentation
- [examples.md](examples.md) - Usage examples
- [voices.json](voices.json) - Voice configurations
- [pronunciations.json](pronunciations.json) - Custom pronunciations

## License

MIT - See ElevenLabs terms for API usage.
