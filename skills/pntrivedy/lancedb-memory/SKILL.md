#!/usr/bin/env python3
"""
LanceDB integration for long-term memory management.
Provides vector search and semantic memory capabilities.
"""

import os
import json
import lancedb
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

class LanceMemoryDB:
    """LanceDB wrapper for long-term memory storage and retrieval."""
    
    def __init__(self, db_path: str = "/Users/prerak/clawd/memory/lancedb"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.db = lancedb.connect(self.db_path)
        
        # Ensure memory table exists
        if "memory" not in self.db.table_names():
            self._create_memory_table()
    
    def _create_memory_table(self):
        """Create the memory table with appropriate schema."""
        schema = [
            {"name": "id", "type": "int", "nullable": False},
            {"name": "timestamp", "type": "timestamp", "nullable": False},
            {"name": "content", "type": "str", "nullable": False},
            {"name": "category", "type": "str", "nullable": True},
            {"name": "tags", "type": "str[]", "nullable": True},
            {"name": "importance", "type": "int", "nullable": True},
            {"name": "metadata", "type": "json", "nullable": True},
        ]
        
        self.db.create_table("memory", schema=schema)
    
    def add_memory(self, content: str, category: str = "general", tags: List[str] = None, 
                   importance: int = 5, metadata: Dict[str, Any] = None) -> int:
        """Add a new memory entry."""
        table = self.db.open_table("memory")
        
        # Get next ID
        max_id = table.to_pandas()["id"].max() if len(table) > 0 else 0
        new_id = max_id + 1
        
        # Insert new memory
        memory_data = {
            "id": new_id,
            "timestamp": datetime.now(),
            "content": content,
            "category": category,
            "tags": tags or [],
            "importance": importance,
            "metadata": metadata or {}
        }
        
        table.add([memory_data])
        return new_id
    
    def search_memories(self, query: str, category: str = None, limit: int = 10) -> List[Dict]:
        """Search memories using vector similarity."""
        table = self.db.open_table("memory")
        
        # Build filter
        where_clause = []
        if category:
            where_clause.append(f"category = '{category}'")
        
        filter_expr = " AND ".join(where_clause) if where_clause else None
        
        # Vector search
        results = table.vector_search(query).limit(limit).where(filter_expr).to_list()
        
        return results
    
    def get_memories_by_category(self, category: str, limit: int = 50) -> List[Dict]:
        """Get memories by category."""
        table = self.db.open_table("memory")
        df = table.to_pandas()
        filtered = df[df["category"] == category].head(limit)
        return filtered.to_dict("records")
    
    def get_memory_by_id(self, memory_id: int) -> Optional[Dict]:
        """Get a specific memory by ID."""
        table = self.db.open_table("memory")
        df = table.to_pandas()
        result = df[df["id"] == memory_id]
        return result.to_dict("records")[0] if len(result) > 0 else None
    
    def update_memory(self, memory_id: int, **kwargs) -> bool:
        """Update a memory entry."""
        table = self.db.open_table("memory")
        
        valid_fields = ["content", "category", "tags", "importance", "metadata"]
        updates = {k: v for k, v in kwargs.items() if k in valid_fields}
        
        if not updates:
            return False
        
        # Convert to proper types for LanceDB
        if "tags" in updates and isinstance(updates["tags"], list):
            updates["tags"] = str(updates["tags"]).replace("'", '"')
        
        table.update(updates, where=f"id = {memory_id}")
        return True
    
    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory entry."""
        table = self.db.open_table("memory")
        current_count = len(table)
        table.delete(f"id = {memory_id}")
        return len(table) < current_count
    
    def get_all_categories(self) -> List[str]:
        """Get all unique categories."""
        table = self.db.open_table("memory")
        df = table.to_pandas()
        return df["category"].dropna().unique().tolist()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory storage."""
        table = self.db.open_table("memory")
        df = table.to_pandas()
        
        return {
            "total_memories": len(df),
            "categories": len(self.get_all_categories()),
            "by_category": df["category"].value_counts().to_dict(),
            "date_range": {
                "earliest": df["timestamp"].min().isoformat() if len(df) > 0 else None,
                "latest": df["timestamp"].max().isoformat() if len(df) > 0 else None
            }
        }

# Global instance
lancedb_memory = LanceMemoryDB()

def add_memory(content: str, category: str = "general", tags: List[str] = None, 
               importance: int = 5, metadata: Dict[str, Any] = None) -> int:
    """Add a memory to the LanceDB store."""
    return lancedb_memory.add_memory(content, category, tags, importance, metadata)

def search_memories(query: str, category: str = None, limit: int = 10) -> List[Dict]:
    """Search memories using semantic similarity."""
    return lancedb_memory.search_memories(query, category, limit)

def get_memories_by_category(category: str, limit: int = 50) -> List[Dict]:
    """Get memories by category."""
    return lancedb_memory.get_memories_by_category(category, limit)

def get_memory_stats() -> Dict[str, Any]:
    """Get memory storage statistics."""
    return lancedb_memory.get_memory_stats()

# Example usage
if __name__ == "__main__":
    # Test the database
    print("Testing LanceDB memory integration...")
    
    # Add a test memory
    test_id = add_memory(
        content="This is a test memory for LanceDB integration",
        category="test",
        tags=["lancedb", "integration", "test"],
        importance=8
    )
    print(f"Added memory with ID: {test_id}")
    
    # Search for memories
    results = search_memories("test memory")
    print(f"Search results: {len(results)} memories found")
    
    # Get stats
    stats = get_memory_stats()
    print(f"Memory stats: {stats}")