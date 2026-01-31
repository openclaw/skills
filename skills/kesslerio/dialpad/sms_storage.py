#!/usr/bin/env python3
"""
SMS Threaded Storage Manager for Dialpad
Stores messages in per-contact directories with thread history
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Base paths
THREADS_DIR = Path("/home/art/clawd/logs/sms_threads")
LEGACY_LOG = Path("/home/art/clawd/logs/dialpad_sms.jsonl")


def sanitize_number(number: str) -> str:
    """Convert phone number to safe directory name"""
    return number.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")


def get_other_number(data: dict) -> tuple[str, str]:
    """
    Get the contact's phone number and name from message data
    Returns: (number, name)
    """
    direction = data.get("direction", "unknown")
    
    if direction == "inbound":
        # For inbound: from_number is the contact
        number = data.get("from_number", "unknown")
        contact = data.get("contact", {})
        name = contact.get("name", number)
    else:
        # For outbound: to_number[0] is the contact
        to_numbers = data.get("to_number", [])
        number = to_numbers[0] if to_numbers else "unknown"
        contact = data.get("contact", {})
        name = contact.get("name", number)
    
    return number, name


def get_thread_dir(number: str) -> Path:
    """Get or create thread directory for a phone number"""
    safe_num = sanitize_number(number)
    thread_dir = THREADS_DIR / safe_num
    thread_dir.mkdir(parents=True, exist_ok=True)
    return thread_dir


def load_metadata(thread_dir: Path) -> dict:
    """Load metadata for a thread"""
    meta_file = thread_dir / "metadata.json"
    if meta_file.exists():
        with open(meta_file, 'r') as f:
            return json.load(f)
    return {
        "phone_number": "",
        "contact_name": "",
        "first_message": None,
        "last_message": None,
        "message_count": 0,
        "unread_count": 0,
        "directions": {"inbound": 0, "outbound": 0}
    }


def save_metadata(thread_dir: Path, metadata: dict):
    """Save metadata for a thread"""
    meta_file = thread_dir / "metadata.json"
    with open(meta_file, 'w') as f:
        json.dump(metadata, f, indent=2)


def normalize_message(data: dict) -> dict:
    """Normalize webhook message to standard format"""
    direction = data.get("direction", "unknown")
    
    if direction == "inbound":
        other_number = data.get("from_number", "unknown")
        our_number = data.get("to_number", ["unknown"])[0] if data.get("to_number") else "unknown"
    else:
        to_numbers = data.get("to_number", [])
        other_number = to_numbers[0] if to_numbers else "unknown"
        our_number = data.get("from_number", "unknown")
    
    contact = data.get("contact", {})
    
    return {
        "id": data.get("id"),
        "timestamp": data.get("created_date"),
        "timestamp_iso": data.get("event_timestamp"),
        "direction": direction,
        "from_number": our_number if direction == "outbound" else other_number,
        "to_number": other_number if direction == "outbound" else our_number,
        "text": data.get("text", ""),
        "text_content": data.get("text_content", ""),
        "contact_name": contact.get("name", other_number),
        "contact_id": contact.get("id"),
        "message_status": data.get("message_status"),
        "delivery_result": data.get("message_delivery_result"),
        "mms": data.get("mms", False),
        "mms_url": data.get("mms_url"),
        "received_at": datetime.now(timezone.utc).isoformat()
    }


def store_message(data: dict, is_new: bool = True) -> dict:
    """
    Store a message in the threaded storage
    
    Args:
        data: Raw webhook data from Dialpad
        is_new: Whether this is a new message (affects unread count)
    
    Returns:
        Normalized message dict
    """
    # Normalize the message
    msg = normalize_message(data)
    
    # Get the contact's number (the OTHER person in the conversation)
    other_number, contact_name = get_other_number(data)
    
    if other_number == "unknown":
        print(f"Warning: Could not determine contact number for message {msg.get('id')}")
        return msg
    
    # Get/create thread directory
    thread_dir = get_thread_dir(other_number)
    
    # Load/update metadata
    metadata = load_metadata(thread_dir)
    metadata["phone_number"] = other_number
    if contact_name and contact_name != other_number:
        metadata["contact_name"] = contact_name
    
    # Update counts
    metadata["message_count"] += 1
    metadata["directions"][msg["direction"]] = metadata["directions"].get(msg["direction"], 0) + 1
    
    # Track first/last message
    ts = msg.get("timestamp")
    if ts:
        if metadata["first_message"] is None or ts < metadata["first_message"]:
            metadata["first_message"] = ts
        if metadata["last_message"] is None or ts > metadata["last_message"]:
            metadata["last_message"] = ts
    
    # Increment unread for new inbound messages
    if is_new and msg["direction"] == "inbound":
        metadata["unread_count"] = metadata.get("unread_count", 0) + 1
    
    # Append to thread
    thread_file = thread_dir / "thread.jsonl"
    with open(thread_file, 'a') as f:
        f.write(json.dumps(msg) + '\n')
    
    # Save metadata
    save_metadata(thread_dir, metadata)
    
    return msg


def migrate_legacy_log():
    """Migrate existing flat-file log to threaded storage"""
    if not LEGACY_LOG.exists():
        print("No legacy log file found")
        return 0
    
    count = 0
    with open(LEGACY_LOG, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                entry = json.loads(line)
                # Extract the actual message data from the webhook format
                data = entry.get("data", entry)  # Handle both formats
                store_message(data, is_new=False)
                count += 1
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON line: {e}")
                continue
            except Exception as e:
                print(f"Error processing line: {e}")
                continue
    
    print(f"Migrated {count} messages to threaded storage")
    return count


def get_thread(number: str) -> list[dict]:
    """Get all messages for a specific phone number"""
    thread_dir = THREADS_DIR / sanitize_number(number)
    thread_file = thread_dir / "thread.jsonl"
    
    if not thread_file.exists():
        return []
    
    messages = []
    with open(thread_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    return messages


def get_all_threads() -> list[dict]:
    """Get summary of all threads with metadata"""
    threads = []
    
    if not THREADS_DIR.exists():
        return threads
    
    for thread_dir in THREADS_DIR.iterdir():
        if thread_dir.is_dir():
            metadata = load_metadata(thread_dir)
            threads.append(metadata)
    
    # Sort by last message (newest first)
    threads.sort(key=lambda x: x.get("last_message") or 0, reverse=True)
    return threads


def mark_as_read(number: str) -> bool:
    """Mark all messages from a number as read"""
    thread_dir = THREADS_DIR / sanitize_number(number)
    metadata = load_metadata(thread_dir)
    metadata["unread_count"] = 0
    save_metadata(thread_dir, metadata)
    return True


def search_threads(query: str) -> list[tuple[str, list[dict]]]:
    """Search across all threads for messages containing query"""
    results = []
    
    for thread_dir in THREADS_DIR.iterdir():
        if not thread_dir.is_dir():
            continue
        
        thread_file = thread_dir / "thread.jsonl"
        if not thread_file.exists():
            continue
        
        matching = []
        with open(thread_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        msg = json.loads(line)
                        if query.lower() in msg.get("text", "").lower():
                            matching.append(msg)
                    except json.JSONDecodeError:
                        continue
        
        if matching:
            results.append((thread_dir.name, matching))
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 sms_storage.py [migrate|list|thread <number>|search <query>|unread]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "migrate":
        migrate_legacy_log()
    
    elif cmd == "list":
        threads = get_all_threads()
        print(f"\n{'Phone Number':<20} {'Name':<25} {'Msgs':>6} {'Unread':>7} {'Last Message'}")
        print("-" * 80)
        for t in threads:
            last = datetime.fromtimestamp(t.get("last_message", 0) / 1000).strftime("%Y-%m-%d %H:%M") if t.get("last_message") else "N/A"
            print(f"{t['phone_number']:<20} {t.get('contact_name', 'Unknown'):<25} {t['message_count']:>6} {t.get('unread_count', 0):>7} {last}")
    
    elif cmd == "thread" and len(sys.argv) >= 3:
        number = sys.argv[2]
        messages = get_thread(number)
        print(f"\nThread with {number} ({len(messages)} messages):\n")
        for msg in messages:
            ts = datetime.fromtimestamp(msg.get("timestamp", 0) / 1000).strftime("%H:%M:%S") if msg.get("timestamp") else "Unknown"
            direction = "←" if msg["direction"] == "inbound" else "→"
            print(f"[{ts}] {direction} {msg.get('text', 'No text')[:80]}...")
    
    elif cmd == "search" and len(sys.argv) >= 3:
        query = sys.argv[2]
        results = search_threads(query)
        print(f"\nFound {len(results)} threads matching '{query}':\n")
        for number, messages in results:
            print(f"\n{number} ({len(messages)} matches):")
            for msg in messages[:3]:  # Show first 3 matches
                ts = datetime.fromtimestamp(msg.get("timestamp", 0) / 1000).strftime("%Y-%m-%d %H:%M") if msg.get("timestamp") else "Unknown"
                print(f"  [{ts}] {msg.get('text', '')[:60]}...")
    
    elif cmd == "unread":
        threads = get_all_threads()
        unread = [t for t in threads if t.get("unread_count", 0) > 0]
        print(f"\n{len(unread)} threads with unread messages:\n")
        for t in unread:
            print(f"  {t['phone_number']} ({t.get('contact_name', 'Unknown')}): {t['unread_count']} unread")
    
    else:
        print("Unknown command. Usage: python3 sms_storage.py [migrate|list|thread <number>|search <query>|unread]")
