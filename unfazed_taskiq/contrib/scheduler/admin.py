from typing import Optional

from unfazed.contrib.admin.registry import ActionKwargs, ModelAdmin, register
from unfazed.contrib.admin.registry.decorators import action

from unfazed_taskiq.agent.handler import agents
from unfazed_taskiq.agent.model import TaskiqAgent

from . import serializer as s


@register(s.PeriodicTaskSerializer)
class PeriodicTaskAdmin(ModelAdmin):
    route_label: str = "TaskIQ"
    component: str = "ModelAdmin"

    list_display: list[str] = [
        "schedule_alias",
        "name",
        "description",
        "task_name",
        "task_args",
        "task_kwargs",
        "labels",
        "cron",
        "last_run_at",
        "time",
        "total_run_count",
        "enabled",
        "schedule_id",
        "created_at",
        "updated_at",
    ]
    list_order: list[str] = list_display
    datetime_fields: list[str] = [
        "created_at",
        "updated_at",
        "last_run_at",
    ]
    json_fields: list[str] = [
        "task_args",
        "task_kwargs",
        "labels",
    ]
    list_search: list[str] = [
        "schedule_alias",
        "name",
        "task_name",
        "last_run_at",
        "created_at",
        "updated_at",
    ]
    list_range_search: list[str] = [
        "created_at",
        "updated_at",
        "last_run_at",
    ]
    detail_display: list[str] = [
        "schedule_alias",
        "name",
        "description",
        "task_name",
        "task_args",
        "task_kwargs",
        "labels",
        "cron",
        "time",
        "last_run_at",
        "total_run_count",
        "enabled",
        "schedule_id",
    ]
    readonly_fields: list[str] = [
        "last_run_at",
        "total_run_count",
        "schedule_id",
    ]

    @action(
        name="async_now",
        batch=False,
    )
    async def async_now(self, ctx: ActionKwargs) -> dict:
        schedule_id = ctx.form_data.get("schedule_id")
        if not schedule_id:
            return {"code": 1, "message": "Schedule ID is required"}
        schedule_alias = ctx.form_data.get("schedule_alias")
        if not schedule_alias:
            return {
                "code": 1,
                "message": f"Schedule alias is required, schedule_id: {schedule_id}",
            }

        agent: Optional[TaskiqAgent] = agents.get_agent(schedule_alias)
        if agent is None:
            return {
                "code": 1,
                "message": f"Agent not found, schedule_id: {schedule_id}",
            }
        if agent.scheduler is None:
            return {
                "code": 1,
                "message": f"Scheduler not found, schedule_id: {schedule_id}",
            }
        await agent.scheduler.trigger_by_schedule_id(schedule_id)
        return {"code": 0, "message": f"Schedule triggered, schedule_id: {schedule_id}"}
