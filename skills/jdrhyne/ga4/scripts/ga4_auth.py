#!/usr/bin/env python3
"""
GA4 OAuth Setup Script

Generates OAuth authorization URL and exchanges code for refresh token.
"""

import argparse
import sys
import urllib.parse

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    import google.auth.transport.requests
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install google-auth-oauthlib")
    sys.exit(1)

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]


def generate_auth_url(client_id, redirect_uri="http://localhost:8080/"):
    """Generate OAuth authorization URL."""
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(SCOPES),
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
    }
    base_url = "https://accounts.google.com/o/oauth2/auth"
    return f"{base_url}?{urllib.parse.urlencode(params)}"


def exchange_code(client_id, client_secret, code, redirect_uri="http://localhost:8080/"):
    """Exchange authorization code for tokens."""
    import requests
    
    response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        },
    )
    
    if response.status_code != 200:
        print(f"Error: {response.text}")
        sys.exit(1)
    
    return response.json()


def main():
    parser = argparse.ArgumentParser(description="GA4 OAuth Setup")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Generate auth URL
    url_parser = subparsers.add_parser("url", help="Generate OAuth URL")
    url_parser.add_argument("--client-id", required=True, help="OAuth Client ID")
    url_parser.add_argument("--redirect-uri", default="http://localhost:8080/", help="Redirect URI")
    
    # Exchange code
    exchange_parser = subparsers.add_parser("exchange", help="Exchange code for tokens")
    exchange_parser.add_argument("--client-id", required=True, help="OAuth Client ID")
    exchange_parser.add_argument("--client-secret", required=True, help="OAuth Client Secret")
    exchange_parser.add_argument("--code", required=True, help="Authorization code")
    exchange_parser.add_argument("--redirect-uri", default="http://localhost:8080/", help="Redirect URI")
    
    args = parser.parse_args()
    
    if args.command == "url":
        url = generate_auth_url(args.client_id, args.redirect_uri)
        print("\n=== GA4 OAuth Authorization ===\n")
        print("1. Open this URL in your browser:")
        print(f"\n{url}\n")
        print("2. Sign in and authorize access to Analytics")
        print("3. Copy the 'code' parameter from the redirect URL")
        print("4. Run: ga4_auth.py exchange --client-id ... --client-secret ... --code ...")
        
    elif args.command == "exchange":
        print("Exchanging code for tokens...")
        tokens = exchange_code(
            args.client_id,
            args.client_secret,
            args.code,
            args.redirect_uri,
        )
        print("\n=== OAuth Tokens ===\n")
        print(f"Access Token: {tokens.get('access_token', 'N/A')[:50]}...")
        print(f"Refresh Token: {tokens.get('refresh_token', 'N/A')}")
        print(f"Expires In: {tokens.get('expires_in', 'N/A')} seconds")
        print("\n=== Environment Variables ===\n")
        print("Add these to your .env or export them:\n")
        print(f"export GOOGLE_REFRESH_TOKEN='{tokens.get('refresh_token')}'")


if __name__ == "__main__":
    main()
