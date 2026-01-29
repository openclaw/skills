# transcribee 🐝

**Open source macOS transcriber for YouTube, Instagram Reels, TikTok, and local media — evolves a self-organizing knowledge base.**

```bash
transcribee "https://youtube.com/watch?v=..."
transcribee "https://instagram.com/reel/..."
transcribee "https://vt.tiktok.com/..."
transcribee ~/Downloads/podcast.mp3
```

Over time, your `~/Documents/transcripts/` folder naturally evolves into a personal library:

```
transcripts/
├── AI-Research/
│   ├── ilya-sutskever-agi-2024/
│   └── anthropic-constitutional-ai/
├── Startups/
│   ├── ycombinator-how-to-get-users/
│   └── pmarca-founder-mode/
└── Health/
    └── huberman-sleep-optimization/
```

Each transcript is speaker-labeled and ready to paste into ChatGPT, Claude, or any LLM.

## Why 🍯

I consume a lot of video content — YouTube, Instagram, TikTok, podcasts, interviews. I wanted to:
- Ask questions about videos in LLMs
- Have all that knowledge searchable and organized
- Not do any manual work to maintain it

transcribee does exactly that. Transcribe once, knowledge stays forever.

## Features 🪻

- **Transcribes** YouTube, Instagram Reels, TikTok, and local audio/video files
- **Speaker diarization** — identifies different speakers
- **Auto-categorizes** transcripts using Claude based on content
- **Builds a knowledge library** that organizes itself over time

## Use with Clawdbot 🤖

transcribee is available as a [Clawdbot](https://github.com/clawdbot/clawdbot) skill. Just ask your agent to transcribe any YouTube video:

> "Transcribe this video: https://youtube.com/watch?v=..."

### Install the skill

```bash
# Install from ClawdHub (recommended)
clawdhub install transcribee

# Or clone manually
git clone https://github.com/itsfabioroma/transcribee.git ~/.clawdbot/skills/transcribee
```

Make sure you have the dependencies installed (`brew install yt-dlp ffmpeg`) and API keys configured.

## Quick Start 🪺

```bash
# Install dependencies (macOS)
brew install yt-dlp ffmpeg
pnpm install

# Configure API keys
cp .env.example .env
# Add your ElevenLabs + Anthropic API keys to .env

# Transcribe anything
transcribee "https://youtube.com/watch?v=..."
transcribee "https://instagram.com/reel/..."
transcribee "https://vt.tiktok.com/..."
transcribee ~/Downloads/podcast.mp3
transcribee ~/Videos/interview.mp4
```

### Shell alias (recommended)

Add to `~/.zshrc`:

```bash
alias transcribee="noglob /path/to/transcribee/transcribe.sh"
```

## Output 🍯

Each transcript saves to `~/Documents/transcripts/{category}/{title}/`:

| File | What it's for |
|------|---------------|
| `transcript.txt` | Speaker-labeled transcript — **paste this into your LLM** |
| `metadata.json` | Video info, language, auto-detected theme |

### Raw JSON (optional)

For power users who need word-level timestamps and confidence scores:

```bash
transcribee --raw "https://youtube.com/watch?v=..."
```

This adds `transcript-raw.json` with the full ElevenLabs response.

## How it works 🐝

1. Downloads audio from YouTube (yt-dlp) or extracts from local video (ffmpeg)
2. Transcribes with ElevenLabs (`scribe_v1_experimental` with speaker diarization)
3. Claude analyzes content and existing library structure
4. Auto-categorizes into the right folder
5. Saves transcript files with metadata

## Requirements

- macOS (tested on Sonoma)
- Node.js 18+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — `brew install yt-dlp`
- [ffmpeg](https://ffmpeg.org/) — `brew install ffmpeg`
- [ElevenLabs API key](https://elevenlabs.io/) — for transcription
- [Anthropic API key](https://anthropic.com/) — for auto-categorization

## Supported formats

| Type | Formats |
|------|---------|
| Audio | mp3, m4a, wav, ogg, flac |
| Video | mp4, mkv, webm, mov, avi |
| URLs | youtube.com, youtu.be, instagram.com/reel, tiktok.com |

---

*bzz bzz* 🐝
