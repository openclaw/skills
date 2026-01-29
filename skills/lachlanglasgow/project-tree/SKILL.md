---
name: project-tree
description: Generate a visual directory tree of the ~/projects folder and update MEMORY.md with the result. Use when the user wants to view, update, or generate a project tree structure, or when they mention "project tree", "tree view", "folder structure", or "show me my projects".
---

# Project Tree

## Overview

Generate a visual tree structure of the ~/projects directory and automatically update MEMORY.md with the current project organization. The tree shows folders and .md files only, with smart grouping for consecutive numbered items.

## Usage

Run the tree generation script:

```bash
node ~/clawd/skills/project-tree/scripts/project-tree.js
```

Or use the convenience wrapper:

```bash
~/clawd/scripts/update-tree
```

## Features

- **Folder-only + .md files**: Only displays directories and markdown files, hiding code files and dependencies
- **Smart grouping**: Detects consecutive numbered sequences (e.g., `script1-video`, `script2-video`...) and collapses them into `script[1-28]-video/ (28 items)`
- **Auto-updates MEMORY.md**: The tree is automatically inserted into the PROJECT_TREE section of MEMORY.md
- **Configurable depth**: Default is 3 levels deep (adjustable in script)

## Configuration

Edit these values in `scripts/project-tree.js`:

- `MAX_DEPTH`: Number of directory levels to display (default: 3)
- `EXCLUDE_DIRS`: Directories to skip (node_modules, .git, etc.)
- `ROOT_DIR`: Base directory to scan (default: ~/projects)

## Resources

### scripts/

- `project-tree.js` - Main tree generation script with smart grouping logic
