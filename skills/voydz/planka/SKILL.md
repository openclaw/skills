---
name: planka
description: Manage Planka (Kanban) projects, boards, lists, cards, and notifications via a custom Python CLI.
metadata: {"clawdbot":{"emoji":"📋","requires":{"bins":["planka-cli"]}}}
---

# Planka CLI

This skill provides a CLI wrapper around the `plankapy` library to interact with a Planka instance.

## Setup

1.  **Install via Homebrew tap:**
    ```bash
    brew tap voydz/homebrew-tap
    brew install planka-cli
    ```

    Source/pipx installs require Python 3.11+ to use plankapy v2.

2.  **Configuration:**
    Use the `login` command to store credentials:
    ```bash
    planka-cli login --url https://planka.example --username alice --password secret
    # or: python3 scripts/planka_cli.py login --url https://planka.example --username alice --password secret
    ```

## Usage

Run the CLI with the installed `planka-cli` binary:

```bash
# Show help
planka-cli

# Check connection
planka-cli status

# Login to planka instance
planka-cli login --url https://planka.example --username alice --password secret

# Remove stored credentials
planka-cli logout

# List Projects
planka-cli projects list

# List Boards (optionally by project ID)
planka-cli boards list [PROJECT_ID]

# List Lists in a Board
planka-cli lists list <BOARD_ID>

# List Cards in a List
planka-cli cards list <LIST_ID>

# Show a Card (includes attachments with URLs and comment text)
planka-cli cards show <CARD_ID>

# Create a Card
planka-cli cards create <LIST_ID> "Card title"

# Update a Card
planka-cli cards update <CARD_ID> --name "New title"
planka-cli cards update <CARD_ID> --list-id <LIST_ID>
planka-cli cards update <CARD_ID> --list-id <LIST_ID> --position top

# Delete a Card
planka-cli cards delete <CARD_ID>

# Notifications
planka-cli notifications all
planka-cli notifications unread
```

## Examples

**List all boards:**
```bash
planka-cli boards list
```

**Show cards in list ID 1619901252164912136:**
```bash
planka-cli cards list 1619901252164912136
```

**Show card details for card ID 1619901252164912137:**
```bash
planka-cli cards show 1619901252164912137
```

**Create a card in list ID 1619901252164912136:**
```bash
planka-cli cards create 1619901252164912136 "Ship CLI"
```

**Move a card to another list:**
```bash
planka-cli cards update 1619901252164912137 --list-id 1619901252164912136
```

**Move a card to another list and pin it to the top:**
```bash
planka-cli cards update 1619901252164912137 --list-id 1619901252164912136 --position top
```

**Mark a card done by updating its name:**
```bash
planka-cli cards update 1619901252164912137 --name "Done: Ship CLI"
```
