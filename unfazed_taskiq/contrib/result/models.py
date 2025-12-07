from enum import IntEnum
from tortoise import fields
from unfazed_taskiq.base_model import BaseModel


class UnfazedTaskiqResult(BaseModel):
    class Meta:
        table = "unfazed_taskiq_result"

    class ProcessStatusEnum(IntEnum):
        PROCESSING = 0
        SUCCEEDED = 1
        FAILED = 2
        CANCELLED = 3

    started_at = fields.IntField(
        description="The started timestamp of the task.",
    )
    finished_at = fields.IntField(
        description="The finished timestamp of the task.",
        default=0,
    )
    execution_time = fields.IntField(
        description="The execution time of the task.",
        default=0,
    )

    process_status = fields.IntEnumField(
        enum_type=ProcessStatusEnum,
        default=ProcessStatusEnum.PROCESSING.value,
        description="The process status of the task.",
    )
    schedule_id = fields.CharField(
        max_length=255,
        description="The id of the schedule.",
        default="",
    )
    schedule_alias = fields.CharField(
        max_length=255,
        description="The alias of the schedule.",
        default="",
    )

    task_id = fields.CharField(
        max_length=255,
        description="The id of the task.",
    )
    task_args = fields.TextField(
        description="The args of the task.",
        default="[]",
    )
    task_kwargs = fields.TextField(
        description="The kwargs of the task.",
        default="{}",
    )
    labels = fields.TextField(
        description="The labels of the task.",
        default="{}",
    )
    cron = fields.CharField(
        max_length=255,
        description="The cron of the task.",
        null=True,
        default=None,
    )
    time = fields.DatetimeField(
        description="The time of the task.",
        null=True,
        default=None,
    )

    task_name = fields.CharField(
        max_length=255,
        description="The name of the task.",
    )

    result = fields.TextField(
        description="The result of the task.",
        default="",
    )
