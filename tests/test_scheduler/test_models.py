import json
from typing import Optional

from taskiq import ScheduledTask

from unfazed_taskiq.contrib.scheduler.models import PeriodicTask
from unfazed_taskiq.contrib.scheduler.serializer import PeriodicTaskSerializer


class TestPeriodicTaskModel(object):
    async def test_periodic_task_model(
        self, test_scheduler_sample_data: list[dict]
    ) -> None:
        assert test_scheduler_sample_data is not None
        assert len(test_scheduler_sample_data) == 4

        db_data = await PeriodicTask.filter().all()

        assert len(db_data) == 4

        db_task_names = {item.task_name for item in db_data}
        sample_task_names = {item["task_name"] for item in test_scheduler_sample_data}
        assert db_task_names == sample_task_names

        db_task_corns = {item.cron for item in db_data}
        sample_task_corns = {item["cron"] for item in test_scheduler_sample_data}
        assert db_task_corns == sample_task_corns

        db_task_kwargs = {item.task_kwargs for item in db_data}
        sample_task_kwargs = {
            item["task_kwargs"] for item in test_scheduler_sample_data
        }
        assert db_task_kwargs == sample_task_kwargs

        db_task_schedule_aliases = {item.schedule_alias for item in db_data}
        sample_task_schedule_aliases = {
            item["schedule_alias"] for item in test_scheduler_sample_data
        }
        assert db_task_schedule_aliases == sample_task_schedule_aliases

    async def test_periodic_task_model_to_taskiq_schedule_task(
        self, test_scheduler_sample_data: list[dict]
    ) -> None:
        assert test_scheduler_sample_data is not None
        assert len(test_scheduler_sample_data) == 4

        for item in test_scheduler_sample_data:
            pt_objs: Optional[PeriodicTask] = await PeriodicTask.filter(
                task_name=item["task_name"]
            ).first()
            assert pt_objs is not None
            schedule_data: ScheduledTask = pt_objs.to_taskiq_schedule_task()
            assert schedule_data.cron == item["cron"]
            assert schedule_data.task_name == item["task_name"]
            assert schedule_data.args == json.loads(item["task_args"])
            assert schedule_data.kwargs == json.loads(item["task_kwargs"])
            assert schedule_data.labels == json.loads(item["labels"])
            assert schedule_data.schedule_id == item["schedule_id"]

    async def test_periodic_task_model_to_taskiq_schedule_task_with_time(self) -> None:
        """Test to_taskiq_schedule_task method with time-based scheduling."""
        from datetime import datetime, timezone

        # Create a PeriodicTask with time-based scheduling (no cron)
        task_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        periodic_task = await PeriodicTask.create(
            task_name="test.time_task",
            task_args="[]",
            task_kwargs="{}",
            labels="{}",
            time=task_time,  # Set time instead of cron
            cron=None,  # Explicitly set cron to None
        )

        # Test the conversion
        scheduled_task = periodic_task.to_taskiq_schedule_task()

        # Verify the scheduled task properties
        assert scheduled_task.task_name == "test.time_task"
        assert scheduled_task.args == []
        assert scheduled_task.kwargs == {}
        assert scheduled_task.labels == {}
        assert scheduled_task.time == task_time
        assert scheduled_task.cron is None
        assert scheduled_task.schedule_id == periodic_task.schedule_id

    async def test_periodic_task_model_to_taskiq_schedule_task_no_schedule_error(
        self,
    ) -> None:
        """Test to_taskiq_schedule_task method raises RuntimeError when no schedule is found."""
        import pytest

        # Create a PeriodicTask with neither cron nor time
        periodic_task = await PeriodicTask.create(
            task_name="test.no_schedule_task",
            task_args="[]",
            task_kwargs="{}",
            labels="{}",
            cron=None,
            time=None,
        )

        # Test that RuntimeError is raised
        with pytest.raises(RuntimeError, match="No schedule found"):
            periodic_task.to_taskiq_schedule_task()

    async def test_periodic_task_model_to_taskiq_schedule_task_invalid_json_error(
        self,
    ) -> None:
        """Test to_taskiq_schedule_task method raises RuntimeError when JSON is invalid."""
        import pytest

        # Create a PeriodicTask with invalid JSON in task_args
        periodic_task = await PeriodicTask.create(
            task_name="test.invalid_json_task",
            task_args="{invalid_json}",  # Invalid JSON
            task_kwargs="{}",
            labels="{}",
            cron="* * * * *",
        )

        # Test that RuntimeError is raised
        with pytest.raises(RuntimeError, match="Invalid JSON in task"):
            periodic_task.to_taskiq_schedule_task()


