#!/usr/bin/env python3
"""
Rebuild Registry Script

Rebuilds the registry index from agents in the registry's agents folder.
Use this after manually adding or editing agents.
"""

import os
import sys
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

def get_skill_dir() -> Path:
    """Get the directory where this skill is installed."""
    return Path(__file__).parent.parent

def get_agents_dir() -> Path:
    """Get the agents directory within this skill."""
    return get_skill_dir() / "agents"

def get_registry_path() -> Path:
    """Get the path to registry.json."""
    return get_skill_dir() / "references" / "registry.json"

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
    
    return found_keywords[:20]

def parse_agent_file(filepath: Path) -> Optional[Dict]:
    """Parse an agent .md file and extract metadata."""
    try:
        content = filepath.read_text(encoding='utf-8')
        
        name = filepath.stem
        summary = extract_summary(content)
        keywords = extract_keywords(content)
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
        print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)
        return None

def scan_agents() -> List[Dict]:
    """Scan the agents directory."""
    agents_dir = get_agents_dir()
    
    if not agents_dir.exists():
        print(f"Agents directory not found: {agents_dir}", file=sys.stderr)
        return []
    
    agents = []
    for md_file in agents_dir.glob("**/*.md"):
        agent_info = parse_agent_file(md_file)
        if agent_info:
            agents.append(agent_info)
    
    return agents

def build_registry(agents: List[Dict]) -> Dict:
    """Build the registry data structure."""
    skill_dir = get_skill_dir()
    
    registry = {
        'version': 1,
        'generated_at': datetime.now().isoformat(),
        'skill_dir': str(skill_dir),
        'agents': [],
        'stats': {
            'total_agents': len(agents),
            'total_tokens': sum(a['token_estimate'] for a in agents),
            'tokens_saved_vs_preload': sum(a['token_estimate'] for a in agents)
        }
    }
    
    for agent in agents:
        # Make path relative to skill dir
        try:
            rel_path = Path(agent['path']).relative_to(skill_dir)
        except ValueError:
            rel_path = agent['path']
        
        registry['agents'].append({
            'name': agent['name'],
            'path': str(rel_path),
            'summary': agent['summary'],
            'keywords': agent['keywords'],
            'token_estimate': agent['token_estimate'],
            'content_hash': agent['content_hash']
        })
    
    return registry

def main():
    """Main entry point."""
    print("Scanning agents directory...")
    
    agents = scan_agents()
    
    if not agents:
        print("No agents found in agents/ directory.")
        print(f"Add .md files to: {get_agents_dir()}")
        sys.exit(1)
    
    print(f"Found {len(agents)} agent(s)")
    
    registry = build_registry(agents)
    
    # Write registry (minified to reduce token count)
    registry_path = get_registry_path()
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, separators=(',', ':'))
    
    print(f"\n✓ Registry rebuilt: {registry_path}")
    print(f"  Agents indexed: {len(agents)}")
    print(f"  Total tokens: {registry['stats']['total_tokens']:,}")
    
    for agent in sorted(agents, key=lambda x: x['name']):
        print(f"    - {agent['name']} ({agent['token_estimate']:,} tokens)")

if __name__ == "__main__":
    main()
