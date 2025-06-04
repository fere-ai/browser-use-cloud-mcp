"""Test configuration and shared fixtures."""

import os
from unittest.mock import AsyncMock

import httpx
import pytest
from pytest_mock import MockFixture

from browser_use_cloud_mcp.client import BrowserUseCloudClient


@pytest.fixture
def mock_api_key():
    """Provide a mock API key."""
    return "test-api-key"


@pytest.fixture
def mock_env(mock_api_key):
    """Mock environment variables."""
    os.environ["BROWSER_USE_CLOUD_API_KEY"] = mock_api_key
    yield
    if "BROWSER_USE_CLOUD_API_KEY" in os.environ:
        del os.environ["BROWSER_USE_CLOUD_API_KEY"]


@pytest.fixture
def mock_httpx_client(mocker: MockFixture):
    """Mock httpx AsyncClient."""
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={"success": True})
    mock_response.text = "Success"
    mock_client.request = AsyncMock(return_value=mock_response)

    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    return mock_client


@pytest.fixture
async def client(mock_env, mock_httpx_client):
    """Create a test client."""
    return BrowserUseCloudClient()


@pytest.fixture
def sample_run_task_request():
    """Sample run task request data."""
    return {
        "task": "Navigate to google.com and search for 'test'",
        "allowed_domains": ["google.com"],
        "use_adblock": True,
    }


@pytest.fixture
def sample_task_response():
    """Sample task response data."""
    return {
        "task_id": "task_123",
        "status": "running",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "task": "Navigate to google.com and search for 'test'",
        "result": None,
        "error": None,
    }


@pytest.fixture
def sample_scheduled_task_request():
    """Sample scheduled task request data."""
    return {
        "name": "Daily Google Search",
        "task": "Navigate to google.com and search for 'daily test'",
        "schedule_type": "interval",
        "schedule_value": "24h",
        "use_adblock": True,
    }
