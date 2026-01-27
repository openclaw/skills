#!/usr/bin/env python3
"""
GitNotesMemory - Git-Notes-Based Knowledge Graph Memory System

A persistent, branch-aware memory system using git notes:
- Each branch has its own memory context
- Memories merge when branches merge
- Auto-inherits from parent branch
- Knowledge graph with entity extraction
- Tiered retrieval for token efficiency
"""

import subprocess
import json
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# =============================================================================
# GIT OPS - BRANCH AWARE
# =============================================================================

def _git(args: List[str], cwd: str = ".") -> Optional[str]:
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None

def _git_ok(args: List[str], cwd: str = ".") -> bool:
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    return r.returncode == 0

def _branch(cwd: str = ".") -> str:
    """Get current branch name."""
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    return branch if branch and branch != "HEAD" else "main"

def _ref(name: str, cwd: str = ".") -> str:
    """Get branch-specific ref name."""
    branch = _branch(cwd)
    # Sanitize branch name for ref (replace / with -)
    safe_branch = branch.replace("/", "-")
    return f"refs/notes/{name}-{safe_branch}"

def _ensure_git(cwd: str = ".") -> str:
    """Ensure git repo exists and has at least one commit, return root commit."""
    path = Path(cwd).resolve()
    
    # Check if git repo exists
    if subprocess.run(["git", "rev-parse", "--git-dir"], cwd=path, capture_output=True).returncode != 0:
        subprocess.run(["git", "init"], cwd=path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "mem@local"], cwd=path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Memory"], cwd=path, capture_output=True)
    
    # Check if repo has any commits
    root = _git(["rev-list", "--max-parents=0", "HEAD"], cwd=str(path))
    
    # If no commits exist, create an initial empty commit
    if not root:
        subprocess.run(["git", "commit", "--allow-empty", "-m", "init"], cwd=path, capture_output=True)
        root = _git(["rev-list", "--max-parents=0", "HEAD"], cwd=str(path))
    
    return root

def _load(name: str, cwd: str = ".") -> Dict:
    """Load notes for current branch, with fallback to parent branches."""
    root = _ensure_git(cwd)
    ref = _ref(name, cwd)

    # Try current branch
    content = _git(["notes", "--ref", ref, "show", root], cwd)
    if content:
        try:
            return json.loads(content)
        except:
            pass

    # Try to inherit from parent branch (main/master)
    for parent in ["main", "master"]:
        if parent != _branch(cwd):
            parent_ref = f"refs/notes/{name}-{parent}"
            content = _git(["notes", "--ref", parent_ref, "show", root], cwd)
            if content:
                try:
                    data = json.loads(content)
                    # Auto-copy to current branch
                    _save(name, data, cwd)
                    return data
                except:
                    pass

    return {}

def _save(name: str, data: Dict, cwd: str = "."):
    """Save notes for current branch."""
    root = _ensure_git(cwd)
    ref = _ref(name, cwd)
    subprocess.run(
        ["git", "notes", "--ref", ref, "add", "-f", "-m", json.dumps(data, separators=(',', ':')), root],
        cwd=cwd, capture_output=True
    )

# Shortcuts
def _mem(cwd=".") -> Dict: return _load("mem", cwd)
def _ent(cwd=".") -> Dict: 
    data = _load("ent", cwd)
    # Ensure required structure exists
    if "e" not in data:
        data["e"] = {}
    return data

def _idx(cwd=".") -> Dict:
    """Load index with guaranteed structure."""
    defaults = {"t": {}, "m": {}, "c": [], "s": {}}
    data = _load("idx", cwd)
    # Merge with defaults to ensure all keys exist
    for key, default_val in defaults.items():
        if key not in data:
            data[key] = default_val
    return data

def _save_mem(d, cwd="."): _save("mem", d, cwd)
def _save_ent(d, cwd="."): _save("ent", d, cwd)
def _save_idx(d, cwd="."): _save("idx", d, cwd)

# =============================================================================
# BRANCH OPERATIONS
# =============================================================================

