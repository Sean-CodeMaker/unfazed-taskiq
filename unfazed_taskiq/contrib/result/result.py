from typing import Any
from taskiq.abc.result_backend import AsyncResultBackend
from taskiq.depends.progress_tracker import TaskProgress
from taskiq.result import TaskiqResult

from unfazed_taskiq.contrib.result.schema import (
    UnfazedTaskiqResultProgressSchema,
    UnfazedTaskiqResultSchema,
)


class UnfazedTaskiqResult(AsyncResultBackend[UnfazedTaskiqResultSchema]):

    async def startup(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def set_result(
        self, task_id: str, result: TaskiqResult[UnfazedTaskiqResultSchema]
    ) -> None:
        pass

    async def is_result_ready(self, task_id: str) -> bool:
        pass

    async def get_result(
        self, task_id: str, with_logs: bool = False
    ) -> TaskiqResult[UnfazedTaskiqResultSchema]:
        pass

    async def set_progress(
        self, task_id: str, progress: TaskProgress[UnfazedTaskiqResultProgressSchema]
    ) -> None:
        pass

    async def get_progress(
        self, task_id: str
    ) -> TaskProgress[UnfazedTaskiqResultProgressSchema]:
        pass
