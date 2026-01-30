# Installation Guide

Setup instructions for callmac skill dependencies.

## Prerequisites

- macOS (tested on macOS 12+)
- Python 3.8+
- Homebrew (for ffmpeg installation)

## Step 1: Install Python Dependencies

### edge-tts
```bash
pip3 install edge-tts
```

Verify installation:
```bash
python3 -m edge_tts --list-voices | head -5
```

### Additional Python Packages (Optional)
```bash
pip3 install requests  # For web functionality
pip3 install pydub     # For advanced audio processing
```

## Step 2: Install Audio Tools

### ffmpeg (for audio merging)
```bash
brew install ffmpeg
```

Verify installation:
```bash
ffmpeg -version | head -1
```

### macOS Audio Tools (Built-in)
Ensure these are available:
- `afplay` - Audio playback
- `osascript` - Volume control

Test:
```bash
which afplay
which osascript
```

## Step 3: Test System Audio

### Check Audio Output
```bash
# Check system volume
osascript -e "output volume of (get volume settings)"

# Check mute status
osascript -e "output muted of (get volume settings)"

# Test audio playback
afplay /System/Library/Sounds/Ping.aiff
```

### Test Edge TTS
```bash
# Generate test audio
python3 -m edge_tts --voice "en-US-JennyNeural" --text "Test audio" --write-media test.mp3

# Play test audio
afplay test.mp3

# Clean up
rm test.mp3
```

## Step 4: Install Skill Scripts

Make scripts executable:
```bash
chmod +x skills/callmac/scripts/*.py
```

## Step 5: Environment Setup (Optional)

### Create Virtual Environment
```bash
python3 -m venv venv-tts
source venv-tts/bin/activate
pip install edge-tts
```

### Set Aliases (for convenience)
Add to `~/.zshrc` or `~/.bashrc`:
```bash
alias tts-gen="python3 /path/to/skills/callmac/scripts/generate_tts.py"
alias tts-play="python3 /path/to/skills/callmac/scripts/play_audio.py"
```

## Troubleshooting

### "edge-tts not found" Error
```bash
# Reinstall edge-tts
pip3 uninstall edge-tts
pip3 install edge-tts

# Check Python path
python3 -c "import edge_tts; print(edge_tts.__file__)"
```

### "ffmpeg not found" Error
```bash
# Reinstall ffmpeg
brew reinstall ffmpeg

# Check installation
brew list ffmpeg
```

### No Audio Output
1. Check system volume:
   ```bash
   osascript -e "set volume output volume 75"
   osascript -e "set volume without output muted"
   ```

2. Test with system sound:
   ```bash
   afplay /System/Library/Sounds/Ping.aiff
   ```

3. Check audio device:
   ```bash
   system_profiler SPAudioDataType
   ```

### Network Issues (Edge TTS requires internet)
```bash
# Test connectivity
curl -I https://speech.platform.bing.com

# If behind proxy, set environment variables:
export HTTP_PROXY="http://proxy:port"
export HTTPS_PROXY="http://proxy:port"
```

### Permission Issues
```bash
# Make scripts executable
chmod +x scripts/*.py

# Run with full path
python3 /full/path/to/scripts/generate_tts.py --text "Test"
```

## Verification

Run complete test:
```bash
# Generate mixed language audio
python3 skills/callmac/scripts/generate_tts.py \
  --text "Hello 你好" \
  --play \
  --voice-en "en-US-JennyNeural" \
  --voice-zh "zh-CN-XiaoxiaoNeural"

# Expected: Should play "Hello 你好" with appropriate voices
```

## Updating

### Update edge-tts
```bash
pip3 install --upgrade edge-tts
```

### Update ffmpeg
```bash
brew upgrade ffmpeg
```

### Update Skill
```bash
# Pull latest skill files
cd skills/callmac
git pull origin main  # if using git
```

## Uninstallation

### Remove Dependencies
```bash
pip3 uninstall edge-tts
brew uninstall ffmpeg
```

### Remove Skill
```bash
rm -rf skills/callmac
```

## Support

For issues:
1. Check error messages
2. Verify all dependencies are installed
3. Test with simple commands
4. Check internet connectivity for Edge TTS

Common issues and solutions are documented in the skill's troubleshooting section.