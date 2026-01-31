---
name: gitea
description: "Interact with Gitea using the `tea` CLI. Use `tea issues`, `tea pulls`, `tea releases`, and other commands for issues, PRs, releases, and repository management."
---

# Gitea Skill

Use the `tea` CLI to interact with Gitea servers. Use `--repo owner/repo` when not in a git directory, or `--login instance.com` to specify a Gitea instance.

## Setup

Add a login once to get started:
```bash
tea login add
```

Check current logged in user:
```bash
tea whoami
```

## Repositories

List repositories you have access to:
```bash
tea repos list
```

Create a new repository:
```bash
tea repos create --name my-repo --description "My project" --init
```

Create a private repository:
```bash
tea repos create --name my-repo --private --init
```

Fork a repository:
```bash
tea repos fork owner/repo
```

Delete a repository:
```bash
tea repos delete --name my-repo --owner myuser --force
```

## Pull Requests

List open pull requests:
```bash
tea pulls --repo owner/repo
```

View a specific PR:
```bash
tea pr 55 --repo owner/repo
```

Checkout a PR locally:
```bash
tea pr checkout 55
```

Create a new PR:
```bash
tea pr create --title "Feature title" --description "Description"
```

## Issues

List open issues:
```bash
tea issues --repo owner/repo
```

View a specific issue:
```bash
tea issue 189 --repo owner/repo
```

Create a new issue:
```bash
tea issue create --title "Bug title" --body "Description"
```

View issues for a milestone:
```bash
tea milestone issues 0.7.0
```

## Comments

Add a comment to an issue or PR:
```bash
tea comment 189 --body "Your comment here"
```

## Releases

List releases:
```bash
tea releases --repo owner/repo
```

Create a new release:
```bash
tea release create --tag v1.0.0 --title "Release 1.0.0"
```

## Actions (CI/CD)

List repository action secrets:
```bash
tea actions secrets list
```

Create a new secret:
```bash
tea actions secrets create API_KEY
```

List action variables:
```bash
tea actions variables list
```

Set an action variable:
```bash
tea actions variables set API_URL https://api.example.com
```

## Webhooks

List repository webhooks:
```bash
tea webhooks list
```

List organization webhooks:
```bash
tea webhooks list --org myorg
```

Create a webhook:
```bash
tea webhooks create https://example.com/hook --events push,pull_request
```

## Other Entities

List branches:
```bash
tea branches --repo owner/repo
```

List labels:
```bash
tea labels --repo owner/repo
```

List milestones:
```bash
tea milestones --repo owner/repo
```

List organizations:
```bash
tea organizations
```

Show repository details:
```bash
tea repo --repo owner/repo
```

## Helpers

Open something in browser:
```bash
tea open 189                 # open issue/PR 189
tea open milestones          # open milestones page
```

Clone a repository:
```bash
tea clone owner/repo
```

Show notifications:
```bash
tea notifications --mine
```

## Output Formats

Use `--output` or `-o` to control output format:
```bash
tea issues --output simple   # simple text output
tea issues --output csv      # CSV format
tea issues --output yaml     # YAML format
```
