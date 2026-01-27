# Notion Skill

This skill enables working with Notion pages and databases via the official Notion API.

## Quick Start

1. Create a Notion Integration at https://www.notion.so/my-integrations
2. Copy the Internal Integration Token
3. Export it: `export NOTION_API_KEY=secret_xxx`
4. Share the integration with pages/databases you want to access

## Features

- Read and create pages
- Append blocks to pages
- Query databases
- Create and update database rows
- Schema inspection and changes (with safety checks)

## Requirements

- `NOTION_API_KEY` environment variable
- `notion-cli` (Node.js) or `notion-cli-py` (Python) - see installation instructions in SKILL.md

## Version

Current version: 0.1.0

This is a declarative skill that documents safe, recommended operations. The actual API calls are performed by a local CLI tool.
