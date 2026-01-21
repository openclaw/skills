#!/usr/bin/env python3
"""
Paged Agent Search Script

Searches the agent registry with pagination support for large result sets.
Useful when dealing with 300+ agents or when you need to browse results systematically.
"""

import os
import sys
import json
import math
import re
import argparse
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
# BM25 Implementation (from search_agents.py)
# ============================================================================

class BM25:
    """
    BM25 (Best Matching 25) ranking function.

    Parameters tuned for short document search (agent summaries/keywords).
    """
    def __init__(self, k1=1.5, b=0.75):
        """
        Initialize BM25.

        Args:
            k1: Term frequency saturation parameter (default 1.5)
            b: Length normalization parameter (default 0.75)
        """
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.doc_freqs = {}
        self.idf = {}
        self.doc_lengths = []
        self.avg_doc_length = 0

    def fit(self, corpus: List[str]):
        """
        Fit the BM25 model on a corpus of documents.

        Args:
            corpus: List of document strings
        """
        self.corpus = corpus
        self.doc_lengths = []

        # Tokenize and compute document frequencies
        tokenized_corpus = []
        for doc in corpus:
            tokens = self._tokenize(doc)
            tokenized_corpus.append(tokens)
            self.doc_lengths.append(len(tokens))

            # Update document frequencies
            for token in set(tokens):
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1

        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0

        # Compute IDF scores
        num_docs = len(corpus)
        for term, freq in self.doc_freqs.items():
            self.idf[term] = math.log((num_docs - freq + 0.5) / (freq + 0.5) + 1)

        self.tokenized_corpus = tokenized_corpus

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into lowercase words."""
        return re.findall(r'\b\w+\b', text.lower())

    def _score_doc(self, query_tokens: List[str], doc_idx: int) -> float:
        """
        Score a single document against the query.

        Args:
            query_tokens: Tokenized query
            doc_idx: Index of document in corpus

        Returns:
            BM25 score
        """
        score = 0.0
        doc_tokens = self.tokenized_corpus[doc_idx]
        doc_length = self.doc_lengths[doc_idx]

        # Count term frequencies in document
        term_freqs = Counter(doc_tokens)

        for token in query_tokens:
            if token not in self.idf:
                continue

            tf = term_freqs.get(token, 0)
            idf = self.idf[token]

            # BM25 formula
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avg_doc_length))

            score += idf * (numerator / denominator)

        return score

    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Search the corpus for relevant documents.

        Args:
            query: Search query string
            top_k: Number of top results to return

        Returns:
            List of (doc_index, score) tuples sorted by score
        """
        query_tokens = self._tokenize(query)

        scores = []
        for i in range(len(self.corpus)):
            score = self._score_doc(query_tokens, i)
            if score > 0:
                scores.append((i, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


def keyword_match_score(query: str, agent: Dict) -> float:
    """
    Compute keyword match score for an agent.

    Matches query terms against agent keywords with fuzzy matching.

    Args:
        query: Search query
        agent: Agent dictionary with 'keywords' field

    Returns:
        Keyword match score (0.0 to 1.0)
    """
    keywords = agent.get('keywords', [])
    if not keywords:
        return 0.0

    query_terms = set(re.findall(r'\b\w+\b', query.lower()))
    if not query_terms:
        return 0.0

    # Weight by keyword importance (earlier keywords more important)
    matches = 0.0
    total_weight = 0.0

    for i, keyword in enumerate(keywords):
        weight = 1.0 / (i + 1)  # Decay weight
        total_weight += weight

        keyword_lower = keyword.lower()

        # Exact match
        if keyword_lower in query_terms:
            matches += weight
        # Partial match (query term contains keyword or vice versa)
        elif any(term in keyword_lower or keyword_lower in term for term in query_terms):
            matches += 0.5 * weight

    return matches / total_weight if total_weight > 0 else 0.0


# ============================================================================
# Paged Search
# ============================================================================

def search_agents_all(query: str, registry: Dict) -> List[Dict]:
    """
    Search agents using combined BM25 and keyword matching.
    Returns ALL matching results (no limit) for pagination.

    Args:
        query: Search query string
        registry: Registry dictionary

    Returns:
        List of all matching agents with scores
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

    # Get BM25 scores for ALL agents
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
    return results


def paginate_results(results: List[Dict], page: int = 1, page_size: int = 20,
                     offset: Optional[int] = None, limit: Optional[int] = None) -> Dict:
    """
    Apply pagination to search results.

    Supports both page-based and offset-based pagination:
    - Page-based: --page 2 --page-size 10 (pages start at 1)
    - Offset-based: --offset 20 --limit 10 (zero-indexed)

    Args:
        results: All search results
        page: Page number (1-indexed) for page-based pagination
        page_size: Items per page for page-based pagination
        offset: Starting index (0-indexed) for offset-based pagination
        limit: Max items to return for offset-based pagination

    Returns:
        Dictionary with paginated results and metadata
    """
    total_results = len(results)

    # Offset-based pagination takes precedence
    if offset is not None:
        start_idx = max(0, offset)
        end_idx = min(total_results, start_idx + (limit or page_size))

        return {
            'query': None,  # Set by caller
            'total_results': total_results,
            'offset': start_idx,
            'limit': end_idx - start_idx,
            'results': results[start_idx:end_idx]
        }

    # Page-based pagination
    page = max(1, page)  # Pages start at 1
    total_pages = math.ceil(total_results / page_size) if page_size > 0 else 1

    start_idx = (page - 1) * page_size
    end_idx = min(total_results, start_idx + page_size)

    return {
        'query': None,  # Set by caller
        'total_results': total_results,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1,
        'results': results[start_idx:end_idx]
    }


def format_results(paginated: Dict, json_output: bool = False) -> str:
    """Format paginated search results for display."""
    if json_output:
        return json.dumps(paginated, indent=2)

    query = paginated.get('query', 'N/A')
    total = paginated['total_results']
    results = paginated['results']

    if total == 0:
        return f"No agents found matching: '{query}'\n\nTry broader search terms or run 'python scripts/list_agents.py' to see all agents."

    lines = []

    # Header with pagination info
    if 'page' in paginated:
        lines.append(f"Found {total} matching agent(s) for: '{query}'")
        lines.append(f"Page {paginated['page']}/{paginated['total_pages']} ({len(results)} results on this page)")
    else:
        lines.append(f"Found {total} matching agent(s) for: '{query}'")
        lines.append(f"Showing results {paginated['offset'] + 1}-{paginated['offset'] + len(results)}")

    lines.append("")

    # Results
    for i, r in enumerate(results, 1):
        # Calculate global index
        if 'page' in paginated:
            global_idx = (paginated['page'] - 1) * paginated['page_size'] + i
        else:
            global_idx = paginated['offset'] + i

        score_bar = "█" * int(r['score'] * 10) + "░" * (10 - int(r['score'] * 10))
        lines.append(f"{global_idx}. {r['name']} (score: {r['score']:.2f}) [{score_bar}]")
        lines.append(f"   {r['summary'][:80]}{'...' if len(r['summary']) > 80 else ''}")
        lines.append(f"   Tokens: ~{r['token_estimate']:,} | Keywords: {', '.join(r['keywords'][:5])}")
        lines.append("")

    # Navigation hints
    if 'page' in paginated:
        if paginated['has_next']:
            lines.append(f"→ Next page: --page {paginated['page'] + 1}")
        if paginated['has_prev']:
            lines.append(f"← Previous page: --page {paginated['page'] - 1}")

    lines.append("")
    lines.append("To load an agent: python scripts/get_agent.py <agent-name>")

    return "\n".join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Search agents with pagination support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Page-based pagination (default)
  python scripts/search_agents_paged.py "security" --page 1 --page-size 10

  # Offset-based pagination
  python scripts/search_agents_paged.py "react" --offset 20 --limit 10

  # JSON output
  python scripts/search_agents_paged.py "backend" --json

  # Large page size
  python scripts/search_agents_paged.py "api" --page-size 50
        """
    )

    parser.add_argument('query', help='Search query')
    parser.add_argument('--page', type=int, default=1, help='Page number (1-indexed, default: 1)')
    parser.add_argument('--page-size', type=int, default=20, help='Items per page (default: 20)')
    parser.add_argument('--offset', type=int, help='Starting offset (0-indexed, overrides --page)')
    parser.add_argument('--limit', type=int, help='Max results to return (used with --offset)')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')

    args = parser.parse_args()

    # Load registry
    registry = load_registry()
    if not registry:
        sys.exit(1)

    # Search all matching agents
    all_results = search_agents_all(args.query, registry)

    # Paginate results
    paginated = paginate_results(
        all_results,
        page=args.page,
        page_size=args.page_size,
        offset=args.offset,
        limit=args.limit
    )
    paginated['query'] = args.query

    # Format and print
    output = format_results(paginated, json_output=args.json)
    print(output)


if __name__ == '__main__':
    main()
