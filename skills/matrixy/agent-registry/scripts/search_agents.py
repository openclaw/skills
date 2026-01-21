#!/usr/bin/env python3
"""
Agent Search Script

Searches the agent registry using BM25 ranking and keyword matching.
Returns relevant agents sorted by relevance score.
"""

import os
import sys
import json
import math
import re
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple, Optional

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

# ============================================================================
# BM25 Implementation
# ============================================================================

class BM25:
    """
    BM25 (Best Matching 25) ranking function.
    
    Parameters tuned for short document search (agent summaries/keywords).
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1  # Term frequency saturation parameter
        self.b = b    # Length normalization parameter
        self.corpus = []
        self.doc_lengths = []
        self.avgdl = 0
        self.idf = {}
        self.doc_freqs = Counter()
        self.N = 0
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into lowercase terms."""
        # Split on non-alphanumeric, convert to lowercase
        tokens = re.findall(r'\b[a-z0-9]+\b', text.lower())
        return tokens
    
    def fit(self, documents: List[str]) -> None:
        """
        Fit BM25 on a corpus of documents.
        
        Args:
            documents: List of document strings to index
        """
        self.corpus = []
        self.doc_lengths = []
        self.doc_freqs = Counter()
        
        # Tokenize all documents
        for doc in documents:
            tokens = self.tokenize(doc)
            self.corpus.append(tokens)
            self.doc_lengths.append(len(tokens))
            
            # Count document frequency for each unique term
            unique_terms = set(tokens)
            for term in unique_terms:
                self.doc_freqs[term] += 1
        
        self.N = len(documents)
        self.avgdl = sum(self.doc_lengths) / self.N if self.N > 0 else 0
        
        # Compute IDF for all terms
        self.idf = {}
        for term, df in self.doc_freqs.items():
            # IDF with smoothing to avoid negative values
            self.idf[term] = math.log((self.N - df + 0.5) / (df + 0.5) + 1)
    
    def score(self, query: str, doc_idx: int) -> float:
        """
        Compute BM25 score for a query against a document.
        
        Args:
            query: Search query string
            doc_idx: Index of document in corpus
        
        Returns:
            BM25 relevance score
        """
        query_tokens = self.tokenize(query)
        doc_tokens = self.corpus[doc_idx]
        doc_len = self.doc_lengths[doc_idx]
        
        # Count term frequencies in document
        tf = Counter(doc_tokens)
        
        score = 0.0
        for term in query_tokens:
            if term not in self.idf:
                continue
            
            term_freq = tf.get(term, 0)
            if term_freq == 0:
                continue
            
            # BM25 formula
            numerator = self.idf[term] * term_freq * (self.k1 + 1)
            denominator = term_freq + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
            score += numerator / denominator
        
        return score
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Search for documents matching the query.
        
        Args:
            query: Search query string
            top_k: Maximum number of results to return
        
        Returns:
            List of (doc_index, score) tuples, sorted by score descending
        """
        scores = []
        for i in range(len(self.corpus)):
            score = self.score(query, i)
            if score > 0:
                scores.append((i, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


# ============================================================================
# Keyword Matching
# ============================================================================

def keyword_match_score(query: str, agent: Dict) -> float:
    """
    Compute keyword match score for an agent.
    
    Args:
        query: Search query string
        agent: Agent dictionary with 'keywords', 'summary', 'name'
    
    Returns:
        Match score between 0.0 and 1.0
    """
    query_lower = query.lower()
    query_terms = set(re.findall(r'\b[a-z0-9]+\b', query_lower))
    
    if not query_terms:
        return 0.0
    
    matches = 0
    total_weight = 0
    
    # Check name (highest weight)
    name_terms = set(re.findall(r'\b[a-z0-9]+\b', agent['name'].lower()))
    name_matches = len(query_terms & name_terms)
    matches += name_matches * 3
    total_weight += len(query_terms) * 3
    
    # Check keywords (medium weight)
    agent_keywords = set(k.lower() for k in agent.get('keywords', []))
    keyword_matches = len(query_terms & agent_keywords)
    matches += keyword_matches * 2
    total_weight += len(query_terms) * 2
    
    # Check summary (lower weight)
    summary_terms = set(re.findall(r'\b[a-z0-9]+\b', agent.get('summary', '').lower()))
    summary_matches = len(query_terms & summary_terms)
    matches += summary_matches * 1
    total_weight += len(query_terms) * 1
    
    # Also check for partial matches in summary
    for term in query_terms:
        if len(term) >= 3 and term in agent.get('summary', '').lower():
            matches += 0.5
    
    return matches / total_weight if total_weight > 0 else 0.0


# ============================================================================
# Combined Search
# ============================================================================

def search_agents(query: str, registry: Dict, top_k: int = 5) -> List[Dict]:
    """
    Search agents using combined BM25 and keyword matching.
    
    Args:
        query: Search query string
        registry: Registry dictionary
        top_k: Maximum results to return
    
    Returns:
        List of matching agents with scores
    """
    agents = registry.get('agents', [])
    
    if not agents:
        return []
    
    # Build BM25 corpus from agent text
    corpus = []
    for agent in agents:
        # Combine name, summary, and keywords for BM25
        text = f"{agent['name']} {agent.get('summary', '')} {' '.join(agent.get('keywords', []))}"
        corpus.append(text)
    
    # Fit BM25
    bm25 = BM25()
    bm25.fit(corpus)
    
    # Get BM25 scores
    bm25_results = bm25.search(query, top_k=len(agents))
    bm25_scores = {idx: score for idx, score in bm25_results}
    
    # Normalize BM25 scores to 0-1 range
    max_bm25 = max(bm25_scores.values()) if bm25_scores else 1.0
    if max_bm25 > 0:
        bm25_scores = {k: v / max_bm25 for k, v in bm25_scores.items()}
    
    # Compute combined scores
    results = []
    for i, agent in enumerate(agents):
        bm25_score = bm25_scores.get(i, 0.0)
        keyword_score = keyword_match_score(query, agent)
        
        # Weighted combination (BM25 60%, keyword 40%)
        combined_score = 0.6 * bm25_score + 0.4 * keyword_score
        
        if combined_score > 0.05:  # Minimum threshold
            results.append({
                'name': agent['name'],
                'summary': agent['summary'],
                'score': round(combined_score, 3),
                'bm25_score': round(bm25_score, 3),
                'keyword_score': round(keyword_score, 3),
                'token_estimate': agent.get('token_estimate', 0),
                'keywords': agent.get('keywords', [])[:5]
            })
    
    # Sort by combined score
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_k]


def format_results(results: List[Dict], query: str) -> str:
    """Format search results for display."""
    if not results:
        return f"No agents found matching: '{query}'\n\nTry broader search terms or run 'python scripts/list_agents.py' to see all agents."
    
    lines = [f"Found {len(results)} matching agent(s) for: '{query}'\n"]
    
    for i, r in enumerate(results, 1):
        score_bar = "█" * int(r['score'] * 10) + "░" * (10 - int(r['score'] * 10))
        lines.append(f"{i}. {r['name']} (score: {r['score']:.2f}) [{score_bar}]")
        lines.append(f"   {r['summary'][:80]}{'...' if len(r['summary']) > 80 else ''}")
        lines.append(f"   Tokens: ~{r['token_estimate']:,} | Keywords: {', '.join(r['keywords'][:5])}")
        lines.append("")
    
    lines.append("To load an agent: python scripts/get_agent.py <agent-name>")
    return "\n".join(lines)


def format_json(results: List[Dict]) -> str:
    """Format results as JSON."""
    return json.dumps(results, indent=2)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python search_agents.py <query> [--json] [--top N]")
        print("")
        print("Examples:")
        print("  python search_agents.py 'code review security'")
        print("  python search_agents.py 'docker kubernetes' --top 3")
        print("  python search_agents.py 'python testing' --json")
        sys.exit(1)
    
    # Parse arguments
    args = sys.argv[1:]
    json_output = '--json' in args
    if json_output:
        args.remove('--json')
    
    top_k = 5
    if '--top' in args:
        idx = args.index('--top')
        if idx + 1 < len(args):
            try:
                top_k = int(args[idx + 1])
            except ValueError:
                pass
            args = args[:idx] + args[idx+2:]
    
    query = ' '.join(args)
    
    # Load registry
    registry = load_registry()
    if not registry:
        sys.exit(1)
    
    # Search
    results = search_agents(query, registry, top_k=top_k)
    
    # Output
    if json_output:
        print(format_json(results))
    else:
        print(format_results(results, query))


if __name__ == "__main__":
    main()
