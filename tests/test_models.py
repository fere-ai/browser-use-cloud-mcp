"""Tests for data models."""

import pytest
from pydantic import ValidationError

from browser_use_cloud_mcp.models import (
    LLMModel,
    RunTaskRequest,
    ScheduledTaskRequest,
    ScheduleType,
    TaskStatusEnum,
    UpdateScheduledTaskRequest,
)


class TestEnums:
    """Test enum classes."""

    def test_llm_model_values(self):
        """Test LLM model enum values."""
        assert LLMModel.GPT_4O == "gpt-4o"
        assert LLMModel.CLAUDE_SONNET_4 == "claude-sonnet-4-20250514"
        assert LLMModel.GEMINI_2_0_FLASH == "gemini-2.0-flash"

    def test_schedule_type_values(self):
        """Test schedule type enum values."""
        assert ScheduleType.INTERVAL == "interval"
        assert ScheduleType.CRON == "cron"

    def test_task_status_values(self):
        """Test task status enum values."""
        assert TaskStatusEnum.CREATED == "created"
        assert TaskStatusEnum.RUNNING == "running"
        assert TaskStatusEnum.FINISHED == "finished"
        assert TaskStatusEnum.STOPPED == "stopped"
        assert TaskStatusEnum.PAUSED == "paused"
        assert TaskStatusEnum.FAILED == "failed"


class TestRunTaskRequest:
    """Test RunTaskRequest model."""

    def test_minimal_valid_request(self):
        """Test minimal valid run task request."""
        request = RunTaskRequest(task="Test task")
        assert request.task == "Test task"
        assert request.secrets is None
        assert request.allowed_domains is None
        assert request.save_browser_data is False
        assert request.use_adblock is True
        assert request.use_proxy is True
        assert request.highlight_elements is True

    def test_full_valid_request(self):
        """Test full run task request with all fields."""
        request = RunTaskRequest(
            task="Test task",
            secrets={"api_key": "secret"},
            allowed_domains=["example.com"],
            save_browser_data=True,
            structured_output_json='{"type": "object"}',
            llm_model=LLMModel.GPT_4O,
            use_adblock=False,
            use_proxy=False,
            highlight_elements=False,
        )
        assert request.task == "Test task"
        assert request.secrets == {"api_key": "secret"}
        assert request.allowed_domains == ["example.com"]
        assert request.save_browser_data is True
        assert request.structured_output_json == '{"type": "object"}'
        assert request.llm_model == LLMModel.GPT_4O
        assert request.use_adblock is False
        assert request.use_proxy is False
        assert request.highlight_elements is False

    def test_invalid_request_missing_task(self):
        """Test validation error when task is missing."""
        with pytest.raises(ValidationError) as exc_info:
            RunTaskRequest()

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert "task" in errors[0]["loc"]


class TestScheduledTaskRequest:
    """Test ScheduledTaskRequest model."""

    def test_minimal_valid_request(self):
        """Test minimal valid scheduled task request."""
        request = ScheduledTaskRequest(
            name="Test",
            task="Test task",
            schedule_type=ScheduleType.INTERVAL,
            schedule_value="1h",
        )
        assert request.name == "Test"
        assert request.task == "Test task"
        assert request.schedule_type == ScheduleType.INTERVAL
        assert request.schedule_value == "1h"

    def test_cron_schedule_type(self):
        """Test scheduled task with cron schedule."""
        request = ScheduledTaskRequest(
            name="Test",
            task="Test task",
            schedule_type=ScheduleType.CRON,
            schedule_value="0 9 * * 1-5",
        )
        assert request.schedule_type == ScheduleType.CRON
        assert request.schedule_value == "0 9 * * 1-5"

    def test_invalid_request_missing_required_fields(self):
        """Test validation error when required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            ScheduledTaskRequest()

        errors = exc_info.value.errors()
        assert len(errors) == 4  # name, task, schedule_type, schedule_value
        required_fields = {"name", "task", "schedule_type", "schedule_value"}
        error_fields = {error["loc"][0] for error in errors}
        assert error_fields == required_fields


class TestUpdateScheduledTaskRequest:
    """Test UpdateScheduledTaskRequest model."""

    def test_empty_request(self):
        """Test empty update request (all fields optional)."""
        request = UpdateScheduledTaskRequest()
        assert request.name is None
        assert request.task is None
        assert request.schedule_type is None
        assert request.schedule_value is None

    def test_partial_update(self):
        """Test partial update with some fields."""
        request = UpdateScheduledTaskRequest(
            name="Updated name",
            schedule_type=ScheduleType.CRON,
        )
        assert request.name == "Updated name"
        assert request.schedule_type == ScheduleType.CRON
        assert request.task is None
        assert request.schedule_value is None

    @pytest.mark.parametrize(
        "field_name,field_value",
        [
            ("name", "Test Name"),
            ("task", "Test Task"),
            ("schedule_type", ScheduleType.INTERVAL),
            ("schedule_value", "2h"),
            ("secrets", {"key": "value"}),
            ("allowed_domains", ["example.com"]),
            ("save_browser_data", True),
            ("structured_output_json", '{"schema": "test"}'),
            ("llm_model", LLMModel.GPT_4O_MINI),
            ("use_adblock", False),
            ("use_proxy", False),
            ("highlight_elements", False),
        ],
    )
    def test_individual_field_updates(self, field_name, field_value):
        """Test updating individual fields."""
        kwargs = {field_name: field_value}
        request = UpdateScheduledTaskRequest(**kwargs)
        assert getattr(request, field_name) == field_value
