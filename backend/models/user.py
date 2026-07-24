from pydantic import (
    EmailStr,
    BaseModel,
    field_validator,
    Field,
    ConfigDict,
    AfterValidator,
)
import uuid
from schema.enums import Roles, Levels
from typing import Annotated
import re
from helper_functions.validators import email_value, password_value, non_empty_value


class User(BaseModel):
    name: non_empty_value
    email: email_value
    password: password_value
    verified: bool
    role: Roles
    is_external: bool = False
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class CreateUser(BaseModel):
    email: email_value
    password: password_value
    name: non_empty_value
    is_external: bool = False


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
    is_external: bool = False
    model_config = ConfigDict(from_attributes=True)


class UserPrivacy(BaseModel):
    level: Levels


class CreateAssignUser(BaseModel):
    user_email: email_value
    task_id: non_empty_value


class AssignUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_email: email_value
    task_id: non_empty_value


class ChangeUserRole(BaseModel):
    user_email: email_value
    user_role: Roles

class VerifyOTP(BaseModel):
    otp_code:str
    user_email:str

class StatusResponse(BaseModel):
    status: str

class SignupUserData(BaseModel):
    id: str
    name: str
    email: str
    role: str
    verified: bool
    is_external: bool = False

class SignupResponse(BaseModel):
    status: str
    user_data: SignupUserData

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class OTPStatusResponse(BaseModel):
    status: str

class UserMeResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    privacy_level: str
    verified: bool
    active: bool
    is_external: bool = False

class UserStatusData(BaseModel):
    email: str
    role: str
    active: bool

class ModifyStatusResponse(BaseModel):
    status: str
    user: UserStatusData

class SoftDeleteResponse(BaseModel):
    status: str
    email: str
    soft_delete: bool

class PrivacyResponse(BaseModel):
    status: str
    email: str
    privacy_level: str

class AssignmentResponse(BaseModel):
    status: str
    user_email: str
    task_id: str

class ChangeRoleResponse(BaseModel):
    status: str
    email: str
    role: str

class CreateExternalCollaborator(BaseModel):
    name: non_empty_value
    email: email_value
    project_id: non_empty_value

class UnassignUser(BaseModel):
    task_id: str
    user_email: str | None = None
    user_id: str | None = None