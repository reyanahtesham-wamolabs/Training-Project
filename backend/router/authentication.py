from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_model import User,CreateUser,UserLogin
from repository.user_CRUD import UserCrud
from services.user_services import UserAuthenticationServices
from database import get_db

router = APIRouter()

@router.post("/SignupUser/")
async def signup(userData: CreateUser, session: AsyncSession = Depends(get_db)):
    userCompleteData = await UserAuthenticationServices.user_signup(userData, session)
    return userCompleteData

@router.post("/Login/")
async def login(userData: UserLogin, session: AsyncSession = Depends(get_db)):
    data = await UserAuthenticationServices.user_login(userData, session)
    return data


