---
name: elevenlabs-voices
description: High-quality voice synthesis with 18 personas, 32 languages, sound effects, batch processing, and voice design using ElevenLabs API.
version: 2.0.1
---

# ElevenLabs Voice Personas v2.0

Comprehensive voice synthesis toolkit using ElevenLabs API.

## ✨ Features

- **18 Voice Personas** - Carefully curated voices for different use cases
- **32 Languages** - Multi-language synthesis with the multilingual v2 model
- **Streaming Mode** - Real-time audio output as it generates
- **Sound Effects (SFX)** - AI-generated sound effects from text prompts
- **Batch Processing** - Process multiple texts in one go
- **Cost Tracking** - Monitor character usage and estimated costs
- **Voice Design** - Create custom voices from descriptions
- **Pronunciation Dictionary** - Custom word pronunciation rules
- **Clawdbot Integration** - Works with Clawdbot's built-in TTS

---

## 🎙️ Available Voices

| Voice | Accent | Gender | Persona | Best For |
|-------|--------|--------|---------|----------|
| rachel | 🇺🇸 US | female | warm | Conversations, tutorials |
| adam | 🇺🇸 US | male | narrator | Documentaries, audiobooks |
| bella | 🇺🇸 US | female | professional | Business, presentations |
| brian | 🇺🇸 US | male | comforting | Meditation, calm content |
| george | 🇬🇧 UK | male | storyteller | Audiobooks, storytelling |
| alice | 🇬🇧 UK | female | educator | Tutorials, explanations |
| callum | 🇺🇸 US | male | trickster | Playful, gaming |
| charlie | 🇦🇺 AU | male | energetic | Sports, motivation |
| jessica | 🇺🇸 US | female | playful | Social media, casual |
| lily | 🇬🇧 UK | female | actress | Drama, elegant content |
| matilda | 🇺🇸 US | female | professional | Corporate, news |
| river | 🇺🇸 US | neutral | neutral | Inclusive, informative |
| roger | 🇺🇸 US | male | casual | Podcasts, relaxed |
| daniel | 🇬🇧 UK | male | broadcaster | News, announcements |
| eric | 🇺🇸 US | male | trustworthy | Business, corporate |
| chris | 🇺🇸 US | male | friendly | Tutorials, approachable |
| will | 🇺🇸 US | male | optimist | Motivation, uplifting |
| liam | 🇺🇸 US | male | social | YouTube, social media |

## 🎯 Quick Presets

- `default` → rachel (warm, friendly)
- `narrator` → adam (documentaries)
- `professional` → matilda (corporate)
- `storyteller` → george (audiobooks)
- `educator` → alice (tutorials)
- `calm` → brian (meditation)
- `energetic` → liam (social media)
- `trustworthy` → eric (business)
- `neutral` → river (inclusive)
- `british` → george
- `australian` → charlie
- `broadcaster` → daniel (news)

---

## 🌍 Supported Languages (32)

The multilingual v2 model supports these languages:

| Code | Language | Code | Language |
|------|----------|------|----------|
| en | English | pl | Polish |
| de | German | nl | Dutch |
| es | Spanish | sv | Swedish |
| fr | French | da | Danish |
| it | Italian | fi | Finnish |
| pt | Portuguese | no | Norwegian |
| ru | Russian | tr | Turkish |
| uk | Ukrainian | cs | Czech |
| ja | Japanese | sk | Slovak |
| ko | Korean | hu | Hungarian |
| zh | Chinese | ro | Romanian |
| ar | Arabic | bg | Bulgarian |
| hi | Hindi | hr | Croatian |
| ta | Tamil | el | Greek |
| id | Indonesian | ms | Malay |
| vi | Vietnamese | th | Thai |

```bash
# Synthesize in German
python3 tts.py --text "Guten Tag!" --voice rachel --lang de

# Synthesize in French
python3 tts.py --text "Bonjour le monde!" --voice adam --lang fr

# List all languages
python3 tts.py --languages
```

