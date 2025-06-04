"""HTTP client for Browser Use Cloud API."""

import os
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from .models import (
    CheckUserBalanceResponse,
    ListScheduledTasksResponse,
    ListTasksResponse,
    LLMModel,
    RunTaskRequest,
    ScheduledTaskRequest,
    ScheduledTaskResponse,
    TaskBrowserDataResponse,
    TaskCreatedResponse,
    TaskGifResponse,
    TaskMediaResponse,
    TaskResponse,
    TaskScreenshotsResponse,
    TaskSimpleResponse,
    UpdateScheduledTaskRequest,
)


class BrowserUseCloudError(Exception):
    """Exception raised when API requests fail."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class BrowserUseCloudClient:
    """HTTP client for Browser Use Cloud API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.browser-use.com",
        default_model: Optional[str] = None,
    ):
        """Initialize the client.

        Args:
            api_key: API key for authentication. If not provided, will look for BROWSER_USE_CLOUD_API_KEY env var.
            base_url: Base URL for the API.
            default_model: Default LLM model to use. If not provided, will look for BROWSER_USE_CLOUD_DEFAULT_MODEL env var.
        """
        self.api_key = api_key or os.getenv("BROWSER_USE_CLOUD_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Set BROWSER_USE_CLOUD_API_KEY environment variable or pass api_key parameter."
            )

        self.default_model = default_model or os.getenv("BROWSER_USE_CLOUD_DEFAULT_MODEL")
        if self.default_model:
            # Validate the default model
            try:
                LLMModel(self.default_model)
            except ValueError:
                valid_models = [model.value for model in LLMModel]
                raise ValueError(
                    f"Invalid default model '{self.default_model}'. Valid models are: {', '.join(valid_models)}"
                )

        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=httpx.Timeout(60.0),
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[BaseModel] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API."""
        url = f"/api/v1{endpoint}"

        try:
            if data:
                response = await self.client.request(
                    method, url, json=data.model_dump(exclude_none=True), params=params
                )
            else:
                response = await self.client.request(method, url, params=params)

            if response.status_code >= 400:
                error_detail = response.text
                try:
                    error_json = response.json()
                    if "detail" in error_json:
                        error_detail = str(error_json["detail"])
                except:
                    pass
                raise BrowserUseCloudError(
                    f"API request failed: {error_detail}",
                    status_code=response.status_code,
                )

            return response.json()

        except httpx.HTTPError as e:
            raise BrowserUseCloudError(f"HTTP error: {str(e)}")

    # Task Management
    async def run_task(self, request: RunTaskRequest) -> TaskCreatedResponse:
        """Run a browser automation task."""
        # Apply default model if none specified
        if not request.llm_model and self.default_model:
            request.llm_model = LLMModel(self.default_model)
        
        data = await self._make_request("POST", "/run-task", data=request)
        return TaskCreatedResponse(**data)

    async def get_task(self, task_id: str) -> TaskResponse:
        """Get details of a specific task."""
        data = await self._make_request("GET", f"/task/{task_id}")
        return TaskResponse(**data)

    async def get_task_status(self, task_id: str) -> TaskSimpleResponse:
        """Get the status of a task."""
        data = await self._make_request("GET", f"/task/{task_id}/status")
        return TaskSimpleResponse(**data)

    async def list_tasks(self, page: int = 1, per_page: int = 10) -> ListTasksResponse:
        """List all tasks."""
        params = {"page": page, "per_page": per_page}
        data = await self._make_request("GET", "/tasks", params=params)
        return ListTasksResponse(**data)

    async def stop_task(self, task_id: str) -> TaskSimpleResponse:
        """Stop a running task."""
        data = await self._make_request(
            "POST", "/stop-task", params={"task_id": task_id}
        )
        return TaskSimpleResponse(**data)

    async def pause_task(self, task_id: str) -> TaskSimpleResponse:
        """Pause a running task."""
        data = await self._make_request(
            "POST", "/pause-task", params={"task_id": task_id}
        )
        return TaskSimpleResponse(**data)

    async def resume_task(self, task_id: str) -> TaskSimpleResponse:
        """Resume a paused task."""
        data = await self._make_request(
            "POST", "/resume-task", params={"task_id": task_id}
        )
        return TaskSimpleResponse(**data)

    # Task Media
    async def get_task_screenshots(self, task_id: str) -> TaskScreenshotsResponse:
        """Get screenshots from a task."""
        data = await self._make_request("GET", f"/task/{task_id}/screenshots")
        return TaskScreenshotsResponse(**data)

    async def get_task_gif(self, task_id: str) -> TaskGifResponse:
        """Get animated GIF of task execution."""
        data = await self._make_request("GET", f"/task/{task_id}/gif")
        return TaskGifResponse(**data)

    async def get_task_media(self, task_id: str) -> TaskMediaResponse:
        """Get media files from a task."""
        data = await self._make_request("GET", f"/task/{task_id}/media")
        return TaskMediaResponse(**data)

    # Scheduled Tasks
    async def create_scheduled_task(
        self, request: ScheduledTaskRequest
    ) -> ScheduledTaskResponse:
        """Create a scheduled task."""
        # Apply default model if none specified
        if not request.llm_model and self.default_model:
            request.llm_model = LLMModel(self.default_model)
        
        data = await self._make_request("POST", "/scheduled-task", data=request)
        return ScheduledTaskResponse(**data)

    async def update_scheduled_task(
        self, task_id: str, request: UpdateScheduledTaskRequest
    ) -> ScheduledTaskResponse:
        """Update a scheduled task."""
        # Apply default model if none specified
        if not request.llm_model and self.default_model:
            request.llm_model = LLMModel(self.default_model)
        
        data = await self._make_request(
            "PUT", f"/scheduled-task/{task_id}", data=request
        )
        return ScheduledTaskResponse(**data)

    async def delete_scheduled_task(self, task_id: str) -> Dict[str, str]:
        """Delete a scheduled task."""
        return await self._make_request("DELETE", f"/scheduled-task/{task_id}")

    async def list_scheduled_tasks(
        self, page: int = 1, per_page: int = 10
    ) -> ListScheduledTasksResponse:
        """List scheduled tasks."""
        params = {"page": page, "per_page": per_page}
        data = await self._make_request("GET", "/scheduled-tasks", params=params)
        return ListScheduledTasksResponse(**data)

    # User Management
    async def get_user_balance(self) -> CheckUserBalanceResponse:
        """Check account balance."""
        data = await self._make_request("GET", "/balance")
        return CheckUserBalanceResponse(**data)

    async def get_user_info(self) -> Dict[str, Any]:
        """Get user information."""
        return await self._make_request("GET", "/me")

    async def delete_browser_profile(self) -> Dict[str, str]:
        """Delete browser profile data."""
        return await self._make_request("POST", "/delete-browser-profile-for-user")

    # Health Check
    async def ping(self) -> Dict[str, str]:
        """Health check endpoint."""
        return await self._make_request("GET", "/ping")
