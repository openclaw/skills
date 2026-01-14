#!/bin/bash
# Pi Optimizations - Safe reversible optimizations

# Usage: ./optimize.sh [--dry-run|--undo]

DRY_RUN=false
UNDO=false

for arg in "$@"; do
  case $arg in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --undo)
      UNDO=true
      shift
      ;;
  esac
done

if [ "$DRY_RUN" = true ]; then
  echo "🔍 DRY RUN MODE - No changes will be made"
  echo "=========================================="
  echo ""
elif [ "$UNDO" = true ]; then
  echo "↩️  UNDO MODE - Reverting optimizations"
  echo "========================================"
  echo ""
fi

echo "⚡ Pi Optimizations"
echo "==================="
echo ""

# Check for sudo
if [ "$DRY_RUN" = false ] && [ "$UNDO" = false ]; then
  if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script requires sudo privileges"
    echo ""
    read -p "Continue with sudo? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      exit 1
    fi
    SUDO="sudo"
  else
    SUDO=""
  fi
else
  SUDO="sudo"
fi

# Show current state
echo "Current State:"
echo "--------------"
echo "  Bluetooth: $(systemctl is-enabled bluetooth.service)"
echo "  ModemManager: $(systemctl is-enabled ModemManager.service)"
echo "  Avahi: $(systemctl is-enabled avahi-daemon.service)"
echo "  Swappiness: $(cat /proc/sys/vm/swappiness)"
echo ""

# RAM savings estimate
RAM_SAVED_MB=0

if [ "$(systemctl is-enabled bluetooth.service)" = "enabled" ]; then
  RAM_SAVED_MB=$((RAM_SAVED_MB + 50))
fi
if [ "$(systemctl is-enabled ModemManager.service)" = "enabled" ]; then
  RAM_SAVED_MB=$((RAM_SAVED_MB + 30))
fi
if [ "$(systemctl is-enabled avahi-daemon.service)" = "enabled" ]; then
  RAM_SAVED_MB=$((RAM_SAVED_MB + 20))
fi

echo "Potential RAM savings: ~${RAM_SAVED_MB}MB"
echo ""

# Exit early in dry-run mode
if [ "$DRY_RUN" = true ]; then
  echo "🔍 Dry run complete. These optimizations would be applied:"
  echo ""
  echo "Changes:"
  if [ "$(systemctl is-enabled bluetooth.service)" = "enabled" ]; then
    echo "  ❌ Disable Bluetooth service"
  fi
  if [ "$(systemctl is-enabled ModemManager.service)" = "enabled" ]; then
    echo "  ❌ Disable ModemManager"
  fi
  if [ "$(systemctl is-enabled avahi-daemon.service)" = "enabled" ]; then
    echo "  ❌ Disable Avahi"
  fi
  echo "  ⚙️  Set swappiness to 10 (current: $(cat /proc/sys/vm/swappiness))"
  echo ""
  echo "Run without --dry-run to apply."
  exit 0
fi

# Undo mode
if [ "$UNDO" = true ]; then
  echo "Reverting optimizations..."
  echo ""

  if [ "$(systemctl is-enabled bluetooth.service)" = "disabled" ]; then
    echo "Enabling Bluetooth..."
    $SUDO systemctl enable bluetooth.service
    echo "✅ Bluetooth enabled"
  fi

  if [ "$(systemctl is-enabled ModemManager.service)" = "disabled" ]; then
    echo "Enabling ModemManager..."
    $SUDO systemctl enable ModemManager.service
    echo "✅ ModemManager enabled"
  fi

  if [ "$(systemctl is-enabled avahi-daemon.service)" = "disabled" ]; then
    echo "Enabling Avahi..."
    $SUDO systemctl enable avahi-daemon.service
    echo "✅ Avahi enabled"
  fi

  echo "Restoring swappiness to 60..."
  $SUDO sysctl vm.swappiness=60
  echo "vm.swappiness=60" | $SUDO tee /etc/sysctl.d/99-swappiness.conf > /dev/null
  echo "✅ Swappiness restored to 60"

  echo ""
  echo "↩️  Undo complete! Restart required for full effect."
  exit 0
fi

# Apply optimizations
echo "Applying optimizations..."
echo ""

# 1. Disable Bluetooth
if [ "$(systemctl is-enabled bluetooth.service)" = "enabled" ]; then
  echo "1. Disabling Bluetooth..."
  $SUDO systemctl disable bluetooth.service
  echo "   ✅ Bluetooth disabled (~50MB RAM saved)"
else
  echo "1. Bluetooth already disabled - skipping"
fi

# 2. Disable ModemManager
if [ "$(systemctl is-enabled ModemManager.service)" = "enabled" ]; then
  echo ""
  echo "2. Disabling ModemManager..."
  $SUDO systemctl disable ModemManager.service
  echo "   ✅ ModemManager disabled (~30MB RAM saved)"
else
  echo ""
  echo "2. ModemManager already disabled - skipping"
fi

# 3. Disable Avahi
if [ "$(systemctl is-enabled avahi-daemon.service)" = "enabled" ]; then
  echo ""
  echo "3. Disabling Avahi..."
  $SUDO systemctl disable avahi-daemon.service
  echo "   ✅ Avahi disabled (~20MB RAM saved)"
else
  echo ""
  echo "3. Avahi already disabled - skipping"
fi

# 4. Set swappiness to 10
echo ""
echo "4. Setting swappiness to 10..."
CURRENT_SWAPPINESS=$(cat /proc/sys/vm/swappiness)
if [ "$CURRENT_SWAPPINESS" -ne 10 ]; then
  $SUDO sysctl vm.swappiness=10
  echo "vm.swappiness=10" | $SUDO tee /etc/sysctl.d/99-swappiness.conf > /dev/null
  echo "   ✅ Swappiness set to 10 (was $CURRENT_SWAPPINESS)"
else
  echo "   Swappiness already 10 - skipping"
fi

# Summary
echo ""
echo "✅ Optimizations applied!"
echo ""
echo "Changes made:"
echo "-------------"
if [ "$(systemctl is-enabled bluetooth.service)" = "disabled" ]; then
  echo "  ❌ Bluetooth disabled"
fi
if [ "$(systemctl is-enabled ModemManager.service)" = "disabled" ]; then
  echo "  ❌ ModemManager disabled"
fi
if [ "$(systemctl is-enabled avahi-daemon.service)" = "disabled" ]; then
  echo "  ❌ Avahi disabled"
fi
echo "  ⚙️  Swappiness set to 10"
echo ""
echo "RAM saved: ~${RAM_SAVED_MB}MB"
echo ""
echo "📝 To undo these changes, run: ./optimize.sh --undo"
echo "🔄 Restart recommended for full effect (run: ./skill.sh reboot)"