# ElevenLabs Voice Personas - Usage Examples v2.0

## Table of Contents

1. [Basic Voice Selection](#basic-voice-selection)
2. [Multi-Language Support](#multi-language-support)
3. [Streaming Mode](#streaming-mode)
4. [Sound Effects](#sound-effects)
5. [Batch Processing](#batch-processing)
6. [Cost Tracking](#cost-tracking)
7. [Voice Design](#voice-design)
8. [Pronunciation Dictionary](#pronunciation-dictionary)
9. [Clawdbot Integration](#clawdbot-integration)
10. [Advanced Patterns](#advanced-patterns)

---

## Basic Voice Selection

### Switching Voices
```bash
# Use Rachel (warm, friendly)
python3 scripts/tts.py --text "Hello there!" --voice rachel

# Use Adam (deep narrator)
python3 scripts/tts.py --text "In the beginning..." --voice adam

# Use a preset
python3 scripts/tts.py --text "Breaking news..." --voice broadcaster
python3 scripts/tts.py --text "Today we learn..." --voice educator
```

### Voice by Use Case
```bash
# Audiobook narration
python3 scripts/tts.py --text "Chapter One" --voice storyteller

# Business presentation
python3 scripts/tts.py --text "Q4 Results" --voice professional

# Meditation
python3 scripts/tts.py --text "Breathe deeply..." --voice calm
```

---

## Multi-Language Support

### Basic Language Synthesis
```bash
# German
python3 scripts/tts.py --text "Guten Tag! Wie geht es Ihnen?" --voice rachel --lang de

# Spanish
python3 scripts/tts.py --text "¡Hola! ¿Cómo estás?" --voice adam --lang es

# French
python3 scripts/tts.py --text "Bonjour, comment allez-vous?" --voice bella --lang fr

# Italian
python3 scripts/tts.py --text "Ciao! Come stai?" --voice george --lang it

# Japanese
python3 scripts/tts.py --text "こんにちは、お元気ですか？" --voice rachel --lang ja

# Chinese
python3 scripts/tts.py --text "你好，你好吗？" --voice adam --lang zh
```

### List All Languages
```bash
python3 scripts/tts.py --languages
```

### Language-Specific Examples

**German Business Presentation:**
```bash
python3 scripts/tts.py \
  --text "Willkommen zur Quartalsübersicht. Heute präsentieren wir unsere Ergebnisse." \
  --voice professional \
  --lang de \
  --output german_presentation.mp3
```

**French Storytelling:**
```bash
python3 scripts/tts.py \
  --text "Il était une fois, dans un royaume lointain, une princesse courageuse..." \
  --voice storyteller \
  --lang fr \
  --output french_story.mp3
```

**Spanish Tutorial:**
```bash
python3 scripts/tts.py \
  --text "En esta lección, aprenderemos los conceptos básicos." \
  --voice educator \
  --lang es \
  --output spanish_tutorial.mp3
```

---

## Streaming Mode

### Basic Streaming
```bash
# Stream audio as it generates (shows progress)
python3 scripts/tts.py --text "This is a longer piece of content..." --voice rachel --stream
```

### Streaming Long Content
```bash
# Good for audiobook chapters
python3 scripts/tts.py \
  --text "$(cat chapter1.txt)" \
  --voice storyteller \
  --stream \
  --output chapter1.mp3
```

### When to Use Streaming

- **Long texts**: More responsive for lengthy content
- **Previewing**: Hear audio before full generation completes
- **Memory efficiency**: Writes chunks instead of loading all in memory

---

## Sound Effects

### Basic Sound Generation
```bash
# Thunder
python3 scripts/sfx.py --prompt "Thunder rumbling in the distance"

# Animal sounds
python3 scripts/sfx.py --prompt "Cat purring contentedly" --output cat.mp3

# Urban sounds
python3 scripts/sfx.py --prompt "Busy city traffic at rush hour" --duration 10
```

### SFX Categories

**Nature:**
```bash
python3 scripts/sfx.py --prompt "Heavy rain on a tin roof" --duration 15
python3 scripts/sfx.py --prompt "Wind howling through bare trees"
python3 scripts/sfx.py --prompt "Ocean waves crashing on rocky shore"
python3 scripts/sfx.py --prompt "Crickets chirping on a summer night" --duration 10
```

**Urban/Mechanical:**
```bash
python3 scripts/sfx.py --prompt "Subway train arriving at platform"
python3 scripts/sfx.py --prompt "Old elevator door opening with a creak"
python3 scripts/sfx.py --prompt "Typing on a mechanical keyboard"
python3 scripts/sfx.py --prompt "Coffee machine brewing espresso"
```

**Actions/Foley:**
```bash
python3 scripts/sfx.py --prompt "Footsteps on wooden floor approaching"
python3 scripts/sfx.py --prompt "Door creaking open slowly"
python3 scripts/sfx.py --prompt "Glass shattering on hard floor"
python3 scripts/sfx.py --prompt "Pages of a book being flipped"
```

**Sci-Fi/Fantasy:**
```bash
python3 scripts/sfx.py --prompt "Spaceship engine powering up" --duration 8
python3 scripts/sfx.py --prompt "Laser gun firing in space"
python3 scripts/sfx.py --prompt "Magic spell casting with sparkles and energy"
python3 scripts/sfx.py --prompt "Portal opening with swirling energy"
```

**Ambient:**
```bash
python3 scripts/sfx.py --prompt "Coffee shop background with quiet chatter" --duration 20
python3 scripts/sfx.py --prompt "Peaceful forest with birds singing" --duration 15
python3 scripts/sfx.py --prompt "Fireplace crackling warmly" --duration 10
```

### Batch Sound Effects

Create `sounds.json`:
```json
[
  {"prompt": "Thunder crack", "duration": 5, "output": "thunder.mp3"},
  {"prompt": "Rain on window", "duration": 10, "output": "rain.mp3"},
  {"prompt": "Wind howling", "duration": 8, "output": "wind.mp3"}
]
```

```bash
python3 scripts/sfx.py --batch sounds.json --output-dir ./sfx
```

---

## Batch Processing

### Text File Input

Create `texts.txt`:
```
Hello and welcome to our podcast.
Today we're discussing artificial intelligence.
Let's dive right in!
```

```bash
python3 scripts/tts.py --batch texts.txt --voice adam --output-dir ./podcast
```

### JSON Input with Per-Item Settings

Create `batch.json`:
```json
[
  {
    "text": "Welcome to the news.",
    "voice": "broadcaster",
    "output": "intro.mp3"
  },
  {
    "text": "First, today's headlines.",
    "voice": "daniel",
    "output": "headlines.mp3"
  },
  {
    "text": "In sports news...",
    "voice": "charlie",
    "output": "sports.mp3"
  }
]
```

```bash
python3 scripts/tts.py --batch batch.json --output-dir ./news
```

### Multi-Language Batch

Create `multilingual.json`:
```json
{
  "texts": [
    {"text": "Hello, welcome!", "voice": "rachel"},
    {"text": "Hallo, willkommen!", "voice": "rachel"},
    {"text": "Bonjour, bienvenue!", "voice": "rachel"},
    {"text": "¡Hola, bienvenido!", "voice": "rachel"}
  ]
}
```

```bash
python3 scripts/tts.py --batch multilingual.json --output-dir ./greetings
```

---

## Cost Tracking

### View Statistics
```bash
python3 scripts/tts.py --stats
```

**Output:**
```
📊 ElevenLabs Usage Statistics

  Total Characters: 45,230
  Total Requests:   127
  Since:            2024-01-15

💰 Estimated Costs:
  Starter    $13.57 ($0.30/1k chars)
  Creator    $10.86 ($0.24/1k chars)
  Pro        $8.14 ($0.18/1k chars)
  Scale      $4.98 ($0.11/1k chars)

📜 Recent Sessions:
  2024-01-20 14:30 |   1250 chars | rachel
  2024-01-20 14:28 |    830 chars | adam
  2024-01-20 13:45 |   2100 chars | george
```

### Reset Statistics
```bash
python3 scripts/tts.py --reset-stats
```

### Cost Planning

Calculate before large jobs:
```bash
# Check file size
wc -c my_book.txt  # e.g., 150000 characters

# Estimate cost: 150,000 / 1000 * $0.30 = $45 (Starter plan)
```

---

## Voice Design

### Create a Custom Voice

```bash
# Female, middle-aged, American accent
python3 scripts/voice-design.py \
  --gender female \
  --age middle_aged \
  --accent american \
  --description "A warm, motherly voice with a gentle, reassuring tone"

# Male, young, British accent with moderate strength
python3 scripts/voice-design.py \
  --gender male \
  --age young \
  --accent british \
  --accent-strength 1.2 \
  --description "Energetic and enthusiastic podcast host"

# Neutral, old, with strong accent
python3 scripts/voice-design.py \
  --gender neutral \
  --age old \
  --accent scandinavian \
  --accent-strength 1.8 \
  --description "Wise storyteller with a mysterious quality"
```

### Preview with Custom Text

```bash
python3 scripts/voice-design.py \
  --gender female \
  --age young \
  --accent american \
  --text "Welcome to my channel! Today we're going to have so much fun!" \
  --output preview.mp3
```

### Save to Library

```bash
python3 scripts/voice-design.py \
  --gender male \
  --age middle_aged \
  --accent british \
  --description "Professional documentary narrator" \
  --save "DocuNarrator"
```

After saving, add to `voices.json` to use with tts.py.

---

## Pronunciation Dictionary

### Basic Configuration

Edit `pronunciations.json`:
```json
{
  "rules": [
    {"word": "GIF", "replacement": "Jif"},
    {"word": "SQL", "replacement": "sequel"},
    {"word": "AWS", "replacement": "A W S"},
    {"word": "Dr.", "replacement": "Doctor"},
    {"word": "St.", "replacement": "Street"}
  ]
}
```

### Technical Terms

```json
{
  "rules": [
    {"word": "kubectl", "replacement": "kube control"},
    {"word": "nginx", "replacement": "engine X"},
    {"word": "OAuth", "replacement": "Oh Auth"},
    {"word": "PostgreSQL", "replacement": "Post gres Q L"},
    {"word": "Redis", "replacement": "Red iss"}
  ]
}
```

### Brand Names

```json
{
  "rules": [
    {"word": "Huawei", "replacement": "Wah way"},
    {"word": "Xiaomi", "replacement": "Show me"},
    {"word": "Porsche", "replacement": "Por sha"},
    {"word": "Hermes", "replacement": "Air mez"}
  ]
}
```

### Usage

```bash
# Pronunciations applied automatically
python3 scripts/tts.py --text "Configure your nginx server" --voice rachel

# Skip pronunciations
python3 scripts/tts.py --text "Configure your nginx server" --voice rachel --no-pronunciations
```

---

## Clawdbot Integration

### Configure Clawdbot TTS

Edit `~/.clawdbot/clawdbot.json`:
```json
{
  "messages": {
    "tts": {
      "auto": "always",
      "provider": "elevenlabs",
      "elevenlabs": {
        "apiKey": "sk-xxxxx",
        "voice": "rachel",
        "model": "eleven_multilingual_v2"
      }
    }
  }
}
```

### Using in Clawdbot Chat

```
User: /tts on
Bot: TTS enabled for this conversation.

User: Tell me a joke
Bot: [Speaks the joke aloud using Rachel voice]

User: /tts off
Bot: TTS disabled.
```

### Direct Script Execution

```
User: Generate speech saying "Hello world" with the Adam voice

Bot: [Runs tts.py script and returns audio file]
```

### Combining with Other Skills

```
User: Summarize this article and read it aloud

Bot: [Summarizes, then uses TTS to speak]
```

---

## Advanced Patterns

### Voice Comparison Test

Generate same text with multiple voices:
```bash
TEXT="Welcome to our product demonstration."

for voice in rachel adam george alice; do
  python3 scripts/tts.py --text "$TEXT" --voice $voice --output "compare_${voice}.mp3"
done
```

### Audiobook Chapter Generator

```bash
#!/bin/bash
# generate_audiobook.sh

VOICE="storyteller"
for chapter in chapters/*.txt; do
  name=$(basename "$chapter" .txt)
  echo "Generating: $name"
  python3 scripts/tts.py \
    --text "$(cat $chapter)" \
    --voice $VOICE \
    --stream \
    --output "audio/${name}.mp3"
done
```

### Multi-Voice Dialog

Create `dialog.json`:
```json
[
  {"text": "Hello, how can I help you today?", "voice": "rachel", "output": "01_host.mp3"},
  {"text": "I'd like to learn about your services.", "voice": "adam", "output": "02_guest.mp3"},
  {"text": "Of course! Let me walk you through everything.", "voice": "rachel", "output": "03_host.mp3"},
  {"text": "That sounds great, please go ahead.", "voice": "adam", "output": "04_guest.mp3"}
]
```

```bash
python3 scripts/tts.py --batch dialog.json --output-dir ./dialog
```

### Localization Pipeline

```bash
#!/bin/bash
# localize.sh - Generate same content in multiple languages

TEXT_EN="Welcome to our application"
python3 scripts/tts.py --text "$TEXT_EN" --voice rachel --output welcome_en.mp3

TEXT_DE="Willkommen in unserer Anwendung"
python3 scripts/tts.py --text "$TEXT_DE" --voice rachel --lang de --output welcome_de.mp3

TEXT_ES="Bienvenido a nuestra aplicación"
python3 scripts/tts.py --text "$TEXT_ES" --voice rachel --lang es --output welcome_es.mp3

TEXT_FR="Bienvenue dans notre application"
python3 scripts/tts.py --text "$TEXT_FR" --voice rachel --lang fr --output welcome_fr.mp3
```

### SFX + TTS Combination

Create a podcast intro with sound effects and voice:
```bash
# Generate sound effects
python3 scripts/sfx.py --prompt "Upbeat podcast intro music jingle" --duration 5 --output intro_music.mp3
python3 scripts/sfx.py --prompt "Swoosh transition sound" --duration 1 --output swoosh.mp3

# Generate voice intro
python3 scripts/tts.py --text "Welcome back to Tech Talk, the podcast where we explore the future of technology!" \
  --voice liam --output intro_voice.mp3

# Combine with ffmpeg (if installed)
# ffmpeg -i intro_music.mp3 -i intro_voice.mp3 -filter_complex "[0:a][1:a]concat=n=2:v=0:a=1" podcast_intro.mp3
```

---

## Voice Selection Guide

### By Content Type

| Content | Primary | Alternative |
|---------|---------|-------------|
| Audiobook Fiction | george (storyteller) | lily (actress) |
| Audiobook Non-Fiction | adam (narrator) | matilda (professional) |
| Business/Corporate | matilda (professional) | eric (trustworthy) |
| Tutorial/Education | alice (educator) | chris (friendly) |
| News/Journalism | daniel (broadcaster) | matilda (professional) |
| Podcast Casual | roger (casual) | liam (social) |
| Meditation/Wellness | brian (comforting) | river (neutral) |
| Gaming/Entertainment | callum (trickster) | jessica (playful) |
| Motivation/Sports | charlie (energetic) | will (optimist) |
| Social Media | liam (social) | jessica (playful) |

### By Accent

| Accent | Voices |
|--------|--------|
| 🇺🇸 American | rachel, adam, bella, brian, callum, jessica, matilda, river, roger, eric, chris, will, liam |
| 🇬🇧 British | george, alice, lily, daniel |
| 🇦🇺 Australian | charlie |

### By Gender

| Gender | Voices |
|--------|--------|
| Female | rachel, bella, alice, jessica, lily, matilda |
| Male | adam, brian, george, callum, charlie, roger, daniel, eric, chris, will, liam |
| Neutral | river |
