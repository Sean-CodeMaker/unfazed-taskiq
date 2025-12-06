import datetime
import json
from typing import Optional

from pydantic import model_validator
from unfazed.serializer import Serializer

from . import models as m


class PeriodicTaskSerializer(Serializer):
    class Meta:
        model = m.PeriodicTask

    @model_validator(mode="before")
    @classmethod
    def validator_all_data(cls, data: dict) -> dict:
        if data.get("task_kwargs"):
            try:
                json.loads(data["task_kwargs"])
            except json.JSONDecodeError:
                raise ValueError("task_kwargs is not a valid JSON string")
        if data.get("task_args"):
            try:
                json.loads(data["task_args"])
            except json.JSONDecodeError:
                raise ValueError("task_args is not a valid JSON string")
        if data.get("labels"):
            try:
                json.loads(data["labels"])
            except json.JSONDecodeError:
                raise ValueError("labels is not a valid JSON string")

        cron: Optional[str] = data.get("cron")
        time: Optional[datetime] = data.get("time")
        if cron is None and time is None:
            raise ValueError("cron or time is required")

        return data
