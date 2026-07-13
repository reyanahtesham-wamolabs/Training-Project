from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_model import User,CreateUser,UserLogin
from repository.user_CRUD import UserCrud
from services.user_services import UserAuthenticationServices
from dependencies.database import get_db

router = APIRouter()


@router.post("/create_task/")
async def create_task(task_data: CreateUser, session: AsyncSession = Depends(get_db)):
    #roles based access and jwt auth in other branch. Will be added after

    return task_data

@router.post("/delete_task/")
async def delet_task(user_data: CreateUser, session: AsyncSession = Depends(get_db)):
    #roles based access and jwt auth in other branch. Will be added after
    userCompleteData = await UserAuthenticationServices.user_signup(user_data, session)
    return userCompleteData

@router.get("/view_task/")
async def view_task(user_data: CreateUser, session: AsyncSession = Depends(get_db)):
    #roles based access and jwt auth in other branch. Will be added after
    userCompleteData = await UserAuthenticationServices.user_signup(user_data, session)
    return userCompleteData

@router.put("/update_task/")
async def update_task(user_data: CreateUser, session: AsyncSession = Depends(get_db)):
    #roles based access and jwt auth in other branch. Will be added after
    userCompleteData = await UserAuthenticationServices.user_signup(user_data, session)
    return userCompleteData

