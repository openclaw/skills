#!/usr/bin/env python3
"""
ElevenLabs Sound Effects (SFX) Generator

Generate AI-powered sound effects using ElevenLabs Sound Generation API.

Usage:
    python3 sfx.py --prompt "Thunder rumbling in the distance"
    python3 sfx.py --prompt "Cat meowing" --duration 3
    python3 sfx.py --prompt "Footsteps on gravel" --output footsteps.mp3

API Documentation: https://elevenlabs.io/docs/api-reference/sound-generation
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
USAGE_FILE = SKILL_DIR / ".usage.json"

# ElevenLabs Sound Generation API
SFX_API_URL = "https://api.elevenlabs.io/v1/sound-generation"


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
    print("   Set ELEVEN_API_KEY environment variable or configure in Clawdbot")
    sys.exit(1)


def load_usage() -> dict:
    """Load usage statistics."""
    if not USAGE_FILE.exists():
        return {"sfx_requests": 0, "sfx_seconds": 0}
    try:
        return json.loads(USAGE_FILE.read_text())
    except Exception:
        return {"sfx_requests": 0, "sfx_seconds": 0}


def save_usage(usage: dict):
    """Save usage statistics."""
    USAGE_FILE.write_text(json.dumps(usage, indent=2))


def track_sfx_usage(duration: float, prompt: str):
    """Track SFX usage."""
    usage = load_usage()
    usage["sfx_requests"] = usage.get("sfx_requests", 0) + 1
    usage["sfx_seconds"] = usage.get("sfx_seconds", 0) + duration
    
    # Add SFX session entry
    if "sfx_sessions" not in usage:
        usage["sfx_sessions"] = []
    
    usage["sfx_sessions"].append({
        "timestamp": datetime.now().isoformat(),
        "duration": duration,
        "prompt": prompt[:100]
    })
    
    # Keep only last 100 SFX sessions
    if len(usage["sfx_sessions"]) > 100:
        usage["sfx_sessions"] = usage["sfx_sessions"][-100:]
    
    save_usage(usage)


def generate_sfx(
    prompt: str,
    output_path: str,
    duration: float = None,
    prompt_influence: float = 0.3,
    api_key: str = None
) -> bool:
    """
    Generate a sound effect from a text prompt.
    
    Args:
        prompt: Text description of the desired sound effect
        output_path: Where to save the generated audio
        duration: Duration in seconds (0.5 to 22, optional - AI decides if not set)
        prompt_influence: How closely to follow the prompt (0.0-1.0)
        api_key: ElevenLabs API key
    
    Returns:
        True if successful, False otherwise
    """
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    
    payload = {
        "text": prompt,
        "prompt_influence": prompt_influence
    }
    
    if duration is not None:
        # Clamp duration to valid range
        duration = max(0.5, min(22.0, duration))
        payload["duration_seconds"] = duration
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(SFX_API_URL, data=data, headers=headers, method="POST")
    
    try:
        print(f"🎵 Generating: {prompt}")
        if duration:
            print(f"   Duration: {duration}s")
        
        with urllib.request.urlopen(req, timeout=60) as response:
            audio_data = response.read()
            
            with open(output_path, "wb") as f:
                f.write(audio_data)
            
            size_kb = len(audio_data) / 1024
            print(f"✅ Saved: {output_path} ({size_kb:.1f} KB)")
            
            # Track usage (estimate duration if not specified)
            actual_duration = duration or 5.0
            track_sfx_usage(actual_duration, prompt)
            
            return True
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"❌ API Error ({e.code}): {error_body[:200]}")
        return False
    except urllib.error.URLError as e:
        print(f"❌ Network Error: {e.reason}")
        return False


def batch_sfx(batch_file: str, output_dir: str, api_key: str) -> tuple:
    """
    Generate multiple sound effects from a batch file.
    
    Batch file format (JSON):
    [
        {"prompt": "Thunder rumbling", "duration": 5, "output": "thunder.mp3"},
        {"prompt": "Rain on window", "output": "rain.mp3"}
    ]
    
    Or newline-separated prompts (one per line).
    """
    batch_path = Path(batch_file)
    if not batch_path.exists():
        print(f"❌ Batch file not found: {batch_file}")
        return 0, 0
    
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    content = batch_path.read_text()
    
    items = []
    try:
        data = json.loads(content)
        if isinstance(data, list):
            items = data
    except json.JSONDecodeError:
        # Treat as newline-separated prompts
        for i, line in enumerate(content.splitlines(), 1):
            line = line.strip()
            if line:
                items.append({
                    "prompt": line,
                    "output": f"sfx_{i:04d}.mp3"
                })
    
    if not items:
        print("❌ No items found in batch file")
        return 0, 0
    
    print(f"📦 Processing SFX batch: {len(items)} items\n")
    
    success = 0
    failed = 0
    
    for i, item in enumerate(items, 1):
        if isinstance(item, str):
            item = {"prompt": item, "output": f"sfx_{i:04d}.mp3"}
        
        prompt = item.get("prompt", "")
        duration = item.get("duration")
        output_name = item.get("output", f"sfx_{i:04d}.mp3")
        output_file = out_path / output_name
        
        print(f"  [{i}/{len(items)}] {prompt[:50]}...")
        
        if generate_sfx(prompt, str(output_file), duration, 0.3, api_key):
            success += 1
        else:
            failed += 1
        
        # Rate limiting
        import time
        time.sleep(1.0)
    
    print(f"\n✅ Complete: {success} success, {failed} failed")
    print(f"📁 Output: {out_path}")
    return success, failed


# Sound effect prompt examples
SFX_EXAMPLES = """
🎵 Sound Effect Prompt Examples:

