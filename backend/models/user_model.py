from pydantic import  EmailStr, BaseModel,field_validator,Field,ConfigDict,AfterValidator
import uuid
from schema.enums import Roles,Levels,AssignmentRole
from typing import Annotated
import re

def check_email(value:str):
    EMAIL_REGEX = re.compile(
    r"^[a-zA-Z][a-zA-Z0-9_.+-]*@wamolabs\.com$"
    )
    ALLOWED_DOMAIN="wamolabs.com"
    value = value.strip().lower()

    if not EMAIL_REGEX.match(value):
        raise ValueError(
            f"Email must be a valid {ALLOWED_DOMAIN} address"
        )

    domain = value.split("@")[-1]
    if domain != ALLOWED_DOMAIN:
        raise ValueError(f"Only {ALLOWED_DOMAIN} email addresses are allowed")
    return value


def check_password(value: str) -> str:
    MIN_LENGTH = 8

    if not (MIN_LENGTH <= len(value)):
        raise ValueError(
            f"Password must be longer than 8 Charecters"
        )

    if not re.search(r"[a-z]", value):
        raise ValueError("Password must contain at least one lowercase letter")

    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain at least one uppercase letter")

    if not re.search(r"\d", value):
        raise ValueError("Password must contain at least one number")

    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", value):
        raise ValueError("Password must contain at least one special character")

    if re.search(r"\s", value):
        raise ValueError("Password must not contain whitespace")

    return value

email_value=Annotated[str,AfterValidator(check_email)]
password_value=Annotated[str,AfterValidator(check_password)]

class User(BaseModel):
    name : str
    email: email_value 
    password:password_value
    role:Roles
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))    
    
class CreateUser(BaseModel):
    email:email_value
    password:password_value
    name:str
    role:Roles
    
class UserLogin(BaseModel):
    email:str
    password:str 

class UserResponse(BaseModel):
    id:str
    name:email_value
    role:Roles
    active:bool
    email:EmailStr
    privacy_level:Levels
    soft_delete:bool
    model_config = ConfigDict(from_attributes=True)

class UserPrivacy(BaseModel):
    level:Levels

class CreateAssignUser(BaseModel):
    user_email:email_value
    task_id:str
    project_name:str
    role:AssignmentRole
class AssignUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))    
    user_email:email_value
    task_id:str
    project_name:str
    role:AssignmentRole
