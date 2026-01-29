#!/usr/bin/env python3
"""
Check inbox for new messages and process them.
"""

import os
import sys
from datetime import datetime, timezone

try:
    from agentmail import AgentMail
except ImportError:
    print("Error: agentmail not installed. Run: pip install agentmail")
    sys.exit(1)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Check inbox for messages')
    parser.add_argument('inbox', help='Inbox ID (email address)')
    parser.add_argument('--limit', '-n', type=int, default=10, help='Max messages')
    parser.add_argument('--since', help='Only show messages since (ISO format)')
    parser.add_argument('--mark-read', action='store_true', help='Mark as read')
    parser.add_argument('--download-attachments', help='Download attachments to directory')
    
    args = parser.parse_args()
    
    # Load client
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('AGENTMAIL_API_KEY')
    if not api_key:
        print("Error: AGENTMAIL_API_KEY not set")
        sys.exit(1)
    
    client = AgentMail(api_key=api_key)
    
    # Parse since date
    since = None
    if args.since:
        since = datetime.fromisoformat(args.since.replace('Z', '+00:00'))
    
    # Fetch messages
    try:
        response = client.inboxes.messages.list(
            inbox_id=args.inbox,
            limit=args.limit
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    messages = response
    if hasattr(response, 'messages'):
        messages = response.messages
    
    if not messages:
        print("No messages found.")
        return
    
    # Filter by date if specified
    if since:
        messages = [m for m in messages if m.date and m.date > since]
    
    print(f"Found {len(messages)} messages:\n")
    
    for msg in messages:
        print("=" * 60)
        print(f"From: {msg.from_}")
        print(f"To: {', '.join(msg.to) if isinstance(msg.to, list) else msg.to}")
        print(f"Subject: {msg.subject}")
        print(f"Date: {msg.date}")
        print(f"ID: {msg.message_id}")
        
        if msg.attachments:
            print(f"Attachments: {len(msg.attachments)}")
            for att in msg.attachments:
                print(f"  - {att.filename}")
        
        # Preview
        preview = (msg.text or msg.html or "")[:200]
        print(f"\nPreview:\n{preview}...")
        print()
        
        # Download attachments
        if args.download_attachments and msg.attachments:
            from pathlib import Path
            download_dir = Path(args.download_attachments)
            download_dir.mkdir(exist_ok=True)
            
            for att in msg.attachments:
                try:
                    content = client.attachments.download(att.attachment_id)
                    file_path = download_dir / att.filename
                    file_path.write_bytes(content)
                    print(f"  Downloaded: {file_path}")
                except Exception as e:
                    print(f"  Error downloading {att.filename}: {e}")


if __name__ == '__main__':
    main()
