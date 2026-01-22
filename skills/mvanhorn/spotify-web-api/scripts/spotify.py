#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "spotipy>=2.23.0",
# ]
# ///
"""
Spotify control via Web API.
Works on any platform - no Mac required.
"""

import argparse
import json
import os
import sys
from pathlib import Path

CACHE_PATH = Path.home() / ".spotify_cache.json"
REDIRECT_URI = "http://localhost:8888/callback"

# Scopes needed for various features
SCOPES = [
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
    "user-read-recently-played",
    "user-top-read",
    "playlist-read-private",
    "playlist-modify-public",
    "playlist-modify-private",
]


def get_spotify():
    """Get authenticated Spotify client."""
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ Missing SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET", file=sys.stderr)
        print("\nSetup instructions:", file=sys.stderr)
        print("1. Go to https://developer.spotify.com/dashboard", file=sys.stderr)
        print("2. Create an app", file=sys.stderr)
        print("3. Add redirect URI: http://localhost:8888/callback", file=sys.stderr)
        print("4. Copy Client ID and Client Secret", file=sys.stderr)
        print("5. Set env vars: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET", file=sys.stderr)
        sys.exit(1)
    
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=REDIRECT_URI,
        scope=" ".join(SCOPES),
        cache_path=str(CACHE_PATH),
        open_browser=False,
    )
    
    # Check if we need to authenticate
    token_info = auth_manager.get_cached_token()
    if not token_info:
        auth_url = auth_manager.get_authorize_url()
        print(f"\n🔐 Open this URL in your browser:\n{auth_url}\n")
        print("After authorizing, paste the full redirect URL here:")
        response = input("\nRedirect URL: ").strip()
        
        code = auth_manager.parse_response_code(response)
        auth_manager.get_access_token(code)
        print("✅ Authenticated!")
    
    return spotipy.Spotify(auth_manager=auth_manager)


def format_duration(ms):
    """Format milliseconds as mm:ss."""
    seconds = ms // 1000
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins}:{secs:02d}"


def cmd_auth(args):
    """Authenticate with Spotify."""
    sp = get_spotify()
    user = sp.current_user()
    print(f"✅ Authenticated as: {user['display_name']}")
    print(f"   Email: {user.get('email', 'N/A')}")
    print(f"   Account: {user.get('product', 'free')}")


def cmd_now(args):
    """Get currently playing track."""
    sp = get_spotify()
    current = sp.current_playback()
    
    if not current or not current.get('item'):
        print("🔇 Nothing playing")
        return
    
    item = current['item']
    artists = ", ".join(a['name'] for a in item['artists'])
    
    print(f"🎵 **Now Playing**")
    print(f"   {item['name']}")
    print(f"   {artists}")
    print(f"   Album: {item['album']['name']}")
    
    progress = current.get('progress_ms', 0)
    duration = item.get('duration_ms', 0)
    print(f"   {format_duration(progress)} / {format_duration(duration)}")
    
    device = current.get('device', {})
    if device:
        print(f"   📱 {device.get('name', 'Unknown')} ({device.get('type', '')})")
    
    if current.get('is_playing'):
        print("   ▶️ Playing")
    else:
        print("   ⏸️ Paused")


def cmd_recent(args):
    """Get recently played tracks."""
    sp = get_spotify()
    results = sp.current_user_recently_played(limit=args.limit)
    
    print(f"🕐 **Recently Played**\n")
    
    for i, item in enumerate(results['items'], 1):
        track = item['track']
        artists = ", ".join(a['name'] for a in track['artists'])
        played_at = item['played_at'][:10]  # Just the date
        print(f"{i}. {track['name']} — {artists}")
        print(f"   {played_at}")
        print()


