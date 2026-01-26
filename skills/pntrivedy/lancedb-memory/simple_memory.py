#!/usr/bin/env python3
"""
Simple LanceDB Memory Integration for Clawdbot
Works with basic data insertion and search
"""

import os
import json
import lancedb
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class SimpleLanceMemory:
    """Simple LanceDB memory integration"""
    
    def __init__(self, db_path: str = "/Users/prerak/clawd/memory/lancedb"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.db = lancedb.connect(self.db_path)
        
        # Create table if it doesn't exist
        if "memories" not in self.db.table_names():
            self._create_table()
    
    def _create_table(self):
        """Create simple memory table"""
        # Create initial data with proper schema
        data = []
        df = pd.DataFrame(data, columns=['id', 'timestamp', 'content', 'metadata'])
        table = self.db.create_table("memories", data=df)
    
    def add_memory(self, content: str, metadata: Dict[str, Any] = None) -> int:
        """Add a memory to LanceDB"""
        table = self.db.open_table("memories")
        
        # Get next ID
        if len(table) > 0:
            max_id = table.to_pandas()["id"].max()
            new_id = max_id + 1
        else:
            new_id = 1
        
        # Add memory
        memory_data = {
            'id': new_id,
            'timestamp': datetime.now(),
            'content': content,
            'metadata': json.dumps(metadata or {})
        }
        
        table.add([memory_data])
        return new_id
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories using text similarity"""
        table = self.db.open_table("memories")
        df = table.to_pandas()
        
        # Simple text-based search (can be enhanced later with embeddings)
        query_lower = query.lower()
        results = df[df['content'].str.lower().str.contains(query_lower, na=False)]
        
        # Sort by timestamp and limit results
        results = results.sort_values('timestamp', ascending=False).head(limit)
        
        return results.to_dict('records')
    
    def get_all_memories(self) -> List[Dict[str, Any]]:
        """Get all memories"""
        table = self.db.open_table("memories")
        df = table.to_pandas()
        return df.sort_values('timestamp', ascending=False).to_dict('records')

# Global instance
lance_memory = SimpleLanceMemory()

def add_memory(content: str, metadata: Dict[str, Any] = None) -> int:
    """Add memory to LanceDB"""
    return lance_memory.add_memory(content, metadata)

def search_memories(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search memories"""
    return lance_memory.search_memories(query, limit)

def get_all_memories() -> List[Dict[str, Any]]:
    """Get all memories"""
    return lance_memory.get_all_memories()

# Test function
if __name__ == "__main__":
    print("Testing Simple LanceDB Memory Integration...")
    
    # Add test memory
    memory_id = add_memory(
        content="This is a test memory for LanceDB integration",
        metadata={"type": "test", "importance": 8}
    )
    print(f"Added memory with ID: {memory_id}")
    
    # Search for memories
    results = search_memories("test memory")
    print(f"Search results: {len(results)} memories found")
    
    # Get all memories
    all_memories = get_all_memories()
    print(f"Total memories: {len(all_memories)}")
    
    print("✅ Simple LanceDB integration working!")