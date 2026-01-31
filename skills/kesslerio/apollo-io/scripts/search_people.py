#!/usr/bin/env python3
"""
Search for people/prospects in Apollo.io.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent dir to path for apollo import
sys.path.insert(0, str(Path(__file__).parent.parent))

from apollo import ApolloClient


def format_person(person: dict) -> str:
    """Format a person record for display."""
    lines = []
    name = person.get("name", "N/A")
    title = person.get("title", "N/A")
    
    org = person.get("organization", {})
    org_name = org.get("name", "N/A") if isinstance(org, dict) else "N/A"
    
    lines.append(f"• {name} — {title} @ {org_name}")
    
    # Contact info
    email = person.get("email")
    if email:
        lines.append(f"  Email: {email}")
    
    phone = person.get("phone")
    if phone:
        lines.append(f"  Phone: {phone}")
    
    linkedin = person.get("linkedin_url")
    if linkedin:
        lines.append(f"  LinkedIn: {linkedin}")
    
    # Location
    location = person.get("location")
    if location:
        lines.append(f"  Location: {location}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search for people on Apollo.io")
    parser.add_argument("--title", help="Job title to search for")
    parser.add_argument("--company", help="Company name")
    parser.add_argument("--keywords", help="General search keywords")
    parser.add_argument("--per-page", type=int, default=10, help="Results per page (max 100)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    client = ApolloClient()
    
    person_titles = [args.title] if args.title else None
    organization_names = [args.company] if args.company else None
    
    try:
        result = client.search_people(
            q_keywords=args.keywords,
            person_titles=person_titles,
            organization_names=organization_names,
            per_page=args.per_page,
        )
        
        if args.json:
            print(json.dumps(result, indent=2))
            return
        
        people = result.get("people", [])
        pagination = result.get("pagination", {})
        
        if not people:
            print("No results found.")
            return
        
        print(f"Found {len(people)} people (page {pagination.get('page', 1)} of {pagination.get('total_pages', 1)}):\n")
        
        for person in people:
            print(format_person(person))
            print()
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
