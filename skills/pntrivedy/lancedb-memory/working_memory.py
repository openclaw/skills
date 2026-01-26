#!/usr/bin/env python3
"""
Working LanceDB Memory Integration for Clawdbot
Simple, functional implementation that works with current LanceDB version
"""

import os
import json
import lancedb
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class WorkingLanceMemory:
    """Working LanceDB memory integration"""
    
    def __init__(self, db_path: str = "/Users/prerak/clawd/memory/lancedb"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.db = lancedb.connect(self.db_path)
        
        # Table should already exist from previous run
    
    def _create_table(self):
        """Create memory table with sample data"""
        # Create sample data with proper schema
        data = [
            {
                "id": 1,
                "timestamp": datetime.now(),
                "content": "Welcome to LanceDB memory system",
                "metadata": '{"type": "system", "importance": 10}'
            }
        ]
        
        self.db.create_table("memories", data=data)
    
    def add_memory(self, content: str, metadata: Dict[str, Any] = None) -> int:
        """Add a memory to LanceDB"""
        table = self.db.open_table("memories")
        
        # Get next ID
        if len(table) > 0:
            df = table.to_pandas()
            max_id = df["id"].max()
            new_id = max_id + 1
        else:
            new_id = 1
        
        # Add memory
        memory_data = {
            "id": new_id,
            "timestamp": datetime.now(),
            "content": content,
            "metadata": json.dumps(metadata or {})
        }
        
        table.add([memory_data])
        return new_id
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories using text similarity"""
        table = self.db.open_table("memories")
        df = table.to_pandas()
        
        # Simple text-based search
        query_lower = query.lower()
        mask = df['content'].str.lower().str.contains(query_lower, na=False)
        results = df[mask].sort_values('timestamp', ascending=False).head(limit)
        
        return results.to_dict('records')
    
    def get_all_memories(self) -> List[Dict[str, Any]]:
        """Get all memories"""
        table = self.db.open_table("memories")
        df = table.to_pandas()
        return df.sort_values('timestamp', ascending=False).to_dict('records')

# Global instance
working_memory = WorkingLanceMemory()

def add_memory(content: str, metadata: Dict[str, Any] = None) -> int:
    """Add memory to LanceDB"""
    return working_memory.add_memory(content, metadata)

def search_memories(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search memories"""
    return working_memory.search_memories(query, limit)

def get_all_memories() -> List[Dict[str, Any]]:
    """Get all memories"""
    return working_memory.get_all_memories()

# Test function
if __name__ == "__main__":
    print("Testing Working LanceDB Memory Integration...")
    
    # Add test memory
    memory_id = add_memory(
        content="This is a test memory for LanceDB integration",
        metadata={"type": "test", "importance": 8}
    )
    print(f"✅ Added memory with ID: {memory_id}")
    
    # Search for memories
    results = search_memories("test memory")
    print(f"✅ Search results: {len(results)} memories found")
    
    # Get all memories
    all_memories = get_all_memories()
    print(f"✅ Total memories: {len(all_memories)}")
    
    print("🎉 Working LanceDB integration ready!")