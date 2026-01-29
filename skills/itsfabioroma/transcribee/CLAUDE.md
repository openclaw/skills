# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A video transcription system that downloads audio from YouTube, Instagram Reels, TikTok, and local files, transcribes it using ElevenLabs, and automatically categorizes transcripts into a knowledge library using Claude AI for theme classification.

## Quick Start

```bash
# Install dependencies
pnpm install

# Setup environment variables
cp .env.example .env
# Edit .env and add your API keys:
# - ELEVEN_LABS_API_KEY (for speech-to-text)
# - ANTHROPIC_API_KEY (for intelligent organization)

# Transcribe a YouTube video
pnpm exec tsx index.ts "https://www.youtube.com/watch?v=..."

# Or use the convenience wrapper script
./transcribe.sh "https://www.youtube.com/watch?v=..."
```

## System Dependencies

This project requires `yt-dlp` to be installed on the system:
- macOS: `brew install yt-dlp`
- Linux: `pip install yt-dlp`
- Windows: `winget install yt-dlp`

## Architecture

### Core Workflow (index.ts)

The main script follows this pipeline:

1. **Video Metadata Extraction** (`getVideoTitle`): Uses yt-dlp to extract and sanitize the video title
2. **Audio Download** (`downloadAudio`): Downloads best quality audio as m4a using yt-dlp with Android/web player clients to bypass restrictions
3. **Transcription** (`transcribeAudio`): Sends audio to ElevenLabs `scribe_v1_experimental` model with diarization (speaker identification) enabled
4. **Library Structure Analysis** (`readLibraryStructure`): Reads existing transcript library from `~/Documents/transcripts/` as a flat folder structure
5. **Category Classification** (`classifyAndOrganize`): Uses Claude Sonnet 4 to analyze the transcript and decide which single-level category folder to place it in
6. **Output Generation**: Saves 4 files per transcript:
   - `transcription-raw.txt`: Raw ElevenLabs output
   - `transcription-raw.json`: Full API response with word timings
   - `transcription.txt`: Formatted with speaker labels
   - `metadata.json`: Video info, theme classification, and summary

### Transcript Organization System

The system maintains a knowledge library at `~/Documents/transcripts/`:

- **Folder Structure**: Single-level categories, kebab-case naming (e.g., `ai-podcasts/video-title-2025-10-21/`)
- **Metadata Tracking**: Each transcript folder contains `metadata.json` with theme classification and summary
- **Category Reuse**: Claude analyzes existing categories and reuses them when semantically appropriate

### Key Functions

- `wordsToTranscript(words: Word[]): string` - Converts word-level timestamps into speaker-labeled dialogue format
- `truncateTranscript(text: string, maxTokens: number): string` - Intelligently samples beginning/middle/end of long transcripts to fit token limits
- `folderTreeToString(node: FolderNode): string` - Converts library structure into compact string representation for Claude

### TypeScript Interfaces

The codebase uses strong typing throughout:

- `Word`: Individual transcribed word with timing and speaker info
- `ThemeClassification`: AI-determined topic categories and confidence
- `TranscriptMetadata`: Video metadata and theme classification
- `FolderNode`: Recursive tree structure for library representation
- `OrganizationPlan`: Claude's decision on which category to use

## Claude AI Integration

The system uses Claude Sonnet 4 (`claude-sonnet-4-20250514`) for category classification with carefully crafted prompts:

- **Token Management**: Estimates ~4 chars per token, truncates transcripts to 150K tokens max using beginning/middle/end sampling
- **Context-Aware**: Provides Claude with full library structure to reuse existing categories when appropriate
- **Confidence Tracking**: Returns high/medium/low confidence levels for category decisions

## Output Location

All transcripts are saved to: `~/Documents/transcripts/{category}/{video-title-YYYY-MM-DD}/`

## Development Notes

- The project uses `tsx` for direct TypeScript execution without compilation
- Uses `pnpm` as package manager (v10.10.0)
- All file operations use Node's `fs.promises` API
- ElevenLabs timeout set to 1200 seconds (20 minutes) for long videos
- Temporary audio files stored in OS tmpdir and cleaned up after processing
