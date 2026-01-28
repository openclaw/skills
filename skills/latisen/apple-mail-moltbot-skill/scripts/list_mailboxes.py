#!/usr/bin/env python3
"""
List all mailboxes for a specific account

Usage:
    python3 list_mailboxes.py "Account Name"

Arguments:
    account_name: Name of the mail account

Output:
    JSON with list of mailbox names for the account
"""

import subprocess
import json
import sys


def run_osascript(script):
    """Run AppleScript and return output"""
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None


def list_mailboxes(account_name):
    """Get all mailboxes for an account"""
    script = f'''
    tell application "Mail"
        set mailboxList to {{}}
        try
            set acc to account "{account_name}"
            repeat with mb in mailboxes of acc
                set end of mailboxList to name of mb
            end repeat
        end try
        return mailboxList
    end tell
    '''
    
    result = run_osascript(script)
    if result is None:
        return {
            "error": "Failed to communicate with Mail app",
            "details": "Is Mail running? Does the account exist?"
        }
    
    if result:
        mailboxes = [mb.strip() for mb in result.split(', ')]
        return {
            "account": account_name,
            "mailboxes": mailboxes,
            "count": len(mailboxes)
        }
    
    return {
        "account": account_name,
        "mailboxes": [],
        "count": 0,
        "details": "No mailboxes found. Check if account name is correct (case-sensitive)."
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Missing required argument",
            "usage": "python3 list_mailboxes.py 'Account Name'"
        }, indent=2))
        sys.exit(1)
    
    account_name = sys.argv[1]
    output = list_mailboxes(account_name)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    
    if "error" in output:
        sys.exit(1)
