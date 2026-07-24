from pydantic import BaseModel
from datetime import datetime
from schema.enums import IntervalUnit

class TaskReminderCreate(BaseModel):
    interval_value: int
    interval_unit: IntervalUnit

class TaskReminderOut(BaseModel):
    id: str
    task_id: str
    user_id: str
    interval_value: int
    interval_unit: IntervalUnit
    next_run_at: datetime

    class Config:
        from_attributes = True
