"""Tests for the MCP server."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from mcp.types import CallToolResult, TextContent

from browser_use_cloud_mcp.client import BrowserUseCloudError
from browser_use_cloud_mcp.server import call_tool, list_tools


@pytest.fixture
def mock_client(mocker):
    """Mock the BrowserUseCloudClient."""
    mock_client_instance = AsyncMock()
    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_client_instance
    mock_context_manager.__aexit__.return_value = None

    mock_client_class = MagicMock(return_value=mock_context_manager)
    mocker.patch(
        "browser_use_cloud_mcp.server.BrowserUseCloudClient", mock_client_class
    )

    return mock_client_instance


class TestListTools:
    """Test the list_tools handler."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_all_tools(self):
        """Test that list_tools returns all expected tools."""
        result = await list_tools()

        tool_names = [tool.name for tool in result.tools]

        # Verify all expected tools are present
        expected_tools = {
            # Task Management
            "run_task",
            "get_task",
            "get_task_status",
            "list_tasks",
            "stop_task",
            "pause_task",
            "resume_task",
            # Task Media
            "get_task_screenshots",
            "get_task_gif",
            "get_task_media",
            # Scheduled Tasks
            "create_scheduled_task",
            "update_scheduled_task",
            "delete_scheduled_task",
            "list_scheduled_tasks",
            # User Management
            "get_user_balance",
            "get_user_info",
            "delete_browser_profile",
            # Health Check
            "ping",
        }

        assert set(tool_names) == expected_tools
        assert len(result.tools) == 18

    @pytest.mark.asyncio
    async def test_run_task_tool_schema(self):
        """Test run_task tool has correct schema."""
        result = await list_tools()

        run_task_tool = next(tool for tool in result.tools if tool.name == "run_task")

        assert run_task_tool.description == "Execute a browser automation task"
        assert "task" in run_task_tool.inputSchema["required"]
        assert run_task_tool.inputSchema["properties"]["task"]["type"] == "string"
        assert "llm_model" in run_task_tool.inputSchema["properties"]
        assert "enum" in run_task_tool.inputSchema["properties"]["llm_model"]


