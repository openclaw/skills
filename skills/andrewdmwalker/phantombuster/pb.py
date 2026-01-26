#!/usr/bin/env python3
"""PhantomBuster CLI for Clawdbot.

Control your PhantomBuster automation agents.

Commands:
- list: List all agents
- launch: Launch an agent
- output: Get agent output
- status: Check agent status
- abort: Abort running agent
- get: Get agent details
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

API_BASE = "https://api.phantombuster.com/api/v2"


def get_api_key():
    """Get API key from environment."""
    api_key = os.environ.get("PHANTOMBUSTER_API_KEY")
    if not api_key:
        print("Error: PHANTOMBUSTER_API_KEY environment variable not set", file=sys.stderr)
        print("Get your key at: https://phantombuster.com/workspace-settings", file=sys.stderr)
        sys.exit(1)
    return api_key


def api_request(method, endpoint, data=None):
    """Make an API request to PhantomBuster."""
    api_key = get_api_key()
    url = f"{API_BASE}{endpoint}"
    
    headers = {
        "X-Phantombuster-Key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    if data:
        data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            error_json = json.loads(error_body)
            print(f"Error {e.code}: {error_json.get('message', error_body)}", file=sys.stderr)
        except:
            print(f"Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args):
    """List all agents."""
    result = api_request("GET", "/agents/fetch-all")
    
    agents = result if isinstance(result, list) else result.get("data", [])
    
    if args.json:
        print(json.dumps(agents, indent=2))
        return
    
    if not agents:
        print("No agents found.")
        return
    
    print(f"Found {len(agents)} agents:\n")
    for agent in agents:
        agent_id = agent.get("id", "?")
        name = agent.get("name", "Unnamed")
        script = agent.get("scriptName", agent.get("script", ""))
        last_status = agent.get("lastEndStatus", "unknown")
        
        status_emoji = {
            "finished": "✅",
            "error": "❌",
            "running": "🔄",
            "unknown": "❓"
        }.get(last_status, "❓")
        
        print(f"{status_emoji} [{agent_id}] {name}")
        if script:
            print(f"   Script: {script}")
        print()


def cmd_launch(args):
    """Launch an agent."""
    data = {"id": args.agent_id}
    
    if args.argument:
        try:
            data["argument"] = json.loads(args.argument)
        except json.JSONDecodeError:
            # Treat as string argument
            data["argument"] = args.argument
    
    result = api_request("POST", "/agents/launch", data)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        container_id = result.get("containerId", "unknown")
        print(f"✅ Agent {args.agent_id} launched!")
        print(f"   Container ID: {container_id}")


def cmd_output(args):
    """Get agent output."""
    result = api_request("GET", f"/agents/fetch-output?id={args.agent_id}")
    
    if args.json:
        print(json.dumps(result, indent=2))
        return
    
    status = result.get("status", "unknown")
    output = result.get("output", "")
    result_object = result.get("resultObject")
    
    print(f"Status: {status}")
    
    if output:
        print(f"\n--- Console Output ---\n{output}")
    
    if result_object:
        print(f"\n--- Result Data ---")
        if isinstance(result_object, str):
            try:
                parsed = json.loads(result_object)
                print(json.dumps(parsed, indent=2))
            except:
                print(result_object)
        else:
            print(json.dumps(result_object, indent=2))


def cmd_status(args):
    """Check agent status."""
    result = api_request("GET", f"/agents/fetch?id={args.agent_id}")
    
    if args.json:
        print(json.dumps(result, indent=2))
        return
    
    name = result.get("name", "Unknown")
    last_status = result.get("lastEndStatus", "unknown")
    last_end = result.get("lastEndMessage", "")
    running = result.get("runningContainers", 0)
    
    status_emoji = {
        "finished": "✅",
        "error": "❌",
        "running": "🔄"
    }.get(last_status, "❓")
    
    print(f"Agent: {name}")
    print(f"Status: {status_emoji} {last_status}")
    if running > 0:
        print(f"Running containers: {running}")
    if last_end:
        print(f"Last message: {last_end}")


def cmd_abort(args):
    """Abort a running agent."""
    result = api_request("POST", "/agents/abort", {"id": args.agent_id})
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"🛑 Abort signal sent to agent {args.agent_id}")


def cmd_get(args):
    """Get agent details."""
    result = api_request("GET", f"/agents/fetch?id={args.agent_id}")
    
    if args.json:
        print(json.dumps(result, indent=2))
        return
    
    print(f"Agent: {result.get('name', 'Unknown')}")
    print(f"ID: {result.get('id', '?')}")
    print(f"Script: {result.get('scriptName', result.get('script', 'N/A'))}")
    print(f"Last Status: {result.get('lastEndStatus', 'unknown')}")
    print(f"Last Message: {result.get('lastEndMessage', 'N/A')}")
    print(f"Running: {result.get('runningContainers', 0)} container(s)")
    
    if result.get("argument"):
        print(f"\nArgument:")
        arg = result["argument"]
        if isinstance(arg, str):
            try:
                print(json.dumps(json.loads(arg), indent=2))
            except:
                print(arg)
        else:
            print(json.dumps(arg, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="PhantomBuster CLI for Clawdbot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pb.py list                          # List all agents
  pb.py launch 12345                  # Launch agent by ID
  pb.py output 12345                  # Get output from agent
  pb.py status 12345                  # Check agent status
  pb.py abort 12345                   # Abort running agent
        """
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # List
    list_parser = subparsers.add_parser("list", help="List all agents")
    list_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Launch
    launch_parser = subparsers.add_parser("launch", help="Launch an agent")
    launch_parser.add_argument("agent_id", help="Agent ID")
    launch_parser.add_argument("--argument", "-a", help="JSON argument to pass")
    launch_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Output
    output_parser = subparsers.add_parser("output", help="Get agent output")
    output_parser.add_argument("agent_id", help="Agent ID")
    output_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Status
    status_parser = subparsers.add_parser("status", help="Check agent status")
    status_parser.add_argument("agent_id", help="Agent ID")
    status_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Abort
    abort_parser = subparsers.add_parser("abort", help="Abort running agent")
    abort_parser.add_argument("agent_id", help="Agent ID")
    abort_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Get
    get_parser = subparsers.add_parser("get", help="Get agent details")
    get_parser.add_argument("agent_id", help="Agent ID")
    get_parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    commands = {
        "list": cmd_list,
        "launch": cmd_launch,
        "output": cmd_output,
        "status": cmd_status,
        "abort": cmd_abort,
        "get": cmd_get,
    }
    
    commands[args.command](args)


if __name__ == "__main__":
    main()
