---
name: mac-tts
description: Text-to-speech using macOS built-in `say` command. Use for voice notifications, audio alerts, reading text aloud, or announcing messages through Mac speakers. Supports multiple languages including Chinese (Mandarin), English, Japanese, etc.
---

# mac-tts

Use macOS built-in `say` command for text-to-speech output through system speakers.

## Basic Usage

```bash
say "Hello, this is a test"
```

## With Voice Selection

```bash
say -v "Meijia" "你好，這是測試"      # 台灣中文 (推薦)
say -v "Tingting" "你好，这是测试"    # 簡體中文
say -v "Samantha" "Hello world"       # 英文
```

## Common Chinese Voices (zh_TW)

| Voice | Description |
|-------|-------------|
| Meijia | 美佳 - 自然女聲 (推薦) |
| Flo | 年輕女聲 |
| Eddy | 男聲 |
| Reed | 男聲 |
| Sandy | 女聲 |
| Shelley | 女聲 |

## List All Available Voices

```bash
say -v "?"                           # 全部語音
say -v "?" | grep zh_TW              # 只列台灣中文
```

## Volume Control

Check/adjust system volume before speaking:

```bash
# Check current volume (0-100) and mute status
osascript -e "output volume of (get volume settings)"
osascript -e "output muted of (get volume settings)"

# Unmute
osascript -e "set volume without output muted"

# Set volume (0-100)
osascript -e "set volume output volume 70"
```

## Use Cases

- **通知**: `say -v "Meijia" "外送到了"`
- **提醒**: `say -v "Meijia" "會議即將開始"`
- **警告**: `say -v "Meijia" "注意，有新的緊急訊息"`

## Notes

- Runs synchronously (blocks until speech completes)
- Add `&` for async: `say "message" &`
- Works only on macOS
