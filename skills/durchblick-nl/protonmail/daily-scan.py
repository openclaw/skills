#!/usr/bin/env python3
"""Daily ProtonMail scan - identifies important emails.

Configuration via environment variables:
    PROTONMAIL_HOST  - IMAP host (default: 127.0.0.1)
    PROTONMAIL_PORT  - IMAP port (default: 143)
    PROTONMAIL_USER  - Email address
    PROTONMAIL_PASS  - Bridge password

Or config file at ~/.config/protonmail-bridge/config.env

Customize important patterns via:
    PROTONMAIL_IMPORTANT_SENDERS  - Comma-separated sender patterns
    PROTONMAIL_URGENT_KEYWORDS    - Comma-separated keywords
    PROTONMAIL_IGNORE_PATTERNS    - Comma-separated ignore patterns
"""

import imaplib
import os
from email.header import decode_header
from datetime import datetime, timedelta
from pathlib import Path
import re

# Load configuration
def get_config():
    """Load configuration from environment or config file."""
    config = {
        'host': '127.0.0.1',
        'port': 143,
        'user': None,
        'password': None,
    }
    
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
    
    config['host'] = os.environ.get('PROTONMAIL_HOST', config['host'])
    config['port'] = int(os.environ.get('PROTONMAIL_PORT', config['port']))
    config['user'] = os.environ.get('PROTONMAIL_USER', config['user'])
    config['password'] = os.environ.get('PROTONMAIL_PASS', config['password'])
    
    # Legacy hydroxide password file
    if not config['password']:
        legacy_file = Path.home() / ".config/hydroxide/bridge-password"
        if legacy_file.exists():
            config['password'] = legacy_file.read_text().strip()
    
    return config


CONFIG = get_config()

# Default important sender patterns (customize via PROTONMAIL_IMPORTANT_SENDERS)
DEFAULT_IMPORTANT_SENDERS = [
    # Banks & Finance (generic)
    "bank", "finance", "paypal", "stripe",
    # Government (generic)
    "gov", "government", "admin", "official",
    # Health
    "health", "insurance", "medical", "hospital",
    # School & Education
    "school", "university", "college", "education",
]

# Default urgent keywords (DE/EN/NL)
DEFAULT_URGENT_KEYWORDS = [
    # English
    "urgent", "important", "action required", "deadline", "reminder", 
    "expiring", "immediate", "critical", "asap",
    # German
    "dringend", "wichtig", "frist", "mahnung", "kündigung", 
    "handlungsbedarf", "sofort", "termin", "erinnerung",
    # Dutch
    "belangrijk", "actie vereist", "herinnering", "vervaldatum", 
    "betalingsherinnering", "aanmaning", "deadline",
]

# Default ignore patterns (newsletters, etc.)
DEFAULT_IGNORE_PATTERNS = [
    "newsletter", "noreply", "no-reply", "marketing", "promo",
    "unsubscribe", "notification", "digest", "updates@",
]

# Load custom patterns from environment
def get_patterns(env_var, defaults):
    """Get patterns from environment or use defaults."""
    custom = os.environ.get(env_var, '')
    if custom:
        return [p.strip().lower() for p in custom.split(',') if p.strip()]
    return defaults

IMPORTANT_SENDERS = get_patterns('PROTONMAIL_IMPORTANT_SENDERS', DEFAULT_IMPORTANT_SENDERS)
URGENT_KEYWORDS = get_patterns('PROTONMAIL_URGENT_KEYWORDS', DEFAULT_URGENT_KEYWORDS)
IGNORE_PATTERNS = get_patterns('PROTONMAIL_IGNORE_PATTERNS', DEFAULT_IGNORE_PATTERNS)


def decode_mime(header):
    """Decode MIME encoded header."""
    if not header:
        return ""
    try:
        decoded = decode_header(header)
        return ''.join(
            p.decode(e or 'utf-8', errors='replace') if isinstance(p, bytes) else p 
            for p, e in decoded
        )
    except:
        return str(header)


def is_important(from_addr, subject):
    """Check if email is important based on sender or subject."""
    from_lower = from_addr.lower()
    subject_lower = subject.lower()
    
    # Skip ignored senders
    for pattern in IGNORE_PATTERNS:
        if pattern in from_lower:
            return False, None
    
    # Check important senders
    for pattern in IMPORTANT_SENDERS:
        if pattern in from_lower:
            return True, f"Sender: {pattern}"
    
    # Check urgent keywords
    for keyword in URGENT_KEYWORDS:
        if keyword in subject_lower:
            return True, f"Keyword: {keyword}"
    
    return False, None


def main():
    if not CONFIG['user'] or not CONFIG['password']:
        print("❌ Missing credentials. Set PROTONMAIL_USER and PROTONMAIL_PASS")
        return 1
    
    imap = imaplib.IMAP4(CONFIG['host'], CONFIG['port'])
    imap.login(CONFIG['user'], CONFIG['password'])
    imap.select('INBOX', readonly=True)
    
    # Get today's date for filtering (last 24h)
    since_date = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
    
    # Search for recent unseen emails
    _, messages = imap.search(None, f'(UNSEEN SINCE {since_date})')
    msg_ids = messages[0].split() if messages[0] else []
    
    important_emails = []
    total_unread = 0
    
    # Get total unread count
    _, all_unseen = imap.search(None, 'UNSEEN')
    total_unread = len(all_unseen[0].split()) if all_unseen[0] else 0
    
    for msg_id in msg_ids[-50:]:  # Limit to last 50
        _, data = imap.fetch(msg_id, '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
        if not data or not data[0]:
            continue
        
        raw = data[0][1].decode('utf-8', errors='replace')
        
        from_addr = ""
        subject = ""
        date = ""
        
        for line in raw.split('\n'):
            line_lower = line.lower()
            if line_lower.startswith('from:'):
                from_addr = decode_mime(line[5:].strip())
            elif line_lower.startswith('subject:'):
                subject = decode_mime(line[8:].strip())
            elif line_lower.startswith('date:'):
                date = line[5:].strip()[:20]
        
        important, reason = is_important(from_addr, subject)
        if important:
            important_emails.append({
                'from': from_addr[:50],
                'subject': subject[:60],
                'date': date,
                'reason': reason
            })
    
    imap.logout()
    
    # Output summary
    print(f"📬 **ProtonMail Daily Digest**")
    print(f"")
    print(f"📊 **Stats:** {total_unread} unread emails total")
    print(f"")
    
    if important_emails:
        print(f"⭐ **{len(important_emails)} important emails (last 24h):**")
        print(f"")
        for email in important_emails:
            print(f"• **{email['subject']}**")
            print(f"  From: {email['from']}")
            print(f"  ({email['reason']})")
            print(f"")
    else:
        print(f"✅ No important emails in the last 24h.")
    
    return len(important_emails)


if __name__ == '__main__':
    exit(main() or 0)