---

## 💻 CLI Usage

### Basic Text-to-Speech

```bash
# List all voices
python3 scripts/tts.py --list

# Generate speech
python3 scripts/tts.py --text "Hello world" --voice rachel --output hello.mp3

# Use a preset
python3 scripts/tts.py --text "Breaking news..." --voice broadcaster --output news.mp3

# Multi-language
python3 scripts/tts.py --text "Bonjour!" --voice rachel --lang fr --output french.mp3
```

### Streaming Mode

Generate audio with real-time streaming (good for long texts):

```bash
# Stream audio as it generates
python3 scripts/tts.py --text "This is a long story..." --voice adam --stream

# Streaming with custom output
python3 scripts/tts.py --text "Chapter one..." --voice george --stream --output chapter1.mp3
```

### Batch Processing

Process multiple texts from a file:

```bash
# From newline-separated text file
python3 scripts/tts.py --batch texts.txt --voice rachel --output-dir ./audio

# From JSON file
python3 scripts/tts.py --batch batch.json --output-dir ./output
```

**JSON batch format:**
```json
[
  {"text": "First line", "voice": "rachel", "output": "line1.mp3"},
  {"text": "Second line", "voice": "adam", "output": "line2.mp3"},
  {"text": "Third line"}
]
```

**Simple text format (one per line):**
```
Hello, this is the first sentence.
This is the second sentence.
And this is the third.
```

### Usage Statistics

```bash
# Show usage stats and cost estimates
python3 scripts/tts.py --stats

# Reset statistics
python3 scripts/tts.py --reset-stats
```

---

## 🎵 Sound Effects (SFX)

Generate AI-powered sound effects from text descriptions:

```bash
# Generate a sound effect
python3 scripts/sfx.py --prompt "Thunder rumbling in the distance"

# With specific duration (0.5-22 seconds)
python3 scripts/sfx.py --prompt "Cat meowing" --duration 3 --output cat.mp3

# Adjust prompt influence (0.0-1.0)
python3 scripts/sfx.py --prompt "Footsteps on gravel" --influence 0.5

# Batch SFX generation
python3 scripts/sfx.py --batch sounds.json --output-dir ./sfx

# Show prompt examples
python3 scripts/sfx.py --examples
```

**Example prompts:**
- "Thunder rumbling in the distance"
- "Cat purring contentedly"
- "Typing on a mechanical keyboard"
- "Spaceship engine humming"
- "Coffee shop background chatter"

---

## 🎨 Voice Design

Create custom voices from text descriptions:

```bash
# Basic voice design
python3 scripts/voice-design.py --gender female --age middle_aged --accent american \
  --description "A warm, motherly voice"

# With custom preview text
python3 scripts/voice-design.py --gender male --age young --accent british \
  --text "Welcome to the adventure!" --output preview.mp3

# Save to your ElevenLabs library
python3 scripts/voice-design.py --gender female --age young --accent american \
  --description "Energetic podcast host" --save "MyHost"

# List all design options
python3 scripts/voice-design.py --options
```

**Voice Design Options:**

| Option | Values |
|--------|--------|
| Gender | male, female, neutral |
| Age | young, middle_aged, old |
| Accent | american, british, african, australian, indian, latin, middle_eastern, scandinavian, eastern_european |
| Accent Strength | 0.3-2.0 (subtle to strong) |

---

## 📖 Pronunciation Dictionary

Customize how words are pronounced:

Edit `pronunciations.json`:
```json
{
  "rules": [
    {
      "word": "Clawdbot",
      "replacement": "Clawd bot",
      "comment": "Pronounce as two words"
    },
    {
      "word": "API",
      "replacement": "A P I",
      "comment": "Spell out acronym"
    }
  ]
}
```

