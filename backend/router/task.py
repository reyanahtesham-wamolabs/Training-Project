from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_model import User,CreateUser,UserLogin
from repository.user_CRUD import UserCrud
from services.user_services import UserAuthenticationServices
from dependencies.database import get_db
from models.task_models import TaskCreation,Task,TaskUpdate
from repository.task import TaskCrud
router = APIRouter()


@router.post("/create_task/")
async def create_task(task_data: TaskCreation, session: AsyncSession = Depends(get_db)):
    #roles based access and jwt auth in other branch. Will be added after
    await TaskCrud.add_task(task_data,session)
    return task_data

@router.delete("/delete_task/")
async def delet_task(task_id: str, session: AsyncSession = Depends(get_db)):
    #roles based access and jwt auth in other branch. Will be added after
    await TaskCrud.delete_task(task_id,session)
    return "User Deleted Successfully"

@router.get("/view_task/")
async def view_task(session: AsyncSession = Depends(get_db)):
    #roles based access and jwt auth in other branch. Will be added after
    return await TaskCrud.get_all_tasks(session)

@router.put("/update_task/")
async def update_task(user_data: TaskUpdate, session: AsyncSession = Depends(get_db)):
    #roles based access and jwt auth in other branch. Will be added after
    await TaskCrud.update_task(user_data)
    return "Updated"

