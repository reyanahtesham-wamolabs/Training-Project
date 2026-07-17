from models.user_model import User,CreateUser,UserLogin,ChangePassword
from repository.user_auth import UserCrud
from .JWT_services import TokenFunctionality
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from helper_functions.hashing import hash_password,check_password
from fastapi import status
from helper_functions.opt_gen import generate_OTP,email_OTP
from schema.otp import OTP as db_otp
from repository.user_repository import update_user
from schema.user_models import User as db_user
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
        user_obj = await UserCrud.user_login(user_data, session)
        access_token = TokenFunctionality.create_access_token(user_obj.id)
        refresh_token = await TokenFunctionality.create_refresh_token(user_obj.id, session)
        return {"access_token": access_token,"refresh_token": refresh_token,"token_type": "bearer"}
       
        
    async def password_change(user_data: ChangePassword, current_user, session):
        if not check_password(user_data.current_password, current_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is not correct",
            )

        otp_code=generate_OTP()

        try:
            await email_OTP (otp_code,current_user.email)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to send OTP, please try again",
            ) from e

        otp = db_otp(
            user_id=current_user.id,
            user_name=current_user.name,
            code=hash_password(otp_code),
            new_desired_password=hash_password(user_data.new_password)
        )

        try:
            await UserCrud.insert_OTP(otp, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store OTP",
            ) from e

        return {"status": "OTP sent, please check your email"}


    @staticmethod
    async def check_otp(otp_code: str, current_user, session):
        try:
            result = await UserCrud.check_otp(otp_code, current_user, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify OTP due to a database error",
            ) from e

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP",
            )

        current_user.password = result.new_desired_password

        try:
            await update_user(current_user, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password",
            ) from e

        return {"status": "Password updated successfully"}