def merge_branch(source_branch: str, cwd: str = ".") -> Dict:
    """Merge memories from another branch into current branch."""
    root = _ensure_git(cwd)
    current = _branch(cwd)
    safe_source = source_branch.replace("/", "-")

    results = {"merged": [], "conflicts": [], "errors": []}

    for name in ["mem", "ent", "idx"]:
        current_ref = _ref(name, cwd)
        source_ref = f"refs/notes/{name}-{safe_source}"

        # Check if source has notes
        if not _git(["notes", "--ref", source_ref, "show", root], cwd):
            continue

        # Load both
        current_data = _load(name, cwd)
        source_content = _git(["notes", "--ref", source_ref, "show", root], cwd)

        try:
            source_data = json.loads(source_content) if source_content else {}
        except:
            source_data = {}

        if not source_data:
            continue

        # Merge strategy: union with conflict detection
        merged = _deep_merge(current_data, source_data, name)
        _save(name, merged, cwd)
        results["merged"].append(name)

    return results

def _deep_merge(base: Dict, incoming: Dict, data_type: str) -> Dict:
    """Deep merge two dicts with type-aware strategy."""
    result = dict(base)

    for key, value in incoming.items():
        if key not in result:
            # New key, just add
            result[key] = value
        elif isinstance(result[key], dict) and isinstance(value, dict):
            # Nested dict, recurse
            result[key] = _deep_merge(result[key], value, data_type)
        elif isinstance(result[key], list) and isinstance(value, list):
            # Lists: union (for memory IDs, entities, etc.)
            existing = set(str(x) for x in result[key])
            for item in value:
                if str(item) not in existing:
                    result[key].append(item)
        elif data_type == "mem" and key in result:
            # For memories, keep the one with latest update
            if isinstance(value, dict) and isinstance(result[key], dict):
                incoming_time = value.get("u", "")
                current_time = result[key].get("u", "")
                if incoming_time > current_time:
                    result[key] = value
        elif data_type == "idx" and key == "t":
            # Topics: merge counts
            if isinstance(value, dict) and isinstance(result[key], dict):
                for topic, data in value.items():
                    if topic not in result[key]:
                        result[key][topic] = data
                    else:
                        result[key][topic]["n"] = max(
                            result[key][topic].get("n", 0),
                            data.get("n", 0)
                        )
                        # Merge recent IDs
                        existing_r = set(result[key][topic].get("r", []))
                        for r in data.get("r", []):
                            existing_r.add(r)
                        result[key][topic]["r"] = list(existing_r)[:5]

    return result

def list_branches(cwd: str = ".") -> Dict:
    """List branches with memory counts."""
    root = _ensure_git(cwd)
    current = _branch(cwd)

    # Get all memory refs
    refs_output = _git(["for-each-ref", "--format=%(refname)", "refs/notes/mem-*"], cwd)

    branches = {}
    if refs_output:
        for ref in refs_output.split("\n"):
            if ref:
                # Extract branch name from ref
                branch = ref.replace("refs/notes/mem-", "")
                content = _git(["notes", "--ref", ref, "show", root], cwd)
                count = 0
                if content:
                    try:
                        data = json.loads(content)
                        count = len(data)
                    except:
                        pass
                branches[branch] = {"count": count, "current": branch == current.replace("/", "-")}

    return {"branches": branches, "current": current}

# =============================================================================
# ENTITY EXTRACTION (Domain-Agnostic)
# =============================================================================

STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "dare",
    "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
    "from", "as", "into", "through", "during", "before", "after", "above",
    "below", "between", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "just", "also", "now", "and",
    "but", "if", "or", "because", "until", "while", "this", "that", "these",
    "those", "it", "its", "i", "me", "my", "we", "our", "you", "your",
    "he", "him", "his", "she", "her", "they", "them", "their", "what",
    "which", "who", "whom", "get", "got", "about", "like", "want", "know",
    "think", "make", "take", "see", "come", "go", "use", "using", "used"
}

def extract_entities(content: Any) -> List[str]:
    """Extract key topics/entities from any content (domain-agnostic)."""
    # Priority entities from explicit fields (always included first)
    priority_entities = []
    generic_entities = set()

    if isinstance(content, dict):
        topic_fields = ["topic", "about", "subject", "name", "title", "category",
                       "area", "domain", "field", "concept", "item", "what",
                       "learning", "studying", "project", "goal", "target"]
        for k in topic_fields:
            if k in content and isinstance(content[k], str):
                val = content[k].lower().strip()
                # Also add without file extension for better matching
                priority_entities.append(val)
                if '.' in val:
                    priority_entities.append(val.rsplit('.', 1)[0])

        list_fields = ["topics", "tags", "categories", "items", "subjects", "areas"]
        for k in list_fields:
            if k in content and isinstance(content[k], list):
                for item in content[k]:
                    if isinstance(item, str):
                        priority_entities.append(item.lower().strip())

        text = json.dumps(content).lower()
    else:
        text = str(content).lower()

    # Extract hashtags
    hashtags = re.findall(r'#(\w+)', text)
    generic_entities.update(h.lower() for h in hashtags)

    # Extract quoted phrases
    quoted = re.findall(r'"([^"]{2,30})"', text)
    generic_entities.update(q.lower().strip() for q in quoted if len(q.split()) <= 4)

    # Extract capitalized phrases
    caps = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b', str(content))
    generic_entities.update(c.lower() for c in caps if c.lower() not in STOP_WORDS)

    # Extract key terms
    words = re.findall(r'\b([a-z]{3,})\b', text)
    for word in words:
        if word not in STOP_WORDS and 3 <= len(word) <= 20:
            generic_entities.add(word)

    # Extract bigrams
    bigrams = re.findall(r'\b([a-z]{3,}\s+[a-z]{3,})\b', text)
    for bg in bigrams:
        parts = bg.split()
        if all(p not in STOP_WORDS for p in parts):
            generic_entities.add(bg)

    generic_entities = {e for e in generic_entities if len(e) >= 3 and e not in STOP_WORDS}
    sorted_generic = sorted(generic_entities, key=lambda x: (len(x.split()), len(x)))
    
    # Combine: priority entities first (deduplicated), then generic entities
    seen = set()
    result = []
    for e in priority_entities:
        if e and e not in seen and len(e) >= 3:
            seen.add(e)
            result.append(e)
    for e in sorted_generic:
        if e not in seen:
            seen.add(e)
            result.append(e)
    
    return result[:15]  # Increased limit to preserve important entities

def classify_memory(content: Any) -> str:
    """Classify memory type (domain-agnostic)."""
    if isinstance(content, dict):
        if "type" in content and isinstance(content["type"], str):
            return content["type"][:20]
        text = json.dumps(content).lower()
    else:
        text = str(content).lower()

    if any(w in text for w in ["decided", "decision", "chose", "choice", "picked",
                                "selected", "going with", "will use", "opted"]):
        return "decision"

    if any(w in text for w in ["prefer", "preference", "favorite", "like best",
                                "rather", "better to", "style"]):
        return "preference"

    if any(w in text for w in ["learned", "learning", "studied", "studying",
                                "understood", "realized", "discovered", "insight"]):
        return "learning"

    if any(w in text for w in ["todo", "task", "need to", "should", "must",
                                "will do", "plan to", "going to", "next step"]):
        return "task"

    if any(w in text for w in ["question", "wondering", "curious", "ask about",
                                "find out", "research", "investigate"]):
        return "question"

    if any(w in text for w in ["note", "noticed", "observed", "important",
                                "remember that", "keep in mind"]):
        return "note"

    if any(w in text for w in ["completed", "finished", "done", "progress",
                                "achieved", "accomplished", "milestone"]):
        return "progress"

    return "info"

# =============================================================================
# CORE HELPERS
# =============================================================================

def _id(content: Any) -> str:
    return hashlib.md5(json.dumps(content, sort_keys=True).encode()).hexdigest()[:8]

def _sum(data: Any, max_len: int = 60) -> str:
    """Ultra-short summary."""
    if isinstance(data, str):
        return data[:max_len]
    if isinstance(data, dict):
        for k in ["summary", "sum", "s", "title", "name", "topic", "what", "decision", "pref", "learned"]:
            if k in data and isinstance(data[k], str):
                return data[k][:max_len]
        parts = []
        for k, v in list(data.items())[:3]:
            if isinstance(v, str) and len(v) < 50:
                parts.append(v)
        if parts:
            return "; ".join(parts)[:max_len]
        return f"({', '.join(list(data.keys())[:3])})"
    if isinstance(data, list):
        return f"[{len(data)} items]"
    return str(data)[:max_len]

