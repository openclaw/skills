---
name: socket-gen
description: Generate WebSocket handlers with Socket.io. Use when building real-time features.
---

# Socket Generator

WebSocket code gets messy fast. Describe your real-time feature and get clean Socket.io handlers.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-socket "real-time chat with rooms"
```

## What It Does

- Generates Socket.io server and client code
- Handles rooms and namespaces
- Includes authentication patterns
- TypeScript types included

## Usage Examples

```bash
# Chat room
npx ai-socket "real-time chat with rooms"

# Live updates
npx ai-socket "live dashboard with data updates"

# Collaborative editing
npx ai-socket "collaborative document editing"
```

## Best Practices

- **Handle reconnection** - connections drop
- **Validate on server** - don't trust clients
- **Use rooms wisely** - don't broadcast everything
- **Clean up listeners** - prevent memory leaks

## When to Use This

- Adding real-time features
- Building chat or notifications
- Live collaboration tools
- Learning Socket.io patterns

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgic.dev

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended. Needs OPENAI_API_KEY environment variable.

```bash
npx ai-socket --help
```

## How It Works

Takes your feature description and generates Socket.io server handlers and client code. Includes event definitions, room management, and TypeScript types.

## License

MIT. Free forever. Use it however you want.
