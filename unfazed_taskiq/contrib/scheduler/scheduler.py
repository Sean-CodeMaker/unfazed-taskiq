from typing import List, Optional

from taskiq import ScheduledTask
from taskiq.abc.broker import AsyncBroker
from taskiq.abc.schedule_source import ScheduleSource
from taskiq.scheduler.scheduler import TaskiqScheduler

from unfazed_taskiq.contrib.scheduler import TortoiseScheduleSource


class UnfazedTaskiqScheduler(TaskiqScheduler):
    def __init__(
        self,
        broker: "AsyncBroker",
        sources: List["ScheduleSource"],
    ) -> None:  # pragma: no cover
        super().__init__(broker, sources)

    async def trigger_by_schedule_id(self, schedule_id: str) -> None:
        for s in self.sources:
            if not isinstance(s, TortoiseScheduleSource):
                continue
            schedule: Optional["ScheduledTask"] = await s.get_schedule_by_id(
                schedule_id
            )
            if schedule is not None:
                await self.on_ready(s, schedule)
                break
        else:
            raise ValueError(f"Schedule {schedule_id} not found")
