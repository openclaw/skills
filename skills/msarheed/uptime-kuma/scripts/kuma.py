#!/usr/bin/env python3
"""
Uptime Kuma CLI wrapper using uptime-kuma-api library.
Requires: pip install uptime-kuma-api

Environment variables:
  UPTIME_KUMA_URL      - Uptime Kuma server URL (e.g., http://localhost:3001)
  UPTIME_KUMA_USERNAME - Username for authentication
  UPTIME_KUMA_PASSWORD - Password for authentication
"""

import argparse
import json
import os
import sys
from typing import Optional

try:
    from uptime_kuma_api import UptimeKumaApi, MonitorType
except ImportError:
    print("Error: uptime-kuma-api not installed. Run: pip install uptime-kuma-api", file=sys.stderr)
    sys.exit(1)


def get_env_or_exit(name: str) -> str:
    """Get environment variable or exit with error."""
    value = os.environ.get(name)
    if not value:
        print(f"Error: {name} environment variable not set", file=sys.stderr)
        sys.exit(1)
    return value


def get_api() -> UptimeKumaApi:
    """Create and authenticate API connection."""
    url = get_env_or_exit("UPTIME_KUMA_URL")
    username = get_env_or_exit("UPTIME_KUMA_USERNAME")
    password = get_env_or_exit("UPTIME_KUMA_PASSWORD")
    
    api = UptimeKumaApi(url)
    api.login(username, password)
    return api


def cmd_list_monitors(args):
    """List all monitors."""
    with get_api() as api:
        monitors = api.get_monitors()
        if args.json:
            print(json.dumps(monitors, indent=2, default=str))
        else:
            for m in monitors:
                status = "🟢" if m.get("active") else "⚫"
                print(f"{status} [{m['id']}] {m['name']} ({m['type']})")


def cmd_get_monitor(args):
    """Get details of a specific monitor."""
    with get_api() as api:
        monitor = api.get_monitor(args.id)
        print(json.dumps(monitor, indent=2, default=str))


def cmd_add_monitor(args):
    """Add a new monitor."""
    monitor_types = {
        "http": MonitorType.HTTP,
        "https": MonitorType.HTTP,
        "port": MonitorType.PORT,
        "ping": MonitorType.PING,
        "keyword": MonitorType.KEYWORD,
        "dns": MonitorType.DNS,
        "docker": MonitorType.DOCKER,
        "push": MonitorType.PUSH,
        "steam": MonitorType.STEAM,
        "gamedig": MonitorType.GAMEDIG,
        "mqtt": MonitorType.MQTT,
        "sqlserver": MonitorType.SQLSERVER,
        "postgres": MonitorType.POSTGRES,
        "mysql": MonitorType.MYSQL,
        "mongodb": MonitorType.MONGODB,
        "radius": MonitorType.RADIUS,
        "redis": MonitorType.REDIS,
        "group": MonitorType.GROUP,
    }
    
    monitor_type = monitor_types.get(args.type.lower())
    if not monitor_type:
        print(f"Error: Unknown monitor type '{args.type}'. Valid types: {', '.join(monitor_types.keys())}", file=sys.stderr)
        sys.exit(1)
    
    kwargs = {
        "type": monitor_type,
        "name": args.name,
    }
    
    if args.url:
        kwargs["url"] = args.url
    if args.hostname:
        kwargs["hostname"] = args.hostname
    if args.port:
        kwargs["port"] = args.port
    if args.interval:
        kwargs["interval"] = args.interval
    if args.keyword:
        kwargs["keyword"] = args.keyword
    
    with get_api() as api:
        result = api.add_monitor(**kwargs)
        print(json.dumps(result, indent=2, default=str))


def cmd_delete_monitor(args):
    """Delete a monitor."""
    with get_api() as api:
        result = api.delete_monitor(args.id)
        print(json.dumps(result, indent=2, default=str))


def cmd_pause_monitor(args):
    """Pause a monitor."""
    with get_api() as api:
        result = api.pause_monitor(args.id)
        print(json.dumps(result, indent=2, default=str))


def cmd_resume_monitor(args):
    """Resume a monitor."""
    with get_api() as api:
        result = api.resume_monitor(args.id)
        print(json.dumps(result, indent=2, default=str))


