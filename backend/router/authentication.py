from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_model import User,CreateUser,UserLogin
from repository.user_auth import UserCrud
from services.auth_services import UserAuthenticationServices
from dependencies.database import get_db
from services.JWT_services import TokenFunctionality
router = APIRouter()

@router.post("/signup_user/")
async def signup(user_data: CreateUser, session: AsyncSession = Depends(get_db)):
    userCompleteData = await UserAuthenticationServices.user_signup(user_data, session)
    return userCompleteData

@router.post("/login/")
async def login(user_data: UserLogin, session: AsyncSession = Depends(get_db)):
    data = await UserAuthenticationServices.user_login(user_data, session)
    return data

@router.post("/refresh")
async def refresh(refresh_token:str,session:AsyncSession=Depends(get_db)):
    token=await TokenFunctionality.refresh_token(refresh_token,session)
    return token

