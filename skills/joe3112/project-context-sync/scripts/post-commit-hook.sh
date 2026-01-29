#!/bin/bash
# project-context-sync: Post-commit hook
# Installed by project-context-sync skill

SKILL_DIR="__SKILL_DIR__"
REPO_ROOT="__REPO_ROOT__"

# Run update in background to not block commit
"$SKILL_DIR/scripts/update-context.sh" "$REPO_ROOT" &
