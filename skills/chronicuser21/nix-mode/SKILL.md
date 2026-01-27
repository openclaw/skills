---
name: nix-mode
description: Handle Clawdbot operations in Nix mode (configuration management, environment detection).
metadata: {"clawdbot":{"emoji":"❄️","requires":{"bins":["nix","bash"],"envs":["CLAWDBOT_NIX_MODE"]},"install":[]}}
---

# Clawdbot Nix Mode Skill

This skill handles Clawdbot operations specifically when running in Nix mode.

## Nix Mode Specific Features

### Environment Detection
- Detect when `CLAWDBOT_NIX_MODE=1` is set
- Identify Nix-managed configuration paths
- Recognize Nix-specific error messages and behaviors

### Configuration Management
- Understand that auto-install flows are disabled in Nix mode
- Guide users to proper Nix package management
- Explain why certain self-modification features are unavailable

### Path Handling
- Recognize Nix store paths
- Understand the difference between config and state directories
- Handle `CLAWDBOT_CONFIG_PATH` and `CLAWDBOT_STATE_DIR` appropriately

### Troubleshooting
- Identify Nix-specific remediation messages
- Guide users to proper dependency management via Nix
- Explain the read-only Nix mode banner behavior

## Usage Guidelines

When operating in Nix mode:
1. Do not attempt to auto-install dependencies
2. Direct users to Nix package management instead
3. Respect the immutable nature of Nix installations
4. Advise on proper configuration practices for Nix environments