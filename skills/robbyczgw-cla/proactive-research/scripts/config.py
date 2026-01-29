#!/usr/bin/env python3
"""
Configuration loader for proactive-research skill.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "config.json"
STATE_FILE = SKILL_DIR / ".research_state.json"
FINDINGS_DIR = SKILL_DIR / ".findings"


def load_config() -> Dict:
    """Load configuration from config.json."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Config file not found: {CONFIG_FILE}\n"
            "Copy config.example.json to config.json and customize it."
        )
    
    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(config: Dict):
    """Save configuration to config.json."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def load_state() -> Dict:
    """Load state from .research_state.json."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "topics": {},
        "deduplication": {"url_hash_map": {}},
        "learning": {"interactions": []}
    }


def save_state(state: Dict):
    """Save state to .research_state.json."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def get_topics() -> List[Dict]:
    """Get all topics from config."""
    config = load_config()
    return config.get("topics", [])


def get_topic(topic_id: str) -> Optional[Dict]:
    """Get a specific topic by ID."""
    topics = get_topics()
    for topic in topics:
        if topic.get("id") == topic_id:
            return topic
    return None


def get_settings() -> Dict:
    """Get global settings."""
    config = load_config()
    return config.get("settings", {})


def get_channel_config(channel: str) -> Dict:
    """Get channel-specific configuration."""
    config = load_config()
    channels = config.get("channels", {})
    return channels.get(channel, {})


def ensure_findings_dir():
    """Ensure .findings directory exists."""
    FINDINGS_DIR.mkdir(exist_ok=True)


def get_findings_file(topic_id: str, date_str: str) -> Path:
    """Get path to findings file for topic and date."""
    ensure_findings_dir()
    return FINDINGS_DIR / f"{date_str}_{topic_id}.json"


def save_finding(topic_id: str, date_str: str, finding: Dict):
    """Save a finding to the findings directory."""
    findings_file = get_findings_file(topic_id, date_str)
    
    # Load existing findings
    findings = []
    if findings_file.exists():
        with open(findings_file) as f:
            findings = json.load(f)
    
    # Append new finding
    findings.append(finding)
    
    # Save
    with open(findings_file, 'w') as f:
        json.dump(findings, f, indent=2)


def load_findings(topic_id: str, date_str: str) -> List[Dict]:
    """Load findings for a topic and date."""
    findings_file = get_findings_file(topic_id, date_str)
    if findings_file.exists():
        with open(findings_file) as f:
            return json.load(f)
    return []
