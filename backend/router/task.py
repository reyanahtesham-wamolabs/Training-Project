from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_model import User,CreateUser,UserLogin
from repository.user_CRUD import UserCrud
from services.user_services import UserAuthenticationServices
from dependencies.database import get_db

router = APIRouter()

#create task
#delete task
#update task
#view all tasks

@router.post("/create_task/")
async def signup(user_data: CreateUser, session: AsyncSession = Depends(get_db)):
    #roles based access and jwt auth in other branch. Will be added after
    userCompleteData = await UserAuthenticationServices.user_signup(user_data, session)
    return userCompleteData

