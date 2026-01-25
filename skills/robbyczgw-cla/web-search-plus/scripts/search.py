#!/usr/bin/env python3
"""
Web Search Plus — Unified Multi-Provider Search with Intelligent Auto-Routing
Supports: Serper (Google), Tavily (Research), Exa (Neural)

Smart Routing uses multi-signal analysis:
  - Query intent classification (shopping, research, discovery)
  - Linguistic pattern detection (how much vs how does)
  - Product/brand recognition
  - URL detection
  - Confidence scoring

Usage:
    python3 search.py --query "..."                    # Auto-route based on query
    python3 search.py --provider [serper|tavily|exa] --query "..." [options]

Examples:
    python3 search.py -q "iPhone 16 Pro price"              # → Serper (shopping intent)
    python3 search.py -q "how does quantum entanglement work"  # → Tavily (research intent)
    python3 search.py -q "startups similar to Notion"       # → Exa (discovery intent)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_CONFIG = {
    "defaults": {
        "provider": "serper",
        "max_results": 5
    },
    "auto_routing": {
        "enabled": True,
        "fallback_provider": "serper",
        "provider_priority": ["serper", "tavily", "exa"],
        "disabled_providers": [],
        "confidence_threshold": 0.3,  # Below this, note low confidence
    },
    "serper": {
        "country": "us",
        "language": "en",
        "type": "search"
    },
    "tavily": {
        "depth": "basic",
        "topic": "general"
    },
    "exa": {
        "type": "neural"
    }
}


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json if it exists, with defaults."""
    config = DEFAULT_CONFIG.copy()
    config_path = Path(__file__).parent.parent / "config.json"
    
    if config_path.exists():
        try:
            with open(config_path) as f:
                user_config = json.load(f)
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in config:
                        config[key] = {**config.get(key, {}), **value}
                    else:
                        config[key] = value
        except (json.JSONDecodeError, IOError) as e:
            print(json.dumps({
                "warning": f"Could not load config.json: {e}",
                "using": "default configuration"
            }), file=sys.stderr)
    
    return config


def get_env_key(provider: str) -> Optional[str]:
    """Get API key for provider from environment."""
    key_map = {
        "serper": "SERPER_API_KEY",
        "tavily": "TAVILY_API_KEY",
        "exa": "EXA_API_KEY",
    }
    return os.environ.get(key_map.get(provider, ""))


def validate_api_key(provider: str) -> str:
    """Validate and return API key, with helpful error messages."""
    key = get_env_key(provider)
    
    if not key:
        env_var = {
            "serper": "SERPER_API_KEY",
            "tavily": "TAVILY_API_KEY", 
            "exa": "EXA_API_KEY"
        }[provider]
        
        urls = {
            "serper": "https://serper.dev",
            "tavily": "https://tavily.com",
            "exa": "https://exa.ai"
        }
        
        error_msg = {
            "error": f"Missing API key for {provider}",
            "env_var": env_var,
            "how_to_fix": [
                f"1. Get your API key from {urls[provider]}",
                f"2. Set the environment variable:",
                f"   export {env_var}=\"your-key\"",
            ],
            "provider": provider
        }
        print(json.dumps(error_msg, indent=2), file=sys.stderr)
        sys.exit(1)
    
    if len(key) < 10:
        print(json.dumps({
            "error": f"API key for {provider} appears invalid (too short)",
            "provider": provider
        }, indent=2), file=sys.stderr)
        sys.exit(1)
    
    return key


# =============================================================================
# Intelligent Auto-Routing Engine
# =============================================================================

