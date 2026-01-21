#!/usr/bin/env python3
"""
List Agents Script

Lists all agents in the registry with their summaries and metadata.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Optional, List

def get_skill_dir() -> Path:
    """Get the directory where this skill is installed."""
    return Path(__file__).parent.parent

def get_registry_path() -> Path:
    """Get the path to registry.json."""
    return get_skill_dir() / "references" / "registry.json"

def load_registry() -> Optional[Dict]:
    """Load the registry index."""
    registry_path = get_registry_path()
    
    if not registry_path.exists():
        print("Error: Registry not found. Run 'python scripts/init_registry.py' first.", file=sys.stderr)
        return None
    
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading registry: {e}", file=sys.stderr)
        return None

def format_table(agents: List[Dict]) -> str:
    """Format agents as a table."""
    if not agents:
        return "No agents registered.\n\nRun 'python scripts/init_registry.py' to set up the registry."
    
    lines = []
    lines.append(f"{'Agent Name':<25} {'Tokens':<10} {'Summary'}")
    lines.append("-" * 80)
    
    total_tokens = 0
    for agent in sorted(agents, key=lambda x: x['name']):
        name = agent['name'][:24]
        tokens = agent.get('token_estimate', 0)
        total_tokens += tokens
        summary = agent.get('summary', '')[:42]
        if len(agent.get('summary', '')) > 42:
            summary += '...'
        
        lines.append(f"{name:<25} {tokens:<10,} {summary}")
    
    lines.append("-" * 80)
    lines.append(f"Total: {len(agents)} agents, {total_tokens:,} tokens (saved from preloading)")
    
    return "\n".join(lines)

def format_detailed(agents: List[Dict]) -> str:
    """Format agents with full details."""
    if not agents:
        return "No agents registered."
    
    lines = []
    total_tokens = 0
    
    for agent in sorted(agents, key=lambda x: x['name']):
        lines.append(f"╭─ {agent['name']} {'─' * (50 - len(agent['name']))}")
        lines.append(f"│ Summary: {agent.get('summary', 'No description')}")
        lines.append(f"│ Tokens:  ~{agent.get('token_estimate', 0):,}")
        lines.append(f"│ Keywords: {', '.join(agent.get('keywords', [])[:8])}")
        lines.append(f"│ Path:    {agent.get('path', 'unknown')}")
        lines.append("╰" + "─" * 55)
        lines.append("")
        total_tokens += agent.get('token_estimate', 0)
    
    lines.append(f"Total: {len(agents)} agents | {total_tokens:,} tokens saved by lazy loading")
    
    return "\n".join(lines)

def format_json(registry: Dict) -> str:
    """Format as JSON."""
    return json.dumps({
        'agents': registry.get('agents', []),
        'stats': registry.get('stats', {}),
        'generated_at': registry.get('generated_at', '')
    }, indent=2)

def format_simple(agents: List[Dict]) -> str:
    """Format as simple name list."""
    return "\n".join(agent['name'] for agent in sorted(agents, key=lambda x: x['name']))

def main():
    """Main entry point."""
    # Parse arguments
    args = sys.argv[1:]
    
    output_format = 'table'
    if '--json' in args:
        output_format = 'json'
    elif '--detailed' in args or '-d' in args:
        output_format = 'detailed'
    elif '--simple' in args or '-s' in args:
        output_format = 'simple'
    elif '--help' in args or '-h' in args:
        print("Usage: python list_agents.py [OPTIONS]")
        print("")
        print("Options:")
        print("  --detailed, -d  Show full details for each agent")
        print("  --simple, -s    Show just agent names")
        print("  --json          Output as JSON")
        print("  --help, -h      Show this help")
        return
    
    # Load registry
    registry = load_registry()
    if not registry:
        sys.exit(1)
    
    agents = registry.get('agents', [])
    
    # Output
    if output_format == 'json':
        print(format_json(registry))
    elif output_format == 'detailed':
        print(format_detailed(agents))
    elif output_format == 'simple':
        print(format_simple(agents))
    else:
        print(format_table(agents))

if __name__ == "__main__":
    main()
