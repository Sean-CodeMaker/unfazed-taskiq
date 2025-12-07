from pydantic import BaseModel


class UnfazedTaskiqResultSchema(BaseModel):
    started_at: int = 0
    finished_at: int = 0
    execution_time: int = 0
    process_status: int = 0
    schedule_id: str = ""
    schedule_alias: str = ""
    task_id: str = ""
    task_args: str = "[]"
    task_kwargs: str = "{}"
    labels: str = "{}"
    cron: str | None
    time: str | None
    task_name: str = ""
    result: str | dict | list | None


class UnfazedTaskiqResultProgressSchema(BaseModel):
    process_status: int = 0
