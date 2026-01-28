---
name: terraform-gen
description: Generate Terraform infrastructure configs. Use when provisioning cloud resources.
---

# Terraform Generator

Terraform syntax is verbose. Describe your infrastructure and get proper .tf files.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-terraform "3 EC2 instances behind load balancer"
```

## What It Does

- Generates Terraform configuration
- Supports AWS, GCP, Azure
- Includes variables and outputs
- Proper resource dependencies

## Usage Examples

```bash
# AWS setup
npx ai-terraform "3 EC2 instances behind load balancer"

# Database
npx ai-terraform "RDS PostgreSQL with read replica"

# Kubernetes
npx ai-terraform "EKS cluster with 3 node groups"
```

## Best Practices

- **Use modules** - reusable infrastructure
- **State in S3** - not local
- **Use variables** - no hardcoded values
- **Plan before apply** - always review changes

## When to Use This

- Starting new infrastructure
- Learning Terraform syntax
- Quick prototyping
- Generating baseline configs

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
npx ai-terraform --help
```

## How It Works

Takes your infrastructure description and generates Terraform HCL code with proper resources, variables, and outputs. Understands cloud provider APIs.

## License

MIT. Free forever. Use it however you want.
