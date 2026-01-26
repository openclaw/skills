# Taskleef Skill for Clawdbot

A Clawdbot skill for managing todos, projects, and kanban boards using [Taskleef.com](https://taskleef.com).

## Installation

```bash
clawdhub install taskleef
```

## Prerequisites

This skill requires the following to be installed:

- `todo` CLI - The Taskleef command-line interface
- `curl` - For making API requests
- `jq` - For parsing JSON responses

### Installing the todo CLI

```bash
# Clone the repository
git clone https://github.com/Xatter/taskleef.git
cd taskleef/taskleef-cli
chmod +x todo

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$PATH:/path/to/taskleef/taskleef-cli"
```

## Configuration

### Get Your API Key

1. Visit [taskleef.com](https://taskleef.com)
2. Generate an API key from your user dashboard

### Set Environment Variable

Add to your Clawdbot configuration (`~/.clawdbot/clawdbot.json`):

```json
{
  "skills": {
    "entries": {
      "taskleef": {
        "enabled": true,
        "apiKey": "your-api-key-here"
      }
    }
  }
}
```

Or set the environment variable:

```bash
export TASKLEEF_API_KEY=your-api-key-here
```

## Features

- **Todo Management**: Add, list, complete, and delete todos
- **Projects**: Organize todos into projects
- **Kanban Boards**: Visual workflow management with boards and columns
- **Subtasks**: Break down complex tasks
- **Flexible Search**: Find items by partial title or ID prefix
- **Inbox View**: See unorganized todos

## Usage

Once installed, the agent can manage your Taskleef todos through natural language:

- "Add a todo to buy groceries"
- "Show me my pending todos"
- "Complete the pull request todo"
- "Create a project called Website Redesign"
- "Show my kanban board"
- "Move the Feature A card to Done"

## License

MIT
