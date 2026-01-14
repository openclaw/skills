#!/bin/bash
# Update system packages

# Usage: ./update.sh [--dry-run]

DRY_RUN=false
if [ "$1" = "--dry-run" ]; then
  DRY_RUN=true
  echo "🔍 DRY RUN MODE - No changes will be made"
  echo "=========================================="
  echo ""
fi

echo "🔄 System Update"
echo "=================="
echo ""

# Check for sudo (skip in dry-run mode)
if [ "$DRY_RUN" = false ]; then
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
  # In dry-run mode, we need sudo for read operations
  SUDO="sudo"
fi

# Update package lists
echo "Updating package lists..."
$SUDO apt update

# Show upgradable packages
echo ""
echo "Upgradable packages:"
echo "--------------------"
$SUDO apt list --upgradable 2>/dev/null | grep -v "^Listing" | head -20

# Count packages
COUNT=$($SUDO apt list --upgradable 2>/dev/null | grep -v "^Listing" | wc -l)

if [ "$COUNT" -eq 0 ]; then
  echo ""
  echo "✅ System is up to date!"
  exit 0
fi

echo ""
echo "Found $COUNT upgradable package(s)"
echo ""

# Exit early in dry run mode
if [ "$DRY_RUN" = true ]; then
  echo "🔍 Dry run complete. These packages would be updated."
  echo "   Run without --dry-run to apply updates."
  exit 0
fi

# Ask for confirmation
read -p "Proceed with upgrade? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Upgrade cancelled."
  exit 0
fi

# Perform upgrade
echo ""
echo "Upgrading packages..."
echo "--------------------"
$SUDO apt upgrade -y

echo ""
echo "✅ Update complete!"

# Show if reboot is needed
if [ -f /var/run/reboot-required ]; then
  echo ""
  echo "⚠️  A reboot is required!"
  echo "   Run: ./skill.sh reboot"
else
  echo ""
  echo "✅ No reboot required"
fi