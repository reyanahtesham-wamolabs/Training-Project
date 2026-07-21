import asyncio
from models.user_model import (
    User,
    CreateUser,
    UserLogin,
    ChangePassword,
    ChangeEmail,
    ChangeName,
)
from repository.user_auth import UserCrud
from .JWT_services import TokenFunctionality
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from helper_functions.hashing import hash_password, check_password
from fastapi import status
from helper_functions.opt_gen import generate_OTP, email_OTP
from schema.otp import OTP as db_otp
from repository.user_repository import update_user
from  schema.user import User as db_user
from schema.enums import OTPAction
from repository.user_repository import get_user_by_email
from schema.enums import Roles
class UserAuthenticationServices:
    async def user_signup(user_data: CreateUser, session):
        existing = await get_user_by_email(user_data.email, session)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        user_data.password = hash_password(user_data.password)
        user_complete_data = User(
            name=user_data.name,
            role=Roles.member,
            password=user_data.password,
            email=user_data.email,
            verified=False,
        )
        try:
            created_user = await UserCrud.add_user(user_complete_data, session)
        except SQLAlchemyError as e:
            print(f"[Signup DB Error]: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user",
            ) from e


        otp_code = generate_OTP()

        # Fire email in background — don't block signup on SMTP
        asyncio.create_task(email_OTP(otp_code, user_complete_data.email))

        otp = db_otp(
            user_id=user_complete_data.id,
            user_name=user_complete_data.name,
            code=hash_password(otp_code),
            action=OTPAction.verify_profile,
        )

        try:
            await UserCrud.insert_OTP(otp, session)
        except SQLAlchemyError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store OTP",
            ) from e

        return {
            "status_code": status.HTTP_201_CREATED,
            "message": "User created successfully. Please check your email to verify your account.",
            "data": {
                "id": created_user.id,
                "name": created_user.name,
                "email": created_user.email,
                "role": created_user.role,
                "verified": created_user.verified,
            },
        }

    async def user_login(user_data: UserLogin, session):
        user_obj = await UserCrud.user_login(user_data, session)
        access_token = TokenFunctionality.create_access_token(user_obj.id)
        refresh_token = await TokenFunctionality.create_refresh_token(
            user_obj.id, session
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    async def user_logout(user_data,session):
        result=await TokenFunctionality.delete_token(user_data.id,session)
        return result
    
    async def password_change(user_data: ChangePassword, current_user, session):
        if not check_password(user_data.current_password, current_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is not correct",
            )

        otp_code = generate_OTP()

        try:
            await email_OTP(otp_code, current_user.email)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to send OTP, please try again",
            ) from e

        otp = db_otp(
            user_id=current_user.id,
            user_name=current_user.name,
            code=hash_password(otp_code),
            new_desired_password=hash_password(user_data.new_password),
            action=OTPAction.change_password,
        )

        try:
            await UserCrud.insert_OTP(otp, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store OTP",
            ) from e

        return {"status": "OTP sent, please check your email"}

    async def email_change(user_data: ChangeEmail, current_user, session):

        otp_code = generate_OTP()

        try:
            await email_OTP(otp_code, current_user.email)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to send OTP, please try again",
            ) from e

        otp = db_otp(
            user_id=current_user.id,
            user_name=current_user.name,
            code=hash_password(otp_code),
            new_desired_email=user_data.new_email,
            action=OTPAction.change_email,
        )

        try:
            await UserCrud.insert_OTP(otp, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store OTP",
            ) from e

        return {"status": "OTP sent, please check your email"}

    async def name_change(user_data: ChangeName, current_user, session):
        otp_code = generate_OTP()

        try:
            await email_OTP(otp_code, current_user.email)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to send OTP, please try again",
            ) from e

        otp = db_otp(
            user_id=current_user.id,
            user_name=current_user.name,
            code=hash_password(otp_code),
            new_desired_name=user_data.new_name,
            action=OTPAction.change_name,
        )

        try:
            await UserCrud.insert_OTP(otp, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store OTP",
            ) from e

        return {"status": "OTP sent, please check your email"}

    async def check_otp(otp_code: str, email: str, session):
        try:
            user = await get_user_by_email(email, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to look up user",
            ) from e

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        try:
            result = await UserCrud.check_otp(otp_code, user, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify OTP due to a database error",
            ) from e

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP",
            )

        if isinstance(result, tuple) and result[0] == "expired":
            expired_otp = result[1]
            new_otp_code = generate_OTP()
            
            import asyncio
            asyncio.create_task(email_OTP(new_otp_code, user.email))
            
            new_otp = db_otp(
                user_id=expired_otp.user_id,
                user_name=expired_otp.user_name,
                code=hash_password(new_otp_code),
                action=expired_otp.action,
                new_desired_password=expired_otp.new_desired_password,
                new_desired_email=expired_otp.new_desired_email,
                new_desired_name=expired_otp.new_desired_name,
            )
            
            try:
                await UserCrud.insert_OTP(new_otp, session)
            except SQLAlchemyError:
                pass
                
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP expired. A new OTP has been sent to your email.",
            )

        if result.action == OTPAction.change_password:
            user.password = result.new_desired_password
            success_message = "Password updated successfully"
        elif result.action == OTPAction.change_email:
            user.email = result.new_desired_email
            success_message = "Email updated successfully"
        elif result.action == OTPAction.change_name:
            user.name = result.new_desired_name
            success_message = "Name updated successfully"
        elif result.action == OTPAction.verify_profile:
            user.verified = True
            success_message = "Account verified successfully"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported OTP action",
            )

        try:
            await update_user(user, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to apply {result.action.value}",
            ) from e

        return {"status": success_message}