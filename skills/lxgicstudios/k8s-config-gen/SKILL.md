---
name: k8s-gen
description: Generate Kubernetes manifests from docker-compose or descriptions. Use when deploying to K8s.
---

# K8s Generator

Translating docker-compose to Kubernetes manifests is tedious YAML shuffling. Feed in your compose file and get proper K8s manifests back.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-k8s docker-compose.yml
```

## What It Does

- Converts docker-compose to Kubernetes manifests
- Generates from plain English descriptions
- Creates Deployments, Services, ConfigMaps
- Handles secrets and persistent volumes

## Usage Examples

```bash
# From docker-compose
npx ai-k8s docker-compose.yml --namespace production

# From description
npx ai-k8s "3 replicas of a node app with redis and postgres"

# Save output
npx ai-k8s docker-compose.yml -o k8s-manifests.yml
```

## Best Practices

- **Use namespaces** - organize your resources
- **Set resource limits** - prevent runaway pods
- **Add health checks** - liveness and readiness probes
- **Use secrets properly** - don't hardcode credentials

## When to Use This

- Migrating from docker-compose to Kubernetes
- Setting up new K8s deployments
- Learning Kubernetes manifest structure
- Quick prototyping before fine-tuning

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgicstudios.com

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended. Needs OPENAI_API_KEY environment variable.

```bash
npx ai-k8s --help
```

## How It Works

Parses your docker-compose.yml or description, understands the services and their relationships, then generates equivalent Kubernetes resources with proper configuration.

## License

MIT. Free forever. Use it however you want.
