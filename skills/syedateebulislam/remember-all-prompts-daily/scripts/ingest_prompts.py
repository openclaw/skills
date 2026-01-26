#!/usr/bin/env python3
"""
Ingest archived prompts from previous session.
Triggered at session start (1% token usage).
"""

import os
from datetime import datetime
from pathlib import Path

def read_latest_archive():
    """Read the most recent session from archive."""
    archive_path = Path.home() / ".clawd" / "memory" / "remember-all-prompts-daily.md"
    
    if not archive_path.exists():
        print("No archive found")
        return None
    
    content = archive_path.read_text()
    
    # Parse the file to get the latest session
    lines = content.split('\n')
    latest_session = []
    in_session = False
    
    for line in reversed(lines):
        if line.startswith("###"):
            in_session = True
            latest_session.insert(0, line)
        elif in_session and (line.startswith("##") or line.startswith("#")):
            break
        elif in_session:
            latest_session.insert(0, line)
    
    return '\n'.join(latest_session) if latest_session else None

def format_for_ingestion(session_content):
    """Format archived session for ingestion as context."""
    if not session_content:
        return None
    
    ingest_text = """
---
## 📚 PREVIOUS SESSION CONTEXT (Archived)

This is your previous conversation, archived before token compaction. Continue naturally from here.

"""
    
    ingest_text += session_content
    
    ingest_text += """
---

"""
    
    return ingest_text

def create_ingestion_summary():
    """Create summary to inject into new session."""
    latest = read_latest_archive()
    if not latest:
        return None
    
    formatted = format_for_ingestion(latest)
    return formatted

def save_ingestion_prompt(content):
    """Save the ingestion prompt to a file for manual reference."""
    ingest_file = Path.home() / ".clawd" / "memory" / ".session-ingest.md"
    ingest_file.parent.mkdir(parents=True, exist_ok=True)
    ingest_file.write_text(content)
    print(f"✅ Ingestion context saved to {ingest_file}")
    return ingest_file

if __name__ == "__main__":
    print("🔍 Checking for archived prompts...")
    
    summary = create_ingestion_summary()
    if summary:
        # Save to file
        ingest_file = save_ingestion_prompt(summary)
        
        # Print for user to see
        print("\n📖 Previous Session Context:")
        print("=" * 80)
        print(summary)
        print("=" * 80)
        print("\n✅ Ready to continue! Your previous context has been loaded.")
        print(f"File: {ingest_file}")
    else:
        print("No previous session to ingest (fresh start)")
