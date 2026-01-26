#!/usr/bin/env python3
"""
LanceDB Memory Integration for Clawdbot
Integrates LanceDB with Clawdbot's memory search system
"""

import os
import json
import asyncio
import lancedb
import pyarrow as pa
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class ClawdbotLanceMemory:
    """LanceDB memory integration for Clawdbot"""
    
    def __init__(self, db_path: str = "/Users/prerak/clawd/memory/lancedb"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.db = lancedb.connect(self.db_path)
        
        # Ensure memory table exists
        if "clawdbot_memory" not in self.db.list_tables():
            self._create_memory_table()
    
    def _create_memory_table(self):
        """Create the memory table with Clawdbot-compatible schema"""
        # Create initial empty table with proper schema
        initial_data = []
        schema = pa.schema([
            pa.field("id", pa.int32(), nullable=False),
            pa.field("timestamp", pa.timestamp('ns'), nullable=False),
            pa.field("content", pa.string(), nullable=False),
            pa.field("metadata", pa.string(), nullable=True),
            pa.field("embedding", pa.list_(pa.float32()), nullable=True)
        ])
        
        table = pa.Table.from_pylist(initial_data, schema=schema)
        self.db.create_table("clawdbot_memory", data=table)
    
    async def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories using semantic similarity"""
        try:
            # For now, use text-based search since we don't have embeddings
            table = self.db.open_table("clawdbot_memory")
            
            # Use simple text filtering as fallback
            results = table.search(query).limit(limit).to_list()
            
            return results[:limit]
            
        except Exception as e:
            print(f"LanceDB search error: {e}")
            return []
    
    async def add_memory(self, content: str, metadata: Dict[str, Any] = None) -> int:
        """Add a memory to LanceDB"""
        table = self.db.open_table("clawdbot_memory")
        
        # Get next ID
        max_id = table.to_pandas()["id"].max() if len(table) > 0 else 0
        new_id = max_id + 1
        
        # Create memory entry
        memory_data = {
            "id": new_id,
            "timestamp": datetime.now(),
            "content": content,
            "metadata": metadata or {},
            "embedding": None  # Placeholder for future embeddings
        }
        
        table.add([memory_data])
        return new_id
    
    async def get_recent_memories(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent memories"""
        table = self.db.open_table("clawdbot_memory")
        df = table.to_pandas()
        recent = df.sort_values("timestamp", ascending=False).head(limit)
        return recent.to_dict("records")

# Global instance
clawdbot_lance_memory = ClawdbotLanceMemory()

# Clawdbot memory search provider
class LanceMemoryProvider:
    """Memory search provider for Clawdbot"""
    
    def __init__(self):
        self.memory_db = clawdbot_lance_memory
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories"""
        return await self.memory_db.search_memories(query, limit)
    
    async def add(self, content: str, metadata: Dict[str, Any] = None) -> int:
        """Add memory"""
        return await self.memory_db.add_memory(content, metadata)
    
    async def get_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent memories"""
        return await self.memory_db.get_recent_memories(limit)

# Create provider instance
lance_memory_provider = LanceMemoryProvider()

# Test function
async def test_lance_memory():
    """Test the LanceDB memory integration"""
    print("Testing LanceDB memory integration...")
    
    # Add test memory
    memory_id = await lance_memory_provider.add(
        content="This is a test memory for LanceDB integration",
        metadata={"type": "test", "importance": 8}
    )
    print(f"Added memory with ID: {memory_id}")
    
    # Search for memories
    results = await lance_memory_provider.search("test memory")
    print(f"Search results: {len(results)} memories found")
    
    # Get recent memories
    recent = await lance_memory_provider.get_recent(5)
    print(f"Recent memories: {len(recent)} memories")

if __name__ == "__main__":
    asyncio.run(test_lance_memory())