#!/usr/bin/env python3
"""
Spotify OAuth flow - gets access and refresh tokens
"""

import http.server
import urllib.parse
import webbrowser
import json
import base64
import os
from pathlib import Path

# Config
CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPES = "user-read-recently-played user-top-read user-read-playback-state user-read-currently-playing"

TOKEN_FILE = Path.home() / ".config" / "spotify-clawd" / "token.json"

auth_code = None

class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Success!</h1><p>You can close this window.</p></body></html>")
        elif "error" in params:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"<html><body><h1>Error</h1><p>{params.get('error', ['Unknown'])}</p></body></html>".encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress logging

def get_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
    }
    return "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)

def exchange_code(code):
    import urllib.request
    
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }).encode()
    
    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=data,
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
    )
    
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)

def save_token(token_data):
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(token_data, indent=2))
    TOKEN_FILE.chmod(0o600)
    print(f"Token saved to {TOKEN_FILE}")

def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables")
        return 1
    
    # Start callback server
    server = http.server.HTTPServer(("127.0.0.1", 8888), CallbackHandler)
    
    # Open browser
    auth_url = get_auth_url()
    print(f"Opening browser for authorization...")
    print(f"If it doesn't open, visit: {auth_url}")
    webbrowser.open(auth_url)
    
    # Wait for callback
    print("Waiting for authorization...")
    while auth_code is None:
        server.handle_request()
    
    # Exchange code for token
    print("Exchanging code for token...")
    token_data = exchange_code(auth_code)
    
    save_token(token_data)
    print("Done! Spotify is now connected.")
    
    return 0

if __name__ == "__main__":
    exit(main())
