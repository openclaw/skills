# 🔧 Mechanic — Vehicle Maintenance Tracker

A [Clawdbot](https://github.com/clawdbot/clawdbot) skill that tracks mileage and service intervals for any vehicle — trucks, cars, motorcycles, dirt bikes, ATVs, RVs, boats, and more.

## Features

- **Multi-vehicle tracking** — Track any number of vehicles with independent schedules
- **Manufacturer service schedules** — Researches and builds interval-based maintenance schedules for your specific year/make/model
- **Cost estimates** — DIY, shop, and dealer pricing for every service item
- **NHTSA recall monitoring** — Checks for open recalls by VIN (free API)
- **Fuel / MPG tracking** — Log fill-ups, calculate trends, detect anomalies that signal mechanical issues
- **Warranty tracking** — Factory, extended, and parts warranties with expiration alerts
- **Pre-trip & seasonal checklists** — Vehicle-specific checks based on destination and weather
- **Mileage projection** — Predicts when services will be due based on driving patterns
- **Service provider history** — Track which shops did what work, satisfaction ratings
- **Tax deduction integration** — Flags deductible maintenance on business-use vehicles
- **Emergency info cards** — VIN, insurance, tire specs, fluid specs, tow ratings at a glance
- **Cost per mile** — Maintenance + fuel operating cost analysis
- **Configurable check-in frequency** — Per-vehicle: weekly, biweekly, monthly, or quarterly
- **Severe duty detection** — Identifies towing, off-road, and extreme climate conditions for shorter intervals
- **Environmental awareness** — Tailors advice based on user location (heat, cold, dust, coastal)

## Supported Vehicle Types

| Type | Tracks | Special Items |
|------|--------|---------------|
| Cars & Trucks | Miles | Full automotive maintenance |
| Motorcycles | Miles | Chain, valve clearance, fork oil |
| Dirt Bikes | Hours + rides | Air filter every ride, frequent oil |
| ATVs / UTVs | Hours + miles | CV boots, belt, winch |
| RVs / Trailers | Miles + months | Roof, seals, slides, bearings, generator, seasonal |
| Boats | Hours | Impeller, lower unit, zincs, winterization |

## Installation

### Clawdbot CLI
```bash
clawdhub install mechanic
```

### Manual
Copy `SKILL.md` into your Clawdbot skills directory:
```
<workspace>/skills/mechanic/SKILL.md
```

## Setup

On first use, the skill will:
1. Ask what vehicles you want to track
2. Ask how often you want mileage check-ins (per vehicle)
3. Research manufacturer maintenance schedules for each vehicle
4. Build schedule files with service intervals and cost estimates
5. Set up a recurring cron job to check in

All user data is stored in `<workspace>/data/mechanic/` — separate from the skill itself.

## Data Structure

```
skills/mechanic/
  SKILL.md              ← Skill logic (this repo)

data/mechanic/
  state.json            ← All vehicles, mileage, history, service records
  f350-schedule.json    ← Per-vehicle service schedule
  rv-schedule.json      ← Another vehicle schedule
  ...
```

## Usage Examples

- "What maintenance does my truck need?"
- "When's my next oil change?"
- "I just hit 70,000 miles"
- "Got my oil changed at 65k, cost $180 at Jiffy Lube"
- "Any recalls on my truck?"
- "I filled up — 25 gallons at $3.89"
- "I'm heading on a road trip next week"
- "What's my cost per mile?"
- "Is my powertrain warranty still active?"
- "What's my VIN?"

## Requirements

- [Clawdbot](https://github.com/clawdbot/clawdbot) v1.0+
- No API keys required (NHTSA recall API is free and public)

## License

MIT
