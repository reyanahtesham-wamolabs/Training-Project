from pydantic import  EmailStr, BaseModel,field_validator,Field
import uuid
from helper_functions.hashing import hash_password
from schema.enums import Roles
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
