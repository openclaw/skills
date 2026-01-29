#!/usr/bin/env python3
"""
Send emails via AgentMail with rich content support.
"""

import os
import sys
import base64
from pathlib import Path

try:
    from agentmail import AgentMail, SendAttachment
except ImportError:
    print("Error: agentmail not installed. Run: pip install agentmail")
    sys.exit(1)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Send email via AgentMail')
    parser.add_argument('--from', dest='sender', required=True, help='From inbox')
    parser.add_argument('--to', required=True, help='To address')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--text', help='Plain text body')
    parser.add_argument('--html', help='HTML body')
    parser.add_argument('--cc', nargs='+', help='CC recipients')
    parser.add_argument('--attachment', help='File to attach')
    
    args = parser.parse_args()
    
    if not args.text and not args.html:
        print("Error: Provide --text or --html (or both)")
        sys.exit(1)
    
    # Load client
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('AGENTMAIL_API_KEY')
    if not api_key:
        print("Error: AGENTMAIL_API_KEY not set")
        sys.exit(1)
    
    client = AgentMail(api_key=api_key)
    
    # Build kwargs
    kwargs = {
        'inbox_id': args.sender,
        'to': args.to,
        'subject': args.subject,
    }
    
    if args.text:
        kwargs['text'] = args.text
    
    if args.html:
        kwargs['html'] = args.html
    else:
        # Auto-generate HTML from text
        kwargs['html'] = f"<html><body><pre>{args.text}</pre></body></html>"
    
    if args.cc:
        kwargs['cc'] = args.cc
    
    # Handle attachment
    if args.attachment:
        file_path = Path(args.attachment)
        if not file_path.exists():
            print(f"Error: File not found: {args.attachment}")
            sys.exit(1)
        
        content = file_path.read_bytes()
        kwargs['attachments'] = [
            SendAttachment(
                filename=file_path.name,
                content=base64.b64encode(content).decode()
            )
        ]
    
    # Send
    try:
        message = client.inboxes.messages.send(**kwargs)
        print(f"✅ Sent: {message.message_id}")
        print(f"   To: {args.to}")
        print(f"   Subject: {args.subject}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
