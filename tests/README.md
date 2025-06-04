# Test Suite Organization

This directory contains different types of tests for the Browser Use Cloud MCP Server:

## Unit Tests (with mocks)
These tests validate individual components in isolation using mocked dependencies:

- **`test_models.py`** - Tests for Pydantic data models and validation
- **`test_client.py`** - Tests for the HTTP client with mocked API responses
- **`test_server.py`** - Tests for the MCP server functionality with mocked client
- **`test_cli.py`** - Tests for the CLI interface with mocked components

## Integration Tests (with mocks)
These tests validate that components work together correctly but still use mocks for external dependencies:

- **`test_integration.py`** - Basic integration tests with mocked API calls

## Real Integration Tests
These tests can run with either mocked responses (CI mode) or real API calls (with valid API key):

- **`test_real_integration.py`** - Complete MCP server workflow tests
  - Uses mocks when `BROWSER_USE_CLOUD_API_KEY` is not set or is a test key
  - Uses real API calls when `BROWSER_USE_CLOUD_API_KEY` is set to a valid key

## Manual Testing Scripts
These are interactive scripts for manual testing and demonstration:

- **`test_manual_integration.py`** - Interactive manual testing script
- **`test_integration_demo.py`** - Demo script showcasing complete workflow

## Test Configuration
- **`conftest.py`** - Shared test fixtures and configuration

## Running Tests

```bash
# Run all unit tests (fast, no API calls)
poetry run pytest tests/test_models.py tests/test_client.py tests/test_server.py tests/test_cli.py -v

# Run integration tests with mocks
poetry run pytest tests/test_integration.py tests/test_real_integration.py -v

# Run real integration tests (requires valid API key)
export BROWSER_USE_CLOUD_API_KEY="your-real-api-key"
poetry run pytest tests/test_real_integration.py::TestRealIntegration::test_full_workflow_real_api -v

# Run manual tests
poetry run python tests/test_manual_integration.py
poetry run python tests/test_integration_demo.py
```