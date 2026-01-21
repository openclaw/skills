#!/usr/bin/env python3
"""
Agent Registry Initialization Script

Interactively migrates agents from default Claude Code locations to the registry.
Builds a lightweight index for fast search and lazy loading.
"""

import os
import sys
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

class PaginationState:
    """Manage selections across paginated views."""

    def __init__(self, all_agents: List[Dict], items_per_page: int = 10):
        self.all_agents = all_agents
        self.items_per_page = items_per_page
        self.current_page = 0
        self.selected_agents = set()  # Track by agent name
        self.total_pages = (len(all_agents) + items_per_page - 1) // items_per_page

    def get_page_items(self, flat_items: List[tuple], page: int) -> List[tuple]:
        """Get items for specific page."""
        start = page * self.items_per_page
        end = start + self.items_per_page
        return flat_items[start:end]

    def add_selections(self, agents: List[Dict]):
        for agent in agents:
            self.selected_agents.add(agent['name'])

    def remove_selections(self, agents: List[Dict]):
        for agent in agents:
            self.selected_agents.discard(agent['name'])

    def is_selected(self, agent_name: str) -> bool:
        return agent_name in self.selected_agents

    def get_final_selection(self) -> List[Dict]:
        return [a for a in self.all_agents if a['name'] in self.selected_agents]

def build_page_choices(
    page_state: 'PaginationState',
    page_items: List[tuple],  # [(category, agent), ...]
    page_num: int
) -> List:
    """Build questionary choices for a single page."""
    import questionary
    from questionary import Separator

    choices = []

    # Header
    selected = len(page_state.selected_agents)
    total = len(page_state.all_agents)
    header = f"Page {page_num + 1}/{page_state.total_pages} | Selected: {selected}/{total}"
    choices.append(Separator(f"{'═' * len(header)}"))
    choices.append(Separator(header))
    choices.append(Separator(f"{'═' * len(header)}"))
    choices.append(Separator(""))

    # Page-level select all
    choices.append(questionary.Choice(
        title=f"✨ [SELECT ALL ON PAGE] - {len(page_items)} agents on this page",
        value="__PAGE_SELECT_ALL__",
        checked=False
    ))
    choices.append(Separator(""))

    # Agents on this page
    current_category = None
    for category, agent in page_items:
        if category != current_category:
            if current_category is not None:
                choices.append(Separator(""))
            choices.append(Separator(f"{'─' * 10} {category} {'─' * 10}"))
            current_category = category

        # Token indicator
        tokens = agent['token_estimate']
        indicator = "🟢" if tokens < 1000 else "🟡" if tokens < 3000 else "🔴"

        # Selection indicator
        prefix = "✓ " if page_state.is_selected(agent['name']) else ""

        summary = agent['summary'][:50] + '...' if len(agent['summary']) > 50 else agent['summary']
        label = f"{prefix}{agent['name']} - {summary} {indicator} {tokens}"

        choices.append(questionary.Choice(
            title=label,
            value=agent,
            checked=page_state.is_selected(agent['name'])
        ))

    # Navigation
    choices.append(Separator(""))
    choices.append(Separator(f"{'─' * 25} Navigation {'─' * 25}"))

    if page_num > 0:
        choices.append(questionary.Choice("◀ Previous Page", value="__PREV__"))

    if page_num < page_state.total_pages - 1:
        choices.append(questionary.Choice("▶ Next Page", value="__NEXT__"))

    choices.append(questionary.Choice("✅ Finish Selection", value="__FINISH__"))
    choices.append(Separator(f"{'─' * 60}"))

    return choices

def colorize(text: str, color: str) -> str:
    """Add color to text if terminal supports it."""
    if sys.stdout.isatty():
        return f"{color}{text}{Colors.ENDC}"
    return text

def get_skill_dir() -> Path:
    """Get the directory where this skill is installed."""
    return Path(__file__).parent.parent

