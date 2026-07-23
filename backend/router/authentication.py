from fastapi import APIRouter, Depends
from models.user_model import (
    CreateUser,
    UserLogin,
    ChangePassword,
    ChangeEmail,
    ChangeName,
    VerifyOTP,
)
from models.token_models import RefreshToken
from services.auth_services import UserAuthenticationServices
from dependencies.services import get_auth_service
from schema.user import User as db_User
from dependencies.authorization import get_current_user

router = APIRouter()


@router.post("/signup_user")
async def signup(
    user_data: CreateUser,
    auth_service: UserAuthenticationServices = Depends(get_auth_service),
):
    user_complete_data = await auth_service.user_signup(user_data)
    return {"status": "User Created Successfully", "User Data": user_complete_data}


@router.post("/login")
async def login(
    user_data: UserLogin,
    auth_service: UserAuthenticationServices = Depends(get_auth_service),
):
    return await auth_service.user_login(user_data)


@router.post("/logout")
async def logout(
    current_user: db_User = Depends(get_current_user),
    auth_service: UserAuthenticationServices = Depends(get_auth_service),
):
    return await auth_service.user_logout(current_user)


@router.post("/refresh")
async def refresh(
    token: RefreshToken,
    auth_service: UserAuthenticationServices = Depends(get_auth_service),
):
    return await auth_service.refresh_token(token.refresh_token)


@router.post("/change_password")
async def change_password(
    user_data: ChangePassword,
    current_user: db_User = Depends(get_current_user),
    auth_service: UserAuthenticationServices = Depends(get_auth_service),
):
    return await auth_service.password_change(user_data, current_user)


@router.post("/change_email")
async def change_email(
    user_data: ChangeEmail,
    current_user: db_User = Depends(get_current_user),
    auth_service: UserAuthenticationServices = Depends(get_auth_service),
):
    return await auth_service.email_change(user_data, current_user)


@router.post("/change_name")
async def change_name(
    user_data: ChangeName,
    current_user: db_User = Depends(get_current_user),
    auth_service: UserAuthenticationServices = Depends(get_auth_service),
):
    return await auth_service.name_change(user_data, current_user)


@router.post("/verify_otp")
async def verify_otp(
    otp: VerifyOTP,
    auth_service: UserAuthenticationServices = Depends(get_auth_service),
):
    return await auth_service.check_otp(otp.otp_code, otp.user_email)
