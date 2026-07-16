from pydantic import  EmailStr, BaseModel,field_validator,Field,ConfigDict
import uuid
from schema.enums import Roles,Levels,AssignmentRole
class User(BaseModel):
    name : str
    email: str 
    password:str
    role:Roles
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))    
    


class CreateUser(BaseModel):
    email:EmailStr
    password:str=Field(pattern=r"^[A-Za-z0-9_]{3,20}$")
    name:str
    role:Roles
    @field_validator("email")
    @classmethod
    def emailValidator(cls,value):
        if value.rsplit("@", 1)[1].lower() != "wamolabs.com":
            raise ValueError("the email must include '@wamolabs.com'")
        return value
    
class UserLogin(BaseModel):
    email:str
    password:str 

class UserResponse(BaseModel):
    id:str
    name:str
    role:Roles
    active:bool
    email:EmailStr
    privacy_level:Levels
    soft_delete:bool
    model_config = ConfigDict(from_attributes=True)

class UserPrivacy(BaseModel):
    level:Levels

class CreateAssignUser(BaseModel):
    user_Email:EmailStr
    task_id:str
    project_name:str
    role:AssignmentRole
class AssignUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))    
    user_Email:EmailStr
    task_id:str
    project_name:str
    role:AssignmentRole