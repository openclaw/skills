# GNO MCP Installation

GNO provides an MCP (Model Context Protocol) server for AI client integration.

> **Full reference**: See [gno.sh/docs/MCP](https://www.gno.sh/docs/MCP) for complete tool documentation.

## Quick Install

```bash
# Claude Desktop (default)
gno mcp install

# Claude Code
gno mcp install -t claude-code

# With write tools enabled
gno mcp install --enable-write
```

## Manual Setup

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gno": {
      "command": "gno",
      "args": ["mcp"]
    }
  }
}
```

Config locations:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

### Claude Code

```bash
gno mcp install -t claude-code -s user    # User scope
gno mcp install -t claude-code -s project # Project scope
```

## Check Status

```bash
gno mcp status
```

## Uninstall

```bash
gno mcp uninstall
gno mcp uninstall -t claude-code
```
