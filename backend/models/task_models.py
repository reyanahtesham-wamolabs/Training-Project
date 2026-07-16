from pydantic import  BaseModel,Field
import uuid
from datetime import date
from schema.enums import ProjectStatus as Status,Levels
from helper_functions.validators import non_empty_value

class Task(BaseModel):
    name : non_empty_value
    schedule_date:date |None=None
    status:Status
    soft_delete:bool |None=False
    priority:Levels
    project_id:non_empty_value
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))    
   

class TaskCreation(BaseModel):
    name : non_empty_value
    schedule_date:date |None=None
    status:Status
    priority:Levels
    project_id:non_empty_value

class TaskUpdate(BaseModel):
    name : str |None=None
    schedule_date:date |None=None
    status:Status |None=None
    soft_delete:bool |None=None
    priority:Levels |None=None
    id: non_empty_value 

