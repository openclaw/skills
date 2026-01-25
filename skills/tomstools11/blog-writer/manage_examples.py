#!/usr/bin/env python3
"""
Utility script for managing the blog examples library.
Helps identify old examples to prune when the library exceeds the limit.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent.parent / "references" / "blog-examples"
MAX_EXAMPLES = 20
PRUNE_COUNT = 5


def list_examples():
    """List all blog examples sorted by date (oldest first)."""
    examples = []
    for f in EXAMPLES_DIR.glob("*.md"):
        # Extract date from filename (YYYY-MM-DD-slug.md)
        try:
            date_str = f.stem[:10]
            date = datetime.strptime(date_str, "%Y-%m-%d")
            examples.append((date, f.name))
        except ValueError:
            # Skip files that don't match the naming convention
            continue
    
    return sorted(examples, key=lambda x: x[0])


def check_library():
    """Check library status and recommend pruning if needed."""
    examples = list_examples()
    count = len(examples)
    
    print(f"Blog Examples Library Status")
    print(f"=" * 40)
    print(f"Total examples: {count}")
    print(f"Maximum allowed: {MAX_EXAMPLES}")
    print()
    
    if count > MAX_EXAMPLES:
        print(f"⚠️  Library exceeds limit by {count - MAX_EXAMPLES} files")
        print(f"Recommend removing the {PRUNE_COUNT} oldest examples:")
        print()
        for i, (date, name) in enumerate(examples[:PRUNE_COUNT]):
            print(f"  {i+1}. {name} ({date.strftime('%B %d, %Y')})")
    else:
        print(f"✓ Library is within limits ({MAX_EXAMPLES - count} slots available)")
    
    print()
    print("All examples (oldest first):")
    print("-" * 40)
    for date, name in examples:
        print(f"  {name}")


def prune_oldest(dry_run=True):
    """Remove the oldest examples to bring library under limit."""
    examples = list_examples()
    count = len(examples)
    
    if count <= MAX_EXAMPLES:
        print("Library is within limits. No pruning needed.")
        return
    
    to_remove = examples[:PRUNE_COUNT]
    
    if dry_run:
        print(f"DRY RUN - Would remove {len(to_remove)} files:")
    else:
        print(f"Removing {len(to_remove)} oldest files:")
    
    for date, name in to_remove:
        filepath = EXAMPLES_DIR / name
        if dry_run:
            print(f"  Would remove: {name}")
        else:
            filepath.unlink()
            print(f"  Removed: {name}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "prune":
        dry_run = "--execute" not in sys.argv
        prune_oldest(dry_run=dry_run)
    else:
        check_library()
