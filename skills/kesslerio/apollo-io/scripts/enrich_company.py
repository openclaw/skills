#!/usr/bin/env python3
"""
Enrich company data from Apollo.io using domain or name.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from apollo import ApolloClient


def format_company(company: dict) -> str:
    """Format enriched company data for display."""
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
    
    # Revenue
    revenue = company.get("annual_revenue")
    if revenue:
        lines.append(f"   Annual Revenue: ${revenue:,.0f}")
    
    # Location
    location = company.get("location")
    if location:
        lines.append(f"   Location: {location}")
    
    # Social
    linkedin = company.get("linkedin_url")
    if linkedin:
        lines.append(f"   LinkedIn: {linkedin}")
    
    twitter = company.get("twitter_url")
    if twitter:
        lines.append(f"   Twitter: {twitter}")
    
    facebook = company.get("facebook_url")
    if facebook:
        lines.append(f"   Facebook: {facebook}")
    
    # Tech stack
    tech = company.get("technologies", [])
    if tech:
        tech_str = ", ".join(tech[:10])
        if len(tech) > 10:
            tech_str += f" (+{len(tech) - 10} more)"
        lines.append(f"   Tech Stack: {tech_str}")
    
    # Description
    description = company.get("short_description") or company.get("description")
    if description:
        lines.append(f"\n   About: {description}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Enrich company data from Apollo.io")
    parser.add_argument("--domain", help="Company domain (e.g., stripe.com)")
    parser.add_argument("--name", help="Company name")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    if not args.domain and not args.name:
        parser.error("Must provide --domain or --name")
    
    client = ApolloClient()
    
    try:
        result = client.enrich_company(
            domain=args.domain,
            name=args.name,
        )
        
        if args.json:
            print(json.dumps(result, indent=2))
            return
        
        company = result.get("organization", {})
        
        if not company:
            print("No match found.")
            return
        
        print(format_company(company))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
