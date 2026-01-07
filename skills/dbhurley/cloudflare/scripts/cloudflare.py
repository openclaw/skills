#!/usr/bin/env python3
"""
Cloudflare CLI - DNS, Cache, Workers Routes

Usage:
    cloudflare.py verify
    cloudflare.py zones [--json]
    cloudflare.py zone <domain> [--json]
    cloudflare.py dns list <domain> [--json]
    cloudflare.py dns add <domain> --type TYPE --name NAME --content CONTENT [--proxied] [--ttl TTL]
    cloudflare.py dns update <domain> <record_id> [--content CONTENT] [--proxied]
    cloudflare.py dns delete <domain> <record_id> [--yes]
    cloudflare.py cache purge <domain> [--all] [--urls URLS] [--prefix PREFIX]
    cloudflare.py routes list <domain> [--json]
    cloudflare.py routes add <domain> --pattern PATTERN --worker WORKER
"""

import argparse
import json
import os
import sys
from typing import Optional

import requests


def confirm(prompt: str, default: bool = False) -> bool:
    """Ask for confirmation"""
    if default:
        choice = input(f"{prompt} [Y/n]: ").strip().lower()
        return choice != 'n'
    else:
        choice = input(f"{prompt} [y/N]: ").strip().lower()
        return choice == 'y'


