#!/usr/bin/env python3
"""GitHub PAT CLI - secure, user-controlled GitHub access."""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.parse
import urllib.error

DEFAULT_TOKEN = os.environ.get("GITHUB_TOKEN", "")
API_BASE = "https://api.github.com"

def get_token(args_token):
    """Get token from args or environment."""
    return args_token or DEFAULT_TOKEN

def api_request(method, endpoint, token, data=None):
    """Make GitHub API request."""
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-pat-skill"
    }
    
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error = e.read().decode()
        print(f"API Error {e.code}: {error}", file=sys.stderr)
        sys.exit(1)

def cmd_repos(args):
    """List repos user has access to."""
    token = get_token(args.token)
    if not token:
        print("Error: No token provided. Use --token or set GITHUB_TOKEN", file=sys.stderr)
        sys.exit(1)
    
    data = api_request("GET", "/user/repos?per_page=50&sort=updated", token)
    
    print(f"📁 Your Repositories ({len(data)}):\n")
    for repo in data[:20]:
        private = "🔒" if repo["private"] else "🌐"
        perms = []
        if repo.get("permissions", {}).get("push"):
            perms.append("write")
        if repo.get("permissions", {}).get("pull"):
            perms.append("read")
        perm_str = ",".join(perms)
        print(f"{private} {repo['full_name']} [{perm_str}]")
        if repo.get("description"):
            print(f"   {repo['description'][:60]}")

