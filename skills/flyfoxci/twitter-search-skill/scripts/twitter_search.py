#!/usr/bin/env python3
"""
Twitter Advanced Search Script for Claude Code Skill

This script fetches tweets from the Twitter API using advanced search,
and returns the data in a structured format for analysis.

Requirements:
- requests library (pip install requests)

Usage:
    python twitter_search.py <api_key> <query> [--max-results MAX_RESULTS]

Environment variable:
    TWITTER_API_KEY - Alternatively, set this environment variable

API Documentation:
    https://docs.twitterapi.io/api-reference/endpoint/tweet_advanced_search

Query Syntax:
    Basic: "keyword"
    Multiple keywords: "AI" OR "ChatGPT"
    From user: from:username
    Since date: since:2024-01-01
    Complex: "AI" OR "ChatGPT" from:elonmusk since:2024-01-01

    More examples: https://github.com/igorbrigadir/twitter-advanced-search
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import requests
except ImportError:
    print("Error: 'requests' library is required. Install it with: pip install requests")
    sys.exit(1)


# Constants
API_BASE_URL = "https://api.twitterapi.io/twitter/tweet/advanced_search"
DEFAULT_MAX_RESULTS = 1000
RESULTS_PER_PAGE = 20


class TwitterSearchError(Exception):
    """Custom exception for Twitter search errors."""
    pass


def get_api_key(api_key_arg: Optional[str]) -> str:
    """
    Get API key from argument or environment variable.

    Args:
        api_key_arg: API key passed as argument

    Returns:
        The API key to use

    Raises:
        TwitterSearchError: If no API key is provided
    """
    api_key = api_key_arg or os.environ.get("TWITTER_API_KEY")
    if not api_key:
        raise TwitterSearchError(
            "API key is required. Provide it as an argument or set TWITTER_API_KEY environment variable."
        )
    return api_key


def fetch_tweets(api_key: str, query: str, query_type: str = "Top", cursor: str = "") -> Dict[str, Any]:
    """
    Fetch a single page of tweets from the Twitter API.

    Args:
        api_key: Twitter API key
        query: Search query string
        query_type: Query type ("Latest" or "Top")
        cursor: Pagination cursor (empty string for first page)

    Returns:
        JSON response from the API

    Raises:
        TwitterSearchError: If the API request fails
    """
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    params = {
        "query": query,
        "queryType": query_type,
        "cursor": cursor
    }

    try:
        response = requests.get(API_BASE_URL, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise TwitterSearchError(f"API request failed: {str(e)}")


def fetch_all_tweets(api_key: str, query: str, max_results: int = DEFAULT_MAX_RESULTS,
                     query_type: str = "Top") -> List[Dict[str, Any]]:
    """
    Fetch all tweets up to max_results using pagination.

    Args:
        api_key: Twitter API key
        query: Search query string
        max_results: Maximum number of results to fetch
        query_type: Query type ("Latest" or "Top")

    Returns:
        List of tweet objects

    Raises:
        TwitterSearchError: If fetching tweets fails
    """
    all_tweets = []
    cursor = ""
    page_count = 0
    max_pages = (max_results + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE

    while len(all_tweets) < max_results:
        try:
            data = fetch_tweets(api_key, query, query_type, cursor)
            page_count += 1

            # Extract tweets from response
            tweets = data.get("tweets", [])
            if not tweets:
                break

            all_tweets.extend(tweets)

            # Check if we've reached max_results
            if len(all_tweets) >= max_results:
                all_tweets = all_tweets[:max_results]
                break

            # Check if there's a next page
            has_next = data.get("has_next_page", False)
            if not has_next:
                break

            cursor = data.get("next_cursor", "")

            # Safety check to prevent infinite loops
            if page_count >= max_pages + 5:
                print(f"Warning: Reached maximum page limit ({page_count} pages)", file=sys.stderr)
                break

        except TwitterSearchError as e:
            print(f"Warning: Failed to fetch page {page_count + 1}: {str(e)}", file=sys.stderr)
            break

    return all_tweets


def extract_tweet_summary(tweet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract key information from a tweet for summary output.

    Args:
        tweet: Raw tweet object from API

    Returns:
        Simplified tweet summary dictionary
    """
    author = tweet.get("author", {})

    return {
        "id": tweet.get("id"),
        "url": tweet.get("url"),
        "text": tweet.get("text"),
        "created_at": tweet.get("createdAt"),
        "lang": tweet.get("lang"),
        "metrics": {
            "retweets": tweet.get("retweetCount", 0),
            "replies": tweet.get("replyCount", 0),
            "likes": tweet.get("likeCount", 0),
            "quotes": tweet.get("quoteCount", 0),
            "views": tweet.get("viewCount", 0),
            "bookmarks": tweet.get("bookmarkCount", 0)
        },
        "author": {
            "username": author.get("userName"),
            "name": author.get("name"),
            "followers": author.get("followers", 0),
            "verified": author.get("isBlueVerified", False)
        },
        "hashtags": [h.get("text") for h in tweet.get("entities", {}).get("hashtags", [])],
        "mentions": [m.get("screen_name") for m in tweet.get("entities", {}).get("user_mentions", [])],
        "is_reply": tweet.get("isReply", False),
        "conversation_id": tweet.get("conversationId")
    }