def _now() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

# =============================================================================
# REMEMBER
# =============================================================================

def remember(content: Any, tags: str = "", importance: str = "n", cwd: str = ".") -> str:
    """Store memory with entity linking."""
    mem = _mem(cwd)
    ent = _ent(cwd)
    idx = _idx(cwd)

    mid = _id(content)
    now = datetime.now().isoformat()
    entities = extract_entities(content)
    mtype = classify_memory(content)
    tags_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    # Add branch context
    branch = _branch(cwd)

    mem[mid] = {
        "d": content,
        "e": entities,
        "t": mtype,
        "g": tags_list,
        "i": importance,
        "b": branch,  # Track originating branch
        "c": now,
        "u": now,
        "a": 0
    }

    # Update entity index
    if "e" not in ent:
        ent["e"] = {}
    for e in entities:
        if e not in ent["e"]:
            ent["e"][e] = {"m": [], "n": 0}
        if mid not in ent["e"][e]["m"]:
            ent["e"][e]["m"].append(mid)
        ent["e"][e]["n"] = len(ent["e"][e]["m"])

    # Update topic index
    primary = entities[0] if entities else mtype
    if "t" not in idx:
        idx["t"] = {}
    if primary not in idx["t"]:
        idx["t"][primary] = {"n": 0, "r": []}
    idx["t"][primary]["n"] += 1
    idx["t"][primary]["r"] = ([mid] + idx["t"][primary].get("r", []))[:5]

    # Update memory index
    if "m" not in idx:
        idx["m"] = {}
    idx["m"][mid] = {
        "s": _sum(content, 50),
        "e": entities[:3],
        "t": mtype,
        "i": importance,
        "u": now[:10]
    }

    # Track critical memories
    if importance == "c":
        if "c" not in idx:
            idx["c"] = []
        if mid not in idx["c"]:
            idx["c"] = [mid] + idx["c"][:4]

    _save_mem(mem, cwd)
    _save_ent(ent, cwd)
    _save_idx(idx, cwd)

    return mid

# =============================================================================
# TIERED RETRIEVAL
# =============================================================================

def sync_start(cwd: str = ".") -> Dict:
    """Tier 0: Ultra-compact session start with branch info."""
    idx = _idx(cwd)
    mem = _mem(cwd)
    branch = _branch(cwd)

    # Auto-init if empty
    if not mem:
        ctx = _init_context(cwd)
        if ctx:
            remember(ctx, tags="project,auto", importance="h", cwd=cwd)
            idx = _idx(cwd)
            mem = _mem(cwd)

    result = {"b": branch}  # Include current branch

    # Topics with counts
    topics = idx.get("t", {})
    if topics:
        sorted_topics = sorted(topics.items(), key=lambda x: x[1]["n"], reverse=True)[:8]
        result["t"] = {k: v["n"] for k, v in sorted_topics}

    # Critical memories
    critical = idx.get("c", [])
    if critical:
        c_list = []
        for mid in critical[:3]:
            if mid in mem:
                c_list.append({
                    "id": mid,
                    "s": _sum(mem[mid]["d"], 40),
                    "t": mem[mid].get("t", "info")
                })
        if c_list:
            result["c"] = c_list

    result["n"] = len(idx.get("m", {}))

    # High-importance
    high_imp = []
    for mid, entry in idx.get("m", {}).items():
        if entry.get("i") == "h" and mid not in critical:
            high_imp.append((mid, entry))
    high_imp.sort(key=lambda x: x[1].get("u", ""), reverse=True)
    if high_imp[:2]:
        result["h"] = [{"id": m, "s": e["s"]} for m, e in high_imp[:2]]

    return result

