---
name: callmac
description: Remote voice control for Mac from mobile devices using commands like /callmac or /voice. Broadcast announcements, play alarms, tell stories, wake up kids - all triggered from Telegram/WhatsApp messages. Uses edge-tts with mixed Chinese/English support, local playback, loops, and volume control. | 从移动设备通过 /callmac 或 /voice 命令远程控制 Mac 语音功能。广播公告、播放闹钟、讲故事、叫孩子起床 - 全部通过 Telegram/WhatsApp 消息触发。使用 edge-tts 支持中英文混合、本地播放、循环播放和音量控制。
---

# Callmac Skill

Remote voice control for your Mac from mobile devices. Broadcast announcements, play alarms, tell stories, wake up kids - all triggered from messaging apps like Telegram or WhatsApp. Uses edge-tts with mixed Chinese/English support.

从移动设备远程控制 Mac 语音功能。广播公告、播放闹钟、讲故事、叫孩子起床 - 全部通过 Telegram 或 WhatsApp 触发。使用 edge-tts 支持中英文混合。

## Quick Start | 快速开始

快速开始使用语音技能，生成和播放中英文混合的 TTS 音频。

### Basic Usage | 基本用法

```bash
# Generate and play a simple announcement
python3 scripts/generate_tts.py --text "Hello world" --play

# Generate mixed Chinese/English content
python3 scripts/generate_tts.py --text "Hello 你好" --play

# Save to file
python3 scripts/generate_tts.py --text "Your message" --output announcement.mp3
```

### Voice Selection

Edge TTS provides high-quality neural voices:
- **English (US):** `en-US-JennyNeural` (friendly), `en-US-AriaNeural` (confident)
- **Chinese (Mandarin):** `zh-CN-XiaoxiaoNeural` (warm), `zh-CN-XiaoyiNeural` (lively)
- **Other languages:** See [VOICES.md](references/VOICES.md) for complete list

## Features

### 1. Mixed Language Support
Automatically detects language segments and uses appropriate voices:
- English segments → English neural voice
- Chinese segments → Chinese neural voice
- Other languages → Default or specified voice

### 2. Playback Control
- Local playback on Mac using `afplay`
- Loop playback support (1-∞ times)
- Volume control (0-100%)
- Background/foreground playback options

### 3. File Management
- Save as MP3 files
- Concatenate multiple audio segments
- Batch processing support

### 4. Advanced Features
- Custom voice selection per segment
- Speech rate adjustment
- Pitch modification
- SSML support for advanced control

## Workflows

### Workflow 1: Simple Announcement Playback
1. User provides text to speak
2. System detects language(s)
3. Generates appropriate TTS audio
4. Plays locally on Mac

### Workflow 2: Mixed Language Audio Creation
1. User provides Chinese/English mixed text
2. System splits by language segments
3. Generates separate audio for each language
4. Concatenates into single MP3 file
5. Optionally plays or saves

### Workflow 3: Scheduled/Repeated Announcements
1. User provides text and playback schedule
2. System creates cron job or loop
3. Plays at specified intervals
4. Can be stopped on demand

## Scripts

### `scripts/generate_tts.py`
Main script for TTS generation and playback.

**Usage:**
```bash
# Basic generation and playback
python3 generate_tts.py --text "Message" --play

# Save to file
python3 generate_tts.py --text "Message" --output file.mp3

# Mixed language with custom voices
python3 generate_tts.py --text "Hello 你好" --voice-en "en-US-AriaNeural" --voice-zh "zh-CN-XiaoyiNeural"

# Loop playback
python3 generate_tts.py --text "Message" --play --loops 5

# Volume control
python3 generate_tts.py --text "Message" --play --volume 80

# SSML support
python3 generate_tts.py --ssml "<speak>Hello <break time='500ms'/> world</speak>"
```

**Parameters:**
- `--text`: Text to convert to speech
- `--ssml`: SSML markup for advanced control
- `--output`: Save to MP3 file
- `--play`: Play immediately after generation
- `--voice`: Default voice (overrides auto-detection)
- `--voice-en`: English voice override
- `--voice-zh`: Chinese voice override
- `--loops`: Number of times to play (default: 1)
- `--volume`: Playback volume 0-100 (default: system volume)
- `--rate`: Speech rate adjustment (+/- %)
- `--pitch`: Pitch adjustment (+/- Hz)

### `scripts/play_audio.py`
Audio playback control utilities.

**Usage:**
```bash
# Play existing audio file
python3 play_audio.py --file audio.mp3

# Loop playback
python3 play_audio.py --file audio.mp3 --loops 3

# Volume control
python3 play_audio.py --file audio.mp3 --volume 75

# Stop all playback
python3 play_audio.py --stop
```

### `scripts/merge_audio.py`
Merge multiple audio files.

**Usage:**
```bash
# Merge two files
python3 merge_audio.py --files part1.mp3 part2.mp3 --output combined.mp3

# Create playlist and merge
python3 merge_audio.py --playlist playlist.txt --output combined.mp3
```

## References

### [VOICES.md](references/VOICES.md)
Complete list of available Edge TTS voices with language, gender, and style information.

### [INSTALLATION.md](references/INSTALLATION.md)
Setup instructions for edge-tts and ffmpeg dependencies.

### [EXAMPLES.md](references/EXAMPLES.md)
Example usage patterns and common scenarios.

## Dependencies

1. **edge-tts**: `pip3 install edge-tts`
2. **ffmpeg**: `brew install ffmpeg` (for audio merging)
3. **macOS tools**: `afplay` (built-in), `osascript` (volume control)

## Common Patterns

### Pattern 1: Welcome Message
```bash
python3 scripts/generate_tts.py --text "Welcome to the system. 系统欢迎您。" --play --voice-en "en-US-JennyNeural" --voice-zh "zh-CN-XiaoxiaoNeural"
```

### Pattern 2: Scheduled Reminder
```bash
# Create audio file
python3 scripts/generate_tts.py --text "Time for your meeting. 会议时间到了。" --output reminder.mp3

# Schedule playback (using cron)
echo "*/30 * * * * afplay /path/to/reminder.mp3" | crontab -
```

### Pattern 3: Multi-language Announcement
```bash
python3 scripts/generate_tts.py --text "Alert: System update in progress. 警报：系统更新进行中。" --play --loops 3 --volume 90
```

## Troubleshooting

### No Audio Output
1. Check system volume: `osascript -e "output volume of (get volume settings)"`
2. Check mute status: `osascript -e "output muted of (get volume settings)"`
3. Test with simple audio: `afplay /System/Library/Sounds/Ping.aiff`

### edge-tts Not Working
1. Verify installation: `python3 -m edge_tts --list-voices`
2. Check internet connection (edge-tts requires online access)
3. Update package: `pip3 install --upgrade edge-tts`

### Audio Quality Issues
1. Use neural voices for best quality
2. Adjust speech rate if too fast/slow
3. Consider SSML for precise control

## Notes

- Edge TTS requires internet connection for voice synthesis
- Local playback uses macOS built-in `afplay` command
- Volume control uses `osascript` to adjust system volume
- For offline use, consider alternative TTS solutions
- Large texts may be split into multiple segments automatically