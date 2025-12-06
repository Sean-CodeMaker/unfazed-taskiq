from typing import List

from taskiq import ScheduledTask
from taskiq.abc.broker import AsyncBroker
from taskiq.scheduler.scheduler import TaskiqScheduler
from unfazed.type import t

from unfazed_taskiq.contrib.scheduler import TortoiseScheduleSource


class UnfazedTaskiqScheduler(TaskiqScheduler):
    def __init__(
        self,
        broker: "AsyncBroker",
        sources: List["TortoiseScheduleSource"],
    ) -> None:  # pragma: no cover
        super().__init__(broker, sources)

    async def trigger_by_schedule_id(self, schedule_id: str):
        source: t.Optional["TortoiseScheduleSource"] = None
        for source in self.sources:
            if not isinstance(source, TortoiseScheduleSource):
                continue
            schedule: t.Optional["ScheduledTask"] = await source.get_schedule_by_id(
                schedule_id
            )
            if schedule is not None:
                await self.on_ready(source, schedule)
                break
        else:
            raise ValueError(f"Schedule {schedule_id} not found")
