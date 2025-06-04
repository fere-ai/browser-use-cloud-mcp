"""Integration tests to verify the basic functionality with mocked dependencies.

These tests validate that all components work together correctly without making
actual API calls to the Browser Use Cloud service. They use mocks to simulate
external dependencies.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from browser_use_cloud_mcp.models import RunTaskRequest, TaskStatusEnum


class TestBasicFunctionality:
    """Test basic functionality without complex mocking."""

    def test_models_import_correctly(self):
        """Test that all models can be imported."""
        from browser_use_cloud_mcp.models import (
            LLMModel,
            RunTaskRequest,
            ScheduleType,
            TaskStatusEnum,
        )

        assert RunTaskRequest
        assert TaskStatusEnum
        assert ScheduleType
        assert LLMModel

    def test_run_task_request_creation(self):
        """Test creating a RunTaskRequest model."""
        request = RunTaskRequest(task="Test task")
        assert request.task == "Test task"
        assert request.use_adblock is True
        assert request.save_browser_data is False

    def test_client_import(self):
        """Test that client can be imported."""
        from browser_use_cloud_mcp.client import BrowserUseCloudClient

        assert BrowserUseCloudClient

    def test_server_import(self):
        """Test that server can be imported."""
        from browser_use_cloud_mcp.server import app, call_tool, list_tools

        assert app
        assert list_tools
        assert call_tool

    def test_cli_import(self):
        """Test that CLI can be imported."""
        from browser_use_cloud_mcp.cli import main

        assert main

    def test_client_requires_api_key(self):
        """Test that client requires API key."""
        from browser_use_cloud_mcp.client import BrowserUseCloudClient

        with pytest.raises(ValueError, match="API key is required"):
            BrowserUseCloudClient()

    def test_client_accepts_api_key(self):
        """Test that client accepts API key."""
        from browser_use_cloud_mcp.client import BrowserUseCloudClient

        client = BrowserUseCloudClient(api_key="test-key")
        assert client.api_key == "test-key"

    @pytest.mark.asyncio
    async def test_list_tools_works(self):
        """Test that list_tools function works."""
        from browser_use_cloud_mcp.server import list_tools

        result = await list_tools()

        assert result.tools
        assert len(result.tools) == 18

        tool_names = [tool.name for tool in result.tools]
        assert "run_task" in tool_names
        assert "get_task" in tool_names
        assert "ping" in tool_names

    def test_package_structure(self):
        """Test that package has correct structure."""
        import browser_use_cloud_mcp

        assert hasattr(browser_use_cloud_mcp, "__version__")
        assert browser_use_cloud_mcp.__version__ == "0.1.0"
