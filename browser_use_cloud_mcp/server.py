"""Browser Use Cloud MCP Server implementation."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)
from pydantic import ValidationError

from .client import BrowserUseCloudClient, BrowserUseCloudError
from .models import RunTaskRequest, ScheduledTaskRequest, UpdateScheduledTaskRequest

logger = logging.getLogger(__name__)

# MCP Server instance
app = Server("browser-use-cloud-mcp")


@app.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(
        tools=[
            # Task Management
            Tool(
                name="run_task",
                description="Execute a browser automation task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task": {"type": "string", "description": "Task description"},
                        "secrets": {
                            "type": "object",
                            "description": "Dictionary of secrets for the task",
                            "additionalProperties": {"type": "string"},
                        },
                        "allowed_domains": {
                            "type": "array",
                            "description": "List of allowed domains",
                            "items": {"type": "string"},
                        },
                        "save_browser_data": {
                            "type": "boolean",
                            "description": "Whether to save browser data",
                            "default": False,
                        },
                        "structured_output_json": {
                            "type": "string",
                            "description": "JSON schema for structured output",
                        },
                        "llm_model": {
                            "type": "string",
                            "description": "LLM model to use",
                            "enum": [
                                "gpt-4o",
                                "gpt-4o-mini",
                                "gpt-4.1",
                                "gpt-4.1-mini",
                                "gemini-2.0-flash",
                                "gemini-2.0-flash-lite",
                                "gemini-2.5-flash-preview-04-17",
                                "claude-3-7-sonnet-20250219",
                                "claude-sonnet-4-20250514",
                                "llama-4-maverick-17b-128e-instruct",
                            ],
                        },
                        "use_adblock": {
                            "type": "boolean",
                            "description": "Whether to use adblock",
                            "default": True,
                        },
                        "use_proxy": {
                            "type": "boolean",
                            "description": "Whether to use proxy",
                            "default": True,
                        },
                        "highlight_elements": {
                            "type": "boolean",
                            "description": "Whether to highlight elements",
                            "default": True,
                        },
                    },
                    "required": ["task"],
                },
            ),
            Tool(
                name="get_task",
                description="Get details of a specific task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID"},
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="get_task_status",
                description="Get the status of a task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID"},
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="list_tasks",
                description="List all tasks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer",
                            "description": "Page number",
                            "default": 1,
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "Items per page",
                            "default": 10,
                        },
                    },
                },
            ),
            Tool(
                name="stop_task",
                description="Stop a running task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID"},
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="pause_task",
                description="Pause a running task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID"},
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="resume_task",
                description="Resume a paused task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID"},
                    },
                    "required": ["task_id"],
                },
            ),
            # Task Media
            Tool(
                name="get_task_screenshots",
                description="Get screenshots from a task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID"},
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="get_task_gif",
                description="Get animated GIF of task execution",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID"},
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="get_task_media",
                description="Get media files from a task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID"},
                    },
                    "required": ["task_id"],
                },
            ),
            # Scheduled Tasks
            Tool(
                name="create_scheduled_task",
                description="Create a scheduled task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Task name"},
                        "task": {"type": "string", "description": "Task description"},
                        "schedule_type": {
                            "type": "string",
                            "description": "Schedule type",
                            "enum": ["interval", "cron"],
                        },
                        "schedule_value": {
                            "type": "string",
                            "description": "Schedule value",
                        },
                        "secrets": {
                            "type": "object",
                            "description": "Dictionary of secrets",
                            "additionalProperties": {"type": "string"},
                        },
                        "allowed_domains": {
                            "type": "array",
                            "description": "List of allowed domains",
                            "items": {"type": "string"},
                        },
                        "save_browser_data": {
                            "type": "boolean",
                            "description": "Whether to save browser data",
                            "default": False,
                        },
                        "structured_output_json": {
                            "type": "string",
                            "description": "JSON schema for structured output",
                        },
                        "llm_model": {
                            "type": "string",
                            "description": "LLM model to use",
                            "enum": [
                                "gpt-4o",
                                "gpt-4o-mini",
                                "gpt-4.1",
                                "gpt-4.1-mini",
                                "gemini-2.0-flash",
                                "gemini-2.0-flash-lite",
                                "gemini-2.5-flash-preview-04-17",
                                "claude-3-7-sonnet-20250219",
                                "claude-sonnet-4-20250514",
                                "llama-4-maverick-17b-128e-instruct",
                            ],
                        },
                        "use_adblock": {
                            "type": "boolean",
                            "description": "Whether to use adblock",
                            "default": True,
                        },
                        "use_proxy": {
                            "type": "boolean",
                            "description": "Whether to use proxy",
                            "default": True,
                        },
                        "highlight_elements": {
                            "type": "boolean",
                            "description": "Whether to highlight elements",
                            "default": True,
                        },
                    },
                    "required": ["name", "task", "schedule_type", "schedule_value"],
                },
            ),
            Tool(
                name="update_scheduled_task",
                description="Update a scheduled task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID"},
                        "name": {"type": "string", "description": "Task name"},
                        "task": {"type": "string", "description": "Task description"},
                        "schedule_type": {
                            "type": "string",
                            "description": "Schedule type",
                            "enum": ["interval", "cron"],
                        },
                        "schedule_value": {
                            "type": "string",
                            "description": "Schedule value",
                        },
                        "secrets": {
                            "type": "object",
                            "description": "Dictionary of secrets",
                            "additionalProperties": {"type": "string"},
                        },
                        "allowed_domains": {
                            "type": "array",
                            "description": "List of allowed domains",
                            "items": {"type": "string"},
                        },
                        "save_browser_data": {
                            "type": "boolean",
                            "description": "Whether to save browser data",
                        },
                        "structured_output_json": {
                            "type": "string",
                            "description": "JSON schema for structured output",
                        },
                        "llm_model": {
                            "type": "string",
                            "description": "LLM model to use",
                            "enum": [
                                "gpt-4o",
                                "gpt-4o-mini",
                                "gpt-4.1",
                                "gpt-4.1-mini",
                                "gemini-2.0-flash",
                                "gemini-2.0-flash-lite",
                                "gemini-2.5-flash-preview-04-17",
                                "claude-3-7-sonnet-20250219",
                                "claude-sonnet-4-20250514",
                                "llama-4-maverick-17b-128e-instruct",
                            ],
                        },
                        "use_adblock": {
                            "type": "boolean",
                            "description": "Whether to use adblock",
                        },
                        "use_proxy": {
                            "type": "boolean",
                            "description": "Whether to use proxy",
                        },
                        "highlight_elements": {
                            "type": "boolean",
                            "description": "Whether to highlight elements",
                        },
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="delete_scheduled_task",
                description="Delete a scheduled task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "Task ID"},
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="list_scheduled_tasks",
                description="List scheduled tasks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer",
                            "description": "Page number",
                            "default": 1,
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "Items per page",
                            "default": 10,
                        },
                    },
                },
            ),
            # User Management
            Tool(
                name="get_user_balance",
                description="Check account balance",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_user_info",
                description="Get user information",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="delete_browser_profile",
                description="Delete browser profile data",
                inputSchema={"type": "object", "properties": {}},
            ),
            # Health Check
            Tool(
                name="ping",
                description="Health check endpoint",
                inputSchema={"type": "object", "properties": {}},
            ),
        ]
    )


@app.call_tool()
async def call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> CallToolResult:
    """Handle tool calls."""
    try:
        async with BrowserUseCloudClient() as client:
            if name == "run_task":
                request = RunTaskRequest(**arguments)
                result = await client.run_task(request)
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=json.dumps(result.model_dump(), indent=2)
                        )
                    ]
                )

            elif name == "get_task":
                task_id = arguments["task_id"]
                result = await client.get_task(task_id)
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=json.dumps(result.model_dump(), indent=2)
                        )
                    ]
                )

            elif name == "get_task_status":
                task_id = arguments["task_id"]
                result = await client.get_task_status(task_id)
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=json.dumps(result.model_dump(), indent=2)
                        )
                    ]
                )

            elif name == "list_tasks":
                page = arguments.get("page", 1)
                per_page = arguments.get("per_page", 10)
                result = await client.list_tasks(page, per_page)
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=json.dumps(result.model_dump(), indent=2)
                        )
                    ]
                )

            elif name == "stop_task":
                task_id = arguments["task_id"]
                result = await client.stop_task(task_id)
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=json.dumps(result.model_dump(), indent=2)
                        )
                    ]
                )

            elif name == "pause_task":
                task_id = arguments["task_id"]
                result = await client.pause_task(task_id)
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=json.dumps(result.model_dump(), indent=2)
                        )
                    ]
                )

            elif name == "resume_task":
                task_id = arguments["task_id"]
                result = await client.resume_task(task_id)
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=json.dumps(result.model_dump(), indent=2)
                        )
                    ]
                )

            elif name == "get_task_screenshots":
                task_id = arguments["task_id"]
                result = await client.get_task_screenshots(task_id)
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=json.dumps(result.model_dump(), indent=2)
                        )
                    ]
                )

            elif name == "get_task_gif":
                task_id = arguments["task_id"]
                result = await client.get_task_gif(task_id)
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=json.dumps(result.model_dump(), indent=2)
                        )
                    ]
                )

            elif name == "get_task_media":
                task_id = arguments["task_id"]
                result = await client.get_task_media(task_id)
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=json.dumps(result.model_dump(), indent=2)
                        )
                    ]
                )

            elif name == "create_scheduled_task":
                request = ScheduledTaskRequest(**arguments)
                result = await client.create_scheduled_task(request)
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=json.dumps(result.model_dump(), indent=2)
                        )
                    ]
                )

            elif name == "update_scheduled_task":
                task_id = arguments.pop("task_id")
                request = UpdateScheduledTaskRequest(**arguments)
                result = await client.update_scheduled_task(task_id, request)
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=json.dumps(result.model_dump(), indent=2)
                        )
                    ]
                )

            elif name == "delete_scheduled_task":
                task_id = arguments["task_id"]
                result = await client.delete_scheduled_task(task_id)
                return CallToolResult(
                    content=[
                        TextContent(type="text", text=json.dumps(result, indent=2))
                    ]
                )

            elif name == "list_scheduled_tasks":
                page = arguments.get("page", 1)
                per_page = arguments.get("per_page", 10)
                result = await client.list_scheduled_tasks(page, per_page)
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=json.dumps(result.model_dump(), indent=2)
                        )
                    ]
                )

            elif name == "get_user_balance":
                result = await client.get_user_balance()
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=json.dumps(result.model_dump(), indent=2)
                        )
                    ]
                )

            elif name == "get_user_info":
                result = await client.get_user_info()
                return CallToolResult(
                    content=[
                        TextContent(type="text", text=json.dumps(result, indent=2))
                    ]
                )

            elif name == "delete_browser_profile":
                result = await client.delete_browser_profile()
                return CallToolResult(
                    content=[
                        TextContent(type="text", text=json.dumps(result, indent=2))
                    ]
                )

            elif name == "ping":
                result = await client.ping()
                return CallToolResult(
                    content=[
                        TextContent(type="text", text=json.dumps(result, indent=2))
                    ]
                )

            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                    isError=True,
                )

    except ValidationError as e:
        logger.error(f"Validation error in {name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Validation error: {str(e)}")],
            isError=True,
        )

    except BrowserUseCloudError as e:
        logger.error(f"API error in {name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"API error: {e.message}")],
            isError=True,
        )

    except Exception as e:
        logger.error(f"Unexpected error in {name}: {e}", exc_info=True)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Unexpected error: {str(e)}")],
            isError=True,
        )


async def main():
    """Main entry point for the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="browser-use-cloud-mcp",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
