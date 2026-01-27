---
name: aws-infra
description: Chat-based AWS infrastructure assistance using AWS CLI and console context. Use for querying, auditing, and monitoring AWS resources (EC2, S3, IAM, Lambda, ECS/EKS, RDS, CloudWatch, billing, etc.), and for proposing safe changes with explicit confirmation before any write/destructive action.
---

# AWS Infra

## Overview
Use the local AWS CLI to answer questions about AWS resources. Default to read‑only queries. Only propose or run write/destructive actions after explicit user confirmation.

## Quick Start
1. Determine profile/region from environment or `~/.aws/config`.
2. Start with identity:
   - `aws sts get-caller-identity`
3. Use read‑only service commands to answer the question.
4. If the user asks for changes, outline the exact command and ask for confirmation before running.

## Safety Rules (must follow)
- Treat all actions as **read‑only** unless the user explicitly requests a change **and** confirms it.
- For any potentially destructive change (delete/terminate/destroy/modify/scale/billing/IAM credentials), require a confirmation step.
- Prefer `--dry-run` when available and show the plan before execution.
- Never reveal or log secrets (access keys, session tokens).

## Task Guide (common requests)
- **Inventory / list**: use `list`/`describe`/`get` commands.
- **Health / errors**: use CloudWatch metrics/logs queries.
- **Security checks**: IAM, S3 public access, SG exposure, KMS key usage.
- **Costs**: Cost Explorer / billing queries (read‑only).
- **Changes**: show exact CLI command and require confirmation.

## Region & Profile Handling
- If the user specifies a region/profile, honor it.
- Otherwise use `AWS_PROFILE` / `AWS_REGION` if set, then fall back to `~/.aws/config`.
- When results are region‑scoped, state the region used.

## References
See `references/aws-cli-queries.md` for common command patterns.

## Assets
- `assets/icon.svg` — custom icon (dark cloud + terminal prompt)
