# Fizzy CLI

A command-line interface for managing Fizzy Kanban boards, cards, and tasks.

## Installation

```bash
npm install -g @emredoganer/fizzy-cli
```

## Setup

### 1. Generate a Personal Access Token

1. Log in to your Fizzy account
2. Go to Profile → API → Generate token
3. Copy your Personal Access Token

### 2. Login

```bash
fizzy auth login
```

Enter your Personal Access Token when prompted.

## Usage

### Authentication

```bash
# Login with PAT
fizzy auth login

# Check auth status
fizzy auth status

# Logout
fizzy auth logout
```

### Accounts

```bash
# List available accounts
fizzy accounts

# Set current account
fizzy account set <slug>

# Show current account
fizzy account current
```

### Boards

```bash
# List all boards
fizzy boards list

# Show archived boards
fizzy boards list --archived

# Get board details
fizzy boards get <slug>

# Create a board
fizzy boards create --name "My Board" --description "Description"

# Update a board
fizzy boards update <slug> --name "New Name"

# Archive a board
fizzy boards archive <slug>

# Delete a board
fizzy boards delete <slug>
```

### Cards

```bash
# List cards in a board
fizzy cards list --board <slug>

# Filter cards
fizzy cards list --board <slug> --status open
fizzy cards list --board <slug> --column <column-id>
fizzy cards list --board <slug> --not-now

# Get card details
fizzy cards get <number> --board <slug>

# Create a card
fizzy cards create --board <slug> --title "My Task"

# Create with options
fizzy cards create --board <slug> --title "My Task" \
  --description "Details" \
  --priority high \
  --due "2024-12-31" \
  --column 123

# Update a card
fizzy cards update <number> --board <slug> --title "Updated Title"

# Close/reopen a card
fizzy cards close <number> --board <slug>
fizzy cards reopen <number> --board <slug>

# Move a card
fizzy cards move <number> --board <slug> --column <column-id>

# Assign/unassign users
fizzy cards assign <number> --board <slug> --users "1,2,3"
fizzy cards unassign <number> --board <slug> --users "1"

# Add tags
fizzy cards tag <number> --board <slug> --tags "1,2"

# Mark as "not now"
fizzy cards not-now <number> --board <slug>
fizzy cards not-now <number> --board <slug> --unset

# Delete a card
fizzy cards delete <number> --board <slug>
```

### Steps (Subtasks)

```bash
# List steps on a card
fizzy steps list --board <slug> --card <number>

# Add a step
fizzy steps add --board <slug> --card <number> --content "Subtask"

# Complete/uncomplete a step
fizzy steps complete <step-id> --board <slug> --card <number>
fizzy steps uncomplete <step-id> --board <slug> --card <number>

# Delete a step
fizzy steps delete <step-id> --board <slug> --card <number>
```

### Comments

```bash
# List comments
fizzy comments list --board <slug> --card <number>

# Add a comment
fizzy comments add --board <slug> --card <number> --content "My comment"

# Update a comment
fizzy comments update <comment-id> --board <slug> --card <number> --content "Updated"

# Delete a comment
fizzy comments delete <comment-id> --board <slug> --card <number>
```

### Tags & Columns

```bash
# List tags
fizzy tags list --board <slug>

# List columns
fizzy columns list --board <slug>

# Create a column
fizzy columns create --board <slug> --name "In Progress"

# Update a column
fizzy columns update <id> --board <slug> --name "Done"

# Delete a column
fizzy columns delete <id> --board <slug>
```

## Output Formats

All commands support `--json` flag for JSON output:

```bash
fizzy boards list --json
fizzy cards get <number> --board <slug> --json
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `FIZZY_ACCESS_TOKEN` | Personal Access Token |
| `FIZZY_ACCOUNT_SLUG` | Default account slug |

## License

MIT