def get_agents_dir() -> Path:
    """Get the agents directory within this skill."""
    return get_skill_dir() / "agents"

def get_registry_path() -> Path:
    """Get the path to registry.json."""
    return get_skill_dir() / "references" / "registry.json"

def find_agent_locations() -> List[Path]:
    """Find all potential agent directories."""
    locations = []
    
    # Global user agents
    home = Path.home()
    global_agents = home / ".claude" / "agents"
    if global_agents.exists():
        locations.append(global_agents)
    
    # Project-level agents (current directory)
    cwd = Path.cwd()
    project_agents = cwd / ".claude" / "agents"
    if project_agents.exists() and project_agents != global_agents:
        locations.append(project_agents)
    
    return locations

def scan_agents(directory: Path) -> List[Dict]:
    """Scan a directory for agent .md files and extract metadata."""
    agents = []
    
    if not directory.exists():
        return agents
    
    for md_file in directory.glob("**/*.md"):
        agent_info = parse_agent_file(md_file)
        if agent_info:
            agent_info['source_dir'] = str(directory)
            agents.append(agent_info)
    
    return agents

def parse_agent_file(filepath: Path) -> Optional[Dict]:
    """Parse an agent .md file and extract metadata."""
    try:
        content = filepath.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Extract name from filename
        name = filepath.stem
        
        # Try to extract description from first paragraph or YAML frontmatter
        summary = extract_summary(content)
        
        # Extract keywords from content
        keywords = extract_keywords(content)
        
        # Estimate tokens (rough: ~4 chars per token)
        token_estimate = len(content) // 4
        
        return {
            'name': name,
            'filename': filepath.name,
            'path': str(filepath),
            'summary': summary,
            'keywords': keywords,
            'token_estimate': token_estimate,
            'content_hash': hashlib.md5(content.encode()).hexdigest()[:8]
        }
    except Exception as e:
        print(colorize(f"  Warning: Could not parse {filepath}: {e}", Colors.YELLOW))
        return None

def extract_summary(content: str) -> str:
    """Extract a summary from agent content."""
    lines = content.strip().split('\n')
    
    # Skip YAML frontmatter if present
    start_idx = 0
    if lines and lines[0].strip() == '---':
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                start_idx = i + 1
                break
    
    # Find first non-empty, non-header line
    summary_lines = []
    for line in lines[start_idx:]:
        stripped = line.strip()
        if not stripped:
            if summary_lines:
                break
            continue
        if stripped.startswith('#'):
            continue
        summary_lines.append(stripped)
        if len(' '.join(summary_lines)) > 150:
            break
    
    summary = ' '.join(summary_lines)
    if len(summary) > 200:
        summary = summary[:197] + '...'
    
    return summary or "No description available"

def extract_keywords(content: str) -> List[str]:
    """Extract relevant keywords from agent content."""
    # Common technical terms to look for
    tech_terms = [
        'python', 'javascript', 'typescript', 'rust', 'go', 'java', 'ruby',
        'react', 'vue', 'angular', 'node', 'docker', 'kubernetes', 'k8s',
        'aws', 'gcp', 'azure', 'terraform', 'ansible',
        'sql', 'postgres', 'mysql', 'mongodb', 'redis',
        'api', 'rest', 'graphql', 'grpc',
        'test', 'testing', 'unittest', 'pytest', 'jest',
        'security', 'auth', 'authentication', 'authorization',
        'ci', 'cd', 'pipeline', 'deploy', 'deployment',
        'code', 'review', 'refactor', 'debug', 'debugging',
        'git', 'github', 'gitlab', 'bitbucket',
        'linux', 'bash', 'shell', 'cli',
        'frontend', 'backend', 'fullstack', 'devops', 'sre',
        'performance', 'optimization', 'monitoring', 'logging',
        'documentation', 'docs', 'readme', 'comment',
        'architecture', 'design', 'pattern', 'patterns',
        'database', 'cache', 'queue', 'message',
        'microservice', 'monolith', 'serverless', 'lambda',
        'machine learning', 'ml', 'ai', 'data', 'analytics',
    ]
    
    content_lower = content.lower()
    found_keywords = []
    
    for term in tech_terms:
        if term in content_lower:
            found_keywords.append(term)
    
    # Also extract words from headers
    for line in content.split('\n'):
        if line.strip().startswith('#'):
            words = line.lower().replace('#', '').strip().split()
            for word in words:
                clean_word = ''.join(c for c in word if c.isalnum())
                if len(clean_word) > 3 and clean_word not in found_keywords:
                    found_keywords.append(clean_word)
    
    return found_keywords[:20]  # Limit to 20 keywords

