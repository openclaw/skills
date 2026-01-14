#!/bin/bash
# Raspberry Pi Administration Skill
# Usage: ./skill.sh [overview|network|tailscale|resources|storage|services|hardware|all|update|clean|reboot|restart-gateway|optimize]
#        Any maintenance command can be run with --dry-run flag
#        Example: ./skill.sh update --dry-run

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Pass --dry-run to maintenance commands if provided
DRY_RUN=""
if [ "$2" = "--dry-run" ]; then
  DRY_RUN="--dry-run"
fi

case "${1:-overview}" in
  overview)
    bash "$SCRIPT_DIR/overview.sh"
    ;;
  network)
    bash "$SCRIPT_DIR/network.sh"
    ;;
  tailscale)
    bash "$SCRIPT_DIR/tailscale.sh"
    ;;
  resources)
    bash "$SCRIPT_DIR/resources.sh"
    ;;
  storage)
    bash "$SCRIPT_DIR/storage.sh"
    ;;
  services)
    bash "$SCRIPT_DIR/services.sh"
    ;;
  hardware)
    bash "$SCRIPT_DIR/hardware.sh"
    ;;
  update)
    bash "$SCRIPT_DIR/update.sh" $DRY_RUN
    ;;
  clean)
    bash "$SCRIPT_DIR/clean.sh" $DRY_RUN
    ;;
  reboot)
    bash "$SCRIPT_DIR/reboot.sh" $DRY_RUN
    ;;
  restart-gateway)
    bash "$SCRIPT_DIR/restart-gateway.sh" $DRY_RUN
    ;;
  optimize)
    bash "$SCRIPT_DIR/optimize.sh" "$@"
    ;;
  all)
    echo "=== COMPLETE SYSTEM INFO ==="
    echo ""
    echo "--- OVERVIEW ---"
    bash "$SCRIPT_DIR/overview.sh"
    echo ""
    echo "--- NETWORK ---"
    bash "$SCRIPT_DIR/network.sh"
    echo ""
    echo "--- TAILSCALE ---"
    bash "$SCRIPT_DIR/tailscale.sh"
    echo ""
    echo "--- RESOURCES ---"
    bash "$SCRIPT_DIR/resources.sh"
    echo ""
    echo "--- STORAGE ---"
    bash "$SCRIPT_DIR/storage.sh"
    echo ""
    echo "--- SERVICES ---"
    bash "$SCRIPT_DIR/services.sh"
    echo ""
    echo "--- HARDWARE ---"
    bash "$SCRIPT_DIR/hardware.sh"
    ;;
  *)
    echo "Usage: $0 [overview|network|tailscale|resources|storage|services|hardware|all]"
    exit 1
    ;;
esac