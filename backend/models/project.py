from pydantic import BaseModel, Field, ConfigDict
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

class ProjectUpdate(BaseModel):
    id: non_empty_value
    name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    category: Categories | None = None
    status: ProjectStatus | None = None
    tags: list[str] | None = None

class CreateProject(BaseModel):
    name : non_empty_value
    start_date:date 
    end_date:date 
    archived:bool
    category:Categories
    status:ProjectStatus
    tags: list[str] | None = None
class CreateTag(BaseModel):
    name:non_empty_value
class AddTagToProject(BaseModel):
    project_id:str
    tag_id:str
class Tag(BaseModel):
    name:non_empty_value
    id:str=Field(default_factory=lambda:str(uuid.uuid4()))

class ProjectActionResponse(BaseModel):
    status: str
    project_id: str

class TagActionResponse(BaseModel):
    status: str
    tag_id: str

class TagOut(BaseModel):
    id: str
    name: str

    model_config = ConfigDict(from_attributes=True)

class ProjectOut(BaseModel):
    id: str
    name: str
    start_date: date
    end_date: date
    status: str
    category: str
    archived: bool
    soft_delete: bool = False
    tags: list[str] = []

    model_config = ConfigDict(from_attributes=True)

class ArchiveResponse(BaseModel):
    status: str
    project_id: str
    archived: bool