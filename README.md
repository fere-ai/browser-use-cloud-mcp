# Browser Use Cloud MCP Server

A Model Context Protocol (MCP) server that provides access to the Browser Use Cloud API for automated browser tasks and web automation.

## Installation

```bash
pip install browser-use-cloud-mcp
```

## Usage

### Environment Variables

Set the following environment variable to authenticate with the Browser Use Cloud API:

```bash
export BROWSER_USE_CLOUD_API_KEY="your-api-key"
```

### Running the Server

#### stdio Transport
```bash
browser-use-cloud-mcp
```

#### HTTP Transport
```bash
browser-use-cloud-mcp --transport http --port 8000
```

## Available Tools

This MCP server provides the following tools that correspond to the Browser Use Cloud API endpoints:

### Task Management
- `run_task` - Execute a browser automation task
- `get_task` - Get details of a specific task
- `get_task_status` - Get the status of a task
- `list_tasks` - List all tasks
- `stop_task` - Stop a running task
- `pause_task` - Pause a running task
- `resume_task` - Resume a paused task

### Task Media
- `get_task_screenshots` - Get screenshots from a task
- `get_task_gif` - Get animated GIF of task execution
- `get_task_media` - Get media files from a task

### Scheduled Tasks
- `create_scheduled_task` - Create a scheduled task
- `update_scheduled_task` - Update a scheduled task
- `delete_scheduled_task` - Delete a scheduled task
- `list_scheduled_tasks` - List scheduled tasks

### User Management
- `get_user_balance` - Check account balance
- `get_user_info` - Get user information
- `delete_browser_profile` - Delete browser profile data

### Health Check
- `ping` - Health check endpoint

## Development

### Prerequisites
- Python 3.10+
- Poetry

### Setup
```bash
git clone https://github.com/fere-ai/browser-use-cloud-mcp.git
cd browser-use-cloud-mcp
poetry install
```

### Running Tests
```bash
poetry run pytest
```

### Code Formatting
```bash
poetry run black .
poetry run isort .
poetry run ruff check .
```

## License

MIT