def cmd_clone(args):
    """Clone a repository."""
    token = get_token(args.token)
    repo = args.repo
    
    if "/" not in repo:
        print("Error: Repo must be in format owner/repo", file=sys.stderr)
        sys.exit(1)
    
    # Use token in URL for auth
    url = f"https://{token}@github.com/{repo}.git"
    dest = repo.split("/")[-1]
    
    print(f"📥 Cloning {repo}...")
    result = subprocess.run(["git", "clone", url, dest], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Cloned to ./{dest}")
    else:
        print(f"❌ Clone failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

def cmd_branch(args):
    """Create and checkout a new branch."""
    branch = args.branch
    
    # Check if we're in a git repo
    result = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True)
    if result.returncode != 0:
        print("Error: Not in a git repository", file=sys.stderr)
        sys.exit(1)
    
    print(f"🌿 Creating branch: {branch}")
    result = subprocess.run(["git", "checkout", "-b", branch], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Switched to new branch '{branch}'")
    else:
        # Maybe branch exists, try switching
        result = subprocess.run(["git", "checkout", branch], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Switched to existing branch '{branch}'")
        else:
            print(f"❌ Failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)

def cmd_push(args):
    """Commit and push changes."""
    token = get_token(args.token)
    message = args.message
    
    # Get current branch
    result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    branch = result.stdout.strip() or "main"
    
    # Get remote URL
    result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
    remote_url = result.stdout.strip()
    
    # Check if token already in URL
    token_in_url = "@github.com" in remote_url
    
    if token and "github.com" in remote_url and not token_in_url:
        # Inject token into remote URL
        auth_url = remote_url.replace("https://", f"https://{token}@")
        use_url = True
    else:
        # Token already in URL or not needed
        use_url = False
    
    # Stage all changes
    print("📦 Staging changes...")
    subprocess.run(["git", "add", "-A"])
    
    # Commit
    print(f"💾 Committing: {message}")
    result = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True)
    if result.returncode != 0 and "nothing to commit" in result.stdout + result.stderr:
        print("ℹ️  Nothing to commit")
        return
    
    # Push
    print(f"🚀 Pushing to {branch}...")
    if use_url:
        result = subprocess.run(
            ["git", "push", "-u", auth_url, branch],
            capture_output=True, text=True
        )
    else:
        result = subprocess.run(
            ["git", "push", "-u", "origin", branch],
            capture_output=True, text=True
        )
    
    if result.returncode == 0:
        print(f"✅ Pushed to {branch}")
    else:
        # Try setting upstream
        if use_url:
            result = subprocess.run(
                ["git", "push", "--set-upstream", auth_url, branch],
                capture_output=True, text=True
            )
        else:
            result = subprocess.run(
                ["git", "push", "--set-upstream", "origin", branch],
                capture_output=True, text=True
            )
        if result.returncode == 0:
            print(f"✅ Pushed to {branch}")
        else:
            print(f"❌ Push failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)

def cmd_pr(args):
    """Create a pull request."""
    token = get_token(args.token)
    if not token:
        print("Error: No token provided", file=sys.stderr)
        sys.exit(1)
    
    # Get repo from git remote
    result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
    remote = result.stdout.strip()
    # Extract owner/repo from URL
    if "github.com" in remote:
        parts = remote.replace(".git", "").split("github.com")[-1].strip("/:")
        if "@" in parts:
            parts = parts.split("@")[-1]
        repo = "/".join(parts.split("/")[-2:])
    else:
        repo = args.repo
    
    if not repo:
        print("Error: Could not determine repo. Use --repo owner/repo", file=sys.stderr)
        sys.exit(1)
    
    # Get current branch
    result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    head = args.head or result.stdout.strip()
    
    print(f"📝 Creating PR: {args.title}")
    print(f"   {head} → {args.base}")
    
    data = api_request("POST", f"/repos/{repo}/pulls", token, {
        "title": args.title,
        "body": args.body or "",
        "head": head,
        "base": args.base
    })
    
    print(f"✅ PR created: {data.get('html_url')}")

def cmd_issue(args):
    """Create an issue."""
    token = get_token(args.token)
    repo = args.repo
    
    if not token:
        print("Error: No token provided", file=sys.stderr)
        sys.exit(1)
    
    if not repo:
        # Try to get from git remote
        result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
        remote = result.stdout.strip()
        if "github.com" in remote:
            parts = remote.replace(".git", "").split("github.com")[-1].strip("/:")
            repo = "/".join(parts.split("/")[-2:])
    
    if not repo:
        print("Error: Could not determine repo. Use --repo owner/repo", file=sys.stderr)
        sys.exit(1)
    
    print(f"📝 Creating issue in {repo}: {args.title}")
    
    data = api_request("POST", f"/repos/{repo}/issues", token, {
        "title": args.title,
        "body": args.body or ""
    })
    
    print(f"✅ Issue created: {data.get('html_url')}")

def cmd_info(args):
    """Get repo info."""
    token = get_token(args.token)
    repo = args.repo
    
    if not token:
        print("Error: No token provided", file=sys.stderr)
        sys.exit(1)
    
    data = api_request("GET", f"/repos/{repo}", token)
    
    print(f"📁 {data['full_name']}")
    print(f"   {'🔒 Private' if data['private'] else '🌐 Public'}")
    if data.get("description"):
        print(f"   {data['description']}")
    print(f"   ⭐ {data['stargazers_count']} | 🍴 {data['forks_count']}")
    print(f"   🌿 Default branch: {data['default_branch']}")
    perms = data.get("permissions", {})
    print(f"   ✏️  Your access: {'admin' if perms.get('admin') else 'push' if perms.get('push') else 'read'}")

def main():
    parser = argparse.ArgumentParser(description="GitHub PAT CLI")
    parser.add_argument("--token", "-t", help="GitHub PAT (or set GITHUB_TOKEN)")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # repos
    subparsers.add_parser("repos", help="List your repositories")
    
    # clone
    clone_p = subparsers.add_parser("clone", help="Clone a repository")
    clone_p.add_argument("repo", help="Repository (owner/repo)")
    
    # branch
    branch_p = subparsers.add_parser("branch", help="Create/switch branch")
    branch_p.add_argument("branch", help="Branch name")
    
    # push
    push_p = subparsers.add_parser("push", help="Commit and push")
    push_p.add_argument("message", help="Commit message")
    
    # pr
    pr_p = subparsers.add_parser("pr", help="Create pull request")
    pr_p.add_argument("title", help="PR title")
    pr_p.add_argument("--body", "-b", help="PR description")
    pr_p.add_argument("--base", default="main", help="Base branch (default: main)")
    pr_p.add_argument("--head", help="Head branch (default: current)")
    pr_p.add_argument("--repo", help="Repository (owner/repo)")
    
    # issue
    issue_p = subparsers.add_parser("issue", help="Create issue")
    issue_p.add_argument("title", help="Issue title")
    issue_p.add_argument("--body", "-b", help="Issue description")
    issue_p.add_argument("--repo", help="Repository (owner/repo)")
    
    # info
    info_p = subparsers.add_parser("info", help="Get repo info")
    info_p.add_argument("repo", help="Repository (owner/repo)")
    
    args = parser.parse_args()
    
    if args.command == "repos":
        cmd_repos(args)
    elif args.command == "clone":
        cmd_clone(args)
    elif args.command == "branch":
        cmd_branch(args)
    elif args.command == "push":
        cmd_push(args)
    elif args.command == "pr":
        cmd_pr(args)
    elif args.command == "issue":
        cmd_issue(args)
    elif args.command == "info":
        cmd_info(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
