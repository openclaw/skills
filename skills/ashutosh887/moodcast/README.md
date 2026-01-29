# MoodCast

**Transform any text into emotionally expressive audio with ambient soundscapes.**

MoodCast is a [Moltbot](https://molt.bot) skill that uses ElevenLabs' most advanced features to create compelling audio content. It analyzes your text, adds emotional expression using Eleven v3 audio tags, and can layer ambient soundscapes for immersive experiences.

[![Demo Video](https://img.shields.io/badge/Demo-Watch%20Video-red?style=for-the-badge&logo=youtube)](YOUR_VIDEO_LINK_HERE)
[![Moltbot Skill](https://img.shields.io/badge/Moltbot-Skill-blue?style=for-the-badge)](https://molt.bot)
[![ElevenLabs](https://img.shields.io/badge/Powered%20by-ElevenLabs-purple?style=for-the-badge)](https://elevenlabs.io)

---

## Features

| Feature | Description |
|---------|-------------|
| **Emotion Detection** | Automatically analyzes text and inserts v3 audio tags (`[excited]`, `[whispers]`, `[laughs]`, etc.) |
| **Ambient Soundscapes** | Generates matching background sounds using Sound Effects API |
| **Multiple Moods** | Pre-configured moods: dramatic, calm, excited, scary, news, story |
| **Smart Text Processing** | Auto-splits long text, handles multiple speakers |

## Demo

**Input:**
```
Breaking news! Scientists have discovered something incredible. 
This could change everything we know about the universe...
I can't believe it.
```

**MoodCast Output:**
```
[excited] Breaking news! Scientists have discovered something incredible.
[pause] This could change everything we know about the universe...
[gasps] [whispers] I can't believe it.
```

*The AI voice delivers this with genuine excitement, dramatic pauses, and a whispered ending.*

---

## Quick Start

### 1. Install the Skill

```bash
# Option 1: Clone to your Moltbot skills directory
git clone https://github.com/ashutosh887/moodcast ~/.clawdbot/skills/moodcast

# Option 2: Install via MoltHub (recommended)
npx molthub@latest install moodcast

# Option 3: Install to workspace (for per-agent skills)
# After installing, move to workspace or use git clone method
```

### 2. Set Your API Key

```bash
export ELEVENLABS_API_KEY="your-api-key-here"
```

Or add to `~/.clawdbot/moltbot.json`:
```json
{
  "skills": {
    "entries": {
      "moodcast": {
        "enabled": true,
        "apiKey": "your-api-key-here",
        "env": {
          "ELEVENLABS_API_KEY": "your-api-key-here"
        }
      }
    }
  }
}
```

Note: `apiKey` automatically maps to `ELEVENLABS_API_KEY` when the skill declares `primaryEnv`.

### 3. Use It!

**Via Moltbot (WhatsApp/Telegram/Discord/iMessage):**
```
Hey Molty, moodcast this: "It was a dark and stormy night..."
```

Or use the slash command:
```
/moodcast "It was a dark and stormy night..."
```

**Via Command Line:**
```bash
python3 ~/.clawdbot/skills/moodcast/scripts/moodcast.py --text "Hello world!"
```

---

## Usage Examples

### Basic Usage
```bash
python moodcast.py --text "This is amazing news!"
```

### With Mood Preset
```bash
python moodcast.py --text "The door creaked open slowly..." --mood scary
```

### With Ambient Sound
```bash
python moodcast.py --text "Welcome to my café" --ambient "coffee shop busy morning"
```

### Save to File
```bash
python moodcast.py --text "Your story here" --output narration.mp3
```

### Show Enhanced Text
```bash
python moodcast.py --text "Wow this is great!" --show-enhanced
# Output: [excited] Wow this is great!
```

### Custom Configuration
```bash
# Custom voice, model, and output format
python moodcast.py --text "Hello" --voice VOICE_ID --model eleven_v3 --output-format mp3_44100_128

# Override mood's default voice
python moodcast.py --text "Dramatic scene" --mood dramatic --voice CUSTOM_VOICE_ID

# Skip emotion enhancement
python moodcast.py --text "Plain text" --no-enhance
```

---

## Supported Audio Tags (Eleven v3)

MoodCast automatically detects emotions and inserts these tags:

### Emotions
| Tag | Triggers |
|-----|----------|
| `[excited]` | amazing, incredible, wow, !!! |
| `[happy]` | happy, delighted, thrilled |
| `[nervous]` | scared, afraid, terrified |
| `[angry]` | angry, furious, hate |
| `[sorrowful]` | sad, sorry, tragic |
| `[calm]` | peaceful, gentle, quiet |

### Delivery
| Tag | Effect |
|-----|--------|
| `[whispers]` | Soft, secretive tone |
| `[shouts]` | Loud, emphatic delivery |
| `[slows down]` | Deliberate pacing |
| `[rushed]` | Fast, urgent speech |

### Reactions
| Tag | Effect |
|-----|--------|
| `[laughs]` | Natural laughter |
| `[sighs]` | Weary exhale |
| `[gasps]` | Surprise intake |
| `[giggles]` | Light laughter |
| `[pause]` | Dramatic beat |

---

## Mood Presets

| Mood | Voice | Style | Best For |
|------|-------|-------|----------|
| `dramatic` | Roger | Theatrical, expressive | Stories, scripts |
| `calm` | Lily | Soothing, peaceful | Meditation, ASMR |
| `excited` | Liam | Energetic, upbeat | News, announcements |
| `scary` | Roger (deep) | Tense, ominous | Horror, thrillers |
| `news` | Lily | Professional, clear | Briefings, reports |
| `story` | Rachel | Warm, engaging | Audiobooks, tales |

---

## Configuration

### Command Line Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `--text` | `-t` | Text to convert to speech (required) |
| `--mood` | `-m` | Mood preset: dramatic, calm, excited, scary, news, story |
| `--voice` | `-v` | Voice ID (overrides mood's default voice) |
| `--model` | | Model ID (default: `eleven_v3`) |
| `--output-format` | | Output format (default: `mp3_44100_128`) |
| `--ambient` | `-a` | Generate ambient sound effect (prompt) |
| `--ambient-duration` | | Ambient duration in seconds (max 30, default: 10) |
| `--output` | `-o` | Save audio to file instead of playing |
| `--no-enhance` | | Skip automatic emotion enhancement |
| `--show-enhanced` | | Print enhanced text before generating |
| `--list-voices` | | List available voices |

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `ELEVENLABS_API_KEY` | Yes | Your ElevenLabs API key | - |
| `MOODCAST_DEFAULT_VOICE` | No | Default voice ID (overridden by `--voice` or `--mood`) | `CwhRBWXzGAHq8TQ4Fs17` |
| `MOODCAST_MODEL` | No | Default model ID (overridden by `--model`) | `eleven_v3` |
| `MOODCAST_OUTPUT_FORMAT` | No | Default output format (overridden by `--output-format`) | `mp3_44100_128` |
| `MOODCAST_AUTO_AMBIENT` | No | Auto-generate ambient sounds when using `--mood` | - |

**Priority order:** CLI arguments > Environment variables > Hardcoded defaults

### Moltbot Config (`~/.clawdbot/moltbot.json`)

```json
{
  "skills": {
    "entries": {
      "moodcast": {
        "enabled": true,
        "apiKey": "xi-xxxxxxxxxxxx",
        "env": {
          "ELEVENLABS_API_KEY": "xi-xxxxxxxxxxxx",
          "MOODCAST_AUTO_AMBIENT": "true"
        }
      }
    }
  }
}
```

Note: `apiKey` is a convenience field that maps to `ELEVENLABS_API_KEY` when `primaryEnv` is set in the skill metadata.

---

## ElevenLabs APIs Used

This skill demonstrates **deep integration** with multiple ElevenLabs APIs:

### 1. Text-to-Speech (Eleven v3)
- Model: `eleven_v3` for audio tag support
- Format: `mp3_44100_128`
- Features: Full audio tag expression system

### 2. Sound Effects API
- Generates ambient soundscapes from text prompts
- Up to 30 seconds per generation
- Seamless looping support

### 3. Voices API
- Lists available voices
- Supports custom voice selection
- Mood-based voice matching

---

## Project Structure

```
moodcast/
├── SKILL.md           # Moltbot skill definition (AgentSkills format)
├── README.md          # Project documentation
├── requirements.txt   # Python dependencies
├── .gitignore         # Git ignore rules
├── scripts/
│   └── moodcast.py    # Main Python script
└── examples/
    ├── news.txt       # News article example
    ├── scary.txt      # Horror story example
    ├── dramatic.txt   # Dramatic narrative example
    ├── calm.txt       # Peaceful scene example
    └── story.txt      # Adventure story example
```

## Skill Installation Locations

Moltbot loads skills from three locations (in precedence order):
1. **Workspace skills**: `<workspace>/skills/moodcast` (per-agent, highest precedence)
2. **Managed skills**: `~/.clawdbot/skills/moodcast` (shared across agents)
3. **Bundled skills**: Shipped with Moltbot install (lowest precedence)

Use `npx molthub@latest install moodcast` to install to the managed directory, or clone directly to your workspace for per-agent installation.

---

## Technical Details

### API Integration

| Criteria | Implementation |
|----------|----------------|
| **ElevenLabs API usage** | Uses Eleven v3 audio tags (deepest TTS feature), Sound Effects API, Voices API |
| **Practical use cases** | Content creators, writers, podcasters, anyone who wants expressive audio |
| **Demo approach** | Single clear hook: "Text that feels emotion" with live demonstration |

---

## License

MIT License - feel free to use, modify, and share!

---

## Acknowledgments

- [ElevenLabs](https://elevenlabs.io) for the incredible audio AI APIs
- [Moltbot](https://molt.bot) / [Peter Steinberger](https://twitter.com/steipete) for the amazing AI assistant platform

Built for the #ClawdEleven Hackathon (ElevenLabs × Moltbot)
