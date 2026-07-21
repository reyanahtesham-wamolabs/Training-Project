from datetime import datetime
from pydantic import BaseModel

class NotificationOut(BaseModel):
    id: str
    user_id: str
    related_task_id: str | None
    related_comment_id: str | None
    related_project_id: str | None
    related_message_id: str | None
    subject: str
    text: str
    delivered: datetime
    read: bool
    read_at: datetime | None

    class Config:
        from_attributes = True
