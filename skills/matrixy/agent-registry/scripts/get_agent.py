#!/usr/bin/env python3
"""
Get Agent Script

Loads the full content of a specific agent from the registry.
This is the lazy-loading mechanism that retrieves agent instructions on demand.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Optional

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

def find_agent(registry: Dict, name: str) -> Optional[Dict]:
    """Find an agent by name (case-insensitive, partial match)."""
    agents = registry.get('agents', [])
    name_lower = name.lower()
    
    # Exact match first
    for agent in agents:
        if agent['name'].lower() == name_lower:
            return agent
    
    # Partial match
    matches = [a for a in agents if name_lower in a['name'].lower()]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(f"Multiple agents match '{name}':", file=sys.stderr)
        for m in matches:
            print(f"  - {m['name']}", file=sys.stderr)
        print("\nPlease specify the exact name.", file=sys.stderr)
        return None
    
    return None

def load_agent_content(agent: Dict) -> Optional[str]:
    """Load the full content of an agent file."""
    skill_dir = get_skill_dir()
    
    # Try relative path first
    agent_path = skill_dir / agent['path']
    
    # If not found, try as absolute
    if not agent_path.exists():
        agent_path = Path(agent['path'])
    
    if not agent_path.exists():
        print(f"Error: Agent file not found: {agent['path']}", file=sys.stderr)
        return None
    
    try:
        return agent_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading agent file: {e}", file=sys.stderr)
        return None

def format_agent_output(agent: Dict, content: str, raw: bool = False) -> str:
    """Format agent content for output."""
    if raw:
        return content
    
    lines = []
    lines.append("=" * 70)
    lines.append(f"AGENT: {agent['name']}")
    lines.append(f"Tokens: ~{agent.get('token_estimate', 0):,}")
    lines.append("=" * 70)
    lines.append("")
    lines.append(content)
    lines.append("")
    lines.append("=" * 70)
    lines.append("END OF AGENT INSTRUCTIONS")
    lines.append("=" * 70)
    
    return "\n".join(lines)

def format_json_output(agent: Dict, content: str) -> str:
    """Format as JSON."""
    return json.dumps({
        'name': agent['name'],
        'summary': agent.get('summary', ''),
        'token_estimate': agent.get('token_estimate', 0),
        'keywords': agent.get('keywords', []),
        'content': content
    }, indent=2)

def list_available_agents(registry: Dict) -> str:
    """List available agents when none specified."""
    agents = registry.get('agents', [])
    if not agents:
        return "No agents in registry."
    
    lines = ["Available agents:"]
    for agent in sorted(agents, key=lambda x: x['name']):
        lines.append(f"  - {agent['name']}: {agent.get('summary', '')[:50]}...")
    
    lines.append("")
    lines.append("Usage: python get_agent.py <agent-name>")
    return "\n".join(lines)

def main():
    """Main entry point."""
    args = sys.argv[1:]
    
    # Parse options
    json_output = '--json' in args
    raw_output = '--raw' in args
    
    if json_output:
        args.remove('--json')
    if raw_output:
        args.remove('--raw')
    
    if '--help' in args or '-h' in args:
        print("Usage: python get_agent.py <agent-name> [OPTIONS]")
        print("")
        print("Loads the full content of a specific agent.")
        print("")
        print("Arguments:")
        print("  agent-name    Name of the agent to load (case-insensitive)")
        print("")
        print("Options:")
        print("  --json        Output as JSON with metadata")
        print("  --raw         Output raw content without headers")
        print("  --help, -h    Show this help")
        print("")
        print("Examples:")
        print("  python get_agent.py code-reviewer")
        print("  python get_agent.py security --json")
        return
    
    # Load registry
    registry = load_registry()
    if not registry:
        sys.exit(1)
    
    # Check if agent name provided
    if not args:
        print(list_available_agents(registry))
        sys.exit(0)
    
    agent_name = ' '.join(args)
    
    # Find agent
    agent = find_agent(registry, agent_name)
    if not agent:
        print(f"Error: Agent '{agent_name}' not found.", file=sys.stderr)
        print("", file=sys.stderr)
        print(list_available_agents(registry), file=sys.stderr)
        sys.exit(1)
    
    # Load content
    content = load_agent_content(agent)
    if not content:
        sys.exit(1)
    
    # Output
    if json_output:
        print(format_json_output(agent, content))
    else:
        print(format_agent_output(agent, content, raw=raw_output))

if __name__ == "__main__":
    main()
