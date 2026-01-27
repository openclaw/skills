#!/usr/bin/env python3
"""
ElevenLabs Voice Design - Create Custom Voices from Text Description

Generate unique AI voices using ElevenLabs Voice Design API.
Describe the voice you want and get a preview, then optionally save it to your account.

Usage:
    python3 voice-design.py --gender female --age middle_aged --accent american --description "A warm, motherly voice with a gentle tone"
    python3 voice-design.py --gender male --age young --accent british --description "Energetic narrator" --save "MyNarrator"

API Documentation: https://elevenlabs.io/docs/api-reference/voice-generation
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent

# ElevenLabs Voice Design API
VOICE_DESIGN_URL = "https://api.elevenlabs.io/v1/voice-generation/generate-voice"
VOICE_PREVIEW_URL = "https://api.elevenlabs.io/v1/voice-generation/generate-voice/preview"

# Valid options for voice design
VALID_GENDERS = ["male", "female", "neutral"]
VALID_AGES = ["young", "middle_aged", "old"]
VALID_ACCENTS = [
    "american", "british", "african", "australian", "indian",
    "latin", "middle_eastern", "scandinavian", "eastern_european"
]

# Sample texts for preview
PREVIEW_TEXTS = {
    "en": "Hello! This is a preview of my voice. I can speak naturally and expressively, adapting my tone to match any content you need.",
    "professional": "Welcome to our quarterly business review. Today, I'll be presenting our key achievements and strategic initiatives for the upcoming fiscal year.",
    "storytelling": "Once upon a time, in a land far, far away, there lived a curious young adventurer who dreamed of discovering the world's greatest mysteries.",
    "casual": "Hey there! Just checking in to see how you're doing. Hope you're having an awesome day! Let me know if you need anything.",
}


def get_api_key() -> str:
    """Get API key from environment or Clawdbot config."""
    api_key = os.environ.get("ELEVEN_API_KEY") or os.environ.get("ELEVENLABS_API_KEY")
    if api_key:
        return api_key
    
    config_paths = [
        Path.home() / ".clawdbot" / "clawdbot.json",
        Path("/root/.clawdbot/clawdbot.json"),
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text())
                api_key = config.get("tts", {}).get("elevenlabs", {}).get("apiKey")
                if api_key:
                    return api_key
            except Exception:
                continue
    
    env_file = SKILL_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("ELEVEN_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"\'')
    
    print("❌ No ElevenLabs API key found.")
    sys.exit(1)


def generate_voice_preview(
    gender: str,
    age: str,
    accent: str,
    accent_strength: float,
    description: str,
    preview_text: str,
    output_path: str,
    api_key: str
) -> dict:
    """
    Generate a preview of a designed voice.
    
    Returns generated_voice_id if successful.
    """
    # Validate inputs
    if gender not in VALID_GENDERS:
        print(f"❌ Invalid gender: {gender}")
        print(f"   Valid options: {', '.join(VALID_GENDERS)}")
        return None
    
    if age not in VALID_AGES:
        print(f"❌ Invalid age: {age}")
        print(f"   Valid options: {', '.join(VALID_AGES)}")
        return None
    
    if accent not in VALID_ACCENTS:
        print(f"❌ Invalid accent: {accent}")
        print(f"   Valid options: {', '.join(VALID_ACCENTS)}")
        return None
    
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    
    payload = {
        "gender": gender,
        "age": age,
        "accent": accent,
        "accent_strength": max(0.3, min(2.0, accent_strength)),
        "text": preview_text
    }
    
    # Add description if provided
    if description:
        payload["text"] = f"{description}\n\n{preview_text}"
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(VOICE_DESIGN_URL, data=data, headers=headers, method="POST")
    
    print(f"🎨 Designing voice...")
    print(f"   Gender: {gender}")
    print(f"   Age: {age}")
    print(f"   Accent: {accent} (strength: {accent_strength})")
    if description:
        print(f"   Description: {description[:50]}...")
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            # Response includes audio and voice ID
            content_type = response.headers.get("Content-Type", "")
            
            if "audio" in content_type:
                audio_data = response.read()
                with open(output_path, "wb") as f:
                    f.write(audio_data)
                print(f"✅ Preview saved: {output_path}")
                
                # Try to get voice ID from header
                voice_id = response.headers.get("generated_voice_id")
                return {"voice_id": voice_id, "audio_saved": True}
            else:
                result = json.loads(response.read().decode("utf-8"))
                
                # Save audio if included
                if "audio_base64" in result:
                    import base64
                    audio_data = base64.b64decode(result["audio_base64"])
                    with open(output_path, "wb") as f:
                        f.write(audio_data)
                    print(f"✅ Preview saved: {output_path}")
                
                return result
                
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"❌ API Error ({e.code}): {error_body[:300]}")
        return None
    except urllib.error.URLError as e:
        print(f"❌ Network Error: {e.reason}")
        return None


def save_voice_to_library(voice_id: str, name: str, description: str, api_key: str) -> bool:
    """
    Save a generated voice preview to your ElevenLabs voice library.
    
    Note: This requires the voice_id from a preview generation.
    """
    url = f"https://api.elevenlabs.io/v1/voice-generation/create-voice"
    
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    
    payload = {
        "voice_name": name,
        "voice_description": description or f"Custom voice: {name}",
        "generated_voice_id": voice_id,
        "labels": {"type": "designed", "source": "clawdbot-skill"}
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            saved_voice_id = result.get("voice_id")
            print(f"✅ Voice saved to library!")
            print(f"   Name: {name}")
            print(f"   Voice ID: {saved_voice_id}")
            print(f"\n💡 Add this to voices.json to use with tts.py:")
            print(f'''
    "{name.lower().replace(' ', '_')}": {{
      "voice_id": "{saved_voice_id}",
      "name": "{name}",
      "language": "en-US",
      "gender": "custom",
      "persona": "designed",
      "description": "{description or 'Custom designed voice'}",
      "settings": {{ "stability": 0.75, "similarity_boost": 0.75, "style": 0.5 }}
    }}
''')
            return True
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"❌ Save Error ({e.code}): {error_body[:200]}")
        return False
    except urllib.error.URLError as e:
        print(f"❌ Network Error: {e.reason}")
        return False


def list_options():
    """Display all valid voice design options."""
    print("🎨 Voice Design Options\n")
    
    print("Gender:")
    for g in VALID_GENDERS:
        print(f"  • {g}")
    
    print("\nAge:")
    for a in VALID_AGES:
        print(f"  • {a}")
    
    print("\nAccent:")
    for a in VALID_ACCENTS:
        print(f"  • {a}")
    
    print("\nAccent Strength: 0.3 - 2.0 (default: 1.0)")
    print("  • 0.3-0.7: Subtle accent")
    print("  • 0.8-1.2: Moderate accent")
    print("  • 1.3-2.0: Strong accent")
    
    print("\nPreview Text Styles:")
    for style, text in PREVIEW_TEXTS.items():
        print(f"  • {style}: {text[:50]}...")


def main():
    parser = argparse.ArgumentParser(
        description="ElevenLabs Voice Design - Create Custom Voices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a preview
  python3 voice-design.py --gender female --age middle_aged --accent american \\
    --description "A warm, motherly voice"
  
  # With custom preview text
  python3 voice-design.py --gender male --age young --accent british \\
    --text "Welcome to the adventure!"
  
  # Save to your library
  python3 voice-design.py --gender female --age young --accent american \\
    --description "Energetic host" --save "MyHost"
  
  # List all options
  python3 voice-design.py --options
        """
    )
    
    # Voice characteristics
    parser.add_argument("--gender", "-g", default="female", 
                       help=f"Gender ({', '.join(VALID_GENDERS)})")
    parser.add_argument("--age", "-a", default="middle_aged",
                       help=f"Age ({', '.join(VALID_AGES)})")
    parser.add_argument("--accent", "-c", default="american",
                       help=f"Accent ({', '.join(VALID_ACCENTS)})")
    parser.add_argument("--accent-strength", "-s", type=float, default=1.0,
                       help="Accent strength (0.3-2.0, default: 1.0)")
    
    # Description and text
    parser.add_argument("--description", "-d", default="",
                       help="Voice description (characteristics, tone, personality)")
    parser.add_argument("--text", "-t", help="Custom preview text")
    parser.add_argument("--style", choices=list(PREVIEW_TEXTS.keys()), default="en",
                       help="Preview text style (default: en)")
    
    # Output
    parser.add_argument("--output", "-o", default="voice_preview.mp3",
                       help="Output file (default: voice_preview.mp3)")
    
    # Save to library
    parser.add_argument("--save", metavar="NAME",
                       help="Save voice to ElevenLabs library with this name")
    
    # Info
    parser.add_argument("--options", action="store_true",
                       help="List all valid options")
    
    args = parser.parse_args()
    
    if args.options:
        list_options()
        return
    
    api_key = get_api_key()
    
    # Determine preview text
    preview_text = args.text or PREVIEW_TEXTS.get(args.style, PREVIEW_TEXTS["en"])
    
    # Generate preview
    result = generate_voice_preview(
        args.gender,
        args.age,
        args.accent,
        args.accent_strength,
        args.description,
        preview_text,
        args.output,
        api_key
    )
    
    if not result:
        sys.exit(1)
    
    # Save to library if requested
    if args.save:
        voice_id = result.get("voice_id") or result.get("generated_voice_id")
        if voice_id:
            save_voice_to_library(
                voice_id,
                args.save,
                args.description,
                api_key
            )
        else:
            print("⚠️  Could not save: No voice ID returned from preview")
            print("   Try generating again and using --save with the resulting ID")


if __name__ == "__main__":
    main()
