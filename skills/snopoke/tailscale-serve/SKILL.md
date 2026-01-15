# Tailscale Serve Skill

Manage multiple paths with `tailscale serve` without conflicts.

## Key Commands

### Check what's currently served
```bash
tailscale serve status
```

### Serve a directory or file at a specific path
```bash
# Directory
tailscale serve --bg --set-path /slides /path/to/directory

# Single file
tailscale serve --bg --set-path /presentation /path/to/file.html

# Port (for running services)
tailscale serve --bg --set-path /api http://localhost:8080
```

### Serve from a port at root (replaces everything)
```bash
tailscale serve --bg 8888
```

### Remove a specific path
```bash
tailscale serve --https=443 /slides off
```

### Reset all serving
```bash
tailscale serve reset
```

## Important Notes

- **Path conflicts:** Serving at `/` will override all other paths
- **Background mode:** Use `--bg` to keep it running
- **Multiple paths:** You can serve multiple things simultaneously with different paths
- **Status first:** Always check `tailscale serve status` before adding new paths

## Common Patterns

### Serve presentation alongside control UI
```bash
# If control UI is at /, serve presentation at a subpath
tailscale serve --bg --set-path /slides ~/clawd/personal-agents-presentation.html

# Access at: https://[hostname].ts.net/slides
```

### Serve multiple directories
```bash
tailscale serve --bg --set-path /docs ~/documents
tailscale serve --bg --set-path /slides ~/presentations
tailscale serve --bg --set-path /files ~/files
```

### Serve a local dev server
```bash
tailscale serve --bg --set-path /app http://localhost:3000
```

## Workflow

1. Check current status: `tailscale serve status`
2. Choose an unused path (e.g., `/slides`, `/docs`, `/api`)
3. Serve with `--set-path /your-path /source`
4. Verify with `tailscale serve status` again
5. Share the full URL: `https://[hostname].ts.net/your-path`

## Troubleshooting

**"Can't access my served content"**
- Check `tailscale serve status` - is it at the path you expect?
- Did something else overwrite the root `/`?

**"Want to replace everything with a port"**
```bash
tailscale serve reset
tailscale serve --bg 8888
```

**"Want to add to existing setup"**
```bash
# Don't use reset! Just add with --set-path
tailscale serve --bg --set-path /newpath /source
```
