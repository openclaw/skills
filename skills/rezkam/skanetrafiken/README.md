# Skånetrafiken Trip Planner Skill

Plan public transport journeys in Skåne, Sweden with real-time information.

An [Agent Skills](https://agentskills.io) compatible skill for AI agents.

## Installation

### Clawdhub

Install from [clawdhub.com/rezkam/skanetrafiken](https://clawdhub.com/rezkam/skanetrafiken)

### Claude Code

```bash
git clone https://github.com/rezkam/skanetrafiken.git ~/.claude/skills/skanetrafiken
```

### Clawdbot

```bash
git clone https://github.com/rezkam/skanetrafiken.git ~/clawdbot/skills/skanetrafiken
```

## Requirements

- `curl` - HTTP requests
- `jq` - JSON processing

## Usage

```bash
./trip.sh <from> <to> [datetime] [mode]
```

## Quick Examples

```bash
./trip.sh "Malmö C" "Lund C"
./trip.sh "Kalendegatan 12, Malmö" "Emporia" "09:00"
./trip.sh "Malmö C" "København H" "tomorrow 18:00" arrive
```

## Query Formatting (Important)

| Location Type | Correct | Wrong |
|--------------|---------|-------|
| Landmarks/POIs | `"Emporia"` | `"Emporia, Malmö"` |
| Street addresses | `"Storgatan 10, Malmö"` | `"Storgatan 10"` |
| Central stations | `"Malmö C"` | `"Malmö"` |

**Key rule**: Never append city names to landmarks or POIs - it returns wrong locations.

## Features

- Single-call trip planning
- Real-time delay information
- Three modes: travel now, depart at, arrive by
- Platform/track information
- Disruption alerts
- Cross-border Copenhagen support

## Documentation

See [SKILL.md](SKILL.md) for complete usage guide and examples.

## License

MIT