Nature:
  "Thunder rumbling in the distance"
  "Heavy rain on a tin roof"
  "Wind howling through trees"
  "Ocean waves crashing on rocks"
  "Crickets chirping at night"

Urban:
  "Traffic noise in a busy city"
  "Subway train arriving at platform"
  "Doorbell ringing"
  "Phone ringing with old-fashioned bell"
  "Typing on a mechanical keyboard"

Animals:
  "Cat purring contentedly"
  "Dog barking in the distance"
  "Birds chirping at dawn"
  "Owl hooting at night"
  "Horse galloping on dirt road"

Actions:
  "Footsteps on wooden floor"
  "Door creaking open slowly"
  "Glass shattering"
  "Paper rustling"
  "Knife chopping vegetables"

Sci-Fi/Fantasy:
  "Spaceship engine humming"
  "Laser gun firing"
  "Magic spell casting with sparkles"
  "Robot walking with mechanical steps"
  "Teleportation whoosh"

Ambient:
  "Coffee shop background chatter"
  "Office ambient noise with keyboard typing"
  "Library quiet ambience"
  "Fireplace crackling"
  "Clock ticking"
"""


def main():
    parser = argparse.ArgumentParser(
        description="ElevenLabs Sound Effects Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 sfx.py --prompt "Thunder rumbling in the distance"
  python3 sfx.py --prompt "Cat meowing" --duration 3
  python3 sfx.py --prompt "Footsteps" --output steps.mp3 --influence 0.5
  python3 sfx.py --batch sounds.json --output-dir ./sfx
  python3 sfx.py --examples
        """
    )
    
    parser.add_argument("--prompt", "-p", help="Text description of the sound effect")
    parser.add_argument("--output", "-o", default="sfx_output.mp3", help="Output file (default: sfx_output.mp3)")
    parser.add_argument("--duration", "-d", type=float, help="Duration in seconds (0.5-22)")
    parser.add_argument("--influence", "-i", type=float, default=0.3, 
                       help="Prompt influence (0.0-1.0, default: 0.3)")
    parser.add_argument("--batch", "-b", help="Batch file (JSON or newline-separated prompts)")
    parser.add_argument("--output-dir", default="./sfx_output", help="Output directory for batch mode")
    parser.add_argument("--examples", "-e", action="store_true", help="Show prompt examples")
    
    args = parser.parse_args()
    
    if args.examples:
        print(SFX_EXAMPLES)
        return
    
    api_key = get_api_key()
    
    if args.batch:
        batch_sfx(args.batch, args.output_dir, api_key)
        return
    
    if not args.prompt:
        parser.print_help()
        print("\n❌ --prompt is required. Try --examples for ideas.")
        sys.exit(1)
    
    generate_sfx(
        args.prompt,
        args.output,
        args.duration,
        args.influence,
        api_key
    )


if __name__ == "__main__":
    main()
