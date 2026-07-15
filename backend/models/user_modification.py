from pydantic import BaseModel, EmailStr
from typing import Optional
from schema.enums import Roles


class UpdatePersonalInfo(BaseModel):
    name: Optional[str] = None
    new_email: Optional[EmailStr] = None
    new_password: Optional[str] = None
    current_password: Optional[str] = None



class ChangeStatus(BaseModel):
    email: EmailStr 
    role: Optional[Roles] = None
    active: Optional[bool] = None
