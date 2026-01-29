#!/usr/bin/env python3
"""
Subtitle Processing Script for tube-summary skill

Processes VTT subtitle files to extract key information and generate summaries.

Usage: python3 process-subtitles.py "path/to/subtitle-file.vtt"
"""

import sys
import re
from pathlib import Path
from collections import defaultdict

def parse_vtt(vtt_file):
    """Parse a VTT subtitle file and extract text with timestamps"""
    subtitles = []
    
    with open(vtt_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Remove header
    content = content.replace('WEBVTT', '').strip()
    
    # Split by double newlines (subtitle blocks)
    blocks = content.split('\n\n')
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 2:
            continue
        
        # Parse timestamp line
        timestamp_line = lines[0]
        if '-->' in timestamp_line:
            time_parts = timestamp_line.split(' --> ')
            if len(time_parts) == 2:
                start_time = time_parts[0].strip()
                # Extract text (remaining lines)
                text = ' '.join(lines[1:]).strip()
                if text:
                    subtitles.append({
                        'time': start_time,
                        'text': text
                    })
    
    return subtitles

def extract_key_topics(subtitles):
    """Extract key topics/keywords from subtitles"""
    all_text = ' '.join([s['text'] for s in subtitles])
    
    # Remove common words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'you', 'i', 'we', 'he', 'she', 'it', 'that', 'this', 'what', 'which',
        'who', 'when', 'where', 'why', 'how', 'so', 'if', 'as', 'can', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'um', 'uh', 'like', 'you know', 'basically', 'sort of', 'kind of'
    }
    
    # Extract words
    words = re.findall(r'\b[a-z]{4,}\b', all_text.lower())
    
    # Count word frequencies (excluding stop words)
    word_freq = defaultdict(int)
    for word in words:
        if word not in stop_words:
            word_freq[word] += 1
    
    # Get top keywords
    top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:15]
    return [word for word, count in top_keywords if count >= 2]

def generate_summary(subtitles, max_length=1000):
    """Generate a summary from the full subtitle text"""
    full_text = ' '.join([s['text'] for s in subtitles])
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', full_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Simple extractive summarization: take first few sentences
    summary_sentences = sentences[:5]
    summary = '. '.join(summary_sentences) + '.'
    
    # Truncate if too long
    if len(summary) > max_length:
        summary = summary[:max_length] + '...'
    
    return summary

def get_key_quotes(subtitles, count=3):
    """Extract the longest/most impactful quotes from subtitles"""
    # Filter for substantial segments
    quotes = [s for s in subtitles if len(s['text']) > 30]
    
    # Sort by length (longer = more substantial)
    quotes_sorted = sorted(quotes, key=lambda x: len(x['text']), reverse=True)
    
    return quotes_sorted[:count]

def get_notable_moments(subtitles):
    """Find notable moments based on specific keywords"""
    keywords = [
        'important', 'remember', 'key', 'main', 'best', 'worst',
        'conclusion', 'summary', 'therefore', 'so', 'now',
        'first', 'second', 'third', 'finally', 'ultimately'
    ]
    
    notable = []
    for sub in subtitles:
        text_lower = sub['text'].lower()
        if any(keyword in text_lower for keyword in keywords):
            notable.append(sub)
    
    return notable[:5]

def format_output(subtitles, vtt_file):
    """Format and print the analysis"""
    if not subtitles:
        print("❌ No subtitles found in the file.")
        return
    
    topics = extract_key_topics(subtitles)
    summary = generate_summary(subtitles)
    quotes = get_key_quotes(subtitles, count=3)
    notable = get_notable_moments(subtitles)
    
    print("\n" + "="*70)
    print("📊 VIDEO SUBTITLE ANALYSIS")
    print("="*70)
    
    print(f"\n📁 File: {Path(vtt_file).name}")
    print(f"⏱️  Total Duration: {subtitles[-1]['time'] if subtitles else 'N/A'}")
    print(f"📝 Total Subtitle Lines: {len(subtitles)}")
    
    print("\n" + "-"*70)
    print("🔑 KEY TOPICS")
    print("-"*70)
    if topics:
        for i, topic in enumerate(topics[:10], 1):
            print(f"  {i}. {topic}")
    else:
        print("  No topics extracted")
    
    print("\n" + "-"*70)
    print("📄 SUMMARY")
    print("-"*70)
    print(f"\n{summary}\n")
    
    print("-"*70)
    print("💬 KEY QUOTES")
    print("-"*70)
    if quotes:
        for i, quote in enumerate(quotes, 1):
            # Clean up quote text
            text = quote['text'].replace('\n', ' ').strip()
            # Limit length
            if len(text) > 150:
                text = text[:150] + "..."
            print(f"\n  [{quote['time']}]")
            print(f"  \"{text}\"")
    else:
        print("  No notable quotes found")
    
    print("\n" + "-"*70)
    print("⭐ NOTABLE MOMENTS")
    print("-"*70)
    if notable:
        for moment in notable:
            text = moment['text'].replace('\n', ' ').strip()
            if len(text) > 100:
                text = text[:100] + "..."
            print(f"  [{moment['time']}] {text}")
    else:
        print("  No notable moments found")
    
    print("\n" + "="*70 + "\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 process-subtitles.py \"path/to/subtitle-file.vtt\"")
        sys.exit(1)
    
    vtt_file = sys.argv[1]
    
    if not Path(vtt_file).exists():
        print(f"❌ File not found: {vtt_file}")
        sys.exit(1)
    
    if not vtt_file.endswith('.vtt'):
        print("⚠️  Warning: File does not end in .vtt, but attempting to parse...")
    
    try:
        subtitles = parse_vtt(vtt_file)
        format_output(subtitles, vtt_file)
    except Exception as e:
        print(f"❌ Error processing subtitles: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
