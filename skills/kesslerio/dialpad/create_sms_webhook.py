#!/usr/bin/env python3
"""
Create SMS webhook subscription via Dialpad API.

Usage:
    python3 create_sms_webhook.py --url "https://your-server.com/webhook/dialpad"
    python3 create_sms_webhook.py --url "https://your-server.com/webhook/dialpad" --events "sms_sent,sms_received"
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


def create_sms_subscription(webhook_url, events=None, office_id=None, direction="all"):
    """
    Create an SMS webhook subscription.

    Args:
        webhook_url: URL to receive webhook events
        events: Comma-separated list of events (default: all SMS events)
        office_id: Optional office ID to filter events
        direction: Direction filter (all, inbound, outbound)

    Returns:
        dict: API response with subscription details
    """
    if not DIALPAD_API_KEY:
        raise ValueError("DIALPAD_API_KEY environment variable not set")

    # Create webhook first
    webhook_url_api = f"{DIALPAD_API_BASE}/webhooks"

    webhook_payload = {
        "hook_url": webhook_url,
    }

    data = json.dumps(webhook_payload).encode("utf-8")

    headers = {
        "Authorization": f"Bearer {DIALPAD_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    request = urllib.request.Request(webhook_url_api, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request) as response:
            response_data = response.read().decode("utf-8")
            webhook = json.loads(response_data)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        raise RuntimeError(f"Dialpad API error (HTTP {e.code}): {error_body}")

    webhook_id = webhook.get("id")

    # Subscribe to SMS events
    subscription_url = f"{DIALPAD_API_BASE}/subscriptions/sms"

    subscription_payload = {
        "webhook_id": webhook_id,
        "event_types": events.split(",") if events else ["sms_sent", "sms_received"],
        "direction": direction,
    }

    if office_id:
        subscription_payload["office_id"] = office_id

    data = json.dumps(subscription_payload).encode("utf-8")
    request = urllib.request.Request(subscription_url, data=data, headers=headers, method="POST")

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


def list_subscriptions():
    """List all SMS webhook subscriptions."""
    if not DIALPAD_API_KEY:
        raise ValueError("DIALPAD_API_KEY environment variable not set")

    url = f"{DIALPAD_API_BASE}/subscriptions/sms"

    headers = {
        "Authorization": f"Bearer {DIALPAD_API_KEY}",
        "Accept": "application/json"
    }

    request = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(request) as response:
            response_data = response.read().decode("utf-8")
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        raise RuntimeError(f"Dialpad API error (HTTP {e.code}): {error_body}")


def main():
    parser = argparse.ArgumentParser(
        description="Create SMS webhook subscriptions via Dialpad API"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new webhook subscription")
    create_parser.add_argument(
        "--url",
        required=True,
        help="Webhook URL to receive events"
    )
    create_parser.add_argument(
        "--events",
        help="Comma-separated events (default: sms_sent,sms_received)"
    )
    create_parser.add_argument(
        "--office-id",
        dest="office_id",
        help="Optional office ID to filter events"
    )
    create_parser.add_argument(
        "--direction",
        default="all",
        choices=["all", "inbound", "outbound"],
        help="Direction filter (default: all)"
    )
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all webhook subscriptions")

    args = parser.parse_args()

    try:
        if args.command == "create" or args.command is None:
            result = create_sms_subscription(
                webhook_url=args.url,
                events=args.events,
                office_id=args.office_id,
                direction=args.direction
            )
            webhook = result.get("webhook", {})
            print("Webhook subscription created!")
            print(f"   Subscription ID: {result.get('id')}")
            print(f"   Webhook ID: {webhook.get('id')}")
            print(f"   Webhook URL: {webhook.get('hook_url')}")
            print(f"   Direction: {result.get('direction')}")
            print(f"   Enabled: {result.get('enabled')}")
        
        elif args.command == "list":
            result = list_subscriptions()
            subscriptions = result.get("items", [])
            print(f"SMS Webhook Subscriptions: {len(subscriptions)}")
            for sub in subscriptions:
                webhook = sub.get("webhook", {})
                print(f"   ID: {sub.get('id')}")
                print(f"   Webhook URL: {webhook.get('hook_url', 'N/A')}")
                print(f"   Events: {sub.get('event_types', [])}")
                print(f"   Direction: {sub.get('direction')}")
                print(f"   Enabled: {sub.get('enabled')}")
                print()
        
        sys.exit(0)

    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
