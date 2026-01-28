# GifHorse Skill for ClawdHub

A Clawdbot skill that enables dialogue search and reaction GIF creation from your video library.

## What is This?

This is the ClawdHub skill package for [gifhorse](https://github.com/Coyote-git/gifhorse) - a CLI tool that lets you search dialogue in your video library and create reaction GIFs with timed subtitles.

## Features

- 🔍 **Search dialogue** across your entire video library instantly
- 🎬 **Create GIFs** with perfectly timed subtitles
- 🏷️ **Automatic branding** - all GIFs include a subtle "gifhorse" watermark
- 📝 **Transcribe videos** using subtitle files or Whisper AI
- 👀 **Preview** before creating to verify timing

## Installation

### Via ClawdHub

```bash
clawdhub install gifhorse
```

### Manual Installation

1. Copy `SKILL.md` to your Clawdbot skills directory
2. Run the installation commands from the skill's install instructions
3. Restart Clawdbot to load the skill

## Prerequisites

- Python 3.8+
- FFmpeg-full (for subtitle rendering)
- macOS, Linux, or Windows

The skill includes automated installation commands for:
- gifhorse CLI tool
- FFmpeg-full (macOS via Homebrew)

## Usage with Clawdbot

Once installed, you can ask Clawdbot naturally:

```
Search my video library for quotes about "perfect"
```

```
Create a GIF from Blade Runner with the "cells" quote
```

```
Make a high-quality reaction GIF with watermark from that scene
```

Clawdbot will automatically invoke the gifhorse skill and execute the appropriate commands.

## Direct Command Usage

You can also use gifhorse commands directly:

```bash
gifhorse search "memorable quote"
gifhorse preview "memorable quote" 1
gifhorse create "memorable quote" 1
```

## Publishing to ClawdHub

To publish this skill to ClawdHub:

1. **Fork or create your own copy** of this skill directory
2. **Test locally** with your Clawdbot instance
3. **Upload to ClawdHub:**
   - Visit https://clawdhub.com
   - Sign in with GitHub
   - Upload the SKILL.md file
   - Add version information and changelog
   - Submit for review

The skill will be available for others to install once approved by ClawdHub moderators.

## Version Information

- **Current Version:** 1.0.0
- **Compatible With:** Clawdbot 2026.1.x+
- **License:** MIT

## Learn More

- **GifHorse Repository:** https://github.com/Coyote-git/gifhorse
- **ClawdHub:** https://clawdhub.com
- **Clawdbot Documentation:** https://docs.clawd.bot

## Contributing

Issues and improvements welcome! Submit PRs to the main gifhorse repository or this skill package.
