"""Tests for the HTTP client."""

from unittest.mock import AsyncMock

import httpx
import pytest

from browser_use_cloud_mcp.client import BrowserUseCloudClient, BrowserUseCloudError
from browser_use_cloud_mcp.models import (
    RunTaskRequest,
    ScheduledTaskRequest,
    UpdateScheduledTaskRequest,
)


class TestBrowserUseCloudClient:
    """Test the Browser Use Cloud HTTP client."""

    def test_client_initialization_with_api_key(self):
        """Test client initialization with API key parameter."""
        client = BrowserUseCloudClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://api.browser-use.com"

    def test_client_initialization_with_env_var(self, mock_env):
        """Test client initialization with environment variable."""
        client = BrowserUseCloudClient()
        assert client.api_key == "test-api-key"

    def test_client_initialization_missing_api_key(self):
        """Test client initialization fails without API key."""
        with pytest.raises(ValueError, match="API key is required"):
            BrowserUseCloudClient()

    def test_client_initialization_custom_base_url(self):
        """Test client initialization with custom base URL."""
        client = BrowserUseCloudClient(
            api_key="test-key", base_url="https://custom.api.com"
        )
        assert client.base_url == "https://custom.api.com"


class TestTaskManagement:
    """Test task management endpoints."""

    @pytest.mark.asyncio
    async def test_run_task(self, client, mock_httpx_client, sample_run_task_request):
        """Test running a task."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={"task_id": "task_123"})
        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        # Make request
        request = RunTaskRequest(**sample_run_task_request)
        result = await client.run_task(request)

        # Verify
        assert result.task_id == "task_123"
        mock_httpx_client.request.assert_called_once_with(
            "POST",
            "/api/v1/run-task",
            json=request.model_dump(exclude_none=True),
            params=None,
        )

    @pytest.mark.asyncio
    async def test_get_task(self, client, mock_httpx_client, sample_task_response):
        """Test getting task details."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value=sample_task_response)
        mock_httpx_client.request = AsyncMock(return_value=mock_response)

        # Make request
        result = await client.get_task("task_123")

        # Verify
        assert result.task_id == "task_123"
        assert result.status.value == "running"
        mock_httpx_client.request.assert_called_once_with(
            "GET", "/api/v1/task/task_123", params=None
        )

    @pytest.mark.asyncio
    async def test_get_task_status(self, client, mock_httpx_client):
        """Test getting task status."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"task_id": "task_123", "status": "running"}
        mock_httpx_client.request.return_value = mock_response

        # Make request
        result = await client.get_task_status("task_123")

        # Verify
        assert result.task_id == "task_123"
        assert result.status.value == "running"

    @pytest.mark.asyncio
    async def test_list_tasks(self, client, mock_httpx_client):
        """Test listing tasks."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tasks": [],
            "total": 0,
            "page": 1,
            "per_page": 10,
        }
        mock_httpx_client.request.return_value = mock_response

        # Make request
        result = await client.list_tasks(page=1, per_page=10)

        # Verify
        assert result.total == 0
        assert result.page == 1
        assert result.per_page == 10
        mock_httpx_client.request.assert_called_once_with(
            "GET", "/api/v1/tasks", params={"page": 1, "per_page": 10}
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("action", ["stop", "pause", "resume"])
    async def test_task_control_actions(self, client, mock_httpx_client, action):
        """Test task control actions (stop, pause, resume)."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"task_id": "task_123", "status": "stopped"}
        mock_httpx_client.request.return_value = mock_response

        # Make request
        method = getattr(client, f"{action}_task")
        result = await method("task_123")

        # Verify
        assert result.task_id == "task_123"
        mock_httpx_client.request.assert_called_once_with(
            "POST", f"/api/v1/{action}-task", params={"task_id": "task_123"}
        )


class TestTaskMedia:
    """Test task media endpoints."""

    @pytest.mark.asyncio
    async def test_get_task_screenshots(self, client, mock_httpx_client):
        """Test getting task screenshots."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"screenshots": ["url1", "url2"]}
        mock_httpx_client.request.return_value = mock_response

        # Make request
        result = await client.get_task_screenshots("task_123")

        # Verify
        assert result.screenshots == ["url1", "url2"]
        mock_httpx_client.request.assert_called_once_with(
            "GET", "/api/v1/task/task_123/screenshots", params=None
        )

    @pytest.mark.asyncio
    async def test_get_task_gif(self, client, mock_httpx_client):
        """Test getting task GIF."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"gif_url": "https://example.com/task.gif"}
        mock_httpx_client.request.return_value = mock_response

        # Make request
        result = await client.get_task_gif("task_123")

        # Verify
        assert result.gif_url == "https://example.com/task.gif"

    @pytest.mark.asyncio
    async def test_get_task_media(self, client, mock_httpx_client):
        """Test getting task media."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"media_files": ["file1.png", "file2.mp4"]}
        mock_httpx_client.request.return_value = mock_response

        # Make request
        result = await client.get_task_media("task_123")

        # Verify
        assert result.media_files == ["file1.png", "file2.mp4"]


class TestScheduledTasks:
    """Test scheduled task endpoints."""

    @pytest.mark.asyncio
    async def test_create_scheduled_task(
        self, client, mock_httpx_client, sample_scheduled_task_request
    ):
        """Test creating a scheduled task."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "task_id": "scheduled_123",
            "name": "Daily Google Search",
            "task": "Navigate to google.com and search for 'daily test'",
            "schedule_type": "interval",
            "schedule_value": "24h",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "status": "active",
        }
        mock_httpx_client.request.return_value = mock_response

        # Make request
        request = ScheduledTaskRequest(**sample_scheduled_task_request)
        result = await client.create_scheduled_task(request)

        # Verify
        assert result.task_id == "scheduled_123"
        assert result.name == "Daily Google Search"
        assert result.schedule_type.value == "interval"

    @pytest.mark.asyncio
    async def test_update_scheduled_task(self, client, mock_httpx_client):
        """Test updating a scheduled task."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "task_id": "scheduled_123",
            "name": "Updated Task",
            "task": "Updated task description",
            "schedule_type": "cron",
            "schedule_value": "0 9 * * 1-5",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z",
            "status": "active",
        }
        mock_httpx_client.request.return_value = mock_response

        # Make request
        update_request = UpdateScheduledTaskRequest(name="Updated Task")
        result = await client.update_scheduled_task("scheduled_123", update_request)

        # Verify
        assert result.name == "Updated Task"
        assert result.schedule_type.value == "cron"

    @pytest.mark.asyncio
    async def test_delete_scheduled_task(self, client, mock_httpx_client):
        """Test deleting a scheduled task."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Task deleted successfully"}
        mock_httpx_client.request.return_value = mock_response

        # Make request
        result = await client.delete_scheduled_task("scheduled_123")

        # Verify
        assert result["message"] == "Task deleted successfully"

    @pytest.mark.asyncio
    async def test_list_scheduled_tasks(self, client, mock_httpx_client):
        """Test listing scheduled tasks."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "scheduled_tasks": [],
            "total": 0,
            "page": 1,
            "per_page": 10,
        }
        mock_httpx_client.request.return_value = mock_response

        # Make request
        result = await client.list_scheduled_tasks()

        # Verify
        assert result.total == 0
        assert len(result.scheduled_tasks) == 0


