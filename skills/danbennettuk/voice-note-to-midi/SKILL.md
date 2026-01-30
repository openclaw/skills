---
name: voice-note-to-midi
description: Convert voice notes, humming, and melodic audio recordings to quantized MIDI files using ML-based pitch detection and intelligent post-processing
author: Clawd
tags: [audio, midi, music, transcription, machine-learning]
---

# 🎵 Voice Note to MIDI

Transform your voice memos, humming, and melodic recordings into clean, quantized MIDI files ready for your DAW.

## What It Does

This skill provides a complete audio-to-MIDI conversion pipeline that:

1. **Stem Separation** - Uses HPSS (Harmonic-Percussive Source Separation) to isolate melodic content from drums, noise, and background sounds
2. **ML-Powered Pitch Detection** - Leverages Spotify's Basic Pitch model for accurate fundamental frequency extraction
3. **Key Detection** - Automatically detects the musical key of your recording using Krumhansl-Kessler key profiles
4. **Intelligent Quantization** - Snaps notes to a configurable timing grid with optional key-aware pitch correction
5. **Post-Processing** - Applies octave pruning, overlap-based harmonic removal, and legato note merging for clean output

### Pipeline Architecture

```
Audio Input (WAV/M4A/MP3)
    ↓
┌─────────────────────────────────────┐
│ Step 1: Stem Separation (HPSS)     │
│ - Isolate harmonic content          │
│ - Remove drums/percussion           │
│ - Noise gating                      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Step 2: Pitch Detection             │
│ - Basic Pitch ML model (Spotify)    │
│ - Polyphonic note detection         │
│ - Onset/offset estimation           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Step 3: Analysis                    │
│ - Pitch class distribution          │
│ - Key detection                     │
│ - Dominant note identification      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Step 4: Quantization & Cleanup      │
│ - Timing grid snap                  │
│ - Key-aware pitch correction        │
│ - Octave pruning (harmonic removal) │
│ - Overlap-based pruning             │
│ - Note merging (legato)             │
│ - Velocity normalization            │
└─────────────────────────────────────┘
    ↓
MIDI Output (Standard MIDI File)
```

## Setup

### Prerequisites

- Python 3.11+ (Python 3.14+ recommended)
- FFmpeg (for audio format support)
- pip

### Installation

**Quick Install (Recommended):**

```bash
cd /path/to/voice-note-to-midi
./setup.sh
```

This automated script will:
- Check Python 3.11+ is installed
- Create the `~/melody-pipeline` directory
- Set up the virtual environment
- Install all dependencies (basic-pitch, librosa, music21, etc.)
- Download and configure the hum2midi script
- Add melody-pipeline to your PATH

**Manual Install:**

If you prefer manual setup:

```bash
mkdir -p ~/melody-pipeline
cd ~/melody-pipeline
python3 -m venv venv-bp
source venv-bp/bin/activate
pip install basic-pitch librosa soundfile mido music21
chmod +x ~/melody-pipeline/hum2midi
```

5. **Add to your PATH (optional):**

```bash
echo 'export PATH="$HOME/melody-pipeline:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Verify Installation

```bash
cd ~/melody-pipeline
./hum2midi --help
```

## Usage

### Basic Usage

Convert a voice memo to MIDI:

```bash
./hum2midi my_humming.wav
```

This creates `my_humming.mid` with 16th-note quantization.

### Specify Output File

```bash
./hum2midi input.wav output.mid
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--grid <value>` | Quantization grid: `1/4`, `1/8`, `1/16`, `1/32` | `1/16` |
| `--min-note <ms>` | Minimum note duration in milliseconds | `50` |
| `--no-quantize` | Skip quantization (output raw Basic Pitch MIDI) | disabled |
| `--key-aware` | Enable key-aware pitch correction | disabled |
| `--no-analysis` | Skip pitch analysis and key detection | disabled |

### Usage Examples

#### Quantize to eighth notes
```bash
./hum2midi melody.wav --grid 1/8
```

#### Key-aware quantization (recommended for tonal music)
```bash
./hum2midi song.wav --key-aware
```

#### Require longer minimum notes
```bash
./hum2midi humming.wav --min-note 100
```

#### Skip analysis for faster processing
```bash
./hum2midi quick.wav --no-analysis
```

#### Combine options
```bash
./hum2midi recording.wav output.mid --grid 1/8 --key-aware --min-note 80
```

### Processing MIDI Input

You can also process existing MIDI files through the quantization pipeline:

```bash
./hum2midi input.mid output.mid --grid 1/16 --key-aware
```

This skips the audio processing steps and goes directly to analysis and quantization.

## Sample Output

```
═══════════════════════════════════════════════════════════════
  hum2midi - Melody-to-MIDI Pipeline (Basic Pitch Edition)
  [Key-Aware Mode Enabled]
