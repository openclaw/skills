#!/usr/bin/env python3
"""
List all mail accounts in Apple Mail

Usage:
    python3 list_accounts.py

Output:
    JSON with list of account names
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


def list_accounts():
    """Get all mail accounts"""
    script = '''
    tell application "Mail"
        set accountList to {}
        repeat with acc in accounts
            set end of accountList to name of acc
        end repeat
        return accountList
    end tell
    '''
    
    result = run_osascript(script)
    if result is None:
        return {"error": "Failed to communicate with Mail app. Is Mail running?"}
    
    if result:
        accounts = [acc.strip() for acc in result.split(', ')]
        return {
            "accounts": accounts,
            "count": len(accounts)
        }
    
    return {"accounts": [], "count": 0}


if __name__ == "__main__":
    output = list_accounts()
    print(json.dumps(output, indent=2, ensure_ascii=False))
    
    if "error" in output:
        sys.exit(1)
