from pydantic import (
    EmailStr,
    BaseModel,
    field_validator,
    Field,
    ConfigDict,
    AfterValidator,
)
import uuid
from schema.enums import Roles, Levels, AssignmentRole
from typing import Annotated
import re
from helper_functions.validators import email_value, password_value, non_empty_value


class User(BaseModel):
    name: non_empty_value
    email: email_value
    password: password_value
    verified: bool
    role: Roles
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class CreateUser(BaseModel):
    email: email_value
    password: password_value
    name: non_empty_value


class ChangePassword(BaseModel):
    current_password: non_empty_value
    new_password: password_value


class ChangeEmail(BaseModel):
    new_email: email_value


class ChangeName(BaseModel):
    new_name: non_empty_value


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    role: Roles
    active: bool
    email: str
    privacy_level: Levels
    soft_delete: bool
    model_config = ConfigDict(from_attributes=True)


class UserPrivacy(BaseModel):
    level: Levels


class CreateAssignUser(BaseModel):
    user_email: email_value
    task_id: non_empty_value
    role: AssignmentRole


class AssignUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_email: email_value
    task_id: non_empty_value
    role: AssignmentRole


class ChangeUserRole(BaseModel):
    user_email: email_value
    user_role: Roles

class VerifyOTP(BaseModel):
    otp_code:str
    user_email:str