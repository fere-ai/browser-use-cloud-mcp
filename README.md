# Browser Use Cloud MCP Server

A Model Context Protocol (MCP) server that provides access to the Browser Use Cloud API for automated browser tasks and web automation.

## Features

- ✅ Complete implementation of all Browser Use Cloud API endpoints
- ✅ Support for both stdio and HTTP transports
- ✅ Comprehensive error handling and validation
- ✅ Full type safety with Pydantic models
- ✅ Async/await support throughout
- ✅ Detailed logging and debugging capabilities
- ✅ Extensive test coverage

## Installation

### From PyPI (when published)
```bash
pip install browser-use-cloud-mcp
```

### From Source
```bash
git clone https://github.com/fere-ai/browser-use-cloud-mcp.git
cd browser-use-cloud-mcp
pip install .
```

### For Development
```bash
git clone https://github.com/fere-ai/browser-use-cloud-mcp.git
cd browser-use-cloud-mcp
poetry install
```

## Configuration

Set your Browser Use Cloud API key as an environment variable:

```bash
export BROWSER_USE_CLOUD_API_KEY="your-api-key-here"
```

Get your API key from [Browser Use Cloud](https://cloud.browser-use.com/).

## Usage

### Running the Server

#### stdio Transport (Default)
```bash
browser-use-cloud-mcp
```

#### HTTP Transport
```bash
browser-use-cloud-mcp --transport http --port 8000
```

#### Custom Host and Port
```bash
browser-use-cloud-mcp --transport http --host 0.0.0.0 --port 9000
```

#### With Debug Logging
```bash
browser-use-cloud-mcp --log-level DEBUG
```

### Available Tools

This MCP server provides 18 tools corresponding to all Browser Use Cloud API endpoints:

#### Task Management
- **`run_task`** - Execute a browser automation task
  - Required: `task` (string) - Description of what the browser should do
  - Optional: `secrets`, `allowed_domains`, `save_browser_data`, `structured_output_json`, `llm_model`, `use_adblock`, `use_proxy`, `highlight_elements`

- **`get_task`** - Get details of a specific task
  - Required: `task_id` (string)

- **`get_task_status`** - Get the status of a task
  - Required: `task_id` (string)

- **`list_tasks`** - List all tasks
  - Optional: `page` (int, default: 1), `per_page` (int, default: 10)

- **`stop_task`** - Stop a running task
  - Required: `task_id` (string)

- **`pause_task`** - Pause a running task
  - Required: `task_id` (string)

- **`resume_task`** - Resume a paused task
  - Required: `task_id` (string)

#### Task Media
- **`get_task_screenshots`** - Get screenshots from a task
  - Required: `task_id` (string)

- **`get_task_gif`** - Get animated GIF of task execution
  - Required: `task_id` (string)

- **`get_task_media`** - Get media files from a task
  - Required: `task_id` (string)

#### Scheduled Tasks
- **`create_scheduled_task`** - Create a scheduled task
  - Required: `name`, `task`, `schedule_type` ("interval" or "cron"), `schedule_value`
  - Optional: Same as `run_task`

- **`update_scheduled_task`** - Update a scheduled task
  - Required: `task_id`
  - Optional: All other fields from `create_scheduled_task`

- **`delete_scheduled_task`** - Delete a scheduled task
  - Required: `task_id` (string)

- **`list_scheduled_tasks`** - List scheduled tasks
  - Optional: `page` (int, default: 1), `per_page` (int, default: 10)

#### User Management
- **`get_user_balance`** - Check account balance
  - No parameters required

- **`get_user_info`** - Get user information
  - No parameters required

- **`delete_browser_profile`** - Delete browser profile data
  - No parameters required

#### Health Check
- **`ping`** - Health check endpoint
  - No parameters required

### Example Usage with Claude Desktop

Add this to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "browser-use-cloud": {
      "command": "browser-use-cloud-mcp",
      "env": {
        "BROWSER_USE_CLOUD_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Example Tool Calls

#### Running a Simple Task
```json
{
  "name": "run_task",
  "arguments": {
    "task": "Go to google.com and search for 'MCP servers'",
    "allowed_domains": ["google.com"]
  }
}
```

#### Running a Task with Structured Output
```json
{
  "name": "run_task",
  "arguments": {
    "task": "Go to a news website and extract the top 3 headlines",
    "structured_output_json": "{\"type\": \"object\", \"properties\": {\"headlines\": {\"type\": \"array\", \"items\": {\"type\": \"string\"}}}}",
    "allowed_domains": ["bbc.com", "cnn.com", "reuters.com"],
    "use_adblock": true
  }
}
```

#### Creating a Scheduled Task
```json
{
  "name": "create_scheduled_task",
  "arguments": {
    "name": "Daily News Check",
    "task": "Check the latest news on BBC and save headlines",
    "schedule_type": "cron",
    "schedule_value": "0 9 * * 1-5",
    "allowed_domains": ["bbc.com"]
  }
}
```

#### Checking Task Status
```json
{
  "name": "get_task_status",
  "arguments": {
    "task_id": "task_12345"
  }
}
```

## Supported LLM Models

The server supports all Browser Use Cloud LLM models:
- `gpt-4o`
- `gpt-4o-mini`
- `gpt-4.1`
- `gpt-4.1-mini`
- `gemini-2.0-flash`
- `gemini-2.0-flash-lite`
- `gemini-2.5-flash-preview-04-17`
- `claude-3-7-sonnet-20250219`
- `claude-sonnet-4-20250514`
- `llama-4-maverick-17b-128e-instruct`

## Development

### Prerequisites
- Python 3.10+
- Poetry
- Git

### Setup
```bash
git clone https://github.com/fere-ai/browser-use-cloud-mcp.git
cd browser-use-cloud-mcp
poetry install
```

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=browser_use_cloud_mcp

# Run only integration tests
poetry run pytest tests/test_integration.py -v
```

### Code Quality
```bash
# Format code
poetry run black .
poetry run isort .

# Lint code
poetry run ruff check .

# Type checking
poetry run mypy browser_use_cloud_mcp
```

### Using the Development Container

This project includes a devcontainer configuration for easy development:

1. Open the project in VS Code
2. Install the "Dev Containers" extension
3. Press `F1` and select "Dev Containers: Reopen in Container"
4. The container will build and install all dependencies automatically

## Project Structure

```
browser-use-cloud-mcp/
├── browser_use_cloud_mcp/
│   ├── __init__.py          # Package initialization
│   ├── models.py            # Pydantic data models
│   ├── client.py            # HTTP client for Browser Use Cloud API
│   ├── server.py            # MCP server implementation
│   └── cli.py               # Command-line interface
├── tests/
│   ├── conftest.py          # Test fixtures and configuration
│   ├── test_models.py       # Model validation tests
│   ├── test_client.py       # HTTP client tests
│   ├── test_server.py       # MCP server tests
│   ├── test_cli.py          # CLI tests
│   └── test_integration.py  # Integration tests
├── .devcontainer/           # Development container configuration
├── .github/workflows/       # GitHub Actions CI/CD
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## Error Handling

The server provides comprehensive error handling:

- **Validation Errors**: Invalid input parameters are caught and returned with helpful messages
- **API Errors**: Browser Use Cloud API errors are properly handled and forwarded
- **Network Errors**: Connection issues are caught and reported
- **Authentication Errors**: Missing or invalid API keys are detected

All errors are returned as proper MCP error responses with detailed messages.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`poetry run pytest`)
6. Format and lint your code (`poetry run black . && poetry run ruff check .`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [Browser Use Cloud Docs](https://docs.browser-use.com/)
- **API Documentation**: Available in the OpenAPI spec
- **Issues**: [GitHub Issues](https://github.com/fere-ai/browser-use-cloud-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/fere-ai/browser-use-cloud-mcp/discussions)

## Changelog

### 0.1.0 (Initial Release)
- Complete implementation of all Browser Use Cloud API endpoints
- Support for stdio and HTTP transports
- Comprehensive test suite
- Development container configuration
- CI/CD pipeline with GitHub Actions