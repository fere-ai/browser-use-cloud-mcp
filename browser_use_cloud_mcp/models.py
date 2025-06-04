"""Data models for Browser Use Cloud API."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class LLMModel(str, Enum):
    """Available LLM models."""

    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_1 = "gpt-4.1"
    GPT_4_1_MINI = "gpt-4.1-mini"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"
    GEMINI_2_5_FLASH_PREVIEW = "gemini-2.5-flash-preview-04-17"
    CLAUDE_3_7_SONNET = "claude-3-7-sonnet-20250219"
    CLAUDE_SONNET_4 = "claude-sonnet-4-20250514"
    LLAMA_4_MAVERICK = "llama-4-maverick-17b-128e-instruct"


class ScheduleType(str, Enum):
    """Schedule types for scheduled tasks."""

    INTERVAL = "interval"
    CRON = "cron"


class TaskStatusEnum(str, Enum):
    """Task status enumeration."""

    CREATED = "created"
    RUNNING = "running"
    FINISHED = "finished"
    STOPPED = "stopped"
    PAUSED = "paused"
    FAILED = "failed"


class RunTaskRequest(BaseModel):
    """Request model for running a task."""

    task: str
    secrets: Optional[Dict[str, str]] = None
    allowed_domains: Optional[List[str]] = None
    save_browser_data: Optional[bool] = False
    structured_output_json: Optional[str] = None
    llm_model: Optional[LLMModel] = None
    use_adblock: Optional[bool] = True
    use_proxy: Optional[bool] = True
    highlight_elements: Optional[bool] = True


class TaskCreatedResponse(BaseModel):
    """Response model for task creation."""

    task_id: str


class TaskSimpleResponse(BaseModel):
    """Simple task response model."""

    task_id: str
    status: TaskStatusEnum


class TaskResponse(BaseModel):
    """Full task response model."""

    task_id: str
    status: TaskStatusEnum
    created_at: str
    updated_at: str
    task: str
    result: Optional[str] = None
    error: Optional[str] = None


class TaskStepResponse(BaseModel):
    """Task step response model."""

    step_id: str
    step_number: int
    action: str
    screenshot_url: Optional[str] = None
    timestamp: str


class TaskBrowserDataResponse(BaseModel):
    """Task browser data response."""

    cookies: Optional[List[Dict[str, Any]]] = None
    local_storage: Optional[Dict[str, str]] = None
    session_storage: Optional[Dict[str, str]] = None


class TaskScreenshotsResponse(BaseModel):
    """Task screenshots response."""

    screenshots: List[str]


class TaskGifResponse(BaseModel):
    """Task GIF response."""

    gif_url: str


class TaskMediaResponse(BaseModel):
    """Task media response."""

    media_files: List[str]


class ScheduledTaskRequest(BaseModel):
    """Request model for creating scheduled task."""

    name: str
    task: str
    schedule_type: ScheduleType
    schedule_value: str
    secrets: Optional[Dict[str, str]] = None
    allowed_domains: Optional[List[str]] = None
    save_browser_data: Optional[bool] = False
    structured_output_json: Optional[str] = None
    llm_model: Optional[LLMModel] = None
    use_adblock: Optional[bool] = True
    use_proxy: Optional[bool] = True
    highlight_elements: Optional[bool] = True


class UpdateScheduledTaskRequest(BaseModel):
    """Request model for updating scheduled task."""

    name: Optional[str] = None
    task: Optional[str] = None
    schedule_type: Optional[ScheduleType] = None
    schedule_value: Optional[str] = None
    secrets: Optional[Dict[str, str]] = None
    allowed_domains: Optional[List[str]] = None
    save_browser_data: Optional[bool] = None
    structured_output_json: Optional[str] = None
    llm_model: Optional[LLMModel] = None
    use_adblock: Optional[bool] = None
    use_proxy: Optional[bool] = None
    highlight_elements: Optional[bool] = None


class ScheduledTaskResponse(BaseModel):
    """Response model for scheduled task."""

    task_id: str
    name: str
    task: str
    schedule_type: ScheduleType
    schedule_value: str
    created_at: str
    updated_at: str
    next_run: Optional[str] = None
    last_run: Optional[str] = None
    status: str


class ListTasksResponse(BaseModel):
    """Response model for listing tasks."""

    tasks: List[TaskResponse]
    total: int
    page: int
    per_page: int


class ListScheduledTasksResponse(BaseModel):
    """Response model for listing scheduled tasks."""

    scheduled_tasks: List[ScheduledTaskResponse]
    total: int
    page: int
    per_page: int


class CheckUserBalanceResponse(BaseModel):
    """Response model for user balance."""

    balance: float
    currency: str


class ValidationError(BaseModel):
    """Validation error model."""

    loc: List[str]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    """HTTP validation error model."""

    detail: List[ValidationError]
