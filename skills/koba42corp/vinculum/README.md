# Vinculum

*Shared consciousness for Clawdbot instances.*

> "The Vinculum is the processing device at the core of every Borg vessel. It interconnects the minds of all the drones." — Seven of Nine

Link multiple Clawdbot instances into a collective using [Gun.js](https://gun.eco) P2P sync.

## Features

- 🔗 **Real-time link** — Changes propagate instantly between drones
- 🌐 **Local network** — Works across machines on the same LAN
- 🔐 **Encrypted** — All shared data encrypted
- 🤖 **Individual identity** — Each drone keeps its own SOUL.md
- 📡 **Drone discovery** — Automatic multicast discovery

## Quick Start

```bash
# Install dependencies
npm install

# Start the Vinculum relay
npm run relay:start

# Check status
npm run cli -- status
```

## CLI Usage

```bash
# Via npm scripts
npm run cli -- status
npm run cli -- relay start
npm run cli -- share "Hello collective!"

# Or directly
node scripts/cli.js status
node scripts/cli.js relay start
```

## Commands

| Command | Description |
|---------|-------------|
| `relay start` | Start Vinculum relay |
| `relay stop` | Stop relay |
| `relay status` | Check relay health |
| `init` | Create new collective |
| `join <code>` | Join existing collective |
| `status` | Show link status |
| `drones` | List connected drones |
| `share "text"` | Share a thought |
| `config` | View/set configuration |

See `SKILL.md` for full documentation.

## Architecture

```
┌─────────────┐     ┌─────────────┐
│   Drone A   │     │   Drone B   │
└──────┬──────┘     └──────┬──────┘
       │   Subspace Link   │
       ▼                   ▼
  ┌────────────────────────────┐
  │      Vinculum Relay        │
  │    ws://localhost:8765     │
  └────────────────────────────┘
```

## Files

```
vinculum/
├── scripts/
│   ├── cli.js           # CLI entry point
│   ├── gun-loader.js    # Gun.js loader
│   ├── gun-adapter.js   # Collective adapter
│   ├── relay-simple.js  # Vinculum relay daemon
│   ├── index.js         # Skill main module
│   ├── commands/        # CLI command handlers
│   └── utils/           # Helpers
├── config/
│   └── defaults.yaml    # Default configuration
├── tests/
│   └── *.js             # Test suite
├── SKILL.md             # Clawdbot skill docs
└── README.md            # This file
```

## License

MIT

---

*Resistance is futile.*
