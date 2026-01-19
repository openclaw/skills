#!/usr/bin/env python3
"""
Gemini Deep Research API client
Performs complex, long-running research tasks via Gemini's Deep Research Agent
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
import requests

API_BASE = "https://generativelanguage.googleapis.com/v1beta"
AGENT_MODEL = "deep-research-pro-preview-12-2025"


def create_interaction(api_key, query, output_format=None, file_search_store=None):
    """Start a new deep research interaction"""
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    payload = {
        "input": query,
        "agent": AGENT_MODEL,
        "background": True
    }
    
    if output_format:
        payload["input"] = f"{query}\n\nFormat the output as follows:\n{output_format}"
    
    if file_search_store:
        payload["tools"] = [{
            "type": "file_search",
            "file_search_store_names": [file_search_store]
        }]
    
    response = requests.post(
        f"{API_BASE}/interactions",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        print(f"Error creating interaction: {response.status_code}", file=sys.stderr)
        print(response.text, file=sys.stderr)
        sys.exit(1)
    
    return response.json()


def poll_interaction(api_key, interaction_id, stream=False):
    """Poll for interaction updates"""
    headers = {
        "x-goog-api-key": api_key
    }
    
    while True:
        response = requests.get(
            f"{API_BASE}/interactions/{interaction_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"Error polling interaction: {response.status_code}", file=sys.stderr)
            print(response.text, file=sys.stderr)
            sys.exit(1)
        
        data = response.json()
        status = data.get("status", "UNKNOWN")
        
        if stream:
            # Show progress updates
            if "statusMessage" in data:
                print(f"[{status}] {data['statusMessage']}", file=sys.stderr)
        
        if status == "completed":
            return data
        elif status == "failed":
            print(f"Research failed: {data.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)
        
        time.sleep(10)  # Poll every 10 seconds


def extract_report(interaction_data):
    """Extract the final report from interaction data"""
    if "output" in interaction_data:
        output = interaction_data["output"]
        if isinstance(output, dict) and "text" in output:
            return output["text"]
        elif isinstance(output, str):
            return output
    
    # Fallback: look in messages
    messages = interaction_data.get("messages", [])
    for msg in reversed(messages):
        if msg.get("role") == "model" and "parts" in msg:
            for part in msg["parts"]:
                if "text" in part:
                    return part["text"]
    
    return None


def main():
    parser = argparse.ArgumentParser(description="Gemini Deep Research API Client")
    parser.add_argument("--query", required=True, help="Research query")
    parser.add_argument("--format", help="Custom output format instructions")
    parser.add_argument("--file-search-store", help="File search store name (optional)")
    parser.add_argument("--stream", action="store_true", help="Show streaming progress updates")
    parser.add_argument("--output-dir", default=".", help="Output directory for results")
    parser.add_argument("--api-key", help="Gemini API key (overrides GEMINI_API_KEY env var)")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set GEMINI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)
    
    # Start research
    print(f"Starting deep research: {args.query}", file=sys.stderr)
    interaction = create_interaction(
        api_key,
        args.query,
        output_format=args.format,
        file_search_store=args.file_search_store
    )
    
    interaction_id = interaction.get("id")
    if not interaction_id:
        print(f"Error: No interaction ID in response: {interaction}", file=sys.stderr)
        sys.exit(1)
    print(f"Interaction started: {interaction_id}", file=sys.stderr)
    
    # Poll for completion
    print("Polling for results (this may take several minutes)...", file=sys.stderr)
    result = poll_interaction(api_key, interaction_id, stream=args.stream)
    
    # Extract report
    report = extract_report(result)
    
    if not report:
        print("Warning: Could not extract report text from response", file=sys.stderr)
        report = json.dumps(result, indent=2)
    
    # Save results
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    md_path = output_dir / f"deep-research-{timestamp}.md"
    json_path = output_dir / f"deep-research-{timestamp}.json"
    
    md_path.write_text(report)
    json_path.write_text(json.dumps(result, indent=2))
    
    print(f"\nResearch complete!", file=sys.stderr)
    print(f"Report saved: {md_path}", file=sys.stderr)
    print(f"Full data saved: {json_path}", file=sys.stderr)
    
    # Print report to stdout
    print(report)


if __name__ == "__main__":
    main()
