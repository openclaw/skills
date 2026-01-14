---
name: pi-admin
description: Raspberry Pi system administration. Monitor resources, manage services, perform updates and maintenance.
metadata: {"clawdis":{"emoji":"🥧","requires":{"bins":[]}}}
---

# Raspberry Pi Administration

Complete system monitoring and introspection for the Raspberry Pi host. Access network details, system resources, storage, services, and more.

## When to Use
- Checking Pi network configuration (IP, Tailscale)
- Monitoring system resources (CPU, memory, storage)
- Viewing running services and their status
- Checking temperature and hardware info
- Troubleshooting system issues
- Getting system overview for debugging

## Usage

```bash
# Information Commands
cd /home/srose/clawd/skills/pi-admin
./skill.sh overview
./skill.sh network
./skill.sh tailscale
./skill.sh resources
./skill.sh storage
./skill.sh services
./skill.sh hardware

# Maintenance Commands
./skill.sh update       # Update system packages
./skill.sh clean        # Clean unused packages, logs, Docker
./skill.sh reboot       # Reboot with countdown
./skill.sh restart-gateway  # Restart the Clawdis Gateway

# Complete system info
./skill.sh all
```

## Tools Available

| Tool | Description |
|------|-------------|
| `overview` | Quick system summary |
| `network` | IP addresses, hostname, network interfaces |
| `tailscale` | Tailscale status, IP, peers |
| `resources` | CPU, memory, temperature |
| `storage` | Disk usage, mount points |
| `services` | Running services, Gateway status |
| `hardware` | CPU info, Raspberry Pi model, GPU |
| `all` | Complete detailed dump |

## Examples

```bash
# Quick system check
./skill.sh overview

# Debug network issues
./skill.sh network && ./skill.sh tailscale

# Check if Gateway is running
./skill.sh services | grep gateway

# Monitor disk space
./skill.sh storage
```

## Information Collected

**Network:**
- Hostname
- Local IP addresses (eth0, wlan0)
- Network interface details
- DNS configuration

**Tailscale:**
- Status (running/stopped)
- Tailscale IP
- Connected peers
- Exit node status

**Resources:**
- CPU usage
- Memory usage (used/free/total)
- CPU temperature
- Uptime

**Storage:**
- Disk usage by mount point
- Inode usage
- Free space

**Services:**
- Gateway service status
- Docker containers
- Systemd services
- Port listeners

**Hardware:**
- CPU model and cores
- Raspberry Pi model
- GPU memory
- Total RAM

## Maintenance Commands

### `update`
Update system packages via apt:
- Updates package lists
- Shows upgradable packages
- Requires confirmation before upgrading
- Reports if reboot is needed
- **Dry run:** `./skill.sh update --dry-run` shows what would be updated

### `clean`
Clean up system to free disk space:
- Removes unused packages (autoremove)
- Clears package cache
- Cleans old journal logs (keeps 7 days)
- Optionally cleans Docker artifacts
- Shows space saved
- **Dry run:** `./skill.sh clean --dry-run` shows what would be cleaned

### `reboot`
Graceful system reboot:
- 10-second countdown
- Ctrl+C to cancel
- Uses systemctl reboot
- **Dry run:** `./skill.sh reboot --dry-run` shows countdown without rebooting

### `restart-gateway`
Restart the Clawdis Gateway service:
- Stops all running gateway processes
- Starts fresh gateway on port 18789
- Confirms port is listening
- Shows access URLs
- **Dry run:** `./skill.sh restart-gateway --dry-run` shows what would happen

### `optimize`
Apply safe system optimizations:
- Disable Bluetooth service (~50MB RAM saved)
- Disable ModemManager (~30MB RAM saved)
- Disable Avahi/Zeroconf (~20MB RAM saved)
- Set swappiness to 10 (better RAM utilization)
- **Dry run:** `./skill.sh optimize --dry-run` shows what would change
- **Undo:** `./skill.sh optimize --undo` reverts all changes

**Total RAM savings:** ~100MB
**Reversibility:** Yes, use `--undo` flag to revert

**Note:** All maintenance commands require sudo and ask for confirmation before making changes. Use `--dry-run` flag to preview changes without applying them.