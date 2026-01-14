#!/bin/bash
# Clean system - remove unused packages, old logs, docker artifacts

# Usage: ./clean.sh [--dry-run]

DRY_RUN=false
if [ "$1" = "--dry-run" ]; then
  DRY_RUN=true
  echo "🔍 DRY RUN MODE - No changes will be made"
  echo "=========================================="
  echo ""
fi

echo "🧹 System Cleanup"
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

# Show space before cleanup
SPACE_BEFORE=$(df / | awk 'NR==2 {print $4}')
echo "Disk space before: $(df -h / | awk 'NR==2 {print $4}') available"
echo ""

# Remove unused packages
echo "1. Unused packages:"
if [ "$DRY_RUN" = true ]; then
  REMOVABLE=$($SUDO apt-get autoremove --dry-run 2>/dev/null | grep "^Remv" | awk '{print $2}' | wc -l)
  echo "   Would remove: $REMOVABLE packages"
  echo "   (Use --dry-run to see package list)"
else
  echo "   Removing unused packages..."
  $SUDO apt autoremove -y
fi

# Clean package cache
echo ""
echo "2. Package cache:"
if [ "$DRY_RUN" = true ]; then
  CACHE_SIZE=$($SUDO du -sh /var/cache/apt/archives 2>/dev/null | awk '{print $1}')
  echo "   Would clear: $CACHE_SIZE from cache"
else
  echo "   Cleaning package cache..."
  $SUDO apt autoclean
fi

# Clean old journal logs (keep 7 days)
echo ""
echo "3. System logs (keeping 7 days):"
if [ "$DRY_RUN" = true ]; then
  LOG_SIZE=$(journalctl --disk-usage 2>/dev/null | awk '{print $1}')
  echo "   Current journal size: $LOG_SIZE"
  echo "   Would vacuum logs older than 7 days"
else
  echo "   Cleaning old system logs..."
  $SUDO journalctl --vacuum-time=7d
fi

# Clean Docker if installed
if command -v docker &> /dev/null; then
  echo ""
  echo "4. Docker artifacts:"
  STOPPED=$(docker ps -a -q | wc -l)
  DANGLING=$(docker images -f "dangling=true" -q | wc -l)
  VOLUMES=$(docker volume ls -qf dangling=true 2>/dev/null | wc -l)
  
  echo "   Stopped containers: $STOPPED"
  echo "   Dangling images: $DANGLING"
  echo "   Unused volumes: $VOLUMES"
  
  if [ "$DRY_RUN" = false ]; then
    read -p "   Clean Docker? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      docker system prune -f
    fi
  else
    echo "   Would prune: stopped containers, dangling images, unused volumes"
  fi
fi

# Clean APT cache more aggressively
echo ""
echo "5. Deep APT cache clean:"
if [ "$DRY_RUN" = false ]; then
  $SUDO apt-get clean
else
  DEEP_CACHE_SIZE=$($SUDO du -sh /var/cache/apt/archives 2>/dev/null | awk '{print $1}')
  echo "   Would deep clean: additional $DEEP_CACHE_SIZE"
fi

# Remove partial packages
echo ""
echo "6. Partial packages:"
if [ "$DRY_RUN" = false ]; then
  $SUDO apt-get autoremove --purge -y
else
  PARTIAL=$($SUDO apt-get --dry-run autoremove --purge 2>/dev/null | grep "^Remv" | wc -l)
  echo "   Would remove partial packages: $PARTIAL"
fi

# Remove old kernels (keep current + 1)
if [ -f /usr/bin/linux-purge ]; then
  echo ""
  echo "7. Old kernel packages:"
  if [ "$DRY_RUN" = false ]; then
    echo "   Removing old kernel packages..."
    $SUDO linux-purge
  else
    OLD_KERNELS=$($SUDO dpkg -l | grep -c "linux-image-.*-raspi")
    echo "   Would remove old kernels (keeping current + 1)"
  fi
fi

# Dry run exit
if [ "$DRY_RUN" = true ]; then
  echo ""
  echo "🔍 Dry run complete. Run without --dry-run to apply cleanup."
  exit 0
fi

# Show space after cleanup
SPACE_AFTER=$(df / | awk 'NR==2 {print $4}')
SPACE_SAVED=$((SPACE_AFTER - SPACE_BEFORE))
SPACE_SAVED_MB=$((SPACE_SAVED / 1024))

echo ""
echo "Disk space after: $(df -h / | awk 'NR==2 {print $4}') available"

if [ $SPACE_SAVED -gt 0 ]; then
  echo "✅ Saved: ${SPACE_SAVED_MB}MB"
else
  echo "ℹ️  No significant space saved"
fi

echo ""
echo "✅ Cleanup complete!"