from pydantic import  BaseModel,Field
import uuid
from datetime import date
from schema.enums import ProjectStatus as Status,Levels

class Task(BaseModel):
    name : str
    schedule_date:date |None=None
    status:Status
    soft_delete:bool |None=False
    priority:Levels
    project_id:str
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))    

class TaskCreation(BaseModel):
    name : str
    schedule_date:date |None=None
    status:Status
    priority:Levels
    project_id:str

class TaskUpdate(BaseModel):
    name : str |None=None
    schedule_date:date |None=None
    status:Status |None=None
    soft_delete:bool |None=None
    priority:Levels |None=None
    id: str 

