from models.user_model import User,CreateUser,UserLogin
from repository.user_CRUD import UserCrud
from .JWT_services import TokenFunctionality
from fastapi import HTTPException
from helper_functions.hashing import hash_password
from fastapi import status

class UserAuthenticationServices:
    async def user_signup(user_data:CreateUser,session):
        user_data.password=hash_password(user_data.password)
        user_complete_data=User(name=user_data.name,role=user_data.role,password=user_data.password,email=user_data.email)
        created_user = await UserCrud.add_user(user_complete_data, session)
        return {
    "status_code": status.HTTP_201_CREATED,
    "message": "User created successfully.",
    "data": {
        "id": created_user.id,
        "name": created_user.name,
        "email": created_user.email,
        "role": created_user.role,
    },
}

    async def user_login(user_data:UserLogin,session):
        await UserCrud.user_login(user_data, session)
        access_token = TokenFunctionality.create_access_token(user_data.email)
        refresh_token = await TokenFunctionality.create_refresh_token(user_data.email,session)
        return {"access_token": access_token,"refresh_token": refresh_token,"token_type": "bearer"}
       