def display_agent_list(agents: List[Dict], title: str) -> None:
    """Display a formatted list of agents."""
    print(colorize(f"\n{title}", Colors.HEADER + Colors.BOLD))
    print("=" * 60)
    
    if not agents:
        print(colorize("  No agents found", Colors.DIM))
        return
    
    for i, agent in enumerate(agents, 1):
        tokens = agent['token_estimate']
        token_color = Colors.GREEN if tokens < 1000 else Colors.YELLOW if tokens < 3000 else Colors.RED
        
        print(f"  [{i}] {colorize(agent['name'], Colors.CYAN)}")
        print(f"      {colorize(agent['summary'][:60] + '...' if len(agent['summary']) > 60 else agent['summary'], Colors.DIM)}")
        print(f"      Tokens: {colorize(str(tokens), token_color)} | Source: {Path(agent['source_dir']).name}")
        print()

def interactive_selection(agents: List[Dict]) -> List[Dict]:
    """Interactive selection with automatic pagination for large lists."""
    if not agents:
        return []

    # Use simple mode for ≤10 agents
    if len(agents) <= 10:
        return interactive_selection_simple(agents)

    try:
        import questionary
        from questionary import Separator
    except ImportError:
        print(colorize("\nℹ  questionary not installed - fallback mode", Colors.YELLOW))
        return interactive_selection_fallback(agents)

    return interactive_selection_paged(agents)


def interactive_selection_simple(agents: List[Dict]) -> List[Dict]:
    """Simple selection for small lists (≤10 agents) with Select All options."""
    try:
        import questionary
        from questionary import Separator
    except ImportError:
        return interactive_selection_fallback(agents)

    # Group agents by category (subdirectory)
    from collections import defaultdict
    categories = defaultdict(list)

    for agent in agents:
        # Extract category from path relative to source_dir
        agent_path = Path(agent['path'])
        source_dir = Path(agent.get('source_dir', ''))

        # Determine category from subdirectory structure
        category = "ROOT"  # Default for agents in root directory
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

    # Build choices list with category headers and select all options
    choices = []

    # Add global "Select All" at top
    select_all_choice = questionary.Choice(
        title=f"✨ [SELECT ALL] - Choose all {len(agents)} agents",
        value="__SELECT_ALL__",
        checked=False
    )
    choices.append(select_all_choice)
    choices.append(Separator(""))

    # Add categories with per-category select all
    for category in sorted(categories.keys()):
        # Add category header as separator
        if len(categories) > 1:  # Only show headers if multiple categories
            header = f"{'─' * 10} {category} {'─' * 10}"
            choices.append(Separator(header))

            # Per-category select all
            category_agents = categories[category]
            select_category_choice = questionary.Choice(
                title=f"  ✓ Select all {len(category_agents)} in {category}",
                value=f"__SELECT_CATEGORY_{category}__",
                checked=False
            )
            choices.append(select_category_choice)
            choices.append(Separator(""))

        # Add agents in this category
        for agent in sorted(categories[category], key=lambda a: a['name']):
            # Visual indicators for token size
            token_estimate = agent['token_estimate']
            if token_estimate < 1000:
                token_indicator = "🟢"
            elif token_estimate < 3000:
                token_indicator = "🟡"
            else:
                token_indicator = "🔴"

            # Format: name - summary (indicator tokens)
            summary = agent['summary'][:50] + '...' if len(agent['summary']) > 50 else agent['summary']
            label = f"{agent['name']} - {summary} {token_indicator} {token_estimate}"
            choices.append(questionary.Choice(title=label, value=agent))

    try:
        selected = questionary.checkbox(
            message="Select agents to migrate (↑↓=navigate, Space=toggle, Enter=confirm, Ctrl-C=cancel)",
            choices=choices
        ).ask()

        if not selected:
            return []

        # Process special selections
        final_selection = []
        select_all = False
        selected_categories = set()

        for item in selected:
            if item == "__SELECT_ALL__":
                select_all = True
            elif isinstance(item, str) and item.startswith("__SELECT_CATEGORY_"):
                category = item.replace("__SELECT_CATEGORY_", "").replace("__", "")
                selected_categories.add(category)
            elif isinstance(item, dict):  # Regular agent selection
                final_selection.append(item)

        # If "Select All" was chosen, return all agents
        if select_all:
            return agents

        # Add agents from selected categories
        if selected_categories:
            for category in selected_categories:
                final_selection.extend(categories[category])

        # Deduplicate in case user selected both category and individual agents
        seen = set()
        unique = []
        for agent in final_selection:
            if agent['name'] not in seen:
                seen.add(agent['name'])
                unique.append(agent)

        return unique

    except KeyboardInterrupt:
        print(colorize("\n\nMigration cancelled.", Colors.YELLOW))
        return []


