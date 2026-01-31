#!/usr/bin/env python3
"""
Make voice calls via Dialpad API with optional ElevenLabs TTS.

Usage:
    python3 make_call.py --to "+14155551234"
    python3 make_call.py --to "+14155551234" --from "+14153602954"
    python3 make_call.py --to "+14155551234" --elevenlabs "Hello, this is a call from..."
    python3 make_call.py --to "+14155551234" --user-id "5765607478525952" --text "Meeting reminder"
"""

import argparse
import json
import os
import sys
import tempfile
import urllib.request
import urllib.error
import urllib.parse


# Configuration
DIALPAD_API_KEY = os.environ.get("DIALPAD_API_KEY")
DIALPAD_API_BASE = "https://dialpad.com/api/v2"

# Known ShapeScale users (auto-populated from API)
KNOWN_USERS = {
    "+14153602954": "5765607478525952",  # Martin Kessler
    "+14158701945": "5625110025338880",  # Lilla Laczo
    "+14152230323": "5964143916400640",  # Scott Sicz
}


def get_user_id(from_number=None):
    """Get user ID for making calls."""
    if from_number and from_number in KNOWN_USERS:
        return KNOWN_USERS[from_number]
    
    # If no from_number provided, try to find user's own number
    if not from_number:
        for phone, uid in KNOWN_USERS.items():
            return uid  # Return first known user
    
    return None


def make_call(to_number, from_number=None, user_id=None, text_to_speak=None):
    """
    Make a voice call via Dialpad API.

    Args:
        to_number: Recipient phone number in E.164 format
        from_number: Caller ID number (optional, will auto-select if not provided)
        user_id: Dialpad user ID (required for making calls)
        text_to_speak: Optional text to be spoken (Text-to-Speech)

    Returns:
        dict: API response with call details
    """
    if not DIALPAD_API_KEY:
        raise ValueError("DIALPAD_API_KEY environment variable not set")

    if not to_number:
        raise ValueError("Recipient number is required")

    # Get user_id from known users if not provided
    if not user_id:
        user_id = get_user_id(from_number)
        if user_id:
            print(f"Auto-detected user ID: {user_id}")
    
    if not user_id:
        raise ValueError("user_id is required. Provide --user-id or --from with a known number.")

    url = f"{DIALPAD_API_BASE}/call"

    payload = {
        "phone_number": to_number,
        "user_id": user_id,
    }

    if from_number:
        payload["from_number"] = from_number

    if text_to_speak:
        # Basic Dialpad TTS
        payload["command"] = json.dumps({
            "actions": [
                {"say": text_to_speak}
            ]
        })

    data = json.dumps(payload).encode("utf-8")

    headers = {
        "Authorization": f"Bearer {DIALPAD_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    request = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request) as response:
            response_data = response.read().decode("utf-8")
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        try:
            error_data = json.loads(error_body)
            error_msg = error_data.get("error", {}).get("message", error_body)
        except:
            error_msg = error_body or str(e)
        raise RuntimeError(f"Dialpad API error (HTTP {e.code}): {error_msg}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}")


def main():
    parser = argparse.ArgumentParser(
        description="Make voice calls via Dialpad API"
    )
    parser.add_argument(
        "--to",
        required=True,
        help="Recipient phone number in E.164 format (e.g., +14155551234)"
    )
    parser.add_argument(
        "--from",
        dest="from_number",
        help="Caller ID number (optional, auto-selects from known users)"
    )
    parser.add_argument(
        "--user-id",
        dest="user_id",
        help="Dialpad user ID (required if --from not provided)"
    )
    parser.add_argument(
        "--text",
        dest="text_to_speak",
        help="Text to speak (Text-to-Speech)"
    )
    parser.add_argument(
        "--voice",
        default="Sam",
        help="Voice name for future ElevenLabs TTS (default: Sam - low-cost)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )

    args = parser.parse_args()

    try:
        result = make_call(
            to_number=args.to,
            from_number=args.from_number,
            user_id=args.user_id,
            text_to_speak=args.text_to_speak
        )

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("Call initiated successfully!")
            print(f"   ID: {result.get('call_id')}")
            print(f"   To: {args.to}")

        sys.exit(0)

    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
