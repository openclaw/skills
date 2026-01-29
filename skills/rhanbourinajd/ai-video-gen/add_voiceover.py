#!/usr/bin/env python3
"""
Add voiceover to existing video
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def generate_audio(text, voice="alloy", output_path="voiceover.mp3"):
    """Generate audio using OpenAI TTS"""
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY not set")
        sys.exit(1)
    
    import openai
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    print(f"🎤 Generating voiceover...")
    
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    
    response.stream_to_file(output_path)
    print(f"✓ Audio saved: {output_path}")
    return output_path


def add_audio_to_video(video_path, audio_path, output_path, mix_audio=False):
    """Combine video with audio using FFmpeg"""
    
    print(f"🎞️ Adding audio to video...")
    
    if mix_audio:
        # Mix new audio with existing audio
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-filter_complex', '[0:a][1:a]amix=inputs=2:duration=longest',
            '-c:v', 'copy',
            output_path
        ]
    else:
        # Replace audio
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',
            output_path
        ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Video with audio created: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error: {e.stderr}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Add voiceover to video')
    parser.add_argument('--video', required=True, help='Input video file')
    parser.add_argument('--text', help='Text for voiceover')
    parser.add_argument('--audio', help='Pre-existing audio file (alternative to --text)')
    parser.add_argument('--output', default='output_with_audio.mp4', help='Output video file')
    parser.add_argument('--voice', default='alloy', 
                       choices=['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'],
                       help='OpenAI TTS voice')
    parser.add_argument('--mix', action='store_true', 
                       help='Mix with existing audio instead of replacing')
    
    args = parser.parse_args()
    
    # Validate video exists
    if not Path(args.video).exists():
        print(f"❌ Error: Video not found: {args.video}")
        sys.exit(1)
    
    # Get or generate audio
    if args.audio:
        if not Path(args.audio).exists():
            print(f"❌ Error: Audio file not found: {args.audio}")
            sys.exit(1)
        audio_path = args.audio
    elif args.text:
        audio_path = generate_audio(args.text, args.voice)
    else:
        print("❌ Error: Must provide either --text or --audio")
        sys.exit(1)
    
    # Combine video and audio
    add_audio_to_video(args.video, audio_path, args.output, args.mix)
    
    # Clean up temp audio if we generated it
    if args.text and not args.audio:
        Path(audio_path).unlink(missing_ok=True)


if __name__ == '__main__':
    main()