def interactive_selection_paged(agents: List[Dict]) -> List[Dict]:
    """Paginated selection for large lists (>10 agents)."""
    import questionary
    from questionary import Separator
    from collections import defaultdict

    # Group by category
    categories = defaultdict(list)
    for agent in agents:
        agent_path = Path(agent['path'])
        source_dir = Path(agent.get('source_dir', ''))
        category = "ROOT"

        try:
            rel_path = agent_path.relative_to(source_dir)
            if len(rel_path.parts) > 1:
                category = rel_path.parts[0].upper().replace('-', ' ')
        except (ValueError, AttributeError):
            pass

        categories[category].append(agent)

    # Flatten into list preserving category grouping
    flat_items = []
    for category in sorted(categories.keys()):
        for agent in sorted(categories[category], key=lambda a: a['name']):
            flat_items.append((category, agent))

    # Initialize pagination
    page_state = PaginationState(agents, items_per_page=10)
    current_page = 0

    # Main loop
    while True:
        try:
            page_items = page_state.get_page_items(flat_items, current_page)
            choices = build_page_choices(page_state, page_items, current_page)

            selected = questionary.checkbox(
                message="Select agents (Space=toggle, Enter=next)",
                choices=choices
            ).ask()

            if not selected:
                return []

            # Process selections
            nav_action = None
            page_select_all = False
            page_agents = [agent for _, agent in page_items]
            regular = []

            for item in selected:
                if item == "__PREV__":
                    nav_action = "prev"
                elif item == "__NEXT__":
                    nav_action = "next"
                elif item == "__FINISH__":
                    nav_action = "finish"
                elif item == "__PAGE_SELECT_ALL__":
                    page_select_all = True
                elif isinstance(item, dict):
                    regular.append(item)

            # Update state
            if page_select_all:
                page_state.add_selections(page_agents)
            else:
                selected_names = {a['name'] for a in regular}
                page_state.add_selections(regular)

                # Remove deselections
                deselected = [a for a in page_agents
                             if a['name'] not in selected_names
                             and page_state.is_selected(a['name'])]
                page_state.remove_selections(deselected)

            # Navigate
            if nav_action == "prev":
                current_page = max(0, current_page - 1)
            elif nav_action == "next":
                current_page = min(page_state.total_pages - 1, current_page + 1)
            elif nav_action == "finish":
                break

        except KeyboardInterrupt:
            print(colorize("\n\nCancelled.", Colors.YELLOW))
            return []

    return page_state.get_final_selection()


