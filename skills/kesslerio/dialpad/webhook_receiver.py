#!/usr/bin/env python3
"""
Webhook receiver for Dialpad SMS with threaded storage
Can be integrated into the webhook server to store messages automatically
"""

import json
import sys
from pathlib import Path

# Add skill directory to path for imports
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from sms_storage import store_message, get_all_threads, mark_as_read


def handle_sms_webhook(data: dict) -> dict:
    """
    Handle incoming SMS webhook from Dialpad
    Stores message in threaded storage
    
    Args:
        data: Raw webhook payload from Dialpad
    
    Returns:
        Response dict with status and message info
    """
    try:
        # Store the message
        msg = store_message(data, is_new=True)
        
        # Get contact info for response
        contact_name = msg.get("contact_name", "Unknown")
        direction = msg["direction"]
        text_preview = msg.get("text", "")[:50] + "..." if len(msg.get("text", "")) > 50 else msg.get("text", "")
        
        return {
            "status": "success",
            "stored": True,
            "message": {
                "id": msg.get("id"),
                "direction": direction,
                "from": msg.get("from_number") if direction == "inbound" else msg.get("to_number"),
                "contact_name": contact_name,
                "preview": text_preview
            }
        }
    
    except Exception as e:
        return {
            "status": "error",
            "stored": False,
            "error": str(e)
        }


def format_notification(response: dict) -> str:
    """Format a stored message for notification"""
    if response.get("status") != "success":
        return f"❌ Failed to store message: {response.get('error', 'Unknown error')}"
    
    msg = response.get("message", {})
    direction_emoji = "📥" if msg.get("direction") == "inbound" else "📤"
    contact = msg.get("contact_name", "Unknown")
    number = msg.get("from", "")
    preview = msg.get("preview", "")
    
    return f"{direction_emoji} **SMS from {contact}** ({number})\n> {preview}"


# For direct testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 webhook_receiver.py [test|threads]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "test":
        # Test with sample data
        test_data = {
            "id": 12345,
            "created_date": 1769550395216,
            "event_timestamp": 1769550395917,
            "direction": "inbound",
            "from_number": "+14155551234",
            "to_number": ["+14152001316"],
            "text": "Test message for threaded storage",
            "text_content": "Test message for threaded storage",
            "contact": {"name": "Test Contact", "id": "123"},
            "message_status": "pending",
            "mms": False
        }
        
        result = handle_sms_webhook(test_data)
        print(json.dumps(result, indent=2))
        print("\n" + format_notification(result))
    
    elif cmd == "threads":
        threads = get_all_threads()
        print(f"\n{len(threads)} active SMS threads:")
        for t in threads[:10]:  # Show first 10
            print(f"  • {t.get('contact_name', 'Unknown')} ({t['phone_number']}): {t['message_count']} msgs")
    
    else:
        print("Unknown command. Use: test, threads")