class TestCallTool:
    """Test the call_tool handler."""

    @pytest.mark.asyncio
    async def test_run_task_success(self, mock_client, sample_run_task_request):
        """Test successful run_task call."""
        # Mock client response
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"task_id": "task_123"}
        mock_client.run_task.return_value = mock_response

        # Call tool
        result = await call_tool("run_task", sample_run_task_request)

        # Verify
        assert isinstance(result, CallToolResult)
        assert len(result.content) == 1
        assert isinstance(result.content[0], TextContent)

        response_data = json.loads(result.content[0].text)
        assert response_data["task_id"] == "task_123"

        mock_client.run_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_task_success(self, mock_client, sample_task_response):
        """Test successful get_task call."""
        # Mock client response
        mock_response = MagicMock()
        mock_response.model_dump.return_value = sample_task_response
        mock_client.get_task.return_value = mock_response

        # Call tool
        result = await call_tool("get_task", {"task_id": "task_123"})

        # Verify
        assert isinstance(result, CallToolResult)
        response_data = json.loads(result.content[0].text)
        assert response_data["task_id"] == "task_123"
        assert response_data["status"] == "running"

        mock_client.get_task.assert_called_once_with("task_123")

    @pytest.mark.asyncio
    async def test_list_tasks_success(self, mock_client):
        """Test successful list_tasks call."""
        # Mock client response
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "tasks": [],
            "total": 0,
            "page": 1,
            "per_page": 10,
        }
        mock_client.list_tasks.return_value = mock_response

        # Call tool
        result = await call_tool("list_tasks", {"page": 1, "per_page": 10})

        # Verify
        assert isinstance(result, CallToolResult)
        response_data = json.loads(result.content[0].text)
        assert response_data["total"] == 0
        assert response_data["page"] == 1

        mock_client.list_tasks.assert_called_once_with(1, 10)

    @pytest.mark.asyncio
    async def test_list_tasks_default_params(self, mock_client):
        """Test list_tasks with default parameters."""
        # Mock client response
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "tasks": [],
            "total": 0,
            "page": 1,
            "per_page": 10,
        }
        mock_client.list_tasks.return_value = mock_response

        # Call tool without parameters
        result = await call_tool("list_tasks", {})

        # Verify default parameters are used
        mock_client.list_tasks.assert_called_once_with(1, 10)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("action", ["stop_task", "pause_task", "resume_task"])
    async def test_task_control_actions(self, mock_client, action):
        """Test task control actions."""
        # Mock client response
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "task_id": "task_123",
            "status": "stopped",
        }
        getattr(mock_client, action).return_value = mock_response

        # Call tool
        result = await call_tool(action, {"task_id": "task_123"})

        # Verify
        assert isinstance(result, CallToolResult)
        response_data = json.loads(result.content[0].text)
        assert response_data["task_id"] == "task_123"

        getattr(mock_client, action).assert_called_once_with("task_123")

    @pytest.mark.asyncio
    async def test_get_task_screenshots(self, mock_client):
        """Test get_task_screenshots call."""
        # Mock client response
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"screenshots": ["url1", "url2"]}
        mock_client.get_task_screenshots.return_value = mock_response

        # Call tool
        result = await call_tool("get_task_screenshots", {"task_id": "task_123"})

        # Verify
        assert isinstance(result, CallToolResult)
        response_data = json.loads(result.content[0].text)
        assert response_data["screenshots"] == ["url1", "url2"]

    @pytest.mark.asyncio
    async def test_create_scheduled_task(
        self, mock_client, sample_scheduled_task_request
    ):
        """Test create_scheduled_task call."""
        # Mock client response
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "task_id": "scheduled_123",
            "name": "Daily Google Search",
            "task": "Navigate to google.com and search for 'daily test'",
            "schedule_type": "interval",
            "schedule_value": "24h",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "status": "active",
        }
        mock_client.create_scheduled_task.return_value = mock_response

        # Call tool
        result = await call_tool("create_scheduled_task", sample_scheduled_task_request)

        # Verify
        assert isinstance(result, CallToolResult)
        response_data = json.loads(result.content[0].text)
        assert response_data["task_id"] == "scheduled_123"
        assert response_data["schedule_type"] == "interval"

    @pytest.mark.asyncio
    async def test_update_scheduled_task(self, mock_client):
        """Test update_scheduled_task call."""
        # Mock client response
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "task_id": "scheduled_123",
            "name": "Updated Task",
            "task": "Updated description",
            "schedule_type": "cron",
            "schedule_value": "0 9 * * 1-5",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z",
            "status": "active",
        }
        mock_client.update_scheduled_task.return_value = mock_response

        # Call tool
        args = {"task_id": "scheduled_123", "name": "Updated Task"}
        result = await call_tool("update_scheduled_task", args)

        # Verify
        assert isinstance(result, CallToolResult)
        response_data = json.loads(result.content[0].text)
        assert response_data["name"] == "Updated Task"

        mock_client.update_scheduled_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_balance(self, mock_client):
        """Test get_user_balance call."""
        # Mock client response
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"balance": 100.50, "currency": "USD"}
        mock_client.get_user_balance.return_value = mock_response

        # Call tool
        result = await call_tool("get_user_balance", {})

        # Verify
        assert isinstance(result, CallToolResult)
        response_data = json.loads(result.content[0].text)
        assert response_data["balance"] == 100.50
        assert response_data["currency"] == "USD"

    @pytest.mark.asyncio
    async def test_get_user_info(self, mock_client):
        """Test get_user_info call."""
        # Mock client response (returns dict, not model)
        mock_client.get_user_info.return_value = {
            "id": 123,
            "email": "test@example.com",
        }

        # Call tool
        result = await call_tool("get_user_info", {})

        # Verify
        assert isinstance(result, CallToolResult)
        response_data = json.loads(result.content[0].text)
        assert response_data["id"] == 123
        assert response_data["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_ping(self, mock_client):
        """Test ping call."""
        # Mock client response (returns dict, not model)
        mock_client.ping.return_value = {"status": "ok"}

        # Call tool
        result = await call_tool("ping", {})

        # Verify
        assert isinstance(result, CallToolResult)
        response_data = json.loads(result.content[0].text)
        assert response_data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_unknown_tool(self, mock_client):
        """Test calling unknown tool."""
        result = await call_tool("unknown_tool", {})

        # Verify error response
        assert isinstance(result, CallToolResult)
        assert result.isError is True
        assert "Unknown tool" in result.content[0].text

    @pytest.mark.asyncio
    async def test_api_error_handling(self, mock_client):
        """Test API error handling."""
        # Mock API error
        mock_client.ping.side_effect = BrowserUseCloudError(
            "API Error", status_code=400
        )

        # Call tool
        result = await call_tool("ping", {})

        # Verify error response
        assert isinstance(result, CallToolResult)
        assert result.isError is True
        assert "API error" in result.content[0].text
        assert "API Error" in result.content[0].text

    @pytest.mark.asyncio
    async def test_validation_error_handling(self, mock_client):
        """Test validation error handling."""
        # Call tool with invalid arguments (missing required field)
        result = await call_tool("run_task", {})

        # Verify error response
        assert isinstance(result, CallToolResult)
        assert result.isError is True
        assert "Validation error" in result.content[0].text

    @pytest.mark.asyncio
    async def test_unexpected_error_handling(self, mock_client):
        """Test unexpected error handling."""
        # Mock unexpected error
        mock_client.ping.side_effect = Exception("Unexpected error")

        # Call tool
        result = await call_tool("ping", {})

        # Verify error response
        assert isinstance(result, CallToolResult)
        assert result.isError is True
        assert "Unexpected error" in result.content[0].text
