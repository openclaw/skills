#!/usr/bin/env python3
"""ProtonMail CLI via IMAP bridge (Proton Bridge or hydroxide).

Configuration via environment variables:
    PROTONMAIL_HOST  - IMAP host (default: 127.0.0.1)
    PROTONMAIL_PORT  - IMAP port (default: 143)
    PROTONMAIL_USER  - Email address
    PROTONMAIL_PASS  - Bridge password

Or config file at ~/.config/protonmail-bridge/config.env
"""

import argparse
import imaplib
import email
import os
from email.header import decode_header
from pathlib import Path
import sys

# Configuration with fallbacks
def get_config():
    """Load configuration from environment or config file."""
    config = {
        'host': '127.0.0.1',
        'port': 143,
        'user': None,
        'password': None,
    }
    
    # Try config file first
    config_file = Path.home() / ".config/protonmail-bridge/config.env"
    if config_file.exists():
        for line in config_file.read_text().splitlines():
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key == 'PROTONMAIL_HOST':
                    config['host'] = value
                elif key == 'PROTONMAIL_PORT':
                    config['port'] = int(value)
                elif key == 'PROTONMAIL_USER':
                    config['user'] = value
                elif key == 'PROTONMAIL_PASS':
                    config['password'] = value
    
    # Environment variables override config file
    config['host'] = os.environ.get('PROTONMAIL_HOST', config['host'])
    config['port'] = int(os.environ.get('PROTONMAIL_PORT', config['port']))
    config['user'] = os.environ.get('PROTONMAIL_USER', config['user'])
    config['password'] = os.environ.get('PROTONMAIL_PASS', config['password'])
    
    # Legacy: try hydroxide password file
    if not config['password']:
        legacy_file = Path.home() / ".config/hydroxide/bridge-password"
        if legacy_file.exists():
            config['password'] = legacy_file.read_text().strip()
    
    return config


CONFIG = get_config()


def decode_mime_header(header):
    """Decode MIME encoded header."""
    if not header:
        return ""
    decoded_parts = decode_header(header)
    result = []
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(encoding or 'utf-8', errors='replace'))
        else:
            result.append(part)
    return ''.join(result)


def connect():
    """Connect and login to IMAP."""
    if not CONFIG['user'] or not CONFIG['password']:
        raise ValueError(
            "Missing credentials. Set PROTONMAIL_USER and PROTONMAIL_PASS "
            "environment variables or create ~/.config/protonmail-bridge/config.env"
        )
    
    imap = imaplib.IMAP4(CONFIG['host'], CONFIG['port'])
    imap.login(CONFIG['user'], CONFIG['password'])
    return imap


def cmd_mailboxes(args):
    """List all mailboxes."""
    imap = connect()
    status, mailboxes = imap.list()
    print("📁 Mailboxes:\n")
    for mb in mailboxes:
        print(f"  {mb.decode()}")
    imap.logout()


def cmd_inbox(args):
    """List recent emails from inbox."""
    imap = connect()
    imap.select('INBOX')
    
    status, messages = imap.search(None, 'ALL')
    msg_ids = messages[0].split()
    
    limit = args.limit or 10
    recent_ids = msg_ids[-limit:]
    
    print(f"📬 INBOX ({len(msg_ids)} total, showing last {len(recent_ids)}):\n")
    
    for msg_id in reversed(recent_ids):
        status, data = imap.fetch(msg_id, '(BODY[HEADER.FIELDS (FROM SUBJECT DATE)])')
        if status == 'OK':
            header = data[0][1].decode('utf-8', errors='replace')
            
            from_addr = ""
            subject = ""
            date = ""
            
            for line in header.split('\n'):
                line = line.strip()
                if line.lower().startswith('from:'):
                    from_addr = decode_mime_header(line[5:].strip())
                elif line.lower().startswith('subject:'):
                    subject = decode_mime_header(line[8:].strip())
                elif line.lower().startswith('date:'):
                    date = line[5:].strip()
            
            print(f"[{msg_id.decode()}] {date[:20]}")
            print(f"  From: {from_addr[:60]}")
            print(f"  Subject: {subject[:70]}")
            print()
    
    imap.logout()


