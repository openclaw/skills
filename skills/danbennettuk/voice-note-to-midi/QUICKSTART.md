# Voice Note to MIDI - Quick Reference

## 🚀 Quick Start

```bash
cd ~/melody-pipeline
./hum2midi my_recording.wav
```

That's it! Creates `my_recording.mid` in the same directory.

## 📝 Common Use Cases

### Convert iPhone Voice Memo
```bash
# Copy from phone, convert if needed
./hum2mui "2025-01-29 14.32.m4a" --key-aware
```

### Quick Melody to DAW
```bash
# 8th note grid for more natural feel
./hum2midi melody.wav --grid 1/8
```

### Clean Up Existing MIDI
```bash
# Re-quantize a messy MIDI file
./hum2midi messy_input.mid cleaned_output.mid --grid 1/16
```

### Song Analysis
```bash
# See key and pitch analysis
./hum2midi song_snippet.wav
```

## ⚙️ Option Reference

| If you want... | Use this |
|----------------|----------|
| Tighter timing | `--grid 1/32` |
| Looser feel | `--grid 1/8` or `--grid 1/4` |
| Snap to scale | `--key-aware` |
| Remove short blips | `--min-note 100` |
| Faster processing | `--no-analysis` |
| Raw Basic Pitch output | `--no-quantize` |

## 🔧 Tips

- **Best results:** Hum/sing clearly, close to mic, minimal background noise
- **Tempo:** Output is always 120 BPM - adjust in your DAW
- **Key-aware mode:** Helps with tonal music, may hurt atonal/experimental melodies
- **Legato:** The pipeline merges staccato chunks automatically

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Too many notes | Check for background noise; use `--key-aware` |
| Wrong octave | Use DAW transpose; check for harmonics in source |
| Timing off | Adjust quantization grid; DAW groove templates |
| No output | Check audio isn't silent; increase `--min-note` |

## 📂 File Locations

- Pipeline: `~/melody-pipeline/hum2midi`
- Virtual env: `~/melody-pipeline/venv-bp/`
- Temp stems: `~/melody-pipeline/.stems/` (auto-cleaned)

---

For detailed documentation, see SKILL.md
