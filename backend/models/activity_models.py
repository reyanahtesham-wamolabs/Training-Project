from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ActivityLogOut(BaseModel):
    id: str
    action_type: str
    message: str
    modified_by_user_id: str
    task_id: str | None = None
    project_id: str | None = None
    change_time: datetime

    model_config = ConfigDict(from_attributes=True)