def get_topic(topic: str, cwd: str = ".") -> Dict:
    """Tier 1: Get memories for a topic."""
    idx = _idx(cwd)
    ent = _ent(cwd)
    mem = _mem(cwd)

    topic_lower = topic.lower()
    mids = set()

    # Check entity index
    entities = ent.get("e", {})
    for e_name, e_data in entities.items():
        if topic_lower in e_name or e_name in topic_lower:
            mids.update(e_data.get("m", []))

    # Check topic index
    topics = idx.get("t", {})
    for t_name, t_data in topics.items():
        if topic_lower in t_name or t_name in topic_lower:
            mids.update(t_data.get("r", []))

    # Search in memory summaries and entities
    for mid, entry in idx.get("m", {}).items():
        if topic_lower in entry.get("s", "").lower():
            mids.add(mid)
        if topic_lower in " ".join(entry.get("e", [])):
            mids.add(mid)
    
    # Also search in tags (stored in mem, not idx)
    for mid, m in mem.items():
        tags = m.get("g", [])
        if any(topic_lower in tag.lower() or tag.lower() in topic_lower for tag in tags):
            mids.add(mid)

    memories = []
    for mid in mids:
        if mid in mem:
            m = mem[mid]
            memories.append({
                "id": mid,
                "s": _sum(m["d"], 60),
                "t": m.get("t", "info"),
                "i": m.get("i", "n"),
                "b": m.get("b", "?")  # Include branch origin
            })

    imp_order = {"c": 0, "h": 1, "n": 2, "l": 3}
    memories.sort(key=lambda x: (imp_order.get(x["i"], 2), x["id"]))

    return {"topic": topic, "mem": memories[:10]}

def recall(mid: str = None, tag: str = None, query: str = None, last: int = None, cwd: str = ".") -> Any:
    """Retrieve memories."""
    idx = _idx(cwd)
    mem = _mem(cwd)

    if not any([mid, tag, query, last]):
        return {
            "b": _branch(cwd),
            "n": len(idx.get("m", {})),
            "t": list(idx.get("t", {}).keys())[:10],
            "recent": list(idx.get("m", {}).keys())[:5]
        }

    if mid:
        if mid in mem:
            mem[mid]["a"] = mem[mid].get("a", 0) + 1
            _save_mem(mem, cwd)
            return mem[mid]
        return None

    if tag:
        matches = {}
        for m_id, entry in idx.get("m", {}).items():
            if m_id in mem and tag.lower() in " ".join(mem[m_id].get("g", [])).lower():
                matches[m_id] = entry
        return matches

    if query:
        return get_topic(query, cwd)

    if last:
        entries = list(idx.get("m", {}).items())
        entries.sort(key=lambda x: x[1].get("u", ""), reverse=True)
        return {m: e for m, e in entries[:last]}

    return None

# =============================================================================
# UPDATE/EVOLVE
# =============================================================================

def update(mid: str, content: Any = None, importance: str = None,
           tags: str = None, merge: bool = False, cwd: str = ".") -> bool:
    """Update existing memory."""
    mem = _mem(cwd)
    ent = _ent(cwd)
    idx = _idx(cwd)
    
    if mid not in mem:
        return False

    entry = mem[mid]
    old_entities = set(entry.get("e", []))
    old_importance = entry.get("i", "n")

    if content is not None:
        if merge and isinstance(entry["d"], dict) and isinstance(content, dict):
            entry["d"] = {**entry["d"], **content}
        else:
            entry["d"] = content
        entry["e"] = extract_entities(entry["d"])

    if importance:
        entry["i"] = importance

    if tags:
        entry["g"] = [t.strip() for t in tags.split(",") if t.strip()]

    entry["u"] = datetime.now().isoformat()
    new_entities = set(entry.get("e", []))

    # Update entity index: remove old, add new
    removed_entities = old_entities - new_entities
    added_entities = new_entities - old_entities
    
    for e in removed_entities:
        if e in ent.get("e", {}):
            ent["e"][e]["m"] = [m for m in ent["e"][e]["m"] if m != mid]
            ent["e"][e]["n"] = len(ent["e"][e]["m"])
    
    for e in added_entities:
        if e not in ent["e"]:
            ent["e"][e] = {"m": [], "n": 0}
        if mid not in ent["e"][e]["m"]:
            ent["e"][e]["m"].append(mid)
        ent["e"][e]["n"] = len(ent["e"][e]["m"])

    # Update memory index
    if mid in idx.get("m", {}):
        idx["m"][mid]["s"] = _sum(entry["d"], 50)
        idx["m"][mid]["e"] = entry["e"][:3]
        idx["m"][mid]["i"] = entry.get("i", "n")
        idx["m"][mid]["u"] = entry["u"][:10]

    # Handle importance changes for critical list
    new_importance = entry.get("i", "n")
    if old_importance != new_importance:
        # Was critical, now isn't
        if old_importance == "c" and new_importance != "c":
            idx["c"] = [m for m in idx.get("c", []) if m != mid]
        # Wasn't critical, now is
        elif new_importance == "c" and old_importance != "c":
            if mid not in idx.get("c", []):
                idx["c"] = [mid] + idx.get("c", [])[:4]

    _save_mem(mem, cwd)
    _save_ent(ent, cwd)
    _save_idx(idx, cwd)
    return True

