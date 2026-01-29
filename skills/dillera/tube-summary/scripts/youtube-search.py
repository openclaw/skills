#!/usr/bin/env python3
"""
YouTube Search Script for tube-summary skill

Searches YouTube for videos on a given topic and returns top 10 results.
Falls back to web scraping if API is unavailable.

Usage: python3 youtube-search.py "search query"
"""

import sys
import json
import subprocess
from urllib.parse import quote, urljoin
import re

def search_via_yt_dlp(query):
    """Search YouTube using yt-dlp (most reliable)"""
    try:
        # Use yt-dlp's search functionality
        cmd = [
            'yt-dlp',
            f'ytsearch10:{query}',
            '--dump-json',
            '--flat-playlist'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            videos = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        entry = json.loads(line)
                        videos.append({
                            'title': entry.get('title', 'Unknown'),
                            'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                            'channel': entry.get('channel', 'Unknown'),
                            'duration': entry.get('duration', 0),
                            'views': entry.get('view_count', 'N/A')
                        })
                    except json.JSONDecodeError:
                        continue
            return videos[:10]
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    
    return None

def search_via_web_scrape(query):
    """Fallback: web scraping via requests"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Extract initial data from the page
        match = re.search(r'var ytInitialData = ({.*?});', response.text)
        if match:
            try:
                data = json.loads(match.group(1))
                videos = []
                
                # Navigate the nested JSON structure
                contents = (
                    data.get('contents', {})
                    .get('twoColumnSearchResultsTabsRenderer', {})
                    .get('tabs', [{}])[0]
                    .get('tabRenderer', {})
                    .get('content', {})
                    .get('sectionListRenderer', {})
                    .get('contents', [])
                )
                
                for section in contents:
                    items = (
                        section.get('itemSectionRenderer', {})
                        .get('contents', [])
                    )
                    
                    for item in items:
                        if 'videoRenderer' in item:
                            video = item['videoRenderer']
                            videos.append({
                                'title': video.get('title', {}).get('runs', [{}])[0].get('text', 'Unknown'),
                                'url': f"https://www.youtube.com/watch?v={video.get('videoId', '')}",
                                'channel': video.get('longBylineText', {}).get('simpleText', 'Unknown'),
                                'duration': video.get('lengthText', {}).get('simpleText', 'N/A'),
                                'views': video.get('viewCountText', {}).get('simpleText', 'N/A')
                            })
                        
                        if len(videos) >= 10:
                            break
                    
                    if len(videos) >= 10:
                        break
                
                return videos[:10]
            except (json.JSONDecodeError, KeyError, IndexError):
                pass
    except (ImportError, Exception):
        pass
    
    return None

def format_results(videos):
    """Format video results for display"""
    output = [f"\n📺 Top 10 YouTube Videos for this search:\n"]
    
    for i, video in enumerate(videos, 1):
        output.append(f"{i}. {video['title']}")
        output.append(f"   Channel: {video['channel']}")
        output.append(f"   Views: {video['views']} • Duration: {video.get('duration', 'N/A')}")
        output.append(f"   URL: {video['url']}\n")
    
    output.append("\n➡️  Respond with the video number (1-10) to summarize that video.\n")
    return "".join(output)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 youtube-search.py \"search query\"")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    # Try yt-dlp first (most reliable)
    videos = search_via_yt_dlp(query)
    
    # Fallback to web scraping
    if not videos:
        videos = search_via_web_scrape(query)
    
    if videos:
        print(format_results(videos))
        # Also output JSON for programmatic access
        print("\n<!-- JSON Data (for tool processing) -->")
        print(json.dumps(videos, indent=2))
    else:
        print("❌ No videos found. Try a different search query or check your internet connection.")
        sys.exit(1)

if __name__ == '__main__':
    main()