Usage:
```bash
# Pronunciations are applied automatically
python3 scripts/tts.py --text "The Clawdbot API is great" --voice rachel

# Disable pronunciations
python3 scripts/tts.py --text "The API is great" --voice rachel --no-pronunciations
```

---

## 💰 Cost Tracking

The skill tracks your character usage and estimates costs:

```bash
python3 scripts/tts.py --stats
```

**Output:**
```
📊 ElevenLabs Usage Statistics

  Total Characters: 15,230
  Total Requests:   42
  Since:            2024-01-15

💰 Estimated Costs:
  Starter    $4.57 ($0.30/1k chars)
  Creator    $3.66 ($0.24/1k chars)
  Pro        $2.74 ($0.18/1k chars)
  Scale      $1.68 ($0.11/1k chars)
```

---

## 🤖 Clawdbot TTS Integration

### Using with Clawdbot's Built-in TTS

Clawdbot has built-in TTS support that can use ElevenLabs. Configure in `~/.clawdbot/clawdbot.json`:

```json
{
  "messages": {
    "tts": {
      "auto": "always",
      "provider": "elevenlabs",
      "elevenlabs": {
        "apiKey": "your-api-key-here",
        "voice": "rachel",
        "model": "eleven_multilingual_v2"
      }
    }
  }
}
```

### Triggering TTS in Chat

In Clawdbot conversations:
- Use `/tts on` to enable automatic TTS
- Use the `tts` tool directly for one-off speech
- Request "read this aloud" or "speak this"

### Using Skill Scripts from Clawdbot

```bash
# Clawdbot can run these scripts directly
exec python3 /path/to/skills/elevenlabs-voices/scripts/tts.py --text "Hello" --voice rachel
```

---

## ⚙️ Configuration

The scripts look for API key in this order:

1. `ELEVEN_API_KEY` or `ELEVENLABS_API_KEY` environment variable
2. Clawdbot config (`~/.clawdbot/clawdbot.json` → tts.elevenlabs.apiKey)
3. Skill-local `.env` file

**Create .env file:**
```bash
echo 'ELEVEN_API_KEY=your-key-here' > .env
```

---

## 🎛️ Voice Settings

Each voice has tuned settings for optimal output:

| Setting | Range | Description |
|---------|-------|-------------|
| stability | 0.0-1.0 | Higher = consistent, lower = expressive |
| similarity_boost | 0.0-1.0 | How closely to match original voice |
| style | 0.0-1.0 | Exaggeration of speaking style |

---

## 📝 Triggers

- "use {voice_name} voice"
- "speak as {persona}"
- "list voices"
- "voice settings"
- "generate sound effect"
- "design a voice"

---

## 📁 Files

```
elevenlabs-voices/
├── SKILL.md              # This documentation
├── README.md             # Quick start guide
├── voices.json           # Voice definitions & settings
├── pronunciations.json   # Custom pronunciation rules
├── examples.md           # Detailed usage examples
├── scripts/
│   ├── tts.py            # Main TTS script
│   ├── sfx.py            # Sound effects generator
│   └── voice-design.py   # Voice design tool
└── references/
    └── voice-guide.md    # Voice selection guide
```

---

## 🔗 Links

- [ElevenLabs](https://elevenlabs.io)
- [API Documentation](https://docs.elevenlabs.io)
- [Voice Library](https://elevenlabs.io/voice-library)
- [Sound Effects API](https://elevenlabs.io/docs/api-reference/sound-generation)
- [Voice Design API](https://elevenlabs.io/docs/api-reference/voice-generation)

---

## 📋 Changelog

### v2.0.0
- Added 32 language support with `--lang` parameter
- Added streaming mode with `--stream` flag
- Added sound effects generation (`sfx.py`)
- Added batch processing with `--batch` flag
- Added cost tracking with `--stats` flag
- Added voice design tool (`voice-design.py`)
- Added pronunciation dictionary support
- Added Clawdbot TTS integration documentation
- Improved error handling and progress output
