#!/usr/bin/env python3
"""xai-search - Search X/Twitter and web using xAI's agentic search."""

import sys
import os

def main():
    if len(sys.argv) < 3:
        print("Usage: xai-search <web|x|both> \"query\"")
        print("  web  - Search the web only")
        print("  x    - Search X/Twitter only")
        print("  both - Search both web and X")
        sys.exit(1)
    
    # Try to import xai_sdk
    try:
        from xai_sdk import Client
        from xai_sdk.chat import user
        from xai_sdk.tools import web_search, x_search
    except ImportError:
        print("Error: xai-sdk not installed.")
        print("Install it with: pip install xai-sdk")
        sys.exit(1)
    
    mode = sys.argv[1]
    query = " ".join(sys.argv[2:])
    
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("Error: XAI_API_KEY not set")
        sys.exit(1)
    
    tools = []
    if mode in ("web", "both"):
        tools.append(web_search())
    if mode in ("x", "both"):
        tools.append(x_search())
    
    if not tools:
        print(f"Unknown mode: {mode} (use web, x, or both)")
        sys.exit(1)
    
    client = Client(api_key=api_key)
    chat = client.chat.create(
        model="grok-4-1-fast",  # grok-4 required for server-side tools
        tools=tools,
    )
    
    chat.append(user(query))
    
    # Stream and collect response
    full_response = ""
    for response, chunk in chat.stream():
        if chunk.content:
            full_response += chunk.content
            print(chunk.content, end="", flush=True)
    
    print()  # newline at end
    
    # Print citations if any
    if response.citations:
        print("\n--- Sources ---")
        for i, url in enumerate(response.citations[:5], 1):
            print(f"[{i}] {url}")

if __name__ == "__main__":
    main()
