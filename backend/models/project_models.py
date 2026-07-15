from pydantic import BaseModel,Field
import uuid
from datetime import date
from schema.enums import ProjectStatus,Categories

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))    
    name : str
    soft_delete:bool |None=False
    start_date:date 
    end_date:date 
    archived:bool
    category:Categories
    status:ProjectStatus
    
class CreateProject(BaseModel):
    name : str
    start_date:date 
    end_date:date 
    archived:bool
    category:Categories
    status:ProjectStatus
class CreateTag(BaseModel):
    name:str

class Tag(BaseModel):
    name:str
    id:str=Field(default_factory=lambda:str(uuid.uuid4()))