def cmd_top(args):
    """Get top tracks or artists."""
    sp = get_spotify()
    
    time_range = {
        'week': 'short_term',
        'month': 'medium_term',
        'year': 'long_term',
        'all': 'long_term',
    }.get(args.period, 'medium_term')
    
    if args.type == 'tracks':
        results = sp.current_user_top_tracks(limit=args.limit, time_range=time_range)
        print(f"🏆 **Top Tracks** ({args.period})\n")
        for i, track in enumerate(results['items'], 1):
            artists = ", ".join(a['name'] for a in track['artists'])
            print(f"{i}. {track['name']} — {artists}")
    else:
        results = sp.current_user_top_artists(limit=args.limit, time_range=time_range)
        print(f"🏆 **Top Artists** ({args.period})\n")
        for i, artist in enumerate(results['items'], 1):
            genres = ", ".join(artist.get('genres', [])[:2])
            print(f"{i}. {artist['name']}")
            if genres:
                print(f"   {genres}")


def cmd_play(args):
    """Play/resume playback."""
    sp = get_spotify()
    
    if args.query:
        # Search and play
        results = sp.search(q=args.query, type='track', limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            sp.start_playback(uris=[track['uri']])
            artists = ", ".join(a['name'] for a in track['artists'])
            print(f"▶️ Playing: {track['name']} — {artists}")
        else:
            print("❌ No tracks found")
    else:
        sp.start_playback()
        print("▶️ Resumed playback")


def cmd_pause(args):
    """Pause playback."""
    sp = get_spotify()
    sp.pause_playback()
    print("⏸️ Paused")


def cmd_next(args):
    """Skip to next track."""
    sp = get_spotify()
    sp.next_track()
    print("⏭️ Skipped to next")


def cmd_prev(args):
    """Go to previous track."""
    sp = get_spotify()
    sp.previous_track()
    print("⏮️ Previous track")


def cmd_search(args):
    """Search for tracks."""
    sp = get_spotify()
    results = sp.search(q=args.query, type='track', limit=args.limit)
    
    print(f"🔍 **Search: '{args.query}'**\n")
    
    for i, track in enumerate(results['tracks']['items'], 1):
        artists = ", ".join(a['name'] for a in track['artists'])
        print(f"{i}. {track['name']} — {artists}")
        print(f"   {track['album']['name']} ({track['album']['release_date'][:4]})")
        print()


def cmd_devices(args):
    """List available devices."""
    sp = get_spotify()
    devices = sp.devices()
    
    print("📱 **Available Devices**\n")
    
    if not devices['devices']:
        print("No active devices found")
        return
    
    for d in devices['devices']:
        active = "✅" if d['is_active'] else "  "
        print(f"{active} {d['name']} ({d['type']})")
        print(f"   ID: {d['id'][:16]}...")


def main():
    parser = argparse.ArgumentParser(description="Spotify control")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Auth
    subparsers.add_parser("auth", help="Authenticate with Spotify")
    
    # Now playing
    subparsers.add_parser("now", help="Currently playing")
    
    # Recent
    recent_parser = subparsers.add_parser("recent", help="Recently played")
    recent_parser.add_argument("--limit", "-l", type=int, default=10)
    
    # Top
    top_parser = subparsers.add_parser("top", help="Top tracks/artists")
    top_parser.add_argument("type", choices=["tracks", "artists"])
    top_parser.add_argument("--period", "-p", default="month", 
                           choices=["week", "month", "year", "all"])
    top_parser.add_argument("--limit", "-l", type=int, default=10)
    
    # Playback
    play_parser = subparsers.add_parser("play", help="Play/resume")
    play_parser.add_argument("query", nargs="?", help="Search and play")
    
    subparsers.add_parser("pause", help="Pause playback")
    subparsers.add_parser("next", help="Next track")
    subparsers.add_parser("prev", help="Previous track")
    
    # Search
    search_parser = subparsers.add_parser("search", help="Search tracks")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", "-l", type=int, default=5)
    
    # Devices
    subparsers.add_parser("devices", help="List devices")
    
    args = parser.parse_args()
    
    commands = {
        "auth": cmd_auth,
        "now": cmd_now,
        "recent": cmd_recent,
        "top": cmd_top,
        "play": cmd_play,
        "pause": cmd_pause,
        "next": cmd_next,
        "prev": cmd_prev,
        "search": cmd_search,
        "devices": cmd_devices,
    }
    
    try:
        commands[args.command](args)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
