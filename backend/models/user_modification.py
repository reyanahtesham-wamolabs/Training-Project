from pydantic import BaseModel, EmailStr
from typing import Optional
from schema.enums import Roles


class UpdatePersonalInfo(BaseModel):
    email: EmailStr  # email of the person to update 
    name: Optional[str] = None
    new_email: Optional[EmailStr] = None
    password: Optional[str] = None
    current_password: Optional[str] = None

#Users to swich own privacy
class ChangePrivacyRequest(BaseModel):
    email: EmailStr
    privacy_level: str

class ChangeStatus(BaseModel):
    email: EmailStr  # email of the person to update 
    role: Optional[Roles] = None
    active: Optional[bool] = None
