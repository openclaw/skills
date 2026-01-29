#!/usr/bin/env python3
"""
Setup webhook for real-time email processing.
"""

import os
import sys

try:
    from agentmail import AgentMail
except ImportError:
    print("Error: agentmail not installed. Run: pip install agentmail")
    sys.exit(1)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup AgentMail webhook')
    parser.add_argument('--url', required=True, help='Webhook URL')
    parser.add_argument('--client-id', default='default-processor', help='Client ID')
    parser.add_argument('--events', nargs='+', default=['message.received'],
                       help='Events to subscribe to')
    parser.add_argument('--list', action='store_true', help='List existing webhooks')
    parser.add_argument('--delete', help='Delete webhook by ID')
    
    args = parser.parse_args()
    
    # Load client
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('AGENTMAIL_API_KEY')
    if not api_key:
        print("Error: AGENTMAIL_API_KEY not set")
        sys.exit(1)
    
    client = AgentMail(api_key=api_key)
    
    # List webhooks
    if args.list:
        try:
            webhooks = client.webhooks.list()
            print(f"Found {len(webhooks)} webhooks:")
            for wh in webhooks:
                print(f"  ID: {wh.id}")
                print(f"  URL: {wh.url}")
                print(f"  Events: {', '.join(wh.events)}")
                print()
        except Exception as e:
            print(f"Error: {e}")
        return
    
    # Delete webhook
    if args.delete:
        try:
            client.webhooks.delete(webhook_id=args.delete)
            print(f"✅ Deleted webhook: {args.delete}")
        except Exception as e:
            print(f"❌ Error: {e}")
        return
    
    # Create webhook
    try:
        webhook = client.webhooks.create(
            url=args.url,
            client_id=args.client_id,
            events=args.events
        )
        print(f"✅ Webhook created:")
        print(f"   ID: {webhook.id}")
        print(f"   URL: {webhook.url}")
        print(f"   Events: {', '.join(webhook.events)}")
        print()
        print("⚠️  SECURITY WARNING:")
        print("   Your webhook endpoint should validate sender allowlists")
        print("   to prevent prompt injection attacks via email.")
        print()
        print("   See references/WEBHOOKS.md for security guidelines.")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
