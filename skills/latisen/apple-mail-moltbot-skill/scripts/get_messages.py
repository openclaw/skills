#!/usr/bin/env python3
"""
Get messages from a specific mailbox

Usage:
    python3 get_messages.py "Account Name" "Mailbox Name" [--limit N]

Arguments:
    account_name: Name of the mail account
    mailbox_name: Name of the mailbox (e.g., "INBOX", "Sent")
    --limit N: Optional, maximum number of messages to retrieve (default: 10)

Output:
    JSON with list of messages and their metadata
"""

import subprocess
import json
import sys
import argparse


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


def get_messages(account_name, mailbox_name, limit=10):
    """Get messages from a mailbox"""
    limit_clause = ""
    if limit:
        limit_clause = f"if messageCount > {limit} then set messageCount to {limit}"
    
    script = f'''
    tell application "Mail"
        set messageList to {{}}
        try
            set acc to account "{account_name}"
            set mb to mailbox "{mailbox_name}" of acc
            set allMessages to messages of mb
            set messageCount to count of allMessages
            {limit_clause}
            
            repeat with i from 1 to messageCount
                set msg to item i of allMessages
                set msgInfo to {{}}
                
                try
                    set msgId to id of msg
                    set msgSubject to subject of msg
                    set msgSender to sender of msg
                    set msgDateSent to date sent of msg
                    set msgDateReceived to date received of msg
                    set msgRead to read status of msg
                    set msgSize to message size of msg
                    
                    set msgData to msgId & "|||" & msgSubject & "|||" & msgSender & "|||" & msgDateSent & "|||" & msgDateReceived & "|||" & msgRead & "|||" & msgSize
                    set end of messageList to msgData
                end try
            end repeat
        end try
        
        set AppleScript's text item delimiters to "%%%"
        set messageString to messageList as string
        set AppleScript's text item delimiters to ""
        return messageString
    end tell
    '''
    
    result = run_osascript(script)
    if result is None:
        return {
            "error": "Failed to communicate with Mail app",
            "details": "Is Mail running? Do the account and mailbox exist?"
        }
    
    messages = []
    if result:
        message_strings = result.split('%%%')
        for msg_str in message_strings:
            if msg_str:
                parts = msg_str.split('|||')
                if len(parts) >= 7:
                    messages.append({
                        'id': parts[0],
                        'subject': parts[1],
                        'sender': parts[2],
                        'date_sent': parts[3],
                        'date_received': parts[4],
                        'read_status': parts[5].lower() == 'true',
                        'message_size': int(parts[6]) if parts[6].isdigit() else 0
                    })
    
    return {
        "account": account_name,
        "mailbox": mailbox_name,
        "messages": messages,
        "count": len(messages)
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get messages from a mailbox')
    parser.add_argument('account_name', help='Name of the mail account')
    parser.add_argument('mailbox_name', help='Name of the mailbox')
    parser.add_argument('--limit', type=int, default=10, 
                        help='Maximum number of messages to retrieve (default: 10)')
    
    args = parser.parse_args()
    
    output = get_messages(args.account_name, args.mailbox_name, args.limit)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    
    if "error" in output:
        sys.exit(1)
