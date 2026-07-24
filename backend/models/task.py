from pydantic import BaseModel, Field, ConfigDict
import uuid
from datetime import date
from schema.enums import ProjectStatus as Status,Levels
from helper_functions.validators import non_empty_value

class Task(BaseModel):
    name : non_empty_value
    schedule_date:date |None=None
    due_date:date |None=None
    status:Status
    soft_delete:bool |None=False
    priority:Levels
    project_id:non_empty_value
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))    


class TaskCreation(BaseModel):
    name : non_empty_value
    schedule_date:date |None=None
    due_date:date |None=None
    status:Status
    priority:Levels
    project_id:non_empty_value

class TaskUpdate(BaseModel):
    name : str |None=None
    schedule_date:date |None=None
    due_date:date |None=None
    status:Status |None=None
    soft_delete:bool |None=None
    priority:Levels |None=None
    id: non_empty_value 

class TaskActionResponse(BaseModel):
    status: str
    task_id: str

class TaskPrerequisiteOut(BaseModel):
    id: str
    name: str
    status: str

    model_config = ConfigDict(from_attributes=True)

class TaskAssignmentOut(BaseModel):
    id: str
    user_id: str
    user_email: str
    user_name: str

    model_config = ConfigDict(from_attributes=True)

class TaskOut(BaseModel):
    id: str
    name: str
    schedule_date: date | None = None
    due_date: date | None = None
    status: str
    priority: str
    project_id: str
    soft_delete: bool = False
    prerequisites: list[TaskPrerequisiteOut] = []
    assignments: list[TaskAssignmentOut] = []
    assigned_user_ids: list[str] = []
    assigned_user_emails: list[str] = []
    assigned_user_names: list[str] = []

    model_config = ConfigDict(from_attributes=True)