class CloudflareClient:
    """Cloudflare API client"""
    
    API_BASE = "https://api.cloudflare.com/client/v4"
    
    def __init__(self, api_token: str):
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        self._zone_cache = {}
    
    def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make API request"""
        url = f"{self.API_BASE}/{endpoint}"
        
        try:
            resp = requests.request(method, url, headers=self.headers, json=data, timeout=30)
        except requests.exceptions.Timeout:
            raise Exception("Request timed out - Cloudflare API may be slow")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection failed - check your internet connection")
        
        try:
            result = resp.json()
        except json.JSONDecodeError:
            raise Exception(f"Invalid response from API (status {resp.status_code})")
        
        if not result.get("success", False):
            errors = result.get("errors", [])
            if errors:
                # Extract meaningful error info
                error_parts = []
                for e in errors:
                    code = e.get("code", "")
                    msg = e.get("message", str(e))
                    if code == 10000:
                        error_parts.append("Authentication failed - check your API token")
                    elif code == 7003:
                        error_parts.append(f"Zone not found or no permission")
                    elif code == 81057:
                        error_parts.append("Record already exists")
                    else:
                        error_parts.append(f"{msg} (code {code})" if code else msg)
                raise Exception("; ".join(error_parts))
            else:
                raise Exception(f"API error (status {resp.status_code})")
        
        return result
    
    def verify_token(self) -> dict:
        """Verify the API token and return token details"""
        result = self._request("GET", "user/tokens/verify")
        return result.get("result", {})
    
    # === Zones ===
    
    def list_zones(self) -> list:
        """List all zones"""
        result = self._request("GET", "zones")
        return result.get("result", [])
    
    def get_zone_id(self, domain: str) -> Optional[str]:
        """Get zone ID by domain name"""
        if domain in self._zone_cache:
            return self._zone_cache[domain]
        
        # Check if it's already a zone ID
        if len(domain) == 32 and domain.isalnum():
            return domain
        
        zones = self.list_zones()
        for zone in zones:
            if zone.get("name") == domain:
                self._zone_cache[domain] = zone.get("id")
                return zone.get("id")
        
        return None
    
    def get_zone(self, domain: str) -> dict:
        """Get zone details"""
        zone_id = self.get_zone_id(domain)
        if not zone_id:
            raise Exception(f"Zone not found: {domain}")
        
        result = self._request("GET", f"zones/{zone_id}")
        return result.get("result", {})
    
    # === DNS ===
    
    def list_dns_records(self, domain: str) -> list:
        """List DNS records for a zone"""
        zone_id = self.get_zone_id(domain)
        if not zone_id:
            raise Exception(f"Zone not found: {domain}")
        
        result = self._request("GET", f"zones/{zone_id}/dns_records")
        return result.get("result", [])
    
    def add_dns_record(self, domain: str, record_type: str, name: str, content: str, 
                       proxied: bool = False, ttl: int = 1) -> dict:
        """Add a DNS record"""
        zone_id = self.get_zone_id(domain)
        if not zone_id:
            raise Exception(f"Zone not found: {domain}")
        
        data = {
            "type": record_type.upper(),
            "name": name,
            "content": content,
            "proxied": proxied,
            "ttl": ttl  # 1 = auto
        }
        
        result = self._request("POST", f"zones/{zone_id}/dns_records", data)
        return result.get("result", {})
    
    def update_dns_record(self, domain: str, record_id: str, 
                          content: str = None, proxied: bool = None) -> dict:
        """Update a DNS record"""
        zone_id = self.get_zone_id(domain)
        if not zone_id:
            raise Exception(f"Zone not found: {domain}")
        
        # Get existing record
        existing = self._request("GET", f"zones/{zone_id}/dns_records/{record_id}")
        record = existing.get("result", {})
        
        data = {
            "type": record.get("type"),
            "name": record.get("name"),
            "content": content if content else record.get("content"),
            "proxied": proxied if proxied is not None else record.get("proxied"),
            "ttl": record.get("ttl", 1)
        }
        
        result = self._request("PUT", f"zones/{zone_id}/dns_records/{record_id}", data)
        return result.get("result", {})
    
    def delete_dns_record(self, domain: str, record_id: str) -> bool:
        """Delete a DNS record"""
        zone_id = self.get_zone_id(domain)
        if not zone_id:
            raise Exception(f"Zone not found: {domain}")
        
        self._request("DELETE", f"zones/{zone_id}/dns_records/{record_id}")
        return True
    
    # === Cache ===
    
    def purge_cache(self, domain: str, purge_all: bool = False, 
                    urls: list = None, prefixes: list = None) -> dict:
        """Purge cache for a zone"""
        zone_id = self.get_zone_id(domain)
        if not zone_id:
            raise Exception(f"Zone not found: {domain}")
        
        if purge_all:
            data = {"purge_everything": True}
        elif urls:
            data = {"files": urls}
        elif prefixes:
            data = {"prefixes": prefixes}
        else:
            raise Exception("Must specify --all, --urls, or --prefix")
        
        result = self._request("POST", f"zones/{zone_id}/purge_cache", data)
        return result.get("result", {})
    
    # === Workers Routes ===
    
    def list_routes(self, domain: str) -> list:
        """List Workers routes for a zone"""
        zone_id = self.get_zone_id(domain)
        if not zone_id:
            raise Exception(f"Zone not found: {domain}")
        
        result = self._request("GET", f"zones/{zone_id}/workers/routes")
        return result.get("result", [])
    
    def add_route(self, domain: str, pattern: str, worker: str) -> dict:
        """Add a Workers route"""
        zone_id = self.get_zone_id(domain)
        if not zone_id:
            raise Exception(f"Zone not found: {domain}")
        
        data = {
            "pattern": pattern,
            "script": worker
        }
        
        result = self._request("POST", f"zones/{zone_id}/workers/routes", data)
        return result.get("result", {})


def main():
    parser = argparse.ArgumentParser(description="Cloudflare CLI")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # verify
    subparsers.add_parser("verify", help="Verify API token")
    
    # zones
    subparsers.add_parser("zones", help="List zones")
    
    # zone
    zone_p = subparsers.add_parser("zone", help="Get zone details")
    zone_p.add_argument("domain", help="Domain or zone ID")
    
    # dns
    dns_p = subparsers.add_parser("dns", help="DNS commands")
    dns_sub = dns_p.add_subparsers(dest="dns_action")
    
    dns_list = dns_sub.add_parser("list", help="List DNS records")
    dns_list.add_argument("domain")
    
    dns_add = dns_sub.add_parser("add", help="Add DNS record")
    dns_add.add_argument("domain")
    dns_add.add_argument("--type", required=True, help="Record type (A, AAAA, CNAME, TXT, MX)")
    dns_add.add_argument("--name", required=True, help="Record name (@ for apex)")
    dns_add.add_argument("--content", required=True, help="Record content")
    dns_add.add_argument("--proxied", action="store_true", help="Enable Cloudflare proxy")
    dns_add.add_argument("--ttl", type=int, default=1, help="TTL (1=auto)")
    
    dns_update = dns_sub.add_parser("update", help="Update DNS record")
    dns_update.add_argument("domain")
    dns_update.add_argument("record_id")
    dns_update.add_argument("--content", help="New content")
    dns_update.add_argument("--proxied", action="store_true", help="Enable proxy")
    dns_update.add_argument("--no-proxied", action="store_true", help="Disable proxy")
    
    dns_delete = dns_sub.add_parser("delete", help="Delete DNS record")
    dns_delete.add_argument("domain")
    dns_delete.add_argument("record_id")
    dns_delete.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    
    # cache
    cache_p = subparsers.add_parser("cache", help="Cache commands")
    cache_sub = cache_p.add_subparsers(dest="cache_action")
    
    cache_purge = cache_sub.add_parser("purge", help="Purge cache")
    cache_purge.add_argument("domain")
    cache_purge.add_argument("--all", action="store_true", help="Purge everything")
    cache_purge.add_argument("--urls", help="Comma-separated URLs to purge")
    cache_purge.add_argument("--prefix", help="URL prefix to purge")
    cache_purge.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    
    # routes
    routes_p = subparsers.add_parser("routes", help="Workers routes commands")
    routes_sub = routes_p.add_subparsers(dest="routes_action")
    
    routes_list = routes_sub.add_parser("list", help="List routes")
    routes_list.add_argument("domain")
    
    routes_add = routes_sub.add_parser("add", help="Add route")
    routes_add.add_argument("domain")
    routes_add.add_argument("--pattern", required=True, help="Route pattern")
    routes_add.add_argument("--worker", required=True, help="Worker script name")
    
    args = parser.parse_args()
    
    # Get token
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not api_token:
        print("Error: CLOUDFLARE_API_TOKEN required", file=sys.stderr)
        sys.exit(1)
    
    client = CloudflareClient(api_token)
    
    try:
        if args.command == "verify":
            result = client.verify_token()
            status = result.get("status", "unknown")
            if status == "active":
                print("✅ Token is valid")
                print(f"   Status: {status}")
                print(f"   ID: {result.get('id', 'N/A')}")
                if args.json:
                    print(json.dumps(result, indent=2))
            else:
                print(f"⚠️  Token status: {status}")
                sys.exit(1)
        
        elif args.command == "zones":
            zones = client.list_zones()
            if args.json:
                print(json.dumps(zones, indent=2))
            else:
                if not zones:
                    print("No zones found (check token permissions)")
                else:
                    for z in zones:
                        status = "✓" if z.get("status") == "active" else "○"
                        print(f"{status} {z.get('name')} ({z.get('id')[:8]}...)")
        
        elif args.command == "zone":
            zone = client.get_zone(args.domain)
            if args.json:
                print(json.dumps(zone, indent=2))
            else:
                print(f"Zone: {zone.get('name')}")
                print(f"ID: {zone.get('id')}")
                print(f"Status: {zone.get('status')}")
                print(f"Nameservers: {', '.join(zone.get('name_servers', []))}")
        
        elif args.command == "dns":
            if args.dns_action == "list":
                records = client.list_dns_records(args.domain)
                if args.json:
                    print(json.dumps(records, indent=2))
                else:
                    for r in records:
                        proxy = "☁️" if r.get("proxied") else "  "
                        print(f"{proxy} {r.get('type'):6} {r.get('name'):30} → {r.get('content')}")
                        print(f"   ID: {r.get('id')}")
            
            elif args.dns_action == "add":
                record = client.add_dns_record(
                    args.domain, args.type, args.name, args.content,
                    proxied=args.proxied, ttl=args.ttl
                )
                print(f"✅ Created {args.type} record: {record.get('name')} → {record.get('content')}")
                print(f"   ID: {record.get('id')}")
            
            elif args.dns_action == "update":
                proxied = None
                if args.proxied:
                    proxied = True
                elif args.no_proxied:
                    proxied = False
                
                record = client.update_dns_record(args.domain, args.record_id, 
                                                   content=args.content, proxied=proxied)
                print(f"✅ Updated: {record.get('name')} → {record.get('content')}")
            
            elif args.dns_action == "delete":
                # Get record details first for confirmation
                records = client.list_dns_records(args.domain)
                record = next((r for r in records if r.get("id") == args.record_id), None)
                
                if not record:
                    print(f"❌ Record not found: {args.record_id}", file=sys.stderr)
                    sys.exit(1)
                
                record_info = f"{record.get('type')} {record.get('name')} → {record.get('content')}"
                
                if not args.yes:
                    print(f"About to delete: {record_info}")
                    if not confirm("Are you sure?"):
                        print("Cancelled")
                        sys.exit(0)
                
                client.delete_dns_record(args.domain, args.record_id)
                print(f"✅ Deleted: {record_info}")
        
        elif args.command == "cache":
            if args.cache_action == "purge":
                urls = args.urls.split(",") if args.urls else None
                prefixes = [args.prefix] if args.prefix else None
                
                # Confirm for purge all
                if args.all and not args.yes:
                    print(f"⚠️  This will purge ALL cached content for {args.domain}")
                    if not confirm("Are you sure?"):
                        print("Cancelled")
                        sys.exit(0)
                
                result = client.purge_cache(args.domain, purge_all=args.all, 
                                           urls=urls, prefixes=prefixes)
                if args.all:
                    print(f"✅ Purged ALL cache for {args.domain}")
                elif urls:
                    print(f"✅ Purged {len(urls)} URL(s) from cache")
                else:
                    print(f"✅ Purged cache by prefix for {args.domain}")
                    
                if args.json:
                    print(json.dumps(result, indent=2))
        
        elif args.command == "routes":
            if args.routes_action == "list":
                routes = client.list_routes(args.domain)
                if args.json:
                    print(json.dumps(routes, indent=2))
                else:
                    for r in routes:
                        print(f"• {r.get('pattern')} → {r.get('script', 'disabled')}")
                        print(f"  ID: {r.get('id')}")
            
            elif args.routes_action == "add":
                route = client.add_route(args.domain, args.pattern, args.worker)
                print(f"✅ Created route: {args.pattern} → {args.worker}")
                print(f"   ID: {route.get('id')}")
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
