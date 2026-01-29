---
name: adr-gen
description: Generate Architecture Decision Records with AI. Use when documenting technical decisions.
---

# ADR Gen

"Why did we use Redis instead of Memcached?" Six months later, nobody remembers. This tool generates Architecture Decision Records from your context. Captures the decision, the alternatives considered, and the reasoning. Future you will thank present you.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-adr "We chose PostgreSQL over MongoDB for our user data"
```

## What It Does

- Generates properly formatted ADR documents
- Documents the context and problem being solved
- Lists alternatives that were considered
- Explains the decision and its reasoning
- Notes consequences and trade-offs

## Usage Examples

```bash
# Generate an ADR from a decision
npx ai-adr "Switching from REST to GraphQL for our public API"

# Include context about your constraints
npx ai-adr "Using Kafka for event streaming" --context "High throughput, multi-consumer"

# Output to your docs folder
npx ai-adr "Adopting TypeScript" --output docs/adr/001-typescript.md
```

## Best Practices

- **Write ADRs when you make decisions** - Not six months later when you forgot why
- **Include the alternatives** - What else did you consider? Why didn't you pick those?
- **Be honest about trade-offs** - Every decision has downsides. Document them.
- **Number your ADRs** - 001-database-choice.md, 002-auth-provider.md, etc.

## When to Use This

- Making a significant technical decision
- Onboarding new team members who ask "why did we..."
- Preparing for architecture reviews
- Building a knowledge base of your technical choices

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgicstudios.com

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended.

```bash
npx ai-adr --help
```

## How It Works

The tool takes your decision statement, researches common alternatives and trade-offs for that technology choice, then generates a structured ADR document following the standard format: Title, Status, Context, Decision, Consequences.

## License

MIT. Free forever. Use it however you want.
