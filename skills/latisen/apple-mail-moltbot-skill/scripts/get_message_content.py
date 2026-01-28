#!/usr/bin/env python3
"""
Get full content of a specific message

Usage:
    python3 get_message_content.py MESSAGE_ID

Arguments:
    message_id: ID of the message (from get_messages.py output)

Output:
    JSON with full message content
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


def get_message_content(message_id):
    """Get full content of a message"""
    script = f'''
    tell application "Mail"
        try
            set msg to first message whose id is {message_id}
            set msgSubject to subject of msg
            set msgSender to sender of msg
            set msgContent to content of msg
            set msgDate to date sent of msg
            
            return msgSubject & "|||" & msgSender & "|||" & msgContent & "|||" & msgDate
        on error errMsg
            return "ERROR: " & errMsg
        end try
    end tell
    '''
    
    result = run_osascript(script)
    if result is None:
        return {
            "error": "Failed to communicate with Mail app",
            "details": "Is Mail running?"
        }
    
    if result.startswith("ERROR:"):
        return {
            "error": "Message not found",
            "details": result,
            "message_id": message_id
        }
    
    parts = result.split('|||')
    if len(parts) >= 4:
        return {
            'subject': parts[0],
            'sender': parts[1],
            'content': parts[2],
            'date_sent': parts[3]
        }
    
    return {
        "error": "Unexpected response from Mail",
        "details": result
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Missing required argument",
            "usage": "python3 get_message_content.py MESSAGE_ID"
        }, indent=2))
        sys.exit(1)
    
    message_id = sys.argv[1]
    output = get_message_content(message_id)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    
    if "error" in output:
        sys.exit(1)
