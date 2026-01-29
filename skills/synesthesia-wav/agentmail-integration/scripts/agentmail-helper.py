#!/usr/bin/env python3
"""
AgentMail helper script for common email operations.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List

try:
    from agentmail import AgentMail, SendAttachment
except ImportError:
    print("Error: agentmail not installed. Run: uv pip install agentmail")
    sys.exit(1)


class AgentMailHelper:
    """Simplified interface for common AgentMail operations."""
    
    def __init__(self, api_key: Optional[str] = None):
        if not api_key:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('AGENTMAIL_API_KEY')
        
        if not api_key:
            raise ValueError("AGENTMAIL_API_KEY required")
        
        self.client = AgentMail(api_key=api_key)
    
    def create_inbox(self, display_name: Optional[str] = None) -> dict:
        """Create a new inbox."""
        inbox = self.client.inboxes.create()
        return {
            'email': inbox.inbox_id,
            'display_name': inbox.display_name,
            'created_at': inbox.created_at.isoformat()
        }
    
    def list_inboxes(self) -> List[dict]:
        """List all inboxes."""
        response = self.client.inboxes.list()
        return [{
            'email': i.inbox_id,
            'display_name': i.display_name,
            'created_at': i.created_at.isoformat()
        } for i in response.inboxes]
    
    def send_simple(self, from_inbox: str, to: str, subject: str, body: str) -> dict:
        """Send a simple text email."""
        message = self.client.inboxes.messages.send(
            inbox_id=from_inbox,
            to=to,
            subject=subject,
            text=body,
            html=f"<html><body><pre>{body}</pre></body></html>"
        )
        return {
            'id': message.message_id,
            'subject': subject,
            'sent_at': datetime.now(timezone.utc).isoformat()
        }
    
    def send_html(self, from_inbox: str, to: str, subject: str, 
                  text: str, html: str, cc: Optional[List[str]] = None) -> dict:
        """Send HTML email with text fallback."""
        kwargs = {
            'inbox_id': from_inbox,
            'to': to,
            'subject': subject,
            'text': text,
            'html': html
        }
        if cc:
            kwargs['cc'] = cc
        
        message = self.client.inboxes.messages.send(**kwargs)
        return {
            'id': message.message_id,
            'subject': subject,
            'sent_at': datetime.now(timezone.utc).isoformat()
        }
    
    def get_recent(self, inbox_id: str, limit: int = 10) -> List[dict]:
        """Get recent messages from an inbox."""
        messages = self.client.inboxes.messages.list(
            inbox_id=inbox_id,
            limit=limit
        )
        return [{
            'id': m.message_id,
            'from': m.from_,
            'subject': m.subject,
            'date': m.date,
            'preview': (m.text or '')[:100]
        } for m in messages]
    
    def watch_and_print(self, inbox_id: str):
        """Watch inbox and print new messages."""
        print(f"Watching {inbox_id} for new messages...")
        print("Press Ctrl+C to stop\n")
        
        try:
            for msg in self.client.inboxes.messages.watch(inbox_id=inbox_id):
                print(f"\n{'='*60}")
                print(f"From: {msg.from_}")
                print(f"Subject: {msg.subject}")
                print(f"Date: {msg.date}")
                print(f"\n{msg.text[:500]}...")
                print('='*60)
        except KeyboardInterrupt:
            print("\n\nStopped watching.")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='AgentMail helper')
    subparsers = parser.add_subparsers(dest='command')
    
    # Create inbox
    subparsers.add_parser('create', help='Create new inbox')
    
    # List inboxes
    subparsers.add_parser('list', help='List all inboxes')
    
    # Send email
    send_parser = subparsers.add_parser('send', help='Send email')
    send_parser.add_argument('--from', dest='sender', required=True)
    send_parser.add_argument('--to', required=True)
    send_parser.add_argument('--subject', required=True)
    send_parser.add_argument('--body', required=True)
    send_parser.add_argument('--html', help='HTML version (optional)')
    
    # Recent messages
    recent_parser = subparsers.add_parser('recent', help='Get recent messages')
    recent_parser.add_argument('--inbox', required=True)
    recent_parser.add_argument('--limit', type=int, default=10)
    
    # Watch inbox
    watch_parser = subparsers.add_parser('watch', help='Watch for new messages')
    watch_parser.add_argument('--inbox', required=True)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        helper = AgentMailHelper()
        
        if args.command == 'create':
            inbox = helper.create_inbox()
            print(f"Created: {inbox['email']}")
        
        elif args.command == 'list':
            inboxes = helper.list_inboxes()
            for i in inboxes:
                print(f"{i['email']} ({i['display_name']})")
        
        elif args.command == 'send':
            if args.html:
                result = helper.send_html(
                    args.sender, args.to, args.subject, args.body, args.html
                )
            else:
                result = helper.send_simple(
                    args.sender, args.to, args.subject, args.body
                )
            print(f"Sent: {result['id']}")
        
        elif args.command == 'recent':
            messages = helper.get_recent(args.inbox, args.limit)
            for m in messages:
                print(f"\nFrom: {m['from']}")
                print(f"Subject: {m['subject']}")
                print(f"Preview: {m['preview'][:80]}...")
        
        elif args.command == 'watch':
            helper.watch_and_print(args.inbox)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
