#!/usr/bin/env python3
"""
Enrich a person's data from Apollo.io using email or LinkedIn URL.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from apollo import ApolloClient


def format_person(person: dict) -> str:
    """Format enriched person data for display."""
    lines = []
    
    # Basic info
    name = person.get("name", "N/A")
    title = person.get("title", "N/A")
    
    lines.append(f"👤 {name}")
    lines.append(f"   Title: {title}")
    
    # Organization
    org = person.get("organization", {})
    if isinstance(org, dict):
        org_name = org.get("name")
        if org_name:
            lines.append(f"   Company: {org_name}")
        org_domain = org.get("primary_domain")
        if org_domain:
            lines.append(f"   Domain: {org_domain}")
    
    # Contact
    email = person.get("email")
    if email:
        lines.append(f"   Email: {email}")
    
    phone = person.get("phone")
    if phone:
        lines.append(f"   Phone: {phone}")
    
    mobile = person.get("mobile_phone")
    if mobile:
        lines.append(f"   Mobile: {mobile}")
    
    linkedin = person.get("linkedin_url")
    if linkedin:
        lines.append(f"   LinkedIn: {linkedin}")
    
    twitter = person.get("twitter_url")
    if twitter:
        lines.append(f"   Twitter: {twitter}")
    
    # Location
    location = person.get("location")
    if location:
        lines.append(f"   Location: {location}")
    
    # Seniority/department
    seniority = person.get("seniority")
    if seniority:
        lines.append(f"   Seniority: {seniority}")
    
    department = person.get("department")
    if department:
        lines.append(f"   Department: {department}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Enrich person data from Apollo.io")
    parser.add_argument("--email", help="Email address")
    parser.add_argument("--linkedin", help="LinkedIn profile URL")
    parser.add_argument("--first-name", help="First name (with last-name + org)")
    parser.add_argument("--last-name", help="Last name")
    parser.add_argument("--organization", help="Organization name")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    if not any([args.email, args.linkedin, (args.first_name and args.last_name)]):
        parser.error("Must provide --email, --linkedin, or --first-name + --last-name")
    
    client = ApolloClient()
    
    try:
        result = client.enrich_person(
            email=args.email,
            linkedin_url=args.linkedin,
            first_name=args.first_name,
            last_name=args.last_name,
            organization_name=args.organization,
        )
        
        if args.json:
            print(json.dumps(result, indent=2))
            return
        
        person = result.get("person", {})
        
        if not person:
            print("No match found.")
            return
        
        print(format_person(person))
        
        # Show confidence/credits info if available
        if "confidence_score" in result:
            print(f"\n   Confidence: {result['confidence_score']}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
