from pydantic import BaseModel,Field
import uuid
from datetime import date
from schema.enums import ProjectStatus,Categories
from helper_functions.validators import email_value,password_value,non_empty_value

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))    
    name : non_empty_value
    soft_delete:bool |None=False
    start_date:date 
    end_date:date 
    archived:bool
    category:Categories
    status:ProjectStatus

class ArchiveProject(BaseModel):
    id:non_empty_value
    archive:bool
class CreateProject(BaseModel):
    name : non_empty_value
    start_date:date 
    end_date:date 
    archived:bool
    category:Categories
    status:ProjectStatus
class CreateTag(BaseModel):
    name:non_empty_value

class Tag(BaseModel):
    name:non_empty_value
    id:str=Field(default_factory=lambda:str(uuid.uuid4()))