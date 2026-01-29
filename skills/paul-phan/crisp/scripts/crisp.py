#!/usr/bin/env python3
"""
Crisp API CLI - Customer Support Interface

Usage:
  python3 crisp.py inbox list [--page N] [--max N] [--filter FILTER]
  python3 crisp.py conversation get <session_id>
  python3 crisp.py messages get <session_id> [--max N]
  python3 crisp.py message send <session_id> "message text"
  python3 crisp.py conversation read <session_id>
  python3 crisp.py conversation resolve <session_id>
  python3 crisp.py conversations search "query" [--filter FILTER] [--max N]
"""

import sys
import os
import json
import base64
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)

# Configuration
API_BASE = "https://api.crisp.chat/v1/website"
WEBSITE_ID = os.environ.get("CRISP_WEBSITE_ID")
TOKEN_ID = os.environ.get("CRISP_TOKEN_ID")
TOKEN_KEY = os.environ.get("CRISP_TOKEN_KEY")

if not WEBSITE_ID or not TOKEN_ID or not TOKEN_KEY:
    print("❌ Error: CRISP_WEBSITE_ID, CRISP_TOKEN_ID, and CRISP_TOKEN_KEY environment variables required")
    print("Set them with:")
    print("  export CRISP_WEBSITE_ID='your_website_id'")
    print("  export CRISP_TOKEN_ID='your_token_identifier'")
    print("  export CRISP_TOKEN_KEY='your_token_key'")
    sys.exit(1)

# Create basic auth header
auth_str = f"{TOKEN_ID}:{TOKEN_KEY}"
auth_bytes = auth_str.encode('utf-8')
auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
headers = {
    "Authorization": f"Basic {auth_b64}",
    "Content-Type": "application/json",
    "X-Crisp-Tier": "plugin"
}

def api_request(method: str, endpoint: str, data=None):
    """Make authenticated request to Crisp API."""
    url = f"{API_BASE}/{WEBSITE_ID}/{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, params=data, timeout=10)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PATCH":
            resp = requests.patch(url, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=10)
        else:
            return {"error": True, "reason": f"Unknown method: {method}"}
        
        return resp.json()
    except requests.exceptions.RequestException as e:
        return {"error": True, "reason": str(e)}
    except json.JSONDecodeError as e:
        return {"error": True, "reason": f"Invalid JSON response: {e}"}

def inbox_list(page=1, per_page=20, filter_type=None):
    """List conversations in inbox."""
    endpoint = f"conversations/{page}"
    params = {"per_page": min(max(20, per_page), 50)}
    
    if filter_type:
        if filter_type == "unread":
            params["filter_unread"] = "1"
        elif filter_type == "unresolved":
            params["filter_not_resolved"] = "1"
        elif filter_type == "resolved":
            params["filter_resolved"] = "1"
        elif filter_type == "assigned":
            # params["filter_assigned"] = ACCOUNT_ID  # Disabled as we don't have user ID
            pass
        elif filter_type == "unassigned":
            params["filter_unassigned"] = "1"
    
    result = api_request("GET", endpoint, params)
    
    if result.get("error"):
        print(f"❌ API Error: {result.get('reason')}")
        print(f"🔗 URL: {API_BASE}/{WEBSITE_ID}/{endpoint}")
        return []
    
    return result.get("data", [])

def conversation_get(session_id: str):
    """Get conversation details."""
    endpoint = f"conversation/{session_id}"
    result = api_request("GET", endpoint)
    
    if result.get("error"):
        print(f"❌ Error: {result.get('reason')}")
        return None
    
    return result.get("data")

def messages_get(session_id: str, max_results: int = 20):
    """Get messages in conversation."""
    endpoint = f"conversation/{session_id}/messages"
    params = {} if max_results == 0 else {"timestamp_before": None}  # Simplified
    
    result = api_request("GET", endpoint, params)
    
    if result.get("error"):
        print(f"❌ Error: {result.get('reason')}")
        return None
    
    messages = result.get("data", [])
    if max_results > 0:
        messages = messages[:max_results]
    return messages

def message_send(session_id: str, text: str):
    """Send a text message to conversation."""
    endpoint = f"conversation/{session_id}/message"
    
    payload = {
        "type": "text",
        "content": text,
        "from": "operator",
        "origin": "chat"
    }
    
    result = api_request("POST", endpoint, payload)
    
    if result.get("error"):
        print(f"❌ Error: {result.get('reason')}")
        return False
    
    print(f"✅ Message sent to conversation {session_id}")
    return True

def conversation_mark_read(session_id: str):
    """Mark conversation as read."""
    endpoint = f"conversation/{session_id}/read"
    
    payload = {
        "from": "operator",
        "read": True
    }
    
    result = api_request("PATCH", endpoint, payload)
    
    if result.get("error"):
        print(f"❌ Error: {result.get('reason')}")
        return False
    
    print(f"✅ Conversation {session_id} marked as read")
    return True

def conversation_resolve(session_id: str):
    """Resolve conversation."""
    endpoint = f"conversation/{session_id}/meta"
    
    payload = {
        "state": "resolved"
    }
    
    result = api_request("PATCH", endpoint, payload)
    
    if result.get("error"):
        print(f"❌ Error: {result.get('reason')}")
        return False
    
    print(f"✅ Conversation {session_id} resolved")
    return True

def conversations_search(query: str, filter_type: Optional[str] = None, max_results: int = 10):
    """Search conversations."""
    endpoint = f"conversations/1"
    params = {
        "per_page": min(max(20, max_results), 50),
        "search_query": query,
        "search_type": "text"
    }
    
    if filter_type:
        if filter_type == "unresolved":
            params["filter_not_resolved"] = "1"
        elif filter_type == "resolved":
            params["filter_resolved"] = "1"
    
    result = api_request("GET", endpoint, params)
    
    if result.get("error"):
        print(f"❌ Error: {result.get('reason')}")
        return None
    
    conversations = result.get("data", [])
    if max_results > 0:
        conversations = conversations[:max_results]
    return conversations