def interactive_selection_fallback(agents: List[Dict]) -> List[Dict]:
    """Fallback to text-based selection when inquirer is not available."""
    if not agents:
        return []

    print(colorize("\nSelect agents to migrate to the registry:", Colors.BOLD))
    print(colorize("  Enter numbers separated by commas (e.g., 1,3,5)", Colors.DIM))
    print(colorize("  Enter 'all' to migrate all agents", Colors.DIM))
    print(colorize("  Enter 'none' or press Enter to skip migration", Colors.DIM))
    print()

    while True:
        selection = input(colorize("Your selection: ", Colors.CYAN)).strip().lower()

        if selection in ('', 'none'):
            return []

        if selection == 'all':
            return agents

        try:
            indices = [int(x.strip()) for x in selection.split(',')]
            selected = []
            for idx in indices:
                if 1 <= idx <= len(agents):
                    selected.append(agents[idx - 1])
                else:
                    print(colorize(f"  Invalid index: {idx}. Valid range: 1-{len(agents)}", Colors.RED))
                    continue

            if selected:
                return selected

        except ValueError:
            print(colorize("  Invalid input. Please enter numbers separated by commas.", Colors.RED))

def migrate_agents(agents: List[Dict], target_dir: Path) -> Tuple[List[Dict], List[str]]:
    """Move selected agents to the registry."""
    migrated = []
    errors = []
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    for agent in agents:
        source = Path(agent['path'])
        target = target_dir / agent['filename']
        
        try:
            # Check if target already exists
            if target.exists():
                print(colorize(f"  Skipping {agent['name']}: already exists in registry", Colors.YELLOW))
                # Still add to migrated list for registry building
                agent['path'] = str(target)
                migrated.append(agent)
                continue
            
            # Move the file
            shutil.move(str(source), str(target))
            agent['path'] = str(target)
            migrated.append(agent)
            print(colorize(f"  ✓ Migrated: {agent['name']}", Colors.GREEN))
            
        except Exception as e:
            errors.append(f"{agent['name']}: {e}")
            print(colorize(f"  ✗ Failed: {agent['name']} - {e}", Colors.RED))
    
    return migrated, errors

def build_registry(agents: List[Dict], registry_path: Path) -> None:
    """Build the registry.json index file."""
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Prepare registry data
    registry = {
        'version': 1,
        'generated_at': datetime.now().isoformat(),
        'skill_dir': str(get_skill_dir()),
        'agents': [],
        'stats': {
            'total_agents': len(agents),
            'total_tokens': sum(a['token_estimate'] for a in agents),
            'tokens_saved_vs_preload': sum(a['token_estimate'] for a in agents)
        }
    }
    
    for agent in agents:
        # Make path relative to skill dir
        rel_path = Path(agent['path']).relative_to(get_skill_dir()) if get_skill_dir() in Path(agent['path']).parents else agent['path']
        
        registry['agents'].append({
            'name': agent['name'],
            'path': str(rel_path),
            'summary': agent['summary'],
            'keywords': agent['keywords'],
            'token_estimate': agent['token_estimate'],
            'content_hash': agent['content_hash']
        })
    
    # Write registry (minified to reduce token count)
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, separators=(',', ':'))
    
    print(colorize(f"\n✓ Registry built: {registry_path}", Colors.GREEN))
    print(f"  Agents indexed: {len(agents)}")
    print(f"  Total tokens available: {registry['stats']['total_tokens']:,}")
    print(colorize(f"  Tokens saved by lazy loading: ~{registry['stats']['tokens_saved_vs_preload']:,}", Colors.GREEN + Colors.BOLD))