def cmd_search(args):
    """Search emails by keyword."""
    imap = connect()
    imap.select('INBOX')
    
    status, messages = imap.search(None, f'(OR SUBJECT "{args.query}" BODY "{args.query}")')
    msg_ids = messages[0].split()
    
    limit = args.limit or 20
    recent_ids = msg_ids[-limit:]
    
    print(f"🔍 Search results for '{args.query}' ({len(msg_ids)} found, showing {len(recent_ids)}):\n")
    
    for msg_id in reversed(recent_ids):
        status, data = imap.fetch(msg_id, '(BODY[HEADER.FIELDS (FROM SUBJECT DATE)])')
        if status == 'OK':
            header = data[0][1].decode('utf-8', errors='replace')
            
            from_addr = ""
            subject = ""
            date = ""
            
            for line in header.split('\n'):
                line = line.strip()
                if line.lower().startswith('from:'):
                    from_addr = decode_mime_header(line[5:].strip())
                elif line.lower().startswith('subject:'):
                    subject = decode_mime_header(line[8:].strip())
                elif line.lower().startswith('date:'):
                    date = line[5:].strip()
            
            print(f"[{msg_id.decode()}] {date[:20]}")
            print(f"  From: {from_addr[:60]}")
            print(f"  Subject: {subject[:70]}")
            print()
    
    imap.logout()


def cmd_read(args):
    """Read a specific email by message ID."""
    imap = connect()
    imap.select('INBOX')
    
    status, data = imap.fetch(str(args.message_id), '(RFC822)')
    if status != 'OK':
        print(f"❌ Message {args.message_id} not found")
        imap.logout()
        return
    
    raw_email = data[0][1]
    msg = email.message_from_bytes(raw_email)
    
    print(f"📧 Message {args.message_id}")
    print(f"{'='*60}")
    print(f"From: {decode_mime_header(msg['From'])}")
    print(f"To: {decode_mime_header(msg['To'])}")
    print(f"Date: {msg['Date']}")
    print(f"Subject: {decode_mime_header(msg['Subject'])}")
    print(f"{'='*60}\n")
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body = part.get_payload(decode=True)
                if body:
                    print(body.decode('utf-8', errors='replace'))
                break
    else:
        body = msg.get_payload(decode=True)
        if body:
            print(body.decode('utf-8', errors='replace'))
    
    imap.logout()


def cmd_unread(args):
    """List unread emails."""
    imap = connect()
    imap.select('INBOX')
    
    status, messages = imap.search(None, 'UNSEEN')
    msg_ids = messages[0].split()
    
    limit = args.limit or 20
    recent_ids = msg_ids[-limit:]
    
    print(f"📭 Unread emails ({len(msg_ids)} total, showing {len(recent_ids)}):\n")
    
    for msg_id in reversed(recent_ids):
        status, data = imap.fetch(msg_id, '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
        if status == 'OK':
            header = data[0][1].decode('utf-8', errors='replace')
            
            from_addr = ""
            subject = ""
            date = ""
            
            for line in header.split('\n'):
                line = line.strip()
                if line.lower().startswith('from:'):
                    from_addr = decode_mime_header(line[5:].strip())
                elif line.lower().startswith('subject:'):
                    subject = decode_mime_header(line[8:].strip())
                elif line.lower().startswith('date:'):
                    date = line[5:].strip()
            
            print(f"[{msg_id.decode()}] {date[:20]}")
            print(f"  From: {from_addr[:60]}")
            print(f"  Subject: {subject[:70]}")
            print()
    
    imap.logout()


def main():
    parser = argparse.ArgumentParser(
        description="ProtonMail CLI via IMAP bridge",
        epilog="Set PROTONMAIL_USER and PROTONMAIL_PASS environment variables for credentials."
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    subparsers.add_parser('mailboxes', help='List mailboxes')
    
    inbox_parser = subparsers.add_parser('inbox', help='List recent inbox emails')
    inbox_parser.add_argument('--limit', '-l', type=int, default=10, help='Number of emails')
    
    unread_parser = subparsers.add_parser('unread', help='List unread emails')
    unread_parser.add_argument('--limit', '-l', type=int, default=20, help='Number of emails')
    
    search_parser = subparsers.add_parser('search', help='Search emails')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', '-l', type=int, default=20, help='Max results')
    
    read_parser = subparsers.add_parser('read', help='Read specific email')
    read_parser.add_argument('message_id', type=int, help='Message ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    commands = {
        'mailboxes': cmd_mailboxes,
        'inbox': cmd_inbox,
        'unread': cmd_unread,
        'search': cmd_search,
        'read': cmd_read,
    }
    
    try:
        commands[args.command](args)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
