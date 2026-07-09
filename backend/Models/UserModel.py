from pydantic import BaseModel,field_validator,Field
import uuid
from Services.Hashing import hash_password
from Schema.Enums import Roles
class User(BaseModel):
    name : str
    email: str 
    password:str
    role:Roles
    ID: str = Field(default_factory=lambda: str(uuid.uuid4()))    
    

class CreateUser(BaseModel):
    email:str
    password:str=Field(pattern=r"[A-Za-z0-9_]{3,20}")
    name:str
    role:Roles
    @field_validator("email")
    @classmethod
    def emailValidator(cls,value):
        if "@wamolabs.com" not in value:
            raise ValueError("the email must include '@wamolabs.com'")
        return value
    
    @field_validator("password",mode="after")
    @classmethod
    def password_hashing(cls,value):
        hashedPassword=hash_password(value)  
        return hashedPassword


class UserLogin(BaseModel):
    email:str
    password:str 

    @field_validator("password",mode="after")
    @classmethod
    def password_hashing(cls,value):
        hashedPassword=hash_password(value)  
        return hashedPassword
