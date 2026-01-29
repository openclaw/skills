---
name: moodcast
description: Transform any text into emotionally expressive audio with ambient soundscapes using ElevenLabs v3 audio tags and Sound Effects API
metadata: {"moltbot":{"requires":{"env":["ELEVENLABS_API_KEY"]},"primaryEnv":"ELEVENLABS_API_KEY","homepage":"https://github.com/ashutosh887/moodcast"}}
---

# MoodCast

Transform any text into emotionally expressive audio with ambient soundscapes. MoodCast analyzes your content, adds expressive delivery using ElevenLabs v3 audio tags, and layers matching ambient soundscapes.

## When to Use This Skill

Use MoodCast when the user wants to:
- Hear text read with natural emotional expression
- Create audio versions of articles, stories, or scripts
- Generate expressive voiceovers with ambient atmosphere
- Listen to morning briefings that actually sound engaging
- Transform boring text into captivating audio content

**Trigger phrases:** "read this dramatically", "make this sound good", "create audio for", "moodcast this", "read with emotion", "narrate this"

**Slash command:** `/moodcast`

## Core Capabilities

### 1. Emotion-Aware Text Enhancement
Automatically analyzes text and inserts appropriate v3 audio tags:
- **Emotions:** `[excited]`, `[nervous]`, `[angry]`, `[sorrowful]`, `[calm]`, `[happy]`
- **Delivery:** `[whispers]`, `[shouts]`, `[rushed]`, `[slows down]`
- **Reactions:** `[laughs]`, `[sighs]`, `[gasps]`, `[giggles]`, `[crying]`
- **Pacing:** `[pause]`, `[breathes]`, `[stammers]`, `[hesitates]`

### 2. Ambient Soundscape Generation
Creates matching background audio using Sound Effects API:
- News → subtle office ambiance
- Story → atmospheric soundscape matching mood
- Motivational → uplifting background
- Scary → tense, eerie atmosphere

### 3. Multi-Voice Dialogue
For conversations/scripts, assigns different voices to speakers with appropriate emotional delivery.

## Instructions

### Quick Read (Single Command)
```bash
python3 {baseDir}/scripts/moodcast.py --text "Your text here"
```

### With Ambient Sound
```bash
python3 {baseDir}/scripts/moodcast.py --text "Your text here" --ambient "coffee shop background noise"
```

### Save to File
```bash
python3 {baseDir}/scripts/moodcast.py --text "Your text here" --output story.mp3
```

### Different Moods
```bash
python3 {baseDir}/scripts/moodcast.py --text "Your text" --mood dramatic
python3 {baseDir}/scripts/moodcast.py --text "Your text" --mood calm
python3 {baseDir}/scripts/moodcast.py --text "Your text" --mood excited
python3 {baseDir}/scripts/moodcast.py --text "Your text" --mood scary
```

### List Available Voices
```bash
python3 {baseDir}/scripts/moodcast.py --list-voices
```

### Custom Configuration
```bash
python3 {baseDir}/scripts/moodcast.py --text "Your text" --voice VOICE_ID --model eleven_v3 --output-format mp3_44100_128
```

## Emotion Detection Rules

The skill automatically detects and enhances:

| Text Pattern | Audio Tag Added |
|-------------|-----------------|
| "amazing", "incredible", "wow" | `[excited]` |
| "scared", "afraid", "terrified" | `[nervous]` |
| "angry", "furious", "hate" | `[angry]` |
| "sad", "sorry", "unfortunately" | `[sorrowful]` |
| "secret", "quiet", "between us" | `[whispers]` |
| "!" exclamations | `[excited]` |
| "..." trailing off | `[pause]` |
| "haha", "lol" | `[laughs]` |
| Questions | Natural rising intonation |

## Example Transformations

**Input:**
```
Breaking news! Scientists have discovered something incredible. 
This could change everything we know about the universe...
I can't believe it.
```

**Enhanced Output:**
```
[excited] Breaking news! Scientists have discovered something incredible.
[pause] This could change everything we know about the universe...
[gasps] [whispers] I can't believe it.
```

**Input:**
```
It was a dark night. The old house creaked. 
Something moved in the shadows...
"Who's there?" she whispered.
```

**Enhanced Output:**
```
[slows down] It was a dark night. [pause] The old house creaked.
[nervous] Something moved in the shadows...
[whispers] "Who's there?" she whispered.
```

## Environment Variables

- `ELEVENLABS_API_KEY` (required) - Your ElevenLabs API key
- `MOODCAST_DEFAULT_VOICE` (optional) - Default voice ID (defaults to `CwhRBWXzGAHq8TQ4Fs17`)
- `MOODCAST_MODEL` (optional) - Default model ID (defaults to `eleven_v3`)
- `MOODCAST_OUTPUT_FORMAT` (optional) - Default output format (defaults to `mp3_44100_128`)
- `MOODCAST_AUTO_AMBIENT` (optional) - Set to `"true"` for automatic ambient sounds when using `--mood`

**Configuration Priority:** CLI arguments override environment variables, which override hardcoded defaults.

## Technical Notes

- Uses ElevenLabs Eleven v3 model for audio tag support
- Sound Effects API for ambient generation (up to 30 seconds)
- Free tier: 10,000 credits/month (~10 min audio)
- Max 2,400 characters per chunk (v3 supports 5,000, but we split conservatively for reliability)
- Audio tags must be lowercase: `[whispers]` not `[WHISPERS]`

## Tips for Best Results

1. **Dramatic content** works best - stories, news, scripts
2. **Shorter segments** (under 500 chars) sound more natural
3. **Combine with ambient** for immersive experience
4. **Roger and Rachel** voices are most expressive with v3

## Credits

Built by [ashutosh887](https://github.com/ashutosh887)  
Using ElevenLabs Text-to-Speech v3 + Sound Effects API  
Created for #ClawdEleven Hackathon