def evolve(mid: str, note: str, cwd: str = ".") -> bool:
    """Add evolution note."""
    mem = _mem(cwd)
    if mid not in mem:
        return False

    if "ev" not in mem[mid]:
        mem[mid]["ev"] = []
    mem[mid]["ev"].append({"n": note, "t": _now(), "b": _branch(cwd)})
    mem[mid]["u"] = datetime.now().isoformat()

    _save_mem(mem, cwd)
    return True

def forget(mid: str, cwd: str = ".") -> bool:
    """Remove memory."""
    mem = _mem(cwd)
    idx = _idx(cwd)
    ent = _ent(cwd)

    if mid not in mem:
        return False

    # Clean up entity index
    for e in mem[mid].get("e", []):
        if e in ent.get("e", {}):
            ent["e"][e]["m"] = [m for m in ent["e"][e]["m"] if m != mid]
            ent["e"][e]["n"] = len(ent["e"][e]["m"])

    # Clean up topic index - remove from recent lists and decrement counts
    topics = idx.get("t", {})
    for topic_name in list(topics.keys()):
        topic_data = topics[topic_name]
        if mid in topic_data.get("r", []):
            topic_data["r"] = [m for m in topic_data["r"] if m != mid]
            topic_data["n"] = max(0, topic_data.get("n", 1) - 1)

    # Clean up memory index
    if mid in idx.get("m", {}):
        del idx["m"][mid]
    
    # Clean up critical list
    if mid in idx.get("c", []):
        idx["c"] = [m for m in idx["c"] if m != mid]

    del mem[mid]

    _save_mem(mem, cwd)
    _save_idx(idx, cwd)
    _save_ent(ent, cwd)
    return True

# =============================================================================
# SEARCH
# =============================================================================

def search(query: str, cwd: str = ".") -> Dict:
    """Full-text search across all memories."""
    mem = _mem(cwd)
    idx = _idx(cwd)
    
    query_lower = query.lower()
    query_terms = [t.strip() for t in query_lower.split() if t.strip()]
    
    results = []
    
    for mid, entry in mem.items():
        score = 0
        
        # Search in content
        content_str = json.dumps(entry.get("d", "")).lower()
        for term in query_terms:
            if term in content_str:
                score += content_str.count(term)
        
        # Search in entities
        entities_str = " ".join(entry.get("e", [])).lower()
        for term in query_terms:
            if term in entities_str:
                score += 2  # Boost entity matches
        
        # Search in tags
        tags_str = " ".join(entry.get("g", [])).lower()
        for term in query_terms:
            if term in tags_str:
                score += 2  # Boost tag matches
        
        if score > 0:
            results.append({
                "id": mid,
                "s": _sum(entry.get("d"), 60),
                "t": entry.get("t", "info"),
                "i": entry.get("i", "n"),
                "b": entry.get("b", "?"),
                "score": score
            })
    
    # Sort by score (descending), then by importance
    imp_order = {"c": 0, "h": 1, "n": 2, "l": 3}
    results.sort(key=lambda x: (-x["score"], imp_order.get(x["i"], 2)))
    
    # Remove score from output (internal use only)
    for r in results:
        del r["score"]
    
    return {"query": query, "results": results[:15]}

# =============================================================================
# ENTITIES
# =============================================================================

