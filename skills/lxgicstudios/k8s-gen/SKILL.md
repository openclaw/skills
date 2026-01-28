---
name: k8s-gen
description: Generate Kubernetes manifests from docker-compose or plain English. Use when deploying apps to K8s.
---

# Kubernetes Manifest Generator

Stop writing YAML by hand. This tool converts your docker-compose files or plain descriptions into production ready Kubernetes manifests. Deployments, Services, ConfigMaps, the whole thing.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-k8s "nginx with 3 replicas, exposed on port 80"
```

## What It Does

- Converts docker-compose.yml to Kubernetes manifests automatically
- Generates Deployments, Services, ConfigMaps, and Secrets
- Creates proper resource limits and health checks
- Outputs clean, production ready YAML you can kubectl apply
- Handles multi-service architectures with proper networking

## Usage Examples

```bash
# Generate from a description
npx ai-k8s "postgres database with persistent volume"

# Convert docker-compose to K8s
npx ai-k8s --compose docker-compose.yml

# Full app stack
npx ai-k8s "node app with redis cache and postgres db, 3 replicas each"
```

## Best Practices

- **Start simple** - Generate one service first, validate it works, then add complexity
- **Review resource limits** - The AI sets reasonable defaults, but adjust for your workload
- **Use namespaces** - Add --namespace flag to keep your deployments organized
- **Version your manifests** - Commit generated YAML to git, treat it as code

## When to Use This

- You know Docker but K8s YAML feels overwhelming
- Migrating docker-compose setups to Kubernetes
- Prototyping new deployments quickly without YAML boilerplate
- Learning K8s concepts through generated examples

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgic.dev

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended.

```bash
npx ai-k8s --help
```

## How It Works

The tool analyzes your docker-compose file or description, understands the services and their relationships, then generates idiomatic Kubernetes manifests. It maps Docker concepts to K8s equivalents like volumes to PersistentVolumeClaims and ports to Services.

## License

MIT. Free forever. Use it however you want.
