#!/usr/bin/env python3
"""
ElevenLabs TTS Script - Text to Speech with Voice Personas v2.0.0

Features:
- 18 voice personas with presets
- 32 language support
- Streaming audio output
- Batch processing
- Cost tracking
- Pronunciation dictionary support

Usage:
    python3 tts.py --text "Hello world" --voice rachel
    python3 tts.py --text "Hallo Welt" --voice rachel --lang de
    python3 tts.py --text "Hello" --voice rachel --stream
    python3 tts.py --batch input.txt --voice rachel
    python3 tts.py --stats
    python3 tts.py --list
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import time
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
VOICES_FILE = SKILL_DIR / "voices.json"
PRONUNCIATIONS_FILE = SKILL_DIR / "pronunciations.json"
USAGE_FILE = SKILL_DIR / ".usage.json"

# ElevenLabs API
API_URL = "https://api.elevenlabs.io/v1/text-to-speech"
STREAM_URL = "https://api.elevenlabs.io/v1/text-to-speech"

# Supported languages (32 languages)
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "code": "en"},
    "de": {"name": "German", "code": "de"},
    "es": {"name": "Spanish", "code": "es"},
    "fr": {"name": "French", "code": "fr"},
    "it": {"name": "Italian", "code": "it"},
    "pt": {"name": "Portuguese", "code": "pt"},
    "pl": {"name": "Polish", "code": "pl"},
    "nl": {"name": "Dutch", "code": "nl"},
    "sv": {"name": "Swedish", "code": "sv"},
    "da": {"name": "Danish", "code": "da"},
    "fi": {"name": "Finnish", "code": "fi"},
    "no": {"name": "Norwegian", "code": "no"},
    "tr": {"name": "Turkish", "code": "tr"},
    "ru": {"name": "Russian", "code": "ru"},
    "uk": {"name": "Ukrainian", "code": "uk"},
    "cs": {"name": "Czech", "code": "cs"},
    "sk": {"name": "Slovak", "code": "sk"},
    "hu": {"name": "Hungarian", "code": "hu"},
    "ro": {"name": "Romanian", "code": "ro"},
    "bg": {"name": "Bulgarian", "code": "bg"},
    "hr": {"name": "Croatian", "code": "hr"},
    "el": {"name": "Greek", "code": "el"},
    "hi": {"name": "Hindi", "code": "hi"},
    "ta": {"name": "Tamil", "code": "ta"},
    "id": {"name": "Indonesian", "code": "id"},
    "ms": {"name": "Malay", "code": "ms"},
    "vi": {"name": "Vietnamese", "code": "vi"},
    "th": {"name": "Thai", "code": "th"},
    "ja": {"name": "Japanese", "code": "ja"},
    "ko": {"name": "Korean", "code": "ko"},
    "zh": {"name": "Chinese", "code": "zh"},
    "ar": {"name": "Arabic", "code": "ar"},
}

# ElevenLabs pricing (per 1000 characters)
PRICING = {
    "starter": 0.30,  # $0.30 per 1000 chars
    "creator": 0.24,
    "pro": 0.18,
    "scale": 0.11,
}


def load_voices() -> dict:
    """Load voice configurations from voices.json."""
    if not VOICES_FILE.exists():
        print(f"❌ voices.json not found at {VOICES_FILE}")
        sys.exit(1)
    return json.loads(VOICES_FILE.read_text())


def load_pronunciations() -> dict:
    """Load custom pronunciation rules."""
    if not PRONUNCIATIONS_FILE.exists():
        return {"rules": [], "phonemes": {}}
    try:
        return json.loads(PRONUNCIATIONS_FILE.read_text())
    except Exception:
        return {"rules": [], "phonemes": {}}


def apply_pronunciations(text: str, pronunciations: dict) -> str:
    """Apply pronunciation rules to text."""
    rules = pronunciations.get("rules", [])
    for rule in rules:
        word = rule.get("word", "")
        replacement = rule.get("replacement", "")
        if word and replacement:
            # Case-insensitive replacement
            import re
            text = re.sub(re.escape(word), replacement, text, flags=re.IGNORECASE)
    return text


def load_usage() -> dict:
    """Load usage statistics."""
    if not USAGE_FILE.exists():
        return {
            "total_characters": 0,
            "total_requests": 0,
            "sessions": [],
            "last_reset": datetime.now().isoformat()
        }
    try:
        return json.loads(USAGE_FILE.read_text())
    except Exception:
        return {
            "total_characters": 0,
            "total_requests": 0,
            "sessions": [],
            "last_reset": datetime.now().isoformat()
        }


def save_usage(usage: dict):
    """Save usage statistics."""
    USAGE_FILE.write_text(json.dumps(usage, indent=2))


def track_usage(chars: int, voice: str):
    """Track character usage."""
    usage = load_usage()
    usage["total_characters"] += chars
    usage["total_requests"] += 1
    
    # Add session entry
    session = {
        "timestamp": datetime.now().isoformat(),
        "characters": chars,
        "voice": voice
    }
    usage["sessions"].append(session)
    
    # Keep only last 1000 sessions
    if len(usage["sessions"]) > 1000:
        usage["sessions"] = usage["sessions"][-1000:]
    
    save_usage(usage)


def show_stats():
    """Display usage statistics."""
    usage = load_usage()
    
    total_chars = usage.get("total_characters", 0)
    total_requests = usage.get("total_requests", 0)
    last_reset = usage.get("last_reset", "Unknown")
    
    print("📊 ElevenLabs Usage Statistics\n")
    print(f"  Total Characters: {total_chars:,}")
    print(f"  Total Requests:   {total_requests:,}")
    print(f"  Since:            {last_reset[:10]}")
    print()
    
    # Estimated costs
    print("💰 Estimated Costs:")
    for plan, rate in PRICING.items():
        cost = (total_chars / 1000) * rate
        print(f"  {plan.capitalize():<10} ${cost:.2f} (${rate}/1k chars)")
    
    # Recent sessions
    sessions = usage.get("sessions", [])[-10:]
    if sessions:
        print("\n📜 Recent Sessions:")
        for s in reversed(sessions):
            ts = s.get("timestamp", "")[:16].replace("T", " ")
            chars = s.get("characters", 0)
            voice = s.get("voice", "unknown")
            print(f"  {ts} | {chars:>6} chars | {voice}")


def reset_stats():
    """Reset usage statistics."""
    usage = {
        "total_characters": 0,
        "total_requests": 0,
        "sessions": [],
        "last_reset": datetime.now().isoformat()
    }
    save_usage(usage)
    print("✅ Usage statistics reset.")


def get_api_key() -> str:
    """Get API key from environment or Clawdbot config."""
    # Try environment first
    api_key = os.environ.get("ELEVEN_API_KEY") or os.environ.get("ELEVENLABS_API_KEY")
    if api_key:
        return api_key
    
    # Try Clawdbot config (multiple possible locations)
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
    
    # Try skill-local .env file
    env_file = SKILL_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("ELEVEN_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"\'')
    
    print("❌ No ElevenLabs API key found.")
    print("   Options:")
    print("   1. Set ELEVEN_API_KEY environment variable")
    print("   2. Configure in Clawdbot (tts.elevenlabs.apiKey)")
    print("   3. Create .env file in skill directory")
    sys.exit(1)


def list_voices(voices_data: dict):
    """List all available voices."""
    voices = voices_data.get("voices", {})
    presets = voices_data.get("presets", {})
    
    print("🎙️  Available Voices\n")
    print(f"{'Name':<15} {'Language':<10} {'Gender':<8} {'Persona':<15} Description")
    print("-" * 80)
    
    for name, v in sorted(voices.items()):
        print(f"{name:<15} {v.get('language', 'n/a'):<10} {v.get('gender', 'n/a'):<8} {v.get('persona', 'n/a'):<15} {v.get('description', '')[:40]}...")
    
    print(f"\n📋 Presets: {', '.join(presets.keys())}")


def list_languages():
    """List all supported languages."""
    print("🌍 Supported Languages (32)\n")
    print(f"{'Code':<6} {'Language':<15}")
    print("-" * 25)
    for code, info in sorted(SUPPORTED_LANGUAGES.items()):
        print(f"{code:<6} {info['name']:<15}")


def synthesize(
    text: str, 
    voice_name: str, 
    output_path: str, 
    voices_data: dict, 
    api_key: str,
    language: str = None,
    stream: bool = False,
    pronunciations: dict = None
) -> bool:
    """Synthesize text to speech."""
    voices = voices_data.get("voices", {})
    
    if voice_name not in voices:
        # Check if it's a preset
        presets = voices_data.get("presets", {})
        if voice_name in presets:
            voice_name = presets[voice_name]
        else:
            print(f"❌ Voice '{voice_name}' not found.")
            print(f"   Available: {', '.join(voices.keys())}")
            return False
    
    voice = voices[voice_name]
    voice_id = voice["voice_id"]
    settings = voice.get("settings", {})
    
    # Apply pronunciation rules
    if pronunciations:
        text = apply_pronunciations(text, pronunciations)
    
    # Build language instruction if specified
    if language and language != "en":
        lang_info = SUPPORTED_LANGUAGES.get(language, {})
        if lang_info:
            # Multilingual model handles this via the text itself
            pass
    
    # Prepare request
    url = f"{API_URL}/{voice_id}"
    if stream:
        url += "/stream"
    
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": settings.get("stability", 0.75),
            "similarity_boost": settings.get("similarity_boost", 0.75),
            "style": settings.get("style", 0.5),
            "use_speaker_boost": True
        }
    }
    
    # Add language hint if specified
    if language:
        payload["language_code"] = language
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        if stream:
            # Streaming mode - write chunks as they arrive
            with urllib.request.urlopen(req, timeout=60) as response:
                with open(output_path, "wb") as f:
                    total_bytes = 0
                    while True:
                        chunk = response.read(4096)
                        if not chunk:
                            break
                        f.write(chunk)
                        total_bytes += len(chunk)
                        print(f"\r⏳ Streaming: {total_bytes / 1024:.1f} KB", end="", flush=True)
                    print()
                print(f"✅ Saved: {output_path} ({total_bytes / 1024:.1f} KB)")
        else:
            with urllib.request.urlopen(req, timeout=30) as response:
                audio_data = response.read()
                
                # Write to file
                with open(output_path, "wb") as f:
                    f.write(audio_data)
                
                print(f"✅ Saved: {output_path} ({len(audio_data) / 1024:.1f} KB)")
        
        # Track usage
        track_usage(len(text), voice_name)
        return True
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"❌ API Error ({e.code}): {error_body[:200]}")
        return False
    except urllib.error.URLError as e:
        print(f"❌ Network Error: {e.reason}")
        return False


def process_batch(
    batch_file: str,
    voice_name: str,
    output_dir: str,
    voices_data: dict,
    api_key: str,
    language: str = None,
    pronunciations: dict = None
) -> tuple:
    """Process batch of texts from file."""
    batch_path = Path(batch_file)
    if not batch_path.exists():
        print(f"❌ Batch file not found: {batch_file}")
        return 0, 0
    
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    content = batch_path.read_text()
    
    # Try to parse as JSON first
    texts = []
    try:
        data = json.loads(content)
        if isinstance(data, list):
            texts = data
        elif isinstance(data, dict) and "texts" in data:
            texts = data["texts"]
    except json.JSONDecodeError:
        # Treat as newline-separated text
        texts = [line.strip() for line in content.splitlines() if line.strip()]
    
    if not texts:
        print("❌ No texts found in batch file")
        return 0, 0
    
    print(f"📦 Processing batch: {len(texts)} items\n")
    
    success = 0
    failed = 0
    
    for i, text in enumerate(texts, 1):
        # Handle dict entries with custom voice/output
        if isinstance(text, dict):
            t = text.get("text", "")
            v = text.get("voice", voice_name)
            o = text.get("output", f"output_{i:04d}.mp3")
        else:
            t = str(text)
            v = voice_name
            o = f"output_{i:04d}.mp3"
        
        output_file = out_path / o
        print(f"  [{i}/{len(texts)}] Processing: {t[:50]}...")
        
        if synthesize(t, v, str(output_file), voices_data, api_key, language, False, pronunciations):
            success += 1
        else:
            failed += 1
        
        # Rate limiting
        time.sleep(0.5)
    
    print(f"\n✅ Complete: {success} success, {failed} failed")
    print(f"📁 Output: {out_path}")
    return success, failed


def test_voices(voices_data: dict, api_key: str):
    """Test all voices with sample text."""
    voices = voices_data.get("voices", {})
    output_dir = SKILL_DIR / "samples"
    output_dir.mkdir(exist_ok=True)
    
    test_texts = {
        "en": "Hello! This is a test of the ElevenLabs voice synthesis.",
        "de": "Hallo! Dies ist ein Test der ElevenLabs Sprachsynthese.",
        "es": "¡Hola! Esta es una prueba de la síntesis de voz de ElevenLabs.",
        "fr": "Bonjour! Ceci est un test de la synthèse vocale ElevenLabs.",
        "it": "Ciao! Questo è un test della sintesi vocale ElevenLabs."
    }
    
    print("🧪 Testing all voices...\n")
    
    success = 0
    failed = 0
    
    for name, v in voices.items():
        lang = v.get("language", "en-US")[:2]
        text = test_texts.get(lang, test_texts["en"])
        output = output_dir / f"{name}.mp3"
        
        print(f"  Testing {name}...", end=" ", flush=True)
        if synthesize(text, name, str(output), voices_data, api_key):
            success += 1
        else:
            failed += 1
    
    print(f"\n✅ Success: {success}, ❌ Failed: {failed}")
    print(f"📁 Samples saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="ElevenLabs TTS with Voice Personas v2.0.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tts.py --text "Hello world" --voice rachel
  python3 tts.py --text "Bonjour" --voice rachel --lang fr
  python3 tts.py --text "Hello" --voice rachel --stream
  python3 tts.py --batch texts.txt --voice adam --output-dir ./audio
  python3 tts.py --stats
  python3 tts.py --languages
        """
    )
    
    # Input options
    parser.add_argument("--text", "-t", help="Text to synthesize")
    parser.add_argument("--batch", "-b", help="Batch file (JSON or newline-separated)")
    
    # Voice options
    parser.add_argument("--voice", "-v", default="rachel", help="Voice name or preset (default: rachel)")
    parser.add_argument("--lang", "-L", help="Language code (e.g., de, fr, es)")
    
    # Output options
    parser.add_argument("--output", "-o", default="output.mp3", help="Output file (default: output.mp3)")
    parser.add_argument("--output-dir", "-d", default="./batch_output", help="Output directory for batch mode")
    parser.add_argument("--stream", "-s", action="store_true", help="Use streaming mode")
    
    # Info options
    parser.add_argument("--list", "-l", action="store_true", help="List available voices")
    parser.add_argument("--languages", action="store_true", help="List supported languages")
    parser.add_argument("--test", action="store_true", help="Test all voices")
    
    # Usage tracking
    parser.add_argument("--stats", action="store_true", help="Show usage statistics")
    parser.add_argument("--reset-stats", action="store_true", help="Reset usage statistics")
    
    # Advanced
    parser.add_argument("--no-pronunciations", action="store_true", help="Disable pronunciation dictionary")
    
    args = parser.parse_args()
    
    voices_data = load_voices()
    
    # Info commands
    if args.list:
        list_voices(voices_data)
        return
    
    if args.languages:
        list_languages()
        return
    
    if args.stats:
        show_stats()
        return
    
    if args.reset_stats:
        reset_stats()
        return
    
    # Commands requiring API key
    api_key = get_api_key()
    
    if args.test:
        test_voices(voices_data, api_key)
        return
    
    # Load pronunciations unless disabled
    pronunciations = None if args.no_pronunciations else load_pronunciations()
    
    # Batch mode
    if args.batch:
        process_batch(
            args.batch,
            args.voice,
            args.output_dir,
            voices_data,
            api_key,
            args.lang,
            pronunciations
        )
        return
    
    # Single synthesis
    if not args.text:
        parser.print_help()
        print("\n❌ --text or --batch is required for synthesis")
        sys.exit(1)
    
    synthesize(
        args.text,
        args.voice,
        args.output,
        voices_data,
        api_key,
        args.lang,
        args.stream,
        pronunciations
    )


if __name__ == "__main__":
    main()
