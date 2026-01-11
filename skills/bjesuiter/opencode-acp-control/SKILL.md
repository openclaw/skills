---
name: opencode-acp-control
description: Control OpenCode directly via the Agent Client Protocol (ACP). Start sessions, send prompts, resume conversations, and manage OpenCode updates.
metadata: {"version": "1.0.0", "author": "Benjamin Jesuiter <bjesuiter@gmail.com>", "license": "MIT", "github_url": "https://github.com/bjesuiter/opencode-acp-skill"}
---

# OpenCode ACP Skill

Control OpenCode directly via the Agent Client Protocol (ACP).

> **More Info for AGENTS**: For detailed ACP protocol documentation, see: https://agentclientprotocol.com/llms.txt
> **GitHub Repo**: https://github.com/bjesuiter/opencode-acp-skill

## Quick Reference

| Action | How |
|--------|-----|
| Start OpenCode | `bash(command: "opencode acp", background: true)` |
| Send message | `process.write(sessionId, data: "<json-rpc>\n")` |
| Read response | `process.poll(sessionId)` - repeat every 2 seconds |
| Stop OpenCode | `process.kill(sessionId)` |
| List sessions | `bash(command: "opencode session list", workdir: "...")` |
| Resume session | List sessions → ask user → `session/load` |
| Check version | `bash(command: "opencode --version")` |

## Starting OpenCode

```
bash(
  command: "opencode acp",
  background: true,
  workdir: "/path/to/your/project"
)
```

Save the returned `sessionId` - you'll need it for all subsequent commands.

## Protocol Basics

- All messages are **JSON-RPC 2.0** format
- Messages are **newline-delimited** (end each with `\n`)
- Maintain a **message ID counter** starting at 0

## Step-by-Step Workflow

### Step 1: Initialize Connection

Send immediately after starting OpenCode:

```json
{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":1,"clientCapabilities":{"fs":{"readTextFile":true,"writeTextFile":true},"terminal":true},"clientInfo":{"name":"clawdbot","title":"Clawdbot","version":"1.0.0"}}}
```

Poll for response. Expect `result.protocolVersion: 1`.

### Step 2: Create Session

```json
{"jsonrpc":"2.0","id":1,"method":"session/new","params":{"cwd":"/path/to/project","mcpServers":[]}}
```

Poll for response. Save `result.sessionId` (e.g., `"sess_abc123"`).

### Step 3: Send Prompts

```json
{"jsonrpc":"2.0","id":2,"method":"session/prompt","params":{"sessionId":"sess_abc123","prompt":[{"type":"text","text":"Your question here"}]}}
```

Poll every 2 seconds. You'll receive:
- `session/update` notifications (streaming content)
- Final response with `result.stopReason`

### Step 4: Read Responses

Each poll may return multiple lines. Parse each line as JSON:

- **Notifications**: `method: "session/update"` - collect these for the response
- **Response**: Has `id` matching your request - stop polling when `stopReason` appears

### Step 5: Cancel (if needed)

```json
{"jsonrpc":"2.0","method":"session/cancel","params":{"sessionId":"sess_abc123"}}
```

No response expected - this is a notification.

## State to Track

