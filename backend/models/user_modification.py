from pydantic import BaseModel, EmailStr
from typing import Optional
from schema.enums import Roles


class UpdatePersonalInfo(BaseModel):
    name: Optional[str] = None
    new_email: Optional[EmailStr] = None
    password: Optional[str] = None
    current_password: Optional[str] = None



class ChangeStatus(BaseModel):
    email: EmailStr  # email of the person to update 
    role: Optional[Roles] = None
    active: Optional[bool] = None
