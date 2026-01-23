#!/usr/bin/env python3
"""
Spotify API helper - fetch listening history and recommendations
"""

import json
import urllib.request
import urllib.parse
import base64
import sys
import os
from pathlib import Path
from datetime import datetime

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
TOKEN_FILE = Path.home() / ".config" / "spotify-clawd" / "token.json"

def load_token():
    if not TOKEN_FILE.exists():
        print("Error: Not authenticated. Run spotify-auth.py first.")
        sys.exit(1)
    return json.loads(TOKEN_FILE.read_text())

def save_token(token_data):
    TOKEN_FILE.write_text(json.dumps(token_data, indent=2))

def refresh_token(token_data):
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": token_data["refresh_token"],
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
        new_data = json.load(resp)
    
    # Keep refresh token if not returned
    if "refresh_token" not in new_data:
        new_data["refresh_token"] = token_data["refresh_token"]
    
    save_token(new_data)
    return new_data

def api_request(endpoint, token_data, params=None):
    url = f"https://api.spotify.com/v1{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token_data['access_token']}"}
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            # Token expired, refresh and retry
            token_data = refresh_token(token_data)
            req = urllib.request.Request(
                url,
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )
            with urllib.request.urlopen(req) as resp:
                return json.load(resp)
        raise

def get_recently_played(token_data, limit=20):
    return api_request("/me/player/recently-played", token_data, {"limit": limit})

def get_top_artists(token_data, time_range="medium_term", limit=20):
    return api_request("/me/top/artists", token_data, {"time_range": time_range, "limit": limit})

def get_top_tracks(token_data, time_range="medium_term", limit=20):
    return api_request("/me/top/tracks", token_data, {"time_range": time_range, "limit": limit})

def get_recommendations(token_data, seed_artists=None, seed_tracks=None, seed_genres=None, limit=20):
    params = {"limit": limit}
    if seed_artists:
        params["seed_artists"] = ",".join(seed_artists[:5])
    if seed_tracks:
        params["seed_tracks"] = ",".join(seed_tracks[:5])
    if seed_genres:
        params["seed_genres"] = ",".join(seed_genres[:5])
    return api_request("/recommendations", token_data, params)

def main():
    if len(sys.argv) < 2:
        print("Usage: spotify-api.py <command>")
        print("Commands: recent, top-artists, top-tracks, recommend")
        return 1
    
    cmd = sys.argv[1]
    token_data = load_token()
    
    if cmd == "recent":
        data = get_recently_played(token_data)
        print("Recently Played:")
        for item in data["items"]:
            track = item["track"]
            played_at = item["played_at"]
            artists = ", ".join(a["name"] for a in track["artists"])
            print(f"  {track['name']} - {artists} ({played_at[:10]})")
    
    elif cmd == "top-artists":
        time_range = sys.argv[2] if len(sys.argv) > 2 else "medium_term"
        data = get_top_artists(token_data, time_range)
        print(f"Top Artists ({time_range}):")
        for i, artist in enumerate(data["items"], 1):
            genres = ", ".join(artist["genres"][:3]) if artist["genres"] else "N/A"
            print(f"  {i}. {artist['name']} [{genres}]")
    
    elif cmd == "top-tracks":
        time_range = sys.argv[2] if len(sys.argv) > 2 else "medium_term"
        data = get_top_tracks(token_data, time_range)
        print(f"Top Tracks ({time_range}):")
        for i, track in enumerate(data["items"], 1):
            artists = ", ".join(a["name"] for a in track["artists"])
            print(f"  {i}. {track['name']} - {artists}")
    
    elif cmd == "recommend":
        # Get top artists for seeds
        top = get_top_artists(token_data, limit=5)
        seed_artists = [a["id"] for a in top["items"][:3]]
        
        data = get_recommendations(token_data, seed_artists=seed_artists)
        print("Recommendations based on your top artists:")
        for track in data["tracks"]:
            artists = ", ".join(a["name"] for a in track["artists"])
            print(f"  {track['name']} - {artists}")
    
    elif cmd == "json":
        # Raw JSON output for any endpoint
        endpoint = sys.argv[2] if len(sys.argv) > 2 else "/me"
        data = api_request(endpoint, token_data)
        print(json.dumps(data, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