def entities(cwd: str = ".") -> Dict:
    """List all entities with counts."""
    ent = _ent(cwd)
    e_dict = ent.get("e", {})
    sorted_ent = sorted(e_dict.items(), key=lambda x: x[1]["n"], reverse=True)
    return {
        "entities": {k: v["n"] for k, v in sorted_ent[:20]},
        "total": len(e_dict)
    }

def entity(name: str, cwd: str = ".") -> Dict:
    """Get entity details and linked memories."""
    ent = _ent(cwd)
    idx = _idx(cwd)
    mem = _mem(cwd)

    name_lower = name.lower()
    e_data = ent.get("e", {}).get(name_lower)

    if not e_data:
        for e_name in ent.get("e", {}):
            if name_lower in e_name or e_name in name_lower:
                e_data = ent["e"][e_name]
                break

    if not e_data:
        return {"error": "not found"}

    memories = []
    for mid in e_data.get("m", []):
        if mid in idx.get("m", {}):
            memories.append({
                "id": mid,
                "s": idx["m"][mid]["s"],
                "t": idx["m"][mid]["t"]
            })

    return {
        "entity": name,
        "count": e_data["n"],
        "memories": memories[:10]
    }

# =============================================================================
# SESSION END
# =============================================================================

def sync_end(summary: Any, cwd: str = ".") -> Dict:
    """End session, store summary."""
    branch = _branch(cwd)

    # Add branch to summary
    if isinstance(summary, dict):
        summary["_branch"] = branch

    mid = remember(summary, tags="session,auto", importance="n", cwd=cwd)
    _maintain(cwd)
    return {"ok": True, "mid": mid, "branch": branch}

def _maintain(cwd: str = "."):
    """Lightweight maintenance - clean up stale references."""
    idx = _idx(cwd)
    mem = _mem(cwd)
    ent = _ent(cwd)

    # Clean up topic index
    topics = idx.get("t", {})
    for t in list(topics.keys()):
        topics[t]["r"] = [m for m in topics[t]["r"] if m in mem]
        # Remove topics with no recent memories and zero count
        if not topics[t]["r"] and topics[t].get("n", 0) <= 0:
            del topics[t]

    # Clean up memory index - remove entries for deleted memories
    mem_index = idx.get("m", {})
    for mid in list(mem_index.keys()):
        if mid not in mem:
            del mem_index[mid]

    # Clean up critical list
    idx["c"] = [m for m in idx.get("c", []) if m in mem]

    # Clean up entity index - remove empty entities and stale memory refs
    entities_dict = ent.get("e", {})
    for e_name in list(entities_dict.keys()):
        # Remove stale memory references
        entities_dict[e_name]["m"] = [m for m in entities_dict[e_name].get("m", []) if m in mem]
        entities_dict[e_name]["n"] = len(entities_dict[e_name]["m"])
        # Remove entities with no memories
        if entities_dict[e_name]["n"] == 0:
            del entities_dict[e_name]

    _save_idx(idx, cwd)
    _save_ent(ent, cwd)

# =============================================================================
# INIT CONTEXT
# =============================================================================

def _init_context(cwd: str = ".") -> Optional[Dict]:
    """Create initial project context."""
    path = Path(cwd).resolve()
    ctx = {"project": path.name, "branch": _branch(cwd)}

    if (path / "package.json").exists():
        ctx["type"] = "node"
        try:
            pkg = json.loads((path / "package.json").read_text())
            if pkg.get("name"):
                ctx["project"] = pkg["name"]
            if pkg.get("description"):
                ctx["desc"] = pkg["description"][:100]
        except:
            pass
    elif (path / "setup.py").exists() or (path / "pyproject.toml").exists():
        ctx["type"] = "python"
    elif (path / "Cargo.toml").exists():
        ctx["type"] = "rust"
    elif (path / "go.mod").exists():
        ctx["type"] = "go"
    elif list(path.glob("*.md")):
        ctx["type"] = "docs"
    else:
        ctx["type"] = "mixed"

    for readme in ["README.md", "README.txt", "readme.md"]:
        rp = path / readme
        if rp.exists():
            try:
                lines = rp.read_text()[:300].split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        ctx["desc"] = line.strip()[:100]
                        break
            except:
                pass
            break

    return ctx if len(ctx) > 1 else None

# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    p = argparse.ArgumentParser(description="Knowledge Graph Memory v4 (Branch Aware)")
    p.add_argument("-p", "--path", default=".", help="Target dir")
    sub = p.add_subparsers(dest="cmd")

    # sync
    s = sub.add_parser("sync")
    s.add_argument("--start", action="store_true")
    s.add_argument("--end", help="Summary JSON")

    # remember
    r = sub.add_parser("remember", aliases=["r"])
    r.add_argument("content")
    r.add_argument("-t", "--tags", default="")
    r.add_argument("-i", "--importance", default="n", choices=["c", "h", "n", "l"])

    # recall
    q = sub.add_parser("recall", aliases=["q"])
    q.add_argument("-i", "--id", dest="mid")
    q.add_argument("-t", "--tag")
    q.add_argument("-q", "--query")
    q.add_argument("--last", type=int)

    # get (topic)
    g = sub.add_parser("get", aliases=["g"])
    g.add_argument("topic")

    # search
    sr = sub.add_parser("search", aliases=["s"])
    sr.add_argument("query")

    # update
    u = sub.add_parser("update", aliases=["u"])
    u.add_argument("mid")
    u.add_argument("content", nargs="?")
    u.add_argument("-i", "--importance", choices=["c", "h", "n", "l"])
    u.add_argument("-t", "--tags")
    u.add_argument("-m", "--merge", action="store_true")

    # evolve
    e = sub.add_parser("evolve", aliases=["e"])
    e.add_argument("mid")
    e.add_argument("note")

    # forget
    f = sub.add_parser("forget", aliases=["f"])
    f.add_argument("mid")

    # entities
    sub.add_parser("entities", aliases=["ent"])

    # entity
    en = sub.add_parser("entity")
    en.add_argument("name")

    # Branch operations
    mb = sub.add_parser("merge-branch", aliases=["mb"])
    mb.add_argument("source", help="Source branch to merge from")

    sub.add_parser("branches", aliases=["br"])

    args = p.parse_args()
    cwd = args.path

    # Execute
    if args.cmd == "sync":
        if args.start:
            print(json.dumps(sync_start(cwd), separators=(',', ':')))
        elif args.end:
            try:
                summary = json.loads(args.end)
            except:
                summary = args.end
            print(json.dumps(sync_end(summary, cwd), separators=(',', ':')))
    elif args.cmd in ("remember", "r"):
        try:
            content = json.loads(args.content)
        except:
            content = args.content
        print(remember(content, args.tags, args.importance, cwd))
    elif args.cmd in ("recall", "q"):
        result = recall(args.mid, args.tag, args.query, args.last, cwd)
        print(json.dumps(result, separators=(',', ':')) if result else "null")
    elif args.cmd in ("get", "g"):
        print(json.dumps(get_topic(args.topic, cwd), separators=(',', ':')))
    elif args.cmd in ("search", "s"):
        print(json.dumps(search(args.query, cwd), separators=(',', ':')))
    elif args.cmd in ("update", "u"):
        content = None
        if args.content:
            try:
                content = json.loads(args.content)
            except:
                content = args.content
        print("ok" if update(args.mid, content, args.importance, args.tags, args.merge, cwd) else "not found")
    elif args.cmd in ("evolve", "e"):
        print("ok" if evolve(args.mid, args.note, cwd) else "not found")
    elif args.cmd in ("forget", "f"):
        print("ok" if forget(args.mid, cwd) else "not found")
    elif args.cmd in ("entities", "ent"):
        print(json.dumps(entities(cwd), separators=(',', ':')))
    elif args.cmd == "entity":
        print(json.dumps(entity(args.name, cwd), separators=(',', ':')))
    elif args.cmd in ("merge-branch", "mb"):
        print(json.dumps(merge_branch(args.source, cwd), separators=(',', ':')))
    elif args.cmd in ("branches", "br"):
        print(json.dumps(list_branches(cwd), separators=(',', ':')))
    else:
        print(json.dumps(recall(cwd=cwd), separators=(',', ':')))

if __name__ == "__main__":
    main()