class TestUserManagement:
    """Test user management endpoints."""

    @pytest.mark.asyncio
    async def test_get_user_balance(self, client, mock_httpx_client):
        """Test getting user balance."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"balance": 100.50, "currency": "USD"}
        mock_httpx_client.request.return_value = mock_response

        # Make request
        result = await client.get_user_balance()

        # Verify
        assert result.balance == 100.50
        assert result.currency == "USD"

    @pytest.mark.asyncio
    async def test_get_user_info(self, client, mock_httpx_client):
        """Test getting user information."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 123, "email": "test@example.com"}
        mock_httpx_client.request.return_value = mock_response

        # Make request
        result = await client.get_user_info()

        # Verify
        assert result["id"] == 123
        assert result["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_delete_browser_profile(self, client, mock_httpx_client):
        """Test deleting browser profile."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Profile deleted successfully"}
        mock_httpx_client.request.return_value = mock_response

        # Make request
        result = await client.delete_browser_profile()

        # Verify
        assert result["message"] == "Profile deleted successfully"


class TestHealthCheck:
    """Test health check endpoint."""

    @pytest.mark.asyncio
    async def test_ping(self, client, mock_httpx_client):
        """Test ping endpoint."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_httpx_client.request.return_value = mock_response

        # Make request
        result = await client.ping()

        # Verify
        assert result["status"] == "ok"


class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_api_error_handling(self, client, mock_httpx_client):
        """Test API error handling."""
        # Mock error response
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.json.return_value = {"detail": "Invalid request"}
        mock_httpx_client.request.return_value = mock_response

        # Make request and expect error
        with pytest.raises(BrowserUseCloudError) as exc_info:
            await client.ping()

        assert "Invalid request" in str(exc_info.value)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_http_error_handling(self, client, mock_httpx_client):
        """Test HTTP error handling."""
        # Mock HTTP error
        mock_httpx_client.request.side_effect = httpx.ConnectError("Connection failed")

        # Make request and expect error
        with pytest.raises(BrowserUseCloudError) as exc_info:
            await client.ping()

        assert "HTTP error" in str(exc_info.value)
        assert "Connection failed" in str(exc_info.value)
