from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_model import User, CreateUser, UserLogin, ChangePassword,ChangeEmail,ChangeName
from models.tokens import RefreshToken
from repository.user_auth import UserCrud
from services.auth_services import UserAuthenticationServices
from dependencies.database import get_db
from services.JWT_services import TokenFunctionality
from schema.user_models import User as db_User
from dependencies.authorization import get_current_user, get_current_admin

router = APIRouter()


@router.post("/signup_user/")
async def signup(user_data: CreateUser, session: AsyncSession = Depends(get_db)):
    userCompleteData = await UserAuthenticationServices.user_signup(user_data, session)
    return {"status": "User Created Successfully", "User Data": userCompleteData}


@router.post("/login/")
async def login(user_data: UserLogin, session: AsyncSession = Depends(get_db)):
    data = await UserAuthenticationServices.user_login(user_data, session)
    return data


@router.post("/refresh")
async def refresh(token: RefreshToken, session: AsyncSession = Depends(get_db)):
    result = await TokenFunctionality.refresh_token(token.refresh_token, session)
    if result.get("status") == "login_required":
        raise HTTPException(status_code=401, detail="Login required")
    return result


# async def password_change(user_data: ChangePassword, current_user, session):


@router.post("/change_password/")
async def change_password(
    user_data: ChangePassword,
    session: AsyncSession = Depends(get_db),
    current_user: db_User = Depends(get_current_user),
):
    result = await UserAuthenticationServices.password_change(
        user_data, current_user, session
    )
    return result
    # async def check_otp(otp_code: str, current_user, session):


@router.post("/change_email/")
async def change_email(
    user_data: ChangeEmail,
    session: AsyncSession = Depends(get_db),
    current_user: db_User = Depends(get_current_user),
):
    result = await UserAuthenticationServices.email_change(
        user_data, current_user, session
    )
    return result
    # async def check_otp(otp_code: str, current_user, session):


@router.post("/change_name/")
async def change_name(
    user_data: ChangeName,
    session: AsyncSession = Depends(get_db),
    current_user: db_User = Depends(get_current_user),
):
    result = await UserAuthenticationServices.name_change(
        user_data, current_user, session
    )
    return result
    # async def check_otp(otp_code: str, current_user, session):


@router.post("/verify_otp")
async def verify_otp(
    opt_code: str,
    user_email:str,
    session: AsyncSession = Depends(get_db),
):
    result = await UserAuthenticationServices.check_otp(opt_code,user_email, session)
    return result