def format_conversation(conv, brief=False):
    """Format conversation for display."""
    session_id = conv.get("session_id", "N/A")
    state = conv.get("state", "unknown")
    
    # Get message excerpt safely
    preview = conv.get("preview_message", {})
    if preview and isinstance(preview, dict):
        last_msg = preview.get("excerpt", "No messages")
    else:
        last_msg = conv.get("last_message", "No messages")
        
    meta = conv.get("meta", {})
    email = meta.get("email", "N/A")
    nickname = meta.get("nickname", "Visitor")
    
    status_emoji = "🟢" if state == "unresolved" else "✅"
    
    if brief:
        return f"{status_emoji} {session_id}: {nickname} ({email or 'Guest'}) - {last_msg[:50]}"
    
    return f"""
{'─'*60}
📋 Conversation: {session_id}
   State: {status_emoji} {state}
   Visitor: {nickname}
   Email: {email}
   Last message: {last_msg[:100]}
   Created: {conv.get('created_at', 'N/A')}
   Updated: {conv.get('updated_at', 'N/A')}
"""

def format_message(msg):
    """Format message for display."""
    from_user = msg.get("from", "user")
    sender = "👤 Visitor" if from_user == "user" else "💬 Operator"
    content = msg.get("content", "")
    
    if isinstance(content, str):
        text = content
    else:
        # Handle different message types
        text = content.get("text", str(content))
    
    timestamp = msg.get("timestamp", "N/A")
    
    return f"""
{sender} [{timestamp}]:
{text[:200]}
"""

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "websites":
        """List websites available to this token."""
        endpoint = "conversations/1"
        result = api_request("GET", endpoint, {"per_page": 1})
        
        if result.get("error"):
            print(f"❌ API Error: {result.get('reason')}")
            return
        
        data = result.get("data", {})
        print(f"🌐 Websites:")
        print(f"  Website ID: {WEBSITE_ID}")
        if result.get("data"):
            print(f"  Response data structure: {json.dumps(result, indent=2)}")
        else:
            print(f"  Raw response: {json.dumps(result, indent=2)}")
        return
    
    if command == "inbox":
        if len(sys.argv) < 3 or sys.argv[2] != "list":
            print(__doc__)
            sys.exit(1)
        
        page = 1
        max_results = 20
        filter_type = None
        
        for i in range(3, len(sys.argv)):
            arg = sys.argv[i]
            if arg.startswith("--page="):
                page = int(arg.split("=")[1])
            elif arg.startswith("--max="):
                max_results = int(arg.split("=")[1])
            elif arg.startswith("--filter="):
                filter_type = arg.split("=")[1]
            elif arg == "--json":
                # Output JSON
                convs = inbox_list(page, max_results, filter_type)
                print(json.dumps(convs, indent=2))
                return
        
        conversations = inbox_list(page, max_results, filter_type)
        print(f"\n📬 Inbox (page {page}) - {len(conversations)} conversations")
        for conv in conversations:
            print(format_conversation(conv, brief=True))
    
    elif command == "conversation":
        if len(sys.argv) < 4:
            print(__doc__)
            sys.exit(1)
        
        action = sys.argv[2]
        session_id = sys.argv[3]
        
        if action == "get":
            conv = conversation_get(session_id)
            if conv:
                print(json.dumps(conv, indent=2))
        
        elif action == "read":
            conversation_mark_read(session_id)
        
        elif action == "resolve":
            conversation_resolve(session_id)
        
        else:
            print(f"❌ Unknown conversation action: {action}")
            print(__doc__)
    
    elif command == "messages":
        if len(sys.argv) < 4 or sys.argv[2] != "get":
            print(__doc__)
            sys.exit(1)
        
        session_id = sys.argv[3]
        max_results = 20
        
        for i in range(4, len(sys.argv)):
            arg = sys.argv[i]
            if arg.startswith("--max="):
                max_results = int(arg.split("=")[1])
            elif arg == "--json":
                msgs = messages_get(session_id, max_results)
                print(json.dumps(msgs, indent=2))
                return
        
        messages = messages_get(session_id, max_results)
        if messages:
            print(f"\n💬 Messages in conversation {session_id}")
            for msg in messages:
                print(format_message(msg))
    
    elif command == "message":
        if len(sys.argv) < 4 or sys.argv[2] != "send":
            print(__doc__)
            sys.exit(1)
        
        session_id = sys.argv[3]
        message_text = " ".join(sys.argv[4:])
        message_send(session_id, message_text)
    
    elif command == "conversations":
        if len(sys.argv) < 4 or sys.argv[2] != "search":
            print(__doc__)
            sys.exit(1)
        
        query = sys.argv[3]
        filter_type = None
        max_results = 10
        
        for i in range(4, len(sys.argv)):
            arg = sys.argv[i]
            if arg.startswith("--filter="):
                filter_type = arg.split("=")[1]
            elif arg.startswith("--max="):
                max_results = int(arg.split("=")[1])
            elif arg == "--json":
                convs = conversations_search(query, filter_type, max_results)
                print(json.dumps(convs, indent=2))
                return
        
        conversations = conversations_search(query, filter_type, max_results)
        print(f"\n🔍 Search results for '{query}' - {len(conversations)} found")
        for conv in conversations:
            print(format_conversation(conv, brief=True))
    
    else:
        print(f"❌ Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