class QueryAnalyzer:
    """
    Intelligent query analysis for smart provider routing.
    
    Uses multi-signal analysis:
    - Intent classification (shopping, research, discovery, local, news)
    - Linguistic patterns (question structure, phrase patterns)
    - Entity detection (products, brands, URLs, dates)
    - Complexity assessment
    """
    
    # Intent signal patterns with weights
    # Higher weight = stronger signal for that provider
    
    SHOPPING_SIGNALS = {
        # Price patterns (very strong)
        r'\bhow much\b': 4.0,
        r'\bprice of\b': 4.0,
        r'\bcost of\b': 4.0,
        r'\bprices?\b': 3.0,
        r'\$\d+|\d+\s*dollars?': 3.0,
        r'€\d+|\d+\s*euros?': 3.0,
        r'£\d+|\d+\s*pounds?': 3.0,
        
        # German price patterns (sehr stark)
        r'\bpreis(e)?\b': 3.5,
        r'\bkosten\b': 3.0,
        r'\bwieviel\b': 3.5,
        r'\bwie viel\b': 3.5,
        r'\bwas kostet\b': 4.0,
        
        # Purchase intent (strong)
        r'\bbuy\b': 3.5,
        r'\bpurchase\b': 3.5,
        r'\border\b(?!\s+by)': 3.0,  # "order" but not "order by"
        r'\bshopping\b': 3.5,
        r'\bshop for\b': 3.5,
        r'\bwhere to (buy|get|purchase)\b': 4.0,
        
        # German purchase intent (stark)
        r'\bkaufen\b': 3.5,
        r'\bbestellen\b': 3.5,
        r'\bwo kaufen\b': 4.0,
        r'\bhändler\b': 3.0,
        r'\bshop\b': 2.5,
        
        # Deal/discount signals
        r'\bdeal(s)?\b': 3.0,
        r'\bdiscount(s)?\b': 3.0,
        r'\bsale\b': 2.5,
        r'\bcheap(er|est)?\b': 3.0,
        r'\baffordable\b': 2.5,
        r'\bbudget\b': 2.5,
        r'\bbest price\b': 3.5,
        r'\bcompare prices\b': 3.5,
        r'\bcoupon\b': 3.0,
        
        # German deal/discount signals
        r'\bgünstig(er|ste)?\b': 3.0,
        r'\bbillig(er|ste)?\b': 3.0,
        r'\bangebot(e)?\b': 3.0,
        r'\brabatt\b': 3.0,
        r'\baktion\b': 2.5,
        r'\bschnäppchen\b': 3.0,
        
        # Product comparison
        r'\bvs\.?\b': 2.0,
        r'\bversus\b': 2.0,
        r'\bor\b.*\bwhich\b': 2.0,
        r'\bspecs?\b': 2.5,
        r'\bspecifications?\b': 2.5,
        r'\breview(s)?\b': 2.0,
        r'\brating(s)?\b': 2.0,
        r'\bunboxing\b': 2.5,
        
        # German product comparison
        r'\btest\b': 2.5,
        r'\bbewertung(en)?\b': 2.5,
        r'\btechnische daten\b': 3.0,
        r'\bspezifikationen\b': 2.5,
    }
    
    RESEARCH_SIGNALS = {
        # Explanation patterns (very strong)
        r'\bhow does\b': 4.0,
        r'\bhow do\b': 3.5,
        r'\bwhy does\b': 4.0,
        r'\bwhy do\b': 3.5,
        r'\bwhy is\b': 3.5,
        r'\bexplain\b': 4.0,
        r'\bexplanation\b': 4.0,
        r'\bwhat is\b': 3.0,
        r'\bwhat are\b': 3.0,
        r'\bdefine\b': 3.5,
        r'\bdefinition of\b': 3.5,
        r'\bmeaning of\b': 3.0,
        
        # Analysis patterns (strong)
        r'\banalyze\b': 3.5,
        r'\banalysis\b': 3.5,
        r'\bcompare\b(?!\s*prices?)': 3.0,  # compare but not "compare prices"
        r'\bcomparison\b': 3.0,
        r'\bpros and cons\b': 4.0,
        r'\badvantages?\b': 3.0,
        r'\bdisadvantages?\b': 3.0,
        r'\bbenefits?\b': 2.5,
        r'\bdrawbacks?\b': 3.0,
        r'\bdifference between\b': 3.5,
        
        # Learning patterns
        r'\bunderstand\b': 3.0,
        r'\blearn(ing)?\b': 2.5,
        r'\btutorial\b': 3.0,
        r'\bguide\b': 2.5,
        r'\bhow to\b': 2.0,  # Lower weight - could be shopping too
        r'\bstep by step\b': 3.0,
        
        # Depth signals
        r'\bin[- ]depth\b': 3.0,
        r'\bdetailed\b': 2.5,
        r'\bcomprehensive\b': 3.0,
        r'\bthorough\b': 2.5,
        r'\bdeep dive\b': 3.5,
        r'\boverall\b': 2.0,
        r'\bsummary\b': 2.0,
        
        # Academic patterns
        r'\bstudy\b': 2.5,
        r'\bresearch shows\b': 3.5,
        r'\baccording to\b': 2.5,
        r'\bevidence\b': 3.0,
        r'\bscientific\b': 3.0,
        r'\bhistory of\b': 3.0,
        r'\bbackground\b': 2.5,
        r'\bcontext\b': 2.5,
        r'\bimplications?\b': 3.0,
        
        # German explanation patterns (sehr stark)
        r'\bwie funktioniert\b': 4.0,
        r'\bwarum\b': 3.5,
        r'\berklär(en|ung)?\b': 4.0,
        r'\bwas ist\b': 3.0,
        r'\bwas sind\b': 3.0,
        r'\bbedeutung\b': 3.0,
        
        # German analysis patterns
        r'\banalyse\b': 3.5,
        r'\bvergleich(en)?\b': 3.0,
        r'\bvor- und nachteile\b': 4.0,
        r'\bvorteile\b': 3.0,
        r'\bnachteile\b': 3.0,
        r'\bunterschied(e)?\b': 3.5,
        
        # German learning patterns
        r'\bverstehen\b': 3.0,
        r'\blernen\b': 2.5,
        r'\banleitung\b': 3.0,
        r'\bübersicht\b': 2.5,
        r'\bhintergrund\b': 2.5,
        r'\bzusammenfassung\b': 2.5,
    }
    
    DISCOVERY_SIGNALS = {
        # Similarity patterns (very strong)
        r'\bsimilar to\b': 5.0,
        r'\blike\s+\w+\.com': 4.5,  # "like notion.com"
        r'\balternatives? to\b': 5.0,
        r'\bcompetitors? (of|to)\b': 4.5,
        r'\bcompeting with\b': 4.0,
        r'\brivals? (of|to)\b': 4.0,
        r'\binstead of\b': 3.0,
        r'\breplacement for\b': 3.5,
        
        # Company/startup patterns (strong)
        r'\bcompanies (like|that|doing|building)\b': 4.5,
        r'\bstartups? (like|that|doing|building)\b': 4.5,
        r'\bwho else\b': 4.0,
        r'\bother (companies|startups|tools|apps)\b': 3.5,
        r'\bfind (companies|startups|tools)\b': 4.0,
        
        # Funding/business patterns
        r'\bseries [a-d]\b': 4.0,
        r'\byc\b|y combinator': 4.0,
        r'\bfund(ed|ing|raise)\b': 3.5,
        r'\bventure\b': 3.0,
        r'\bvaluation\b': 3.0,
        
        # Category patterns
        r'\bresearch papers? (on|about)\b': 4.0,
        r'\barxiv\b': 4.5,
        r'\bgithub (projects?|repos?)\b': 4.5,
        r'\bopen source\b.*\bprojects?\b': 4.0,
        r'\btweets? (about|on)\b': 3.5,
        r'\bblogs? (about|on|like)\b': 3.0,
        
        # URL detection (very strong signal for Exa similar)
        r'https?://[^\s]+': 5.0,
        r'\b\w+\.(com|org|io|ai|co|dev)\b': 3.5,
    }
    
    LOCAL_NEWS_SIGNALS = {
        # Local patterns → Serper
        r'\bnear me\b': 4.0,
        r'\bnearby\b': 3.5,
        r'\blocal\b': 3.0,
        r'\bin (my )?(city|area|town|neighborhood)\b': 3.5,
        r'\brestaurants?\b': 2.5,
        r'\bhotels?\b': 2.5,
        r'\bcafes?\b': 2.5,
        r'\bstores?\b': 2.0,
        r'\bdirections? to\b': 3.5,
        r'\bmap of\b': 3.0,
        r'\bphone number\b': 3.0,
        r'\baddress of\b': 3.0,
        r'\bopen(ing)? hours\b': 3.0,
        
        # Weather/time
        r'\bweather\b': 4.0,
        r'\bforecast\b': 3.5,
        r'\btemperature\b': 3.0,
        r'\btime in\b': 3.0,
        
        # News/recency patterns → Serper (or Tavily for news depth)
        r'\blatest\b': 2.5,
        r'\brecent\b': 2.5,
        r'\btoday\b': 2.5,
        r'\bbreaking\b': 3.5,
        r'\bnews\b': 2.5,
        r'\bheadlines?\b': 3.0,
        r'\b202[4-9]\b': 2.0,  # Current year mentions
        r'\blast (week|month|year)\b': 2.0,
    }
    
    # Brand/product patterns for shopping detection
    BRAND_PATTERNS = [
        # Tech brands
        r'\b(apple|iphone|ipad|macbook|airpods?)\b',
        r'\b(samsung|galaxy)\b',
        r'\b(google|pixel)\b',
        r'\b(microsoft|surface|xbox)\b',
        r'\b(sony|playstation)\b',
        r'\b(nvidia|geforce|rtx)\b',
        r'\b(amd|ryzen|radeon)\b',
        r'\b(intel|core i[3579])\b',
        r'\b(dell|hp|lenovo|asus|acer)\b',
        r'\b(lg|tcl|hisense)\b',
        
        # Product categories
        r'\b(laptop|phone|tablet|tv|monitor|headphones?|earbuds?)\b',
        r'\b(camera|lens|drone)\b',
        r'\b(watch|smartwatch|fitbit|garmin)\b',
        r'\b(router|modem|wifi)\b',
        r'\b(keyboard|mouse|gaming)\b',
    ]
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.auto_config = config.get("auto_routing", DEFAULT_CONFIG["auto_routing"])
    
    def _calculate_signal_score(
        self, 
        query: str, 
        signals: Dict[str, float]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calculate score for a signal category.
        Returns (total_score, list of matched signals with details).
        """
        query_lower = query.lower()
        matches = []
        total_score = 0.0
        
        for pattern, weight in signals.items():
            regex = re.compile(pattern, re.IGNORECASE)
            found = regex.findall(query_lower)
            if found:
                # Normalize found matches
                match_text = found[0] if isinstance(found[0], str) else found[0][0] if found[0] else pattern
                matches.append({
                    "pattern": pattern,
                    "matched": match_text,
                    "weight": weight
                })
                total_score += weight
        
        return total_score, matches
    
    def _detect_product_brand_combo(self, query: str) -> float:
        """
        Detect product + brand combinations which strongly indicate shopping intent.
        Returns a bonus score.
        """
        query_lower = query.lower()
        brand_found = False
        product_found = False
        
        for pattern in self.BRAND_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                brand_found = True
                break
        
        # Check for product indicators
        product_indicators = [
            r'\b(buy|price|specs?|review|vs|compare)\b',
            r'\b(pro|max|plus|mini|ultra|lite)\b',  # Product tier names
            r'\b\d+\s*(gb|tb|inch|mm|hz)\b',  # Specifications
        ]
        for pattern in product_indicators:
            if re.search(pattern, query_lower, re.IGNORECASE):
                product_found = True
                break
        
        if brand_found and product_found:
            return 3.0  # Strong shopping signal
        elif brand_found:
            return 1.5  # Moderate shopping signal
        return 0.0
    
    def _detect_url(self, query: str) -> Optional[str]:
        """Detect URLs in query - strong signal for Exa similar search."""
        url_pattern = r'https?://[^\s]+'
        match = re.search(url_pattern, query)
        if match:
            return match.group()
        
        # Also check for domain-like patterns
        domain_pattern = r'\b(\w+\.(com|org|io|ai|co|dev|net|app))\b'
        match = re.search(domain_pattern, query, re.IGNORECASE)
        if match:
            return match.group()
        
        return None
    
    def _assess_query_complexity(self, query: str) -> Dict[str, Any]:
        """
        Assess query complexity - complex queries favor Tavily.
        """
        words = query.split()
        word_count = len(words)
        
        # Count question words
        question_words = len(re.findall(
            r'\b(what|why|how|when|where|which|who|whose|whom)\b', 
            query, re.IGNORECASE
        ))
        
        # Check for multiple clauses
        clause_markers = len(re.findall(
            r'\b(and|but|or|because|since|while|although|if|when)\b',
            query, re.IGNORECASE
        ))
        
        complexity_score = 0.0
        if word_count > 10:
            complexity_score += 1.5
        if word_count > 20:
            complexity_score += 1.0
        if question_words > 1:
            complexity_score += 1.0
        if clause_markers > 0:
            complexity_score += 0.5 * clause_markers
        
        return {
            "word_count": word_count,
            "question_words": question_words,
            "clause_markers": clause_markers,
            "complexity_score": complexity_score,
            "is_complex": complexity_score > 2.0
        }
    
    def _detect_recency_intent(self, query: str) -> Tuple[bool, float]:
        """
        Detect if query wants recent/timely information.
        Returns (is_recency_focused, score).
        """
        recency_patterns = [
            (r'\b(latest|newest|recent|current)\b', 2.5),
            (r'\b(today|yesterday|this week|this month)\b', 3.0),
            (r'\b(202[4-9]|2030)\b', 2.0),
            (r'\b(breaking|live|just|now)\b', 3.0),
            (r'\blast (hour|day|week|month)\b', 2.5),
        ]
        
        total = 0.0
        for pattern, weight in recency_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                total += weight
        
        return total > 2.0, total
    
    def analyze(self, query: str) -> Dict[str, Any]:
        """
        Perform comprehensive query analysis.
        Returns detailed analysis with scores for each provider.
        """
        # Calculate scores for each intent category
        shopping_score, shopping_matches = self._calculate_signal_score(
            query, self.SHOPPING_SIGNALS
        )
        research_score, research_matches = self._calculate_signal_score(
            query, self.RESEARCH_SIGNALS
        )
        discovery_score, discovery_matches = self._calculate_signal_score(
            query, self.DISCOVERY_SIGNALS
        )
        local_news_score, local_news_matches = self._calculate_signal_score(
            query, self.LOCAL_NEWS_SIGNALS
        )
        
        # Apply product/brand bonus to shopping
        brand_bonus = self._detect_product_brand_combo(query)
        if brand_bonus > 0:
            shopping_score += brand_bonus
            shopping_matches.append({
                "pattern": "product_brand_combo",
                "matched": "brand + product detected",
                "weight": brand_bonus
            })
        
        # Detect URL → strong Exa signal
        detected_url = self._detect_url(query)
        if detected_url:
            discovery_score += 5.0
            discovery_matches.append({
                "pattern": "url_detected",
                "matched": detected_url,
                "weight": 5.0
            })
        
        # Assess complexity → favors Tavily
        complexity = self._assess_query_complexity(query)
        if complexity["is_complex"]:
            research_score += complexity["complexity_score"]
            research_matches.append({
                "pattern": "query_complexity",
                "matched": f"complex query ({complexity['word_count']} words)",
                "weight": complexity["complexity_score"]
            })
        
        # Check recency intent
        is_recency, recency_score = self._detect_recency_intent(query)
        
        # Map intents to providers with final scores
        provider_scores = {
            "serper": shopping_score + local_news_score + (recency_score * 0.5),
            "tavily": research_score + (complexity["complexity_score"] if not complexity["is_complex"] else 0),
            "exa": discovery_score,
        }
        
        # Build match details per provider
        provider_matches = {
            "serper": shopping_matches + local_news_matches,
            "tavily": research_matches,
            "exa": discovery_matches,
        }
        
        return {
            "query": query,
            "provider_scores": provider_scores,
            "provider_matches": provider_matches,
            "detected_url": detected_url,
            "complexity": complexity,
            "recency_focused": is_recency,
            "recency_score": recency_score,
        }
    
    def route(self, query: str) -> Dict[str, Any]:
        """
        Route query to optimal provider with confidence scoring.
        """
        analysis = self.analyze(query)
        scores = analysis["provider_scores"]
        
        # Filter to available providers
        disabled = set(self.auto_config.get("disabled_providers", []))
        available = {
            p: s for p, s in scores.items() 
            if p not in disabled and get_env_key(p)
        }
        
        if not available:
            # No providers available, use fallback
            fallback = self.auto_config.get("fallback_provider", "serper")
            return {
                "provider": fallback,
                "confidence": 0.0,
                "reason": "no_available_providers",
                "scores": scores,
                "top_signals": [],
                "analysis": analysis,
            }
        
        # Find the winner
        max_score = max(available.values())
        total_score = sum(available.values()) or 1.0
        
        # Handle ties using priority
        priority = self.auto_config.get("provider_priority", ["serper", "tavily", "exa"])
        winners = [p for p, s in available.items() if s == max_score]
        
        if len(winners) > 1:
            # Use priority to break tie
            for p in priority:
                if p in winners:
                    winner = p
                    break
            else:
                winner = winners[0]
        else:
            winner = winners[0]
        
        # Calculate confidence
        # High confidence = clear winner with good margin
        if max_score == 0:
            confidence = 0.0
            reason = "no_signals_matched"
        else:
            # Confidence based on:
            # 1. Absolute score (is it strong enough?)
            # 2. Relative margin (is there a clear winner?)
            second_best = sorted(available.values(), reverse=True)[1] if len(available) > 1 else 0
            margin = (max_score - second_best) / max_score if max_score > 0 else 0
            
            # Normalize score to 0-1 range (assuming max reasonable score ~15)
            normalized_score = min(max_score / 15.0, 1.0)
            
            # Confidence is combination of absolute strength and relative margin
            confidence = round((normalized_score * 0.6 + margin * 0.4), 3)
            
            if confidence >= 0.7:
                reason = "high_confidence_match"
            elif confidence >= 0.4:
                reason = "moderate_confidence_match"
            else:
                reason = "low_confidence_match"
        
        # Get top signals for the winning provider
        matches = analysis["provider_matches"].get(winner, [])
        top_signals = sorted(matches, key=lambda x: x["weight"], reverse=True)[:5]
        
        # Special case: URL detected and Exa available → strong recommendation
        if analysis["detected_url"] and "exa" in available:
            if winner != "exa":
                # Override if URL is present but didn't win
                # (user might want similar search)
                pass  # Keep current winner but note it
        
        # Build detailed routing result
        threshold = self.auto_config.get("confidence_threshold", 0.3)
        
        return {
            "provider": winner,
            "confidence": confidence,
            "confidence_level": "high" if confidence >= 0.7 else "medium" if confidence >= 0.4 else "low",
            "reason": reason,
            "scores": {p: round(s, 2) for p, s in available.items()},
            "winning_score": round(max_score, 2),
            "top_signals": [
                {"matched": s["matched"], "weight": s["weight"]} 
                for s in top_signals
            ],
            "below_threshold": confidence < threshold,
            "analysis_summary": {
                "query_length": len(query.split()),
                "is_complex": analysis["complexity"]["is_complex"],
                "has_url": analysis["detected_url"] is not None,
                "recency_focused": analysis["recency_focused"],
            }
        }


def auto_route_provider(query: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Intelligently route query to the best provider.
    Returns detailed routing decision with confidence.
    """
    analyzer = QueryAnalyzer(config)
    return analyzer.route(query)


def explain_routing(query: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provide detailed explanation of routing decision for debugging.
    """
    analyzer = QueryAnalyzer(config)
    analysis = analyzer.analyze(query)
    routing = analyzer.route(query)
    
    return {
        "query": query,
        "routing_decision": {
            "provider": routing["provider"],
            "confidence": routing["confidence"],
            "confidence_level": routing["confidence_level"],
            "reason": routing["reason"],
        },
        "scores": routing["scores"],
        "top_signals": routing["top_signals"],
        "intent_breakdown": {
            "shopping_signals": len(analysis["provider_matches"]["serper"]),
            "research_signals": len(analysis["provider_matches"]["tavily"]),
            "discovery_signals": len(analysis["provider_matches"]["exa"]),
        },
        "query_analysis": {
            "word_count": analysis["complexity"]["word_count"],
            "is_complex": analysis["complexity"]["is_complex"],
            "complexity_score": round(analysis["complexity"]["complexity_score"], 2),
            "has_url": analysis["detected_url"],
            "recency_focused": analysis["recency_focused"],
        },
        "all_matches": {
            provider: [
                {"matched": m["matched"], "weight": m["weight"]}
                for m in matches
            ]
            for provider, matches in analysis["provider_matches"].items()
            if matches
        },
        "available_providers": [
            p for p in ["serper", "tavily", "exa"] 
            if get_env_key(p) and p not in config.get("auto_routing", {}).get("disabled_providers", [])
        ]
    }


# =============================================================================
# HTTP Client
# =============================================================================

def make_request(url: str, headers: dict, body: dict, timeout: int = 30) -> dict:
    """Make HTTP POST request and return JSON response."""
    data = json.dumps(body).encode("utf-8")
    req = Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        try:
            error_json = json.loads(error_body)
            error_detail = error_json.get("error") or error_json.get("message") or error_body
        except json.JSONDecodeError:
            error_detail = error_body[:500]
        
        error_messages = {
            401: "Invalid or expired API key. Please check your credentials.",
            403: "Access forbidden. Your API key may not have permission for this operation.",
            429: "Rate limit exceeded. Please wait a moment and try again.",
            500: "Server error. The search provider is experiencing issues.",
            503: "Service unavailable. The search provider may be down."
        }
        
        friendly_msg = error_messages.get(e.code, f"API error: {error_detail}")
        raise Exception(f"{friendly_msg} (HTTP {e.code})")
    except URLError as e:
        raise Exception(f"Network error: {e.reason}. Check your internet connection.")
    except TimeoutError:
        raise Exception(f"Request timed out after {timeout}s. Try again or reduce max_results.")


# =============================================================================
# Serper (Google Search API)
# =============================================================================

def search_serper(
    query: str,
    api_key: str,
    max_results: int = 5,
    country: str = "us",
    language: str = "en",
    search_type: str = "search",
    time_range: Optional[str] = None,
    include_images: bool = False,
) -> dict:
    """Search using Serper (Google Search API)."""
    endpoint = f"https://google.serper.dev/{search_type}"
    
    body = {
        "q": query,
        "gl": country,
        "hl": language,
        "num": max_results,
        "autocorrect": True,
    }
    
    if time_range and time_range != "none":
        tbs_map = {
            "hour": "qdr:h",
            "day": "qdr:d",
            "week": "qdr:w",
            "month": "qdr:m",
            "year": "qdr:y",
        }
        if time_range in tbs_map:
            body["tbs"] = tbs_map[time_range]
    
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    
    data = make_request(endpoint, headers, body)
    
    results = []
    for i, item in enumerate(data.get("organic", [])[:max_results]):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", ""),
            "score": round(1.0 - i * 0.1, 2),
            "date": item.get("date"),
        })
    
    answer = ""
    if data.get("answerBox", {}).get("answer"):
        answer = data["answerBox"]["answer"]
    elif data.get("answerBox", {}).get("snippet"):
        answer = data["answerBox"]["snippet"]
    elif data.get("knowledgeGraph", {}).get("description"):
        answer = data["knowledgeGraph"]["description"]
    elif results:
        answer = results[0]["snippet"]
    
    images = []
    if include_images:
        try:
            img_data = make_request(
                "https://google.serper.dev/images",
                headers,
                {"q": query, "gl": country, "hl": language, "num": 5},
            )
            images = [img.get("imageUrl", "") for img in img_data.get("images", [])[:5] if img.get("imageUrl")]
        except Exception:
            pass
    
    return {
        "provider": "serper",
        "query": query,
        "results": results,
        "images": images,
        "answer": answer,
        "knowledge_graph": data.get("knowledgeGraph"),
        "related_searches": [r.get("query") for r in data.get("relatedSearches", [])]
    }


# =============================================================================
# Tavily (Research Search)
# =============================================================================

def search_tavily(
    query: str,
    api_key: str,
    max_results: int = 5,
    depth: str = "basic",
    topic: str = "general",
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    include_images: bool = False,
    include_raw_content: bool = False,
) -> dict:
    """Search using Tavily (AI Research Search)."""
    endpoint = "https://api.tavily.com/search"
    
    body = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": depth,
        "topic": topic,
        "include_images": include_images,
        "include_answer": True,
        "include_raw_content": include_raw_content,
    }
    
    if include_domains:
        body["include_domains"] = include_domains
    if exclude_domains:
        body["exclude_domains"] = exclude_domains
    
    headers = {"Content-Type": "application/json"}
    
    data = make_request(endpoint, headers, body)
    
    results = []
    for item in data.get("results", [])[:max_results]:
        result = {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("content", ""),
            "score": round(item.get("score", 0.0), 3),
        }
        if include_raw_content and item.get("raw_content"):
            result["raw_content"] = item["raw_content"]
        results.append(result)
    
    return {
        "provider": "tavily",
        "query": query,
        "results": results,
        "images": data.get("images", []),
        "answer": data.get("answer", ""),
    }


# =============================================================================
# Exa (Neural/Semantic Search)
# =============================================================================

def search_exa(
    query: str,
    api_key: str,
    max_results: int = 5,
    search_type: str = "neural",
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    similar_url: Optional[str] = None,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
) -> dict:
    """Search using Exa (Neural/Semantic Search)."""
    if similar_url:
        endpoint = "https://api.exa.ai/findSimilar"
        body = {
            "url": similar_url,
            "numResults": max_results,
            "contents": {
                "text": {"maxCharacters": 1000},
                "highlights": True,
            },
        }
    else:
        endpoint = "https://api.exa.ai/search"
        body = {
            "query": query,
            "numResults": max_results,
            "type": search_type,
            "contents": {
                "text": {"maxCharacters": 1000},
                "highlights": True,
            },
        }
    
    if category:
        body["category"] = category
    if start_date:
        body["startPublishedDate"] = start_date
    if end_date:
        body["endPublishedDate"] = end_date
    if include_domains:
        body["includeDomains"] = include_domains
    if exclude_domains:
        body["excludeDomains"] = exclude_domains
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }
    
    data = make_request(endpoint, headers, body)
    
    results = []
    for item in data.get("results", [])[:max_results]:
        highlights = item.get("highlights", [])
        snippet = highlights[0] if highlights else (item.get("text", "") or "")[:500]
        
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": snippet,
            "score": round(item.get("score", 0.0), 3),
            "published_date": item.get("publishedDate"),
            "author": item.get("author"),
        })
    
    answer = results[0]["snippet"] if results else ""
    
    return {
        "provider": "exa",
        "query": query if not similar_url else f"Similar to: {similar_url}",
        "results": results,
        "images": [],
        "answer": answer,
    }


# =============================================================================
# CLI
# =============================================================================

def main():
    config = load_config()
    
    parser = argparse.ArgumentParser(
        description="Web Search Plus — Intelligent multi-provider search with smart auto-routing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Intelligent Auto-Routing:
  The query is analyzed using multi-signal detection to find the optimal provider:
  
  Shopping Intent → Serper (Google)
    "how much", "price of", "buy", product+brand combos, deals, specs
  
  Research Intent → Tavily  
    "how does", "explain", "what is", analysis, pros/cons, tutorials
  
  Discovery Intent → Exa (Neural)
    "similar to", "companies like", "alternatives", URLs, startups, papers

Examples:
  python3 search.py -q "iPhone 16 Pro Max price"          # → Serper (shopping)
  python3 search.py -q "how does HTTPS encryption work"   # → Tavily (research)
  python3 search.py -q "startups similar to Notion"       # → Exa (discovery)
  python3 search.py --explain-routing -q "your query"     # Debug routing

Full docs: See README.md and SKILL.md
        """,
    )
    
    # Common arguments
    parser.add_argument(
        "--provider", "-p", 
        choices=["serper", "tavily", "exa", "auto"],
        help="Search provider (auto=intelligent routing)"
    )
    parser.add_argument(
        "--query", "-q", 
        help="Search query"
    )
    parser.add_argument(
        "--max-results", "-n", 
        type=int, 
        default=config.get("defaults", {}).get("max_results", 5),
        help="Maximum results (default: 5)"
    )
    parser.add_argument(
        "--images", 
        action="store_true",
        help="Include images (Serper/Tavily)"
    )
    
    # Auto-routing options
    parser.add_argument(
        "--auto", "-a",
        action="store_true",
        help="Use intelligent auto-routing (default when no provider specified)"
    )
    parser.add_argument(
        "--explain-routing",
        action="store_true",
        help="Show detailed routing analysis (debug mode)"
    )
    
    # Serper-specific
    serper_config = config.get("serper", {})
    parser.add_argument("--country", default=serper_config.get("country", "us"))
    parser.add_argument("--language", default=serper_config.get("language", "en"))
    parser.add_argument(
        "--type", 
        dest="search_type", 
        default=serper_config.get("type", "search"),
        choices=["search", "news", "images", "videos", "places", "shopping"]
    )
    parser.add_argument(
        "--time-range", 
        choices=["hour", "day", "week", "month", "year"]
    )
    
    # Tavily-specific
    tavily_config = config.get("tavily", {})
    parser.add_argument(
        "--depth", 
        default=tavily_config.get("depth", "basic"), 
        choices=["basic", "advanced"]
    )
    parser.add_argument(
        "--topic", 
        default=tavily_config.get("topic", "general"), 
        choices=["general", "news"]
    )
    parser.add_argument("--raw-content", action="store_true")
    
    # Exa-specific
    exa_config = config.get("exa", {})
    parser.add_argument(
        "--exa-type", 
        default=exa_config.get("type", "neural"), 
        choices=["neural", "keyword"]
    )
    parser.add_argument(
        "--category",
        choices=[
            "company", "research paper", "news", "pdf", "github", 
            "tweet", "personal site", "linkedin profile"
        ]
    )
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--similar-url")
    
    # Domain filters
    parser.add_argument("--include-domains", nargs="+")
    parser.add_argument("--exclude-domains", nargs="+")
    
    # Output
    parser.add_argument("--compact", action="store_true")
    
    args = parser.parse_args()
    
    if not args.query and not args.similar_url:
        parser.error("--query is required (unless using --similar-url with Exa)")
    
    # Handle --explain-routing
    if args.explain_routing:
        if not args.query:
            parser.error("--query is required for --explain-routing")
        explanation = explain_routing(args.query, config)
        indent = None if args.compact else 2
        print(json.dumps(explanation, indent=indent, ensure_ascii=False))
        return
    
    # Determine provider
    if args.provider == "auto" or (args.provider is None and not args.similar_url):
        if args.query:
            routing = auto_route_provider(args.query, config)
            provider = routing["provider"]
            routing_info = {
                "auto_routed": True,
                "provider": provider,
                "confidence": routing["confidence"],
                "confidence_level": routing["confidence_level"],
                "reason": routing["reason"],
                "top_signals": routing["top_signals"],
                "scores": routing["scores"],
            }
        else:
            provider = "exa"
            routing_info = {
                "auto_routed": True,
                "provider": "exa",
                "confidence": 1.0,
                "confidence_level": "high",
                "reason": "similar_url_specified",
            }
    else:
        provider = args.provider or "serper"
        routing_info = {"auto_routed": False, "provider": provider}
    
    # Validate API key
    api_key = validate_api_key(provider)
    
    try:
        if provider == "serper":
            result = search_serper(
                query=args.query,
                api_key=api_key,
                max_results=args.max_results,
                country=args.country,
                language=args.language,
                search_type=args.search_type,
                time_range=args.time_range,
                include_images=args.images,
            )
        elif provider == "tavily":
            result = search_tavily(
                query=args.query,
                api_key=api_key,
                max_results=args.max_results,
                depth=args.depth,
                topic=args.topic,
                include_domains=args.include_domains,
                exclude_domains=args.exclude_domains,
                include_images=args.images,
                include_raw_content=args.raw_content,
            )
        elif provider == "exa":
            result = search_exa(
                query=args.query or "",
                api_key=api_key,
                max_results=args.max_results,
                search_type=args.exa_type,
                category=args.category,
                start_date=args.start_date,
                end_date=args.end_date,
                similar_url=args.similar_url,
                include_domains=args.include_domains,
                exclude_domains=args.exclude_domains,
            )
        
        result["routing"] = routing_info
        
        indent = None if args.compact else 2
        print(json.dumps(result, indent=indent, ensure_ascii=False))
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "provider": provider,
            "query": args.query,
            "routing": routing_info,
        }
        print(json.dumps(error_result, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
