#!/usr/bin/env python3
"""
Webhook receiver for Dialpad SMS using SQLite storage
Integrates with sms_sqlite.py for persistent storage
"""

import json
import sys
from pathlib import Path

# Add skill directory to path
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from sms_sqlite import init_db, store_message, get_all_threads, get_unread, mark_as_read


def handle_sms_webhook(data: dict) -> dict:
    """
    Handle incoming SMS webhook from Dialpad
    Stores message in SQLite with FTS5 indexing
    """
    conn = init_db()
    try:
        msg = store_message(conn, data, is_new=True)
        
        # Get updated unread count for this contact
        cursor = conn.execute(
            "SELECT unread_count, name FROM contacts WHERE phone_number = ?",
            (msg["contact_number"],)
        )
        row = cursor.fetchone()
        
        return {
            "status": "success",
            "stored": True,
            "message": {
                "id": msg.get("id"),
                "direction": msg["direction"],
                "contact_number": msg["contact_number"],
                "contact_name": msg.get("contact_name") or row["name"] if row else "Unknown",
                "preview": msg.get("text", "")[:60] + "..." if len(msg.get("text", "")) > 60 else msg.get("text", ""),
                "unread_count": row["unread_count"] if row else 0
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "stored": False,
            "error": str(e)
        }
    finally:
        conn.close()


def format_notification(response: dict) -> str:
    """Format a stored message for notification"""
    if response.get("status") != "success":
        return f"❌ Failed to store message: {response.get('error', 'Unknown error')}"
    
    msg = response.get("message", {})
    direction_emoji = "📥" if msg.get("direction") == "inbound" else "📤"
    contact = msg.get("contact_name", "Unknown")
    number = msg.get("contact_number", "")
    preview = msg.get("preview", "")
    unread = msg.get("unread_count", 0)
    
    unread_indicator = f" ({unread} unread)" if unread > 1 else ""
    
    return f"{direction_emoji} **SMS from {contact}** ({number}){unread_indicator}\n> {preview}"


def get_inbox_summary() -> str:
    """Get summary of unread messages for notifications"""
    conn = init_db()
    try:
        threads = get_unread(conn)
        if not threads:
            return "📭 No unread messages"
        
        total_unread = sum(t.get("unread_count", 0) for t in threads)
        lines = [f"📬 {total_unread} unread message(s) from {len(threads)} contact(s):\n"]
        
        for t in threads[:5]:  # Show top 5
            name = t.get("name") or t["phone_number"]
            count = t["unread_count"]
            preview = (t.get("last_message_preview") or "")[:40]
            lines.append(f"  • **{name}**: {count} unread\n    > {preview}...")
        
        if len(threads) > 5:
            lines.append(f"\n  ... and {len(threads) - 5} more")
        
        return "\n".join(lines)
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 webhook_sqlite.py [test|inbox|mark-read <number>]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "test":
        test_data = {
            "id": 99999,
            "created_date": 1769550395216,
            "event_timestamp": 1769550395917,
            "direction": "inbound",
            "from_number": "+14155559999",
            "to_number": ["+14152001316"],
            "text": "Testing the new SQLite storage with FTS5 search!",
            "text_content": "Testing the new SQLite storage with FTS5 search!",
            "contact": {"name": "Test SQLite", "id": "999"},
            "message_status": "pending",
            "mms": False
        }
        
        result = handle_sms_webhook(test_data)
        print(json.dumps(result, indent=2))
        print("\n" + format_notification(result))
    
    elif cmd == "inbox":
        print(get_inbox_summary())
    
    elif cmd == "mark-read" and len(sys.argv) >= 3:
        number = sys.argv[2]
        conn = init_db()
        try:
            count = mark_as_read(conn, number)
            print(f"✓ Marked {count} messages from {number} as read")
        finally:
            conn.close()
    
    else:
        print("Unknown command")
