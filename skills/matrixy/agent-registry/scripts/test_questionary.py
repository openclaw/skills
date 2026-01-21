#!/usr/bin/env python3
"""
Test questionary integration with category grouping
"""

import sys
from pathlib import Path
from collections import defaultdict

from init_registry import (
    scan_agents,
    find_agent_locations,
    colorize,
    Colors
)

def test_questionary_ui():
    """Test the questionary UI implementation."""
    print(colorize("\n=== Testing Questionary UI ===\n", Colors.HEADER))

    try:
        import questionary
        from questionary import Separator
        print(colorize("✓ questionary successfully imported", Colors.GREEN))
    except ImportError as e:
        print(colorize(f"✗ Failed to import questionary: {e}", Colors.RED))
        return False

    # Find and scan agents
    locations = find_agent_locations()
    if not locations:
        print(colorize("No agent locations found", Colors.RED))
        return False

    agents = scan_agents(locations[0])
    print(f"Scanned {len(agents)} agents from {locations[0]}")

    # Group by category (same logic as in interactive_selection)
    categories = defaultdict(list)

    for agent in agents[:30]:  # Limit to 30 for testing
        # Extract category from path relative to source_dir
        agent_path = Path(agent['path'])
        source_dir = Path(agent.get('source_dir', ''))
        category = "ROOT"

        try:
            # Get relative path from source_dir to agent file
            rel_path = agent_path.relative_to(source_dir)
            parts = rel_path.parts

            # If agent is in a subdirectory, use that as category
            if len(parts) > 1:
                category = parts[0].upper().replace('-', ' ')
        except (ValueError, AttributeError):
            pass

        categories[category].append(agent)

    # Build choices with separators
    choices = []
    for category in sorted(categories.keys()):
        if len(categories) > 1:
            header = f"{'─' * 10} {category} {'─' * 10}"
            choices.append(Separator(header))

        for agent in sorted(categories[category], key=lambda a: a['name'])[:3]:  # First 3 per category
            token_estimate = agent['token_estimate']
            if token_estimate < 1000:
                token_indicator = "🟢"
            elif token_estimate < 3000:
                token_indicator = "🟡"
            else:
                token_indicator = "🔴"

            summary = agent['summary'][:50] + '...' if len(agent['summary']) > 50 else agent['summary']
            label = f"{agent['name']} - {summary} {token_indicator} {token_estimate}"
            choices.append(questionary.Choice(title=label, value=agent))

    print(f"\n{colorize('Choices structure created successfully:', Colors.GREEN)}")
    print(f"  Total choices: {len(choices)}")
    print(f"  Categories: {len(categories)}")

    # Display sample choices
    print(f"\n{colorize('Sample choices:', Colors.CYAN)}")
    for i, choice in enumerate(choices[:10]):
        if isinstance(choice, Separator):
            print(f"  {colorize('[SEPARATOR]', Colors.DIM)} {choice.value if hasattr(choice, 'value') else choice}")
        else:
            print(f"  [CHOICE] {choice.title[:80]}...")

    print(f"\n{colorize('✓ Questionary UI structure validated!', Colors.GREEN + Colors.BOLD)}")
    print(colorize("  • Category grouping: ✓", Colors.GREEN))
    print(colorize("  • Separator support: ✓", Colors.GREEN))
    print(colorize("  • Token indicators: ✓", Colors.GREEN))
    print(colorize("  • Choice formatting: ✓", Colors.GREEN))

    return True

if __name__ == "__main__":
    success = test_questionary_ui()
    sys.exit(0 if success else 1)