def scan_existing_registry() -> List[Dict]:
    """Scan agents already in the registry's agents folder."""
    agents_dir = get_agents_dir()
    if not agents_dir.exists():
        return []
    
    agents = []
    for md_file in agents_dir.glob("**/*.md"):
        agent_info = parse_agent_file(md_file)
        if agent_info:
            agent_info['source_dir'] = str(agents_dir)
            agents.append(agent_info)
    
    return agents

def main():
    """Main entry point."""
    print(colorize("\n╔══════════════════════════════════════════════════════════╗", Colors.HEADER))
    print(colorize("║          Agent Registry Initialization                   ║", Colors.HEADER))
    print(colorize("║  Reduce token overhead by lazy-loading agents            ║", Colors.HEADER))
    print(colorize("╚══════════════════════════════════════════════════════════╝", Colors.HEADER))
    
    # Find agent locations
    locations = find_agent_locations()
    
    if not locations:
        print(colorize("\nNo agent directories found at:", Colors.YELLOW))
        print("  - ~/.claude/agents/")
        print("  - .claude/agents/")
        
        # Check if we already have agents in registry
        existing = scan_existing_registry()
        if existing:
            print(colorize(f"\nFound {len(existing)} agents already in registry.", Colors.CYAN))
            print("Rebuilding registry index...")
            build_registry(existing, get_registry_path())
            return
        
        print("\nCreate agent files in these directories, then run this script again.")
        return
    
    # Scan all locations
    all_agents = []
    for loc in locations:
        print(colorize(f"\nScanning: {loc}", Colors.BLUE))
        agents = scan_agents(loc)
        all_agents.extend(agents)
        print(f"  Found {len(agents)} agent(s)")
    
    # Also scan existing registry agents
    existing_registry_agents = scan_existing_registry()
    existing_names = {a['name'] for a in existing_registry_agents}
    
    # Filter out agents already in registry
    new_agents = [a for a in all_agents if a['name'] not in existing_names]
    
    if existing_registry_agents:
        print(colorize(f"\nAlready in registry: {len(existing_registry_agents)} agent(s)", Colors.CYAN))
    
    if not new_agents and not existing_registry_agents:
        print(colorize("\nNo agents found to migrate.", Colors.YELLOW))
        return
    
    # Display agents for selection
    if new_agents:
        display_agent_list(new_agents, "Available Agents to Migrate")
        
        # Interactive selection
        selected = interactive_selection(new_agents)
        
        if selected:
            print(colorize(f"\nMigrating {len(selected)} agent(s)...", Colors.BLUE))
            migrated, errors = migrate_agents(selected, get_agents_dir())
            
            if errors:
                print(colorize(f"\nEncountered {len(errors)} error(s):", Colors.RED))
                for err in errors:
                    print(f"  - {err}")
            
            # Combine with existing
            all_registry_agents = existing_registry_agents + migrated
        else:
            print(colorize("\nNo agents selected for migration.", Colors.YELLOW))
            all_registry_agents = existing_registry_agents
    else:
        print(colorize("\nNo new agents to migrate.", Colors.CYAN))
        all_registry_agents = existing_registry_agents
    
    # Build/rebuild registry
    if all_registry_agents:
        print(colorize("\nBuilding registry index...", Colors.BLUE))
        build_registry(all_registry_agents, get_registry_path())
        
        print(colorize("\n✓ Setup complete!", Colors.GREEN + Colors.BOLD))
        print("\nNext steps:")
        print("  1. The skill is ready to use")
        print("  2. Claude will now search agents on-demand instead of loading all upfront")
        print("  3. Run 'python scripts/list_agents.py' to see indexed agents")
        print("  4. Run 'python scripts/search_agents.py <query>' to search")
    else:
        print(colorize("\nNo agents in registry. Run this script again after adding agents.", Colors.YELLOW))

if __name__ == "__main__":
    main()
