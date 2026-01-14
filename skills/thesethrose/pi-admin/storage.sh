#!/bin/bash
# Storage and disk usage

echo "💾 Storage Information"
echo "======================="
echo ""

# Disk usage by mount point
echo "Disk Usage:"
echo "-----------"
df -h | grep -E "^/dev" | awk '{
  printf "  %s\n", $6
  printf "    Device: %s\n", $1
  printf "    Total: %s\n", $2
  printf "    Used:  %s (%s)\n", $3, $5
  printf "    Free:  %s\n", $4
  printf "    Type:  %s\n\n", $7
}'

# Inode usage
echo "Inode Usage:"
echo "------------"
df -i | grep -E "^/dev" | awk '{
  if ($5 != "0%") {
    printf "  %s: %s used (%s)\n", $6, $3, $5
  }
}'
echo ""

# Mount points
echo "Mount Points:"
echo "-------------"
mount | grep -E "^/dev" | awk '{
  printf "  %s mounted on %s (%s)\n", $1, $3, $5
}'

# Check for large directories
echo ""
echo "Top 5 Largest Directories in /home:"
echo "------------------------------------"
du -sh /home/*/ 2>/dev/null | sort -hr | head -5 | while read size dir; do
  dir_name=$(basename "$dir")
  printf "  %-20s %s\n" "$dir_name:" "$size"
done