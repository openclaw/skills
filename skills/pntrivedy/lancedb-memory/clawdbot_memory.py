#!/usr/bin/env python3
"""
Clawdbot Memory Integration using LanceDB
This module provides memory search capabilities for Clawdbot
"""

import sys
import os
sys.path.append('/Users/prerak/clawd/skills/lancedb-memory')

from final_memory import search_memories, add_memory, get_all_memories

class ClawdbotMemoryProvider:
    """Memory provider for Clawdbot using LanceDB"""
    
    def __init__(self):
        pass
    
    async def search(self, query: str, limit: int = 10) -> list:
        """Search memories"""
        try:
            results = search_memories(query, limit)
            return results
        except Exception as e:
            print(f"Memory search error: {e}")
            return []
    
    async def add(self, content: str, metadata: dict = None) -> int:
        """Add memory"""
        try:
            return add_memory(content, metadata)
        except Exception as e:
            print(f"Memory add error: {e}")
            return -1
    
    async def get_recent(self, limit: int = 50) -> list:
        """Get recent memories"""
        try:
            return get_all_memories()[:limit]
        except Exception as e:
            print(f"Memory get recent error: {e}")
            return []

# Create provider instance
memory_provider = ClawdbotMemoryProvider()

# Test the integration
if __name__ == "__main__":
    print("Testing Clawdbot Memory Integration...")
    
    # Test search
    results = memory_provider.search("test")
    print(f"Search results: {len(results)} memories")
    
    # Test add
    memory_id = memory_provider.add(
        "This is a test memory from Clawdbot",
        {"type": "clawbot_test", "importance": 7}
    )
    print(f"Added memory ID: {memory_id}")
    
    print("✅ Clawdbot integration ready!")