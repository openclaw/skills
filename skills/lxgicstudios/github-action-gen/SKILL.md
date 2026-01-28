---
name: github-action-gen
description: Generate GitHub Actions workflows from plain English. Use when setting up CI.
---

# GitHub Action Generator

Stop copy-pasting workflow YAML from StackOverflow. Describe what you want and get a working GitHub Actions workflow.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-github-action "test and deploy on push to main"
```

## What It Does

- Generates complete GitHub Actions workflow files
- Handles common patterns like test, build, deploy
- Includes caching for faster runs
- Supports multiple deploy targets

## Usage Examples

```bash
# Test and deploy
npx ai-github-action "test and deploy on push to main"

# PR checks
npx ai-github-action "run eslint and prettier on PRs" --install

# Docker workflow
npx ai-github-action "build docker image and push to ECR" -o deploy.yml

# Scheduled job
npx ai-github-action "run database backup every night at 2am"
```

## Best Practices

- **Use secrets** - never hardcode credentials
- **Cache dependencies** - saves minutes per run
- **Fail fast** - run quick checks first
- **Use matrix builds** - test multiple node versions

## When to Use This

- Setting up CI for a new repo
- Adding deployment automation
- Creating custom workflows
- Learning GitHub Actions syntax

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
npx ai-github-action --help
```

## How It Works

Takes your plain English description and generates GitHub Actions YAML with the right triggers, jobs, and steps. The AI knows common patterns and best practices for different workflows.

## License

MIT. Free forever. Use it however you want.