def calculate_statistics(tweets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate aggregate statistics from tweets.

    Args:
        tweets: List of tweet summary objects

    Returns:
        Dictionary with various statistics
    """
    if not tweets:
        return {}

    total_likes = sum(t.get("metrics", {}).get("likes", 0) for t in tweets)
    total_retweets = sum(t.get("metrics", {}).get("retweets", 0) for t in tweets)
    total_replies = sum(t.get("metrics", {}).get("replies", 0) for t in tweets)
    total_quotes = sum(t.get("metrics", {}).get("quotes", 0) for t in tweets)
    total_views = sum(t.get("metrics", {}).get("views", 0) for t in tweets)

    # Language distribution
    languages = {}
    for t in tweets:
        lang = t.get("lang", "unknown")
        if not lang:
            lang = "unknown"
        languages[lang] = languages.get(lang, 0) + 1

    # Top hashtags
    all_hashtags = []
    for t in tweets:
        all_hashtags.extend(t.get("hashtags", []))
    hashtag_counts = {}
    for tag in all_hashtags:
        hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1

    # Top mentioned users
    all_mentions = []
    for t in tweets:
        all_mentions.extend(t.get("mentions", []))
    mention_counts = {}
    for mention in all_mentions:
        mention_counts[mention] = mention_counts.get(mention, 0) + 1

    # Reply vs original tweets
    reply_count = sum(1 for t in tweets if t.get("is_reply", False))

    # Most influential authors (by followers)
    authors = {}
    for t in tweets:
        username = t.get("author", {}).get("username")
        if username:
            if username not in authors:
                authors[username] = {
                    "name": t.get("author", {}).get("name"),
                    "followers": t.get("author", {}).get("followers", 0),
                    "verified": t.get("author", {}).get("verified", False),
                    "tweet_count": 0
                }
            authors[username]["tweet_count"] += 1

    return {
        "total_tweets": len(tweets),
        "total_engagement": {
            "likes": total_likes,
            "retweets": total_retweets,
            "replies": total_replies,
            "quotes": total_quotes,
            "views": total_views
        },
        "averages": {
            "likes_per_tweet": round(total_likes / len(tweets), 2),
            "retweets_per_tweet": round(total_retweets / len(tweets), 2),
            "replies_per_tweet": round(total_replies / len(tweets), 2)
        },
        "language_distribution": dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)[:10]),
        "top_hashtags": dict(sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:20]),
        "top_mentions": dict(sorted(mention_counts.items(), key=lambda x: x[1], reverse=True)[:20]),
        "reply_ratio": round(reply_count / len(tweets) * 100, 2),
        "top_authors_by_followers": sorted(
            [{"username": k, **v} for k, v in authors.items()],
            key=lambda x: x["followers"],
            reverse=True
        )[:10],
        "most_active_authors": sorted(
            [{"username": k, **v} for k, v in authors.items()],
            key=lambda x: x["tweet_count"],
            reverse=True
        )[:10]
    }


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Search Twitter using advanced search and analyze results"
    )
    parser.add_argument("api_key", nargs="?", help="Twitter API key (or set TWITTER_API_KEY env var)")
    parser.add_argument("query", help="Search query (e.g., 'AI' OR 'ChatGPT' from:elonmusk)")
    parser.add_argument("--max-results", type=int, default=DEFAULT_MAX_RESULTS,
                       help=f"Maximum results to fetch (default: {DEFAULT_MAX_RESULTS})")
    parser.add_argument("--query-type", choices=["Latest", "Top"], default="Top",
                       help="Query type (default: Top)")
    parser.add_argument("--format", choices=["json", "summary"], default="summary",
                       help="Output format (default: summary)")

    args = parser.parse_args()

    try:
        # Get API key
        api_key = get_api_key(args.api_key)

        # Fetch tweets
        print(f"Searching for: {args.query}", file=sys.stderr)
        print(f"Query type: {args.query_type}", file=sys.stderr)
        print(f"Max results: {args.max_results}", file=sys.stderr)
        print(file=sys.stderr)

        raw_tweets = fetch_all_tweets(api_key, args.query, args.max_results, args.query_type)

        if not raw_tweets:
            print("No tweets found.", file=sys.stderr)
            sys.exit(0)

        print(f"Fetched {len(raw_tweets)} tweets.", file=sys.stderr)

        # Process tweets
        tweet_summaries = [extract_tweet_summary(t) for t in raw_tweets]
        statistics = calculate_statistics(tweet_summaries)

        # Output results
        result = {
            "query": args.query,
            "query_type": args.query_type,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "total_tweets": len(tweet_summaries),
            "statistics": statistics,
            "tweets": tweet_summaries if args.format == "json" else []
        }

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except TwitterSearchError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