def cmd_status(args):
    """Get overall status summary."""
    with get_api() as api:
        monitors = api.get_monitors()
        
        total = len(monitors)
        active = sum(1 for m in monitors if m.get("active"))
        paused = total - active
        
        # Get heartbeats for status
        up = 0
        down = 0
        pending = 0
        
        for m in monitors:
            if not m.get("active"):
                continue
            beats = api.get_monitor_beats(m["id"], 1)
            if beats:
                status = beats[0].get("status")
                if status == 1:
                    up += 1
                elif status == 0:
                    down += 1
                else:
                    pending += 1
            else:
                pending += 1
        
        if args.json:
            print(json.dumps({
                "total": total,
                "active": active,
                "paused": paused,
                "up": up,
                "down": down,
                "pending": pending
            }, indent=2))
        else:
            print(f"📊 Uptime Kuma Status")
            print(f"   Total monitors: {total}")
            print(f"   Active: {active} | Paused: {paused}")
            print(f"   🟢 Up: {up} | 🔴 Down: {down} | ⏳ Pending: {pending}")


def cmd_heartbeats(args):
    """Get recent heartbeats for a monitor."""
    with get_api() as api:
        beats = api.get_monitor_beats(args.id, args.hours)
        if args.json:
            print(json.dumps(beats, indent=2, default=str))
        else:
            for b in beats[-10:]:  # Show last 10
                status = "🟢" if b.get("status") == 1 else "🔴"
                time = b.get("time", "?")
                ping = b.get("ping", "?")
                print(f"{status} {time} - {ping}ms")


def cmd_notifications(args):
    """List notification channels."""
    with get_api() as api:
        notifications = api.get_notifications()
        if args.json:
            print(json.dumps(notifications, indent=2, default=str))
        else:
            for n in notifications:
                active = "✓" if n.get("active") else "✗"
                print(f"[{active}] [{n['id']}] {n['name']} ({n['type']})")


def main():
    parser = argparse.ArgumentParser(description="Uptime Kuma CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # list
    p_list = subparsers.add_parser("list", help="List all monitors")
    p_list.add_argument("--json", action="store_true", help="Output as JSON")
    p_list.set_defaults(func=cmd_list_monitors)
    
    # get
    p_get = subparsers.add_parser("get", help="Get monitor details")
    p_get.add_argument("id", type=int, help="Monitor ID")
    p_get.set_defaults(func=cmd_get_monitor)
    
    # add
    p_add = subparsers.add_parser("add", help="Add a new monitor")
    p_add.add_argument("--name", required=True, help="Monitor name")
    p_add.add_argument("--type", required=True, help="Monitor type (http, ping, port, etc.)")
    p_add.add_argument("--url", help="URL to monitor (for HTTP)")
    p_add.add_argument("--hostname", help="Hostname (for ping/port)")
    p_add.add_argument("--port", type=int, help="Port number")
    p_add.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    p_add.add_argument("--keyword", help="Keyword to search (for keyword type)")
    p_add.set_defaults(func=cmd_add_monitor)
    
    # delete
    p_del = subparsers.add_parser("delete", help="Delete a monitor")
    p_del.add_argument("id", type=int, help="Monitor ID")
    p_del.set_defaults(func=cmd_delete_monitor)
    
    # pause
    p_pause = subparsers.add_parser("pause", help="Pause a monitor")
    p_pause.add_argument("id", type=int, help="Monitor ID")
    p_pause.set_defaults(func=cmd_pause_monitor)
    
    # resume
    p_resume = subparsers.add_parser("resume", help="Resume a monitor")
    p_resume.add_argument("id", type=int, help="Monitor ID")
    p_resume.set_defaults(func=cmd_resume_monitor)
    
    # status
    p_status = subparsers.add_parser("status", help="Get overall status")
    p_status.add_argument("--json", action="store_true", help="Output as JSON")
    p_status.set_defaults(func=cmd_status)
    
    # heartbeats
    p_hb = subparsers.add_parser("heartbeats", help="Get heartbeats for a monitor")
    p_hb.add_argument("id", type=int, help="Monitor ID")
    p_hb.add_argument("--hours", type=int, default=24, help="Hours of history")
    p_hb.add_argument("--json", action="store_true", help="Output as JSON")
    p_hb.set_defaults(func=cmd_heartbeats)
    
    # notifications
    p_notif = subparsers.add_parser("notifications", help="List notification channels")
    p_notif.add_argument("--json", action="store_true", help="Output as JSON")
    p_notif.set_defaults(func=cmd_notifications)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
