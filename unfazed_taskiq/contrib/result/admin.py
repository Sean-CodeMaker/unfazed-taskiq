from unfazed.contrib.admin.registry import ModelAdmin, register
from . import serializer as s


@register(s.UnfazedTaskiqResultSerializer)
class TaskResultAdmin(ModelAdmin):
    route_label: str = "TaskIQ"
    component: str = "ModelAdmin"
    can_add: bool = False
    can_delete: bool = False
    can_edit: bool = False

    list_display: list[str] = [
        "execution_time",
        "process_status",
        "started_at",
        "finished_at",
        "schedule_id",
        "schedule_alias",
        "task_id",
        "task_args",
        "task_kwargs",
        "labels",
        "cron",
        "time",
        "task_name",
        "result",
    ]
    list_order: list[str] = list_display
    datetime_fields: list[str] = [
        "started_at",
        "finished_at",
        "created_at",
        "updated_at",
    ]
    json_fields: list[str] = [
        "task_args",
        "task_kwargs",
        "labels",
        "result",
    ]
    list_search: list[str] = [
        "schedule_id",
        "schedule_alias",
        "task_id",
        "task_name",
        "execution_time",
        "process_status",
        "started_at",
        "finished_at",
        "created_at",
        "updated_at",
    ]
    list_range_search: list[str] = [
        "created_at",
        "updated_at",
        "started_at",
        "finished_at",
        "execution_time",
    ]