═══════════════════════════════════════════════════════════════

Input:  my_humming.wav
Output: my_humming.mid

→ Step 1: Stem Separation (HPSS)
  Isolating melodic content...
  Loaded: 5.23s @ 44100Hz
  ✓ Melody stem extracted → 5.23s

→ Step 2: Audio-to-MIDI Conversion (Basic Pitch)
  Running Spotify's Basic Pitch ML model on melody stem...
  ✓ Raw MIDI generated (Basic Pitch)

→ Step 3: Pitch Analysis & Key Detection
  Notes detected: 42 total, 7 unique
  Note range: C3 - G4
  Pitch classes: C3, E3, G3, A3, C4, D4, G4
  Dominant note: G3 (23.8% of notes)
  Detected key: G major

→ Step 4: Quantization & Cleanup
  Octave pruning: removed 3 harmonic notes above 67 (median+12)
  Overlap pruning: removed 2 harmonic notes at overlapping positions
  Note merging: merged 5 staccato chunks into legato notes (gap<=60 ticks)
  Grid:   240 ticks (1/16)
  Notes:  38 notes
  Key:    G major
  Key-aware: 2 notes corrected to scale
  Tempo:  120 BPM
  ✓ Quantized MIDI saved

═══════════════════════════════════════════════════════════════
  ✓ Done! Output: my_humming.mid
═══════════════════════════════════════════════════════════════

📊 ANALYSIS SUMMARY
─────────────────────────────────────────────────────────────
  Detected Notes: C3, E3, G3, A3, C4, D4, G4
  Detected Key:   G major
  Quantization:   Key-aware mode (notes snapped to scale)

MIDI Info: 38 notes, 7 unique pitches, 120 BPM
Pitches: C3, E3, G3, A3, C4, D4, G4
```

## Notes & Limitations

### Audio Quality Matters

- **Clear, loud melody** produces the best results
- **Background noise** can cause false note detection
- **Reverb and effects** may confuse pitch detection
- **Close-mic'd vocals** work significantly better than room recordings

### Musical Considerations

- **Monophonic sources** work best (single melody line)
- **Polyphonic audio** (chords, multiple instruments) will produce messy results
- **Vibrato and pitch bends** may be quantized to stepped pitches
- **Rapid note passages** may be missed or merged

### Technical Limitations

- **Tempo is fixed** at 120 BPM in output (time positions are preserved, but tempo may need adjustment in your DAW)
- **Note velocities** are normalized but may need manual adjustment
- **Very short notes** (<50ms) may be filtered out by default
- **Extreme pitch ranges** may cause octave detection issues

### Post-Processing Recommendations

After generating MIDI, you may want to:

1. **Import into your DAW** and adjust tempo to match your original recording
2. **Quantize further** if stricter timing is needed
3. **Adjust note velocities** for dynamics
4. **Apply swing/groove** templates if the rigid grid sounds too mechanical
5. **Edit individual notes** that were misdetected (common with fast runs)

### Supported Audio Formats

Input formats supported via FFmpeg:
- WAV, AIFF, FLAC (uncompressed, best quality)
- MP3, M4A, AAC (compressed, acceptable)
- OGG, OPUS (open source formats)
- Most other formats FFmpeg supports

## Troubleshooting

### No notes detected
- Check that input file isn't silent or corrupted
- Try increasing `--min-note` threshold
- Verify audio has clear melodic content (not just noise)

### Too many notes / messy output
- Enable octave pruning and overlap pruning (on by default)
- Use `--key-aware` to constrain to musical scale
- Check for background noise in source audio

### Wrong key detected
- Key detection works best with at least 8-10 measures of music
- Chromatic passages may confuse the detector
- Manually review and adjust in your DAW if needed

### Notes in wrong octave
- Basic Pitch sometimes detects harmonics instead of fundamentals
- The pipeline includes pruning, but some may slip through
- Use your DAW's transpose function for simple octave shifts

## References

- [Basic Pitch](https://github.com/spotify/basic-pitch) - Spotify's polyphonic pitch detection model
- [librosa HPSS](https://librosa.org/doc/latest/generated/librosa.decompose.hpss.html) - Harmonic-Percussive Source Separation
- [Krumhansl-Kessler Key Profiles](https://rnhart.net/articles/key-finding/) - Key detection algorithm

## License

This skill integrates Basic Pitch by Spotify, which is licensed under Apache 2.0. The pipeline script and documentation are provided under MIT license.
