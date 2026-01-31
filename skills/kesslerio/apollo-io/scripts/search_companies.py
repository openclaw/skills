#!/usr/bin/env python3
"""
Search for companies in Apollo.io.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from apollo import ApolloClient


def format_company(company: dict) -> str:
    """Format a company record for display."""
    lines = []
    
    name = company.get("name", "N/A")
    lines.append(f"🏢 {name}")
    
    # Domain/website
    domain = company.get("primary_domain")
    if domain:
        lines.append(f"   Domain: {domain}")
    
    website = company.get("website_url")
    if website:
        lines.append(f"   Website: {website}")
    
    # Industry
    industry = company.get("industry")
    if industry:
        lines.append(f"   Industry: {industry}")
    
    # Size
    size = company.get("estimated_num_employees")
    if size:
        lines.append(f"   Employees: ~{size}")
    
    # Location
    location = company.get("location")
    if location:
        lines.append(f"   Location: {location}")
    
    # LinkedIn
    linkedin = company.get("linkedin_url")
    if linkedin:
        lines.append(f"   LinkedIn: {linkedin}")
    
    # Description (truncated)
    description = company.get("short_description") or company.get("description")
    if description:
        desc = description[:150] + "..." if len(description) > 150 else description
        lines.append(f"   About: {desc}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search for companies on Apollo.io")
    parser.add_argument("--keywords", help="Company name or keywords")
    parser.add_argument("--industry", help="Industry name")
    parser.add_argument("--size", help="Employee range (e.g., '1-10', '11-50', '51-200', '201-500', '501-1000', '1001-5000', '5001-10000', '10001+')")
    parser.add_argument("--location", help="Location (city/country)")
    parser.add_argument("--per-page", type=int, default=10, help="Results per page")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    client = ApolloClient()
    
    locations = [args.location] if args.location else None
    
    try:
        result = client.search_companies(
            q_keywords=args.keywords,
            organization_num_employees_range=args.size,
            organization_locations=locations,
            per_page=args.per_page,
        )
        
        if args.json:
            print(json.dumps(result, indent=2))
            return
        
        companies = result.get("organizations", [])
        pagination = result.get("pagination", {})
        
        if not companies:
            print("No results found.")
            return
        
        print(f"Found {len(companies)} companies (page {pagination.get('page', 1)} of {pagination.get('total_pages', 1)}):\n")
        
        for company in companies:
            print(format_company(company))
            print()
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
