#!/bin/bash
# Fast SQLite-based email search (~50ms vs minutes with AppleScript)
# ⚠️  WARNING: REQUIRES MAIL.APP TO BE QUIT - direct database access can corrupt Mail's index
# Usage: mail-fast-search.sh <query> [limit]

set -e

QUERY="${1:?Usage: mail-fast-search.sh <query> [limit]}"
LIMIT="${2:-20}"

# CRITICAL SAFETY CHECK: Mail.app MUST be quit to avoid WAL locking conflicts
# Direct SQLite access while Mail.app is running can corrupt the Envelope Index database
if pgrep -x "Mail" >/dev/null 2>&1; then
  echo "╔══════════════════════════════════════════════════════════════════════════════╗" >&2
  echo "║  ⛔ ERROR: Mail.app is running - CANNOT safely access database              ║" >&2
  echo "║                                                                              ║" >&2
  echo "║  Direct SQLite access while Mail is running can CORRUPT the database.       ║" >&2
  echo "║                                                                              ║" >&2
  echo "║  Options:                                                                    ║" >&2
  echo "║    1. Quit Mail.app first, then retry this command                          ║" >&2
  echo "║    2. Use mail-search.sh instead (slower but safe while Mail is running)    ║" >&2
  echo "╚══════════════════════════════════════════════════════════════════════════════╝" >&2
  exit 1
fi

# Find the Mail envelope index database
# Note: macOS has two databases - "Envelope Index" (has messages table) and "Envelope Index-1" (different schema)
# We need the one with the messages table
DB_PATH=""
for version in 11 10 9; do
  CANDIDATE="$HOME/Library/Mail/V${version}/MailData/Envelope Index"
  if [[ -f "$CANDIDATE" ]]; then
    # Verify this DB has the messages table
    if sqlite3 "$CANDIDATE" "SELECT 1 FROM messages LIMIT 1" &>/dev/null; then
      DB_PATH="$CANDIDATE"
      break
    fi
  fi
done

if [[ -z "$DB_PATH" ]]; then
  echo "Error: Mail database not found or schema incompatible" >&2
  echo "Note: This can happen when Mail.app is syncing or on newer macOS versions" >&2
  echo "Try: mail-search.sh (slower AppleScript method)" >&2
  exit 1
fi

# Search by subject, sender address, or sender name
sqlite3 -header -separator ' | ' "$DB_PATH" "
SELECT 
  m.ROWID as id,
  CASE WHEN (m.flags & 1) = 0 THEN '●' ELSE ' ' END as unread,
  datetime(m.date_sent, 'unixepoch', 'localtime') as date,
  COALESCE(a.comment, a.address, 'Unknown') as sender,
  COALESCE(s.subject, '(no subject)') as subject
FROM messages m
LEFT JOIN subjects s ON m.subject = s.ROWID
LEFT JOIN addresses a ON m.sender = a.ROWID
WHERE s.subject LIKE '%${QUERY}%' 
   OR a.address LIKE '%${QUERY}%'
   OR a.comment LIKE '%${QUERY}%'
ORDER BY m.date_sent DESC
LIMIT ${LIMIT};
"
