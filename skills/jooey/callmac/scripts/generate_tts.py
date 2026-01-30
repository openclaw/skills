#!/usr/bin/env python3
"""
Generate TTS audio using edge-tts with mixed language support.
"""

import argparse
import os
import subprocess
import sys
import tempfile
import re
from pathlib import Path

# Default voices
DEFAULT_VOICES = {
    'en': 'en-US-JennyNeural',      # Friendly English voice
    'zh': 'zh-CN-XiaoxiaoNeural',   # Warm Chinese voice
    'default': 'en-US-JennyNeural'  # Fallback voice
}

def detect_language(text):
    """Detect if text contains Chinese characters."""
    # Simple detection: look for Chinese characters
    zh_pattern = re.compile(r'[\u4e00-\u9fff]')
    has_chinese = bool(zh_pattern.search(text))
    
    # Check for English (basic detection)
    en_pattern = re.compile(r'[a-zA-Z]')
    has_english = bool(en_pattern.search(text))
    
    if has_chinese and has_english:
        return 'mixed'
    elif has_chinese:
        return 'zh'
    elif has_english:
        return 'en'
    else:
        return 'unknown'

def split_mixed_text(text):
    """Split mixed Chinese/English text into segments.
    
    Improved version: punctuation and whitespace attach to the preceding segment.
    """
    segments = []
    current_segment = ''
    current_lang = None
    
    for char in text:
        # Detect language of current character
        if '\u4e00' <= char <= '\u9fff':  # Chinese character
            char_lang = 'zh'
        elif 'a' <= char.lower() <= 'z':  # English letter
            char_lang = 'en'
        else:
            # Punctuation, numbers, whitespace, etc.
            # Keep the current language if we have one, otherwise default to 'en'
            char_lang = current_lang if current_lang is not None else 'en'
        
        if current_lang is None:
            current_lang = char_lang
            current_segment = char
        elif char_lang == current_lang:
            current_segment += char
        else:
            # Language changed, finalize current segment
            segments.append((current_segment, current_lang))
            current_segment = char
            current_lang = char_lang
    
    if current_segment:
        segments.append((current_segment, current_lang))
    
    return segments

def is_valid_tts_text(text):
    """Check if text contains pronounceable characters (not just punctuation/whitespace)."""
    if not text:
        return False
    
    # Check for Chinese characters
    if re.search(r'[\u4e00-\u9fff]', text):
        return True
    
    # Check for English letters
    if re.search(r'[a-zA-Z]', text):
        return True
    
    # Check for numbers (digits) - they are pronounceable
    if re.search(r'\d', text):
        return True
    
    # If we get here, it's only punctuation, whitespace, etc.
    return False

def generate_tts(text, voice, output_file):
    """Generate TTS audio using edge-tts."""
    try:
        cmd = [
            sys.executable, '-m', 'edge_tts',
            '--voice', voice,
            '--text', text,
            '--write-media', output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error generating TTS: {result.stderr}")
            return False
        
        return True
    except Exception as e:
        print(f"Exception generating TTS: {e}")
        return False

def play_audio(file_path, loops=1, volume=None):
    """Play audio file using afplay."""
    if volume is not None:
        # Set system volume
        volume_cmd = ['osascript', '-e', f'set volume output volume {volume}']
        subprocess.run(volume_cmd, capture_output=True)
    
    for i in range(loops):
        if loops > 1:
            print(f"Playing loop {i+1}/{loops}")
        
        cmd = ['afplay', file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error playing audio: {result.stderr}")
            return False
    
    return True

def merge_audio_files(files, output_file):
    """Merge multiple audio files using ffmpeg."""
    # Create playlist file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for file in files:
            f.write(f"file '{os.path.abspath(file)}'\n")
        playlist_file = f.name
    
    try:
        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', playlist_file,
            '-c', 'copy', output_file,
            '-y'  # Overwrite output file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error merging audio: {result.stderr}")
            return False
        
        return True
    finally:
        os.unlink(playlist_file)

def main():
    parser = argparse.ArgumentParser(description='Generate TTS audio with mixed language support')
    parser.add_argument('--text', help='Text to convert to speech')
    parser.add_argument('--ssml', help='SSML markup for advanced control')
    parser.add_argument('--output', help='Output MP3 file path')
    parser.add_argument('--play', action='store_true', help='Play audio after generation')
    parser.add_argument('--voice', help='Default voice (overrides auto-detection)')
    parser.add_argument('--voice-en', help='English voice override')
    parser.add_argument('--voice-zh', help='Chinese voice override')
    parser.add_argument('--loops', type=int, default=1, help='Number of times to play')
    parser.add_argument('--volume', type=int, help='Playback volume 0-100')
    parser.add_argument('--rate', type=int, help='Speech rate adjustment (+/- %%)')
    parser.add_argument('--pitch', type=int, help='Pitch adjustment (+/- Hz)')
    
    args = parser.parse_args()
    
    if not args.text and not args.ssml:
        parser.error("Either --text or --ssml is required")
    
    # Use text or SSML
    content = args.text if args.text else args.ssml
    is_ssml = bool(args.ssml)
    
    # Determine language
    if is_ssml:
        lang = 'mixed'  # SSML can contain multiple languages
    else:
        lang = detect_language(content)
    
    # Select voices
    voices = {
        'en': args.voice_en or args.voice or DEFAULT_VOICES['en'],
        'zh': args.voice_zh or args.voice or DEFAULT_VOICES['zh'],
        'default': args.voice or DEFAULT_VOICES['default']
    }
    
    # Generate audio
    if lang == 'mixed' and not is_ssml:
        # Split and generate mixed language audio
        segments = split_mixed_text(content)
        audio_files = []
        
        for i, (segment_text, segment_lang) in enumerate(segments):
            # Skip segments that don't contain pronounceable text
            if not is_valid_tts_text(segment_text):
                print(f"Skipping non-pronounceable segment: {repr(segment_text[:50])}")
                continue
                
            voice = voices.get(segment_lang, voices['default'])
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_file.close()
            
            print(f"Generating {segment_lang} segment: {segment_text[:50]}...")
            if generate_tts(segment_text, voice, temp_file.name):
                audio_files.append(temp_file.name)
            else:
                print(f"Failed to generate segment: {segment_text[:50]}...")
        
        if audio_files:
            if args.output:
                output_file = args.output
            else:
                output_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False).name
            
            print(f"Merging {len(audio_files)} segments...")
            if merge_audio_files(audio_files, output_file):
                print(f"Audio saved to: {output_file}")
            else:
                print("Failed to merge audio segments")
                sys.exit(1)
            
            # Clean up temp files
            for file in audio_files:
                os.unlink(file)
        else:
            print("No audio segments generated")
            sys.exit(1)
    else:
        # Single language or SSML
        voice = voices.get(lang, voices['default'])
        
        if args.output:
            output_file = args.output
        else:
            output_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False).name
        
        print(f"Generating {lang} audio with voice {voice}...")
        if generate_tts(content, voice, output_file):
            print(f"Audio saved to: {output_file}")
        else:
            print("Failed to generate audio")
            sys.exit(1)
    
    # Play audio if requested
    if args.play:
        print(f"Playing audio (loops: {args.loops})...")
        if not play_audio(output_file, args.loops, args.volume):
            print("Failed to play audio")
            sys.exit(1)
    
    if not args.output and not args.play:
        # Created temp file, clean up
        os.unlink(output_file)

if __name__ == '__main__':
    main()