#!/usr/bin/env python3
"""
MoodCast - Emotionally Expressive Audio Generator
Transform any text into emotionally expressive audio with ambient soundscapes using ElevenLabs v3 audio tags and Sound Effects API.

Author: ashutosh887 (https://github.com/ashutosh887)
Built for #ClawdEleven Hackathon
"""

import os
import sys
import re
import argparse
import tempfile
import subprocess
from typing import Optional, List

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import play
except ImportError:
    print("Installing elevenlabs package...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "elevenlabs", "-q"])
    from elevenlabs.client import ElevenLabs
    from elevenlabs import play

DEFAULT_VOICE_ID = os.environ.get("MOODCAST_DEFAULT_VOICE", "CwhRBWXzGAHq8TQ4Fs17")
MODEL_ID = os.environ.get("MOODCAST_MODEL", "eleven_v3")
OUTPUT_FORMAT = os.environ.get("MOODCAST_OUTPUT_FORMAT", "mp3_44100_128")

MOOD_VOICES = {
    "dramatic": "CwhRBWXzGAHq8TQ4Fs17",
    "calm": "pFZP5JQG7iQjIQuC4Bku",
    "excited": "TX3LPaxmHKxFdv7VOQHJ",
    "scary": "CwhRBWXzGAHq8TQ4Fs17",
    "news": "pFZP5JQG7iQjIQuC4Bku",
    "story": "EXAVITQu4vr4xnSDxMaL",
}

EMOTION_PATTERNS = [
    (r'\b(amazing|incredible|wow|awesome|fantastic|brilliant)\b', '[excited]'),
    (r'\b(happy|delighted|thrilled|ecstatic|overjoyed)\b', '[happy]'),
    (r'[!]{2,}', '[excited]'),
    (r'\b(scared|afraid|terrified|frightened|horror)\b', '[nervous]'),
    (r'\b(nervous|anxious|worried|uneasy)\b', '[nervous]'),
    (r'\b(angry|furious|hate|enraged|outraged)\b', '[angry]'),
    (r'\b(damn|hell|stupid|idiot)\b', '[angry]'),
    (r'\b(sad|sorry|unfortunately|tragic|heartbreaking)\b', '[sorrowful]'),
    (r'\b(crying|tears|grief|mourning|loss)\b', '[crying]'),
    (r'\b(secret|whisper|quiet|shh|between us|confidential)\b', '[whispers]'),
    (r'\b(psst|listen closely)\b', '[whispers]'),
    (r'\b(attention|listen up|important|urgent|emergency)\b', '[shouts]'),
    (r'^[A-Z\s]{10,}[!]', '[shouts]'),
    (r'\b(haha|hehe|lol|funny|hilarious)\b', '[laughs]'),
    (r'\b(sigh|exhausted|tired|finally)\b', '[sighs]'),
    (r'\b(oh my|what|really|no way)\b', '[gasps]'),
    (r'\.\.\.$', '[pause]'),
    (r'\b(um|uh|well|so)\b', '[hesitates]'),
    (r'[—–-]{2,}', '[pause]'),
]

MOOD_TAGS = {
    "dramatic": ['[pause]', '[gasps]', '[whispers]', '[shouts]'],
    "calm": ['[calm]', '[pause]', '[breathes]'],
    "excited": ['[excited]', '[happy]', '[laughs]'],
    "scary": ['[nervous]', '[whispers]', '[slows down]', '[pause]'],
    "news": ['[pause]', '[calm]'],
    "story": ['[pause]', '[whispers]', '[excited]', '[nervous]'],
}

AMBIENT_PRESETS = {
    "dramatic": "orchestral tension building suspense cinematic",
    "calm": "gentle rain on window peaceful ambient",
    "excited": "upbeat cheerful background music celebration",
    "scary": "creepy ambient horror dark atmosphere wind howling",
    "news": "subtle office background white noise professional",
    "story": "fantasy adventure ambient atmospheric",
    "default": "soft ambient background peaceful",
}

def get_client() -> ElevenLabs:
    """Initialize ElevenLabs client."""
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY environment variable not set")
        print("   Set it with: export ELEVENLABS_API_KEY='your-key-here'")
        sys.exit(1)
    return ElevenLabs(api_key=api_key)


def enhance_text_with_emotions(text: str, mood: Optional[str] = None) -> str:
    """
    Analyze text and insert appropriate v3 audio tags for emotional delivery.
    """
    enhanced = text
    tags_added = set()
    
    for pattern, tag in EMOTION_PATTERNS:
        matches = list(re.finditer(pattern, enhanced, re.IGNORECASE | re.MULTILINE))
        for match in reversed(matches):
            if tag not in tags_added or tag in ['[pause]', '[laughs]']:
                start = match.start()
                sentence_start = enhanced.rfind('.', 0, start)
                sentence_start = max(0, sentence_start + 1)
                
                if not re.match(r'\s*\[', enhanced[sentence_start:start]):
                    enhanced = enhanced[:start] + f"{tag} " + enhanced[start:]
                    tags_added.add(tag)
    
    if mood and mood in MOOD_TAGS:
        if not enhanced.startswith('['):
            mood_tag = MOOD_TAGS[mood][0]
            enhanced = f"{mood_tag} {enhanced}"
    
    enhanced = re.sub(r'\s+', ' ', enhanced)
    enhanced = re.sub(r'\[\s+', '[', enhanced)
    enhanced = re.sub(r'\s+\]', ']', enhanced)
    
    return enhanced.strip()


def split_text_for_api(text: str, max_chars: int = 2400) -> List[str]:
    """
    Split text into chunks under the API character limit.
    Tries to split at sentence boundaries.
    Note: Eleven v3 supports up to 5,000 chars, but we use 2,400 for safety.
    """
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    current_chunk = ""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_chars:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def generate_speech(
    client: ElevenLabs,
    text: str,
    voice_id: str = DEFAULT_VOICE_ID,
    model_id: str = MODEL_ID,
    output_format: str = OUTPUT_FORMAT,
    output_path: Optional[str] = None
) -> bytes:
    """
    Generate speech using ElevenLabs v3 with audio tags.
    """
    try:
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format,
        )
        
        audio_bytes = b""
        for chunk in audio:
            audio_bytes += chunk
        
        if output_path:
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            print(f"Audio saved to: {output_path}")
        
        return audio_bytes
        
    except Exception as e:
        print(f"Error generating speech: {e}")
        raise


def generate_sound_effect(
    client: ElevenLabs,
    prompt: str,
    duration: float = 10.0,
    output_path: Optional[str] = None
) -> bytes:
    """
    Generate ambient sound effect using Sound Effects API.
    """
    try:
        audio = client.text_to_sound_effects.convert(
            text=prompt,
            duration_seconds=duration,
        )
        
        audio_bytes = b""
        for chunk in audio:
            audio_bytes += chunk
        
        if output_path:
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            print(f"Sound effect saved to: {output_path}")
        
        return audio_bytes
        
    except Exception as e:
        print(f"Warning: Sound effect generation failed: {e}")
        return b""


def play_audio(audio_bytes: bytes):
    """Play audio bytes through speakers."""
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        players = ["afplay", "mpv", "ffplay", "aplay"]
        for player in players:
            try:
                if player == "ffplay":
                    subprocess.run([player, "-nodisp", "-autoexit", temp_path], 
                                 check=True, capture_output=True)
                else:
                    subprocess.run([player, temp_path], check=True, capture_output=True)
                break
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
        
        os.unlink(temp_path)
        
    except Exception as e:
        print(f"Warning: Could not play audio: {e}")


def list_voices(client: ElevenLabs):
    """List available voices."""
    print("\nAvailable Voices:\n")
    print(f"{'Name':<20} {'Voice ID':<30} {'Labels'}")
    print("-" * 70)
    
    try:
        voices = client.voices.get_all()
        for voice in voices.voices[:20]:
            labels = ", ".join(voice.labels.values()) if voice.labels else ""
            print(f"{voice.name:<20} {voice.voice_id:<30} {labels[:30]}")
    except Exception as e:
        print(f"Error listing voices: {e}")
    
    print("\nTip: Use --voice VOICE_ID to select a specific voice")