Per OpenCode instance, track:
- `processSessionId` - from bash tool (clawdbot's process ID)
- `opencodeSessionId` - from session/new response (OpenCode's session ID)  
- `messageId` - increment for each request you send

## Polling Strategy

- Poll every **2 seconds**
- Continue until you receive a response with `stopReason`
- Max wait: **5 minutes** (150 polls)
- If no response, consider the operation timed out

## Common Stop Reasons

| stopReason | Meaning |
|------------|---------|
| `end_turn` | Agent finished responding |
| `cancelled` | You cancelled the prompt |
| `max_tokens` | Token limit reached |

## Error Handling

| Issue | Solution |
|-------|----------|
| Empty poll response | Keep polling - agent is thinking |
| Parse error | Skip malformed line, continue |
| Process exited | Restart OpenCode |
| No response after 5min | Kill process, start fresh |

## Example: Complete Interaction

```
1. bash(command: "opencode acp", background: true, workdir: "/home/user/myproject")
   -> processSessionId: "bg_42"

2. process.write(sessionId: "bg_42", data: '{"jsonrpc":"2.0","id":0,"method":"initialize",...}\n')
   process.poll(sessionId: "bg_42") -> initialize response

3. process.write(sessionId: "bg_42", data: '{"jsonrpc":"2.0","id":1,"method":"session/new","params":{"cwd":"/home/user/myproject","mcpServers":[]}}\n')
   process.poll(sessionId: "bg_42") -> opencodeSessionId: "sess_xyz789"

4. process.write(sessionId: "bg_42", data: '{"jsonrpc":"2.0","id":2,"method":"session/prompt","params":{"sessionId":"sess_xyz789","prompt":[{"type":"text","text":"List all TypeScript files"}]}}\n')
   
5. process.poll(sessionId: "bg_42") every 2 sec until stopReason
   -> Collect all session/update content
   -> Final response: stopReason: "end_turn"

6. When done: process.kill(sessionId: "bg_42")
```

---

## Resume Session

Resume a previous OpenCode session by letting the user choose from available sessions.

### Step 1: List Available Sessions

```
bash(command: "opencode session list", workdir: "/path/to/project")
```

Example output:
```
ID                                  Updated              Messages
ses_451cd8ae0ffegNQsh59nuM3VVy      2026-01-11 15:30     12
ses_451a89e63ffea2TQIpnDGtJBkS      2026-01-10 09:15     5
ses_4518e90d0ffeJIpOFI3t3Jd23Q      2026-01-09 14:22     8
```

### Step 2: Ask User to Choose

Present the list to the user and ask which session to resume:

```
"Which session would you like to resume?
 
1. ses_451cd8ae... (12 messages, updated 2026-01-11)
2. ses_451a89e6... (5 messages, updated 2026-01-10)
3. ses_4518e90d... (8 messages, updated 2026-01-09)

Enter session number or ID:"
```

### Step 3: Load Selected Session

Once user responds (e.g., "1", "the first one", or "ses_451cd8ae..."):

1. **Start OpenCode ACP**:
   ```
   bash(command: "opencode acp", background: true, workdir: "/path/to/project")
   ```

2. **Initialize**:
   ```json
   {"jsonrpc":"2.0","id":0,"method":"initialize","params":{...}}
   ```

3. **Load the session**:
   ```json
   {"jsonrpc":"2.0","id":1,"method":"session/load","params":{"sessionId":"ses_451cd8ae0ffegNQsh59nuM3VVy","cwd":"/path/to/project","mcpServers":[]}}
   ```

**Note**: `session/load` requires `cwd` and `mcpServers` parameters.

On load, OpenCode streams the full conversation history back to you.

### Resume Workflow Summary

```
function resumeSession(workdir):
    # List available sessions
    output = bash("opencode session list", workdir: workdir)
    sessions = parseSessionList(output)
    
    if sessions.empty:
        notify("No previous sessions found. Starting fresh.")
        return createNewSession(workdir)
    
    # Ask user to choose
    choice = askUser("Which session to resume?", sessions)
    selectedId = matchUserChoice(choice, sessions)
    
    # Start OpenCode and load session
    process = bash("opencode acp", background: true, workdir: workdir)
    initialize(process)
    
    session_load(process, selectedId, workdir, mcpServers: [])
    
    notify("Session resumed. Conversation history loaded.")
    return process
```

### Important Notes

- **History replay**: On load, all previous messages stream back
- **Memory preserved**: Agent remembers the full conversation
- **Process independent**: Sessions survive OpenCode restarts

---

## Updating OpenCode

OpenCode auto-updates when restarted. Use this workflow to check and trigger updates.

### Step 1: Check Current Version

```
bash(command: "opencode --version")
```

Returns something like: `opencode version 1.1.13`

Extract the version number (e.g., `1.1.13`).

### Step 2: Check Latest Version

```
webfetch(url: "https://github.com/anomalyco/opencode/releases/latest", format: "text")
```

The redirect URL contains the latest version tag:
- Redirects to: `https://github.com/anomalyco/opencode/releases/tag/v1.2.0`
- Extract version from the URL path (e.g., `1.2.0`)

### Step 3: Compare and Update

If latest version > current version:

1. **Stop all running OpenCode processes**:
   ```
   process.list()  # Find all "opencode acp" processes
   process.kill(sessionId) # For each running instance
   ```

2. **Restart instances** (OpenCode auto-downloads new binary on start):
   ```
   bash(command: "opencode acp", background: true, workdir: "/path/to/project")
   ```

3. **Re-initialize** each instance (initialize + session/load for existing sessions)

### Step 4: Verify Update

```
bash(command: "opencode --version")
```

If version still doesn't match latest:
- Inform user: "OpenCode auto-update may have failed. Current: X.X.X, Latest: Y.Y.Y"
- Suggest manual update: `curl -fsSL https://opencode.dev/install | bash`

### Update Workflow Summary

```
function updateOpenCode():
    current = bash("opencode --version")  # e.g., "1.1.13"
    
    latestPage = webfetch("https://github.com/anomalyco/opencode/releases/latest")
    latest = extractVersionFromRedirectUrl(latestPage)  # e.g., "1.2.0"
    
    if semverCompare(latest, current) > 0:
        # Stop all instances
        for process in process.list():
            if process.command.includes("opencode"):
                process.kill(process.sessionId)
        
        # Wait briefly for processes to terminate
        sleep(2 seconds)
        
        # Restart triggers auto-update
        bash("opencode acp", background: true)
        
        # Verify
        newVersion = bash("opencode --version")
        if newVersion != latest:
            notify("Auto-update may have failed. Manual update recommended.")
    else:
        notify("OpenCode is up to date: " + current)
```

### Important Notes

- **Sessions persist**: `opencodeSessionId` survives restarts — use `session/load` to recover
- **Auto-update**: OpenCode downloads new binary automatically on restart
- **No data loss**: Conversation history is preserved server-side
