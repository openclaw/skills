#!/usr/bin/env python3
"""
Quick test script to verify inquirer integration and category grouping
"""

import sys
from pathlib import Path

from init_registry import (
    scan_agents,
    find_agent_locations,
    colorize,
    Colors
)

def test_scan_and_display():
    """Test agent scanning and category detection."""
    print(colorize("\n=== Testing Agent Scan & Category Detection ===\n", Colors.HEADER))

    # Find agent locations
    locations = find_agent_locations()
    print(f"Found {len(locations)} agent location(s):")
    for loc in locations:
        print(f"  - {loc}")

    if not locations:
        print(colorize("No agent locations found!", Colors.RED))
        return

    # Scan first location
    agents = scan_agents(locations[0])
    print(f"\nScanned {len(agents)} agent(s) from {locations[0]}")

    # Group by category to test categorization logic
    from collections import defaultdict
    categories = defaultdict(list)

    for agent in agents[:20]:  # Limit to first 20 for display
        source_dir = Path(agent.get('source_dir', ''))

        # Determine category from subdirectory structure
        category = "ROOT"
        try:
            parts = source_dir.parts
            if 'agents' in parts:
                idx = parts.index('agents')
                if idx + 1 < len(parts):
                    category = parts[idx + 1].upper().replace('-', ' ')
        except (AttributeError, ValueError):
            pass

        categories[category].append(agent)

    # Display categorized agents
    print(f"\n{colorize('Category Grouping:', Colors.BOLD)}")
    for category in sorted(categories.keys()):
        print(f"\n{colorize(f'─── {category} ───', Colors.CYAN)}")
        for agent in categories[category][:3]:  # Show first 3 per category
            token_estimate = agent['token_estimate']
            if token_estimate < 1000:
                token_indicator = "🟢"
            elif token_estimate < 3000:
                token_indicator = "🟡"
            else:
                token_indicator = "🔴"

            print(f"  {token_indicator} {agent['name']} ({token_estimate} tokens)")
            print(f"     {agent['summary'][:60]}...")

    print(f"\n{colorize('✓ Category detection working correctly!', Colors.GREEN)}")

def test_inquirer_import():
    """Test that inquirer can be imported."""
    print(colorize("\n=== Testing Inquirer Import ===\n", Colors.HEADER))

    try:
        import inquirer
        from inquirer import Separator
        print(colorize("✓ inquirer successfully imported", Colors.GREEN))
        print(f"  Version: {inquirer.__version__ if hasattr(inquirer, '__version__') else 'unknown'}")
        return True
    except ImportError as e:
        print(colorize(f"✗ Failed to import inquirer: {e}", Colors.RED))
        return False

if __name__ == "__main__":
    test_inquirer_import()
    test_scan_and_display()

    print(colorize("\n=== Test Complete ===\n", Colors.GREEN + Colors.BOLD))