def main():
    parser = argparse.ArgumentParser(
        description="MoodCast - Transform text into emotionally expressive audio with ambient soundscapes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python moodcast.py --text "This is amazing news!"
  python moodcast.py --text "A dark night..." --mood scary
  python moodcast.py --text "Hello world" --ambient "coffee shop"
  python moodcast.py --text "Story..." --output story.mp3
  python moodcast.py --text "Test" --voice VOICE_ID --model eleven_v3 --output-format mp3_44100_128
  python moodcast.py --list-voices
        """
    )
    
    parser.add_argument("--text", "-t", help="Text to convert to speech")
    parser.add_argument("--mood", "-m", choices=list(MOOD_VOICES.keys()),
                       help="Mood preset (affects voice and emotion tags)")
    parser.add_argument("--voice", "-v", help=f"Voice ID to use (overrides mood selection; default: {DEFAULT_VOICE_ID})")
    parser.add_argument("--model", help=f"Model ID (default: {MODEL_ID}, or MOODCAST_MODEL env var)")
    parser.add_argument("--output-format", help=f"Output format (default: {OUTPUT_FORMAT}, or MOODCAST_OUTPUT_FORMAT env var)")
    parser.add_argument("--ambient", "-a", help="Generate ambient sound effect (prompt)")
    parser.add_argument("--ambient-duration", type=float, default=10.0,
                       help="Ambient sound duration in seconds (max 30)")
    parser.add_argument("--output", "-o", help="Save audio to file instead of playing")
    parser.add_argument("--no-enhance", action="store_true",
                       help="Skip automatic emotion enhancement")
    parser.add_argument("--show-enhanced", action="store_true",
                       help="Print enhanced text before generating")
    parser.add_argument("--list-voices", action="store_true",
                       help="List available voices")
    
    args = parser.parse_args()
    
    client = get_client()
    
    if args.list_voices:
        list_voices(client)
        return
    
    if not args.text:
        parser.print_help()
        print("\nError: --text is required")
        sys.exit(1)
    
    voice_id = args.voice or (MOOD_VOICES.get(args.mood) if args.mood else None) or DEFAULT_VOICE_ID
    model_id = args.model or MODEL_ID
    output_format = args.output_format or OUTPUT_FORMAT
    
    text = args.text
    if not args.no_enhance:
        text = enhance_text_with_emotions(text, args.mood)
    
    if args.show_enhanced:
        print(f"\nEnhanced text:\n{text}\n")
    
    chunks = split_text_for_api(text)
    if len(chunks) > 1:
        print(f"Text split into {len(chunks)} chunks")
    
    print(f"Generating expressive audio...")
    all_audio = b""
    
    for i, chunk in enumerate(chunks):
        if len(chunks) > 1:
            print(f"   Processing chunk {i+1}/{len(chunks)}...")
        audio_bytes = generate_speech(client, chunk, voice_id, model_id, output_format, None)
        all_audio += audio_bytes
    
    ambient_audio = b""
    if args.ambient:
        print(f"Generating ambient soundscape...")
        ambient_prompt = args.ambient
        ambient_audio = generate_sound_effect(
            client, 
            ambient_prompt, 
            min(args.ambient_duration, 30.0)
        )
    elif args.mood and os.environ.get("MOODCAST_AUTO_AMBIENT"):
        print(f"Generating mood-matched ambient...")
        ambient_prompt = AMBIENT_PRESETS.get(args.mood, AMBIENT_PRESETS["default"])
        ambient_audio = generate_sound_effect(client, ambient_prompt, 15.0)
    
    if args.output:
        with open(args.output, "wb") as f:
            f.write(all_audio)
        print(f"Speech saved to: {args.output}")
        
        if ambient_audio:
            ambient_path = args.output.replace(".mp3", "_ambient.mp3")
            with open(ambient_path, "wb") as f:
                f.write(ambient_audio)
            print(f"Ambient saved to: {ambient_path}")
    else:
        print("Playing audio...")
        play_audio(all_audio)
        
        if ambient_audio:
            print("Playing ambient...")
            play_audio(ambient_audio)
    
    print("\nMoodCast complete!")


if __name__ == "__main__":
    main()
