#!/usr/bin/env python3
"""
Send SMS via Dialpad API.

Usage:
    python3 send_sms.py --to "+14155551234" --message "Hello!"
    python3 send_sms.py --to "+14155551234" "+14155555678" --message "Group message"
    python3 send_sms.py --to "+14155551234" --message "Test" --from "+14155550000"
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


# Configuration
DIALPAD_API_KEY = os.environ.get("DIALPAD_API_KEY")
DIALPAD_API_BASE = "https://dialpad.com/api/v2"


def send_sms(to_numbers, message, from_number=None, infer_country_code=False):
    """
    Send SMS via Dialpad API.

    Args:
        to_numbers: List of E.164 phone numbers (max 10)
        message: SMS text content
        from_number: Optional sender number (must be assigned to your Dialpad account)
        infer_country_code: If True, assume numbers are from sender's country

    Returns:
        dict: API response with SMS details
    """
    if not DIALPAD_API_KEY:
        raise ValueError("DIALPAD_API_KEY environment variable not set")

    if not to_numbers:
        raise ValueError("At least one recipient number is required")

    if len(to_numbers) > 10:
        raise ValueError("Maximum 10 recipients per SMS request")

    url = f"{DIALPAD_API_BASE}/sms"

    payload = {
        "to_numbers": to_numbers,
        "text": message,
        "infer_country_code": infer_country_code
    }

    if from_number:
        payload["from_number"] = from_number

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
        description="Send SMS via Dialpad API"
    )
    parser.add_argument(
        "--to",
        nargs="+",
        required=True,
        help="Recipient phone number(s) in E.164 format (e.g., +14155551234)"
    )
    parser.add_argument(
        "--message",
        required=True,
        help="SMS message content"
    )
    parser.add_argument(
        "--from",
        dest="from_number",
        help="Sender phone number (optional, must be assigned to your Dialpad account)"
    )
    parser.add_argument(
        "--infer-country-code",
        action="store_true",
        help="Assume recipient numbers are from sender's country"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )

    args = parser.parse_args()

    try:
        result = send_sms(
            to_numbers=args.to,
            message=args.message,
            from_number=args.from_number,
            infer_country_code=args.infer_country_code
        )

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("SMS sent successfully!")
            print(f"   ID: {result.get('id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   To: {', '.join(result.get('to_numbers', []))}")

        sys.exit(0)

    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
