---
name: tube-summary
description: Search YouTube for videos on any topic and get intelligent summaries from video subtitles. Use when you need to: (1) Find and preview YouTube videos on a subject, (2) Get a detailed description of what a video covers based on its actual content, (3) Quickly understand video topics without watching. Workflow: search YouTube → pick a video → extract and summarize subtitles.
---

# tube-summary

Search YouTube for videos on any topic, then extract and summarize their content using subtitles.

## Quick Start

### Step 1: Search for Videos

When asked about a topic, search YouTube and list the top 10 results:

```bash
python3 scripts/youtube-search.py "your search query"
```

This returns a numbered list of videos with titles, channels, and view counts.

### Step 2: User Picks a Video

The user selects one video by number (e.g., "3" for the third video).

### Step 3: Download Subtitles

Extract English subtitles from the selected video using yt-dlp:

```bash
yt-dlp --write-subs --sub-langs en --skip-download "VIDEO_URL"
```

This creates a `.en.vtt` subtitle file without downloading the video.

### Step 4: Process & Summarize

Use the subtitle processor to analyze and summarize:

```bash
python3 scripts/process-subtitles.py "path/to/subtitle-file.vtt"
```

This generates:
- **Key Topics**: Main subjects covered in the video
- **Summary**: Concise 2-3 paragraph description of content
- **Timestamps**: Notable moments with context
- **Key Quotes**: Important statements from speakers

## Workflow

1. **Search** → `youtube-search.py "<topic>"` → Display top 10 videos
2. **User selects** → e.g., "Video 5"
3. **Extract URL** → From the search results
4. **Download subs** → `yt-dlp --write-subs --sub-langs en --skip-download "URL"`
5. **Process** → `process-subtitles.py "subtitle.vtt"`
6. **Present** → Formatted summary with key points

## Prerequisites

- `yt-dlp` (install: `pip install yt-dlp`)
- `requests` (for YouTube search fallback)
- Python 3.7+

## Notes

- If YouTube search API is unavailable, the fallback uses web scraping via requests
- Subtitles may be auto-generated if not manually authored
- Some videos may not have English subtitles available
- The subtitle file is created in the same directory as yt-dlp is run

## Example Usage

```
User: "Tell me about Rust programming language"

→ Search returns 10 videos about Rust

User: "Summarize video 3"

→ Downloads subtitles from video 3
→ Processes and returns detailed summary
```