class TestPeriodicTaskSerializer(object):
    async def test_periodic_task_serializer(
        self, test_scheduler_sample_data: list[dict]
    ) -> None:
        assert test_scheduler_sample_data is not None
        assert len(test_scheduler_sample_data) == 4

        result = await PeriodicTaskSerializer.list(
            PeriodicTask.filter(), page=1, size=2
        )
        assert result is not None
        assert len(result.data) == 2

    async def test_validator_accepts_valid_json_strings(self) -> None:
        """Test that validator accepts valid JSON strings for task_kwargs, task_args, and labels."""
        valid_data = {
            "task_name": "test.task",
            "task_kwargs": '{"key": "value"}',
            "task_args": '["arg1", "arg2"]',
            "labels": '{"label1": "value1"}',
            "cron": "* * * * *",
        }
        # Use model_validate to trigger the validator
        serializer = PeriodicTaskSerializer.model_validate(valid_data)
        assert serializer.task_name == valid_data["task_name"]
        assert serializer.task_kwargs == valid_data["task_kwargs"]
        assert serializer.task_args == valid_data["task_args"]
        assert serializer.labels == valid_data["labels"]

    async def test_validator_accepts_none_json_fields(self) -> None:
        """Test that validator accepts None values for JSON fields (skips validation)."""
        data_with_none_fields = {
            "task_name": "test.task",
            "task_args": "[]",
            "task_kwargs": "{}",
            "labels": "{}",
            "cron": "* * * * *",
        }
        # Use model_validate to trigger the validator - should not raise
        serializer = PeriodicTaskSerializer.model_validate(data_with_none_fields)
        assert serializer.task_name == data_with_none_fields["task_name"]

    async def test_validator_rejects_invalid_task_kwargs(self) -> None:
        """Test that validator rejects invalid JSON in task_kwargs."""
        import pytest
        from pydantic import ValidationError

        invalid_data = {
            "task_name": "test.task",
            "task_kwargs": "{invalid}",
        }
        with pytest.raises(
            ValidationError, match="task_kwargs is not a valid JSON string"
        ):
            PeriodicTaskSerializer.model_validate(invalid_data)

    async def test_validator_rejects_invalid_task_args(self) -> None:
        """Test that validator rejects invalid JSON in task_args."""
        import pytest
        from pydantic import ValidationError

        invalid_data = {
            "task_name": "test.task",
            "task_args": "{invalid}",
        }
        with pytest.raises(
            ValidationError, match="task_args is not a valid JSON string"
        ):
            PeriodicTaskSerializer.model_validate(invalid_data)

    async def test_validator_rejects_invalid_labels(self) -> None:
        """Test that validator rejects invalid JSON in labels."""
        import pytest
        from pydantic import ValidationError

        invalid_data = {
            "task_name": "test.task",
            "labels": "{invalid}",
        }
        with pytest.raises(ValidationError, match="labels is not a valid JSON string"):
            PeriodicTaskSerializer.model_validate(invalid_data)

    async def test_validator_rejects_missing_cron_and_time(self) -> None:
        """Test that validator rejects data without cron or time."""
        import pytest
        from pydantic import ValidationError

        invalid_data = {
            "task_name": "test.task",
            "task_args": "[]",
            "task_kwargs": "{}",
            "labels": "{}",
            # No cron or time provided
        }
        with pytest.raises(ValidationError, match="cron or time is required"):
            PeriodicTaskSerializer.model_validate(invalid_data)
