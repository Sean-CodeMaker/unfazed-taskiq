import time
from typing import Any, Optional

import orjson as json
from taskiq.abc.result_backend import AsyncResultBackend
from taskiq.depends.progress_tracker import TaskProgress, TaskState
from taskiq.result import TaskiqResult

from unfazed_taskiq.contrib.result import models as m
from unfazed_taskiq.contrib.result.schema import (
    UnfazedTaskiqResultProgressSchema,
    UnfazedTaskiqResultSchema,
)


class UnfazedTaskiqResultBackend(AsyncResultBackend[Any]):
    """
    Unfazed Taskiq Result Backend using Tortoise ORM.

    Stores task execution results in the database.
    """

    async def startup(self) -> None:
        """Initialize the result backend (no-op for Tortoise ORM)."""
        pass

    async def shutdown(self) -> None:
        """Cleanup the result backend (no-op for Tortoise ORM)."""
        pass

    async def set_result(self, task_id: str, result: TaskiqResult[Any]) -> None:
        """
        Save task execution result to the database.

        :param task_id: Unique task identifier.
        :param result: TaskiqResult containing execution details.
        """
        finished_at = int(time.time())

        # Determine process status based on result
        if result.is_err:
            process_status = m.UnfazedTaskiqResult.ProcessStatusEnum.FAILED
        else:
            process_status = m.UnfazedTaskiqResult.ProcessStatusEnum.SUCCEEDED

        # Serialize the return value
        result_str: str = ""
        try:
            result_str = json.dumps(result.return_value).decode()
        except (TypeError, ValueError):
            result_str = json.dumps({"data": str(result.return_value)}).decode()

        # Update existing record or create new one
        await m.UnfazedTaskiqResult.filter(task_id=task_id).update(
            finished_at=finished_at,
            execution_time=result.execution_time,
            process_status=process_status,
            result=result_str,
        )

    async def is_result_ready(self, task_id: str) -> bool:
        """
        Check if the task result is ready.

        :param task_id: Unique task identifier.
        :return: True if the task has completed (success or failure).
        """
        record: Optional[m.UnfazedTaskiqResult] = await m.UnfazedTaskiqResult.filter(
            task_id=task_id
        ).first()
        if record is None:
            return False

        return (
            record.process_status
            != m.UnfazedTaskiqResult.ProcessStatusEnum.STARTED.value
        )

    async def get_result(
        self, task_id: str, with_logs: bool = False
    ) -> TaskiqResult[Any]:
        """
        Retrieve task execution result from the database.

        :param task_id: Unique task identifier.
        :param with_logs: Whether to include logs (deprecated, ignored).
        :return: TaskiqResult with execution details.
        """
        record: Optional[m.UnfazedTaskiqResult] = await m.UnfazedTaskiqResult.filter(
            task_id=task_id
        ).first()

        if record is None:
            return TaskiqResult(
                is_err=True,
                log=None,
                return_value=None,
                execution_time=0.0,
                labels={},
                error=ValueError(f"Task {task_id} not found"),
            )

        # Determine if task failed
        is_err = record.process_status == m.UnfazedTaskiqResult.ProcessStatusEnum.FAILED

        # Parse result
        return_value: Any = None
        error: Optional[BaseException] = None

        if record.result:
            try:
                return_value = json.loads(record.result.encode())
            except (json.JSONDecodeError, ValueError):
                return_value = record.result

        # Parse labels
        try:
            labels = json.loads(record.labels.encode()) if record.labels else {}
        except (json.JSONDecodeError, ValueError):
            labels = {}

        if is_err and return_value:
            error = Exception(str(return_value))
            return_value = None

        return TaskiqResult(
            is_err=is_err,
            log=None,
            return_value=return_value,
            execution_time=record.execution_time / 1000.0,  # Convert back to seconds
            labels=labels,
            error=error,
        )

    async def set_progress(self, task_id: str, progress: TaskProgress[Any]) -> None:
        """
        Update task progress in the database.

        :param task_id: Unique task identifier.
        :param progress: TaskProgress containing state and metadata.
        """
        # Map TaskState to ProcessStatusEnum
        state = progress.state
        if isinstance(state, TaskState):
            state_mapping = {
                TaskState.STARTED: m.UnfazedTaskiqResult.ProcessStatusEnum.PROCESSING,
                TaskState.SUCCESS: m.UnfazedTaskiqResult.ProcessStatusEnum.SUCCEEDED,
                TaskState.FAILURE: m.UnfazedTaskiqResult.ProcessStatusEnum.FAILED,
                TaskState.RETRY: m.UnfazedTaskiqResult.ProcessStatusEnum.PROCESSING,
            }
            process_status = state_mapping.get(
                state, m.UnfazedTaskiqResult.ProcessStatusEnum.PROCESSING
            )
        else:
            # Custom string state - treat as processing
            process_status = m.UnfazedTaskiqResult.ProcessStatusEnum.PROCESSING

        await m.UnfazedTaskiqResult.filter(task_id=task_id).update(
            process_status=process_status,
        )

    async def get_progress(
        self, task_id: str
    ) -> Optional[TaskProgress[UnfazedTaskiqResultProgressSchema]]:
        """
        Retrieve task progress from the database.

        :param task_id: Unique task identifier.
        :return: TaskProgress with current state, or None if task not found.
        """
        record = await m.UnfazedTaskiqResult.filter(task_id=task_id).first()

        if record is None:
            return None

        # Map ProcessStatusEnum to TaskState
        status_mapping = {
            m.UnfazedTaskiqResult.ProcessStatusEnum.PROCESSING: TaskState.STARTED,
            m.UnfazedTaskiqResult.ProcessStatusEnum.SUCCEEDED: TaskState.SUCCESS,
            m.UnfazedTaskiqResult.ProcessStatusEnum.FAILED: TaskState.FAILURE,
            m.UnfazedTaskiqResult.ProcessStatusEnum.CANCELLED: TaskState.FAILURE,
        }
        state = status_mapping.get(record.process_status, TaskState.STARTED)

        return TaskProgress(
            state=state,
            meta=UnfazedTaskiqResultProgressSchema(
                process_status=record.process_status.value,
            ),
        )
