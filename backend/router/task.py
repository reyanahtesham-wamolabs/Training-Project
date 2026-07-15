from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies.database import get_db
from models.task_models import TaskCreation,Task,TaskUpdate
from dependencies.Authorization import get_current_user, get_current_admin
from repository.task import TaskCrud
from schema.user_models import User as db_User
router_task = APIRouter()


@router_task.post("/create_task/")
async def create_task_route(task_data: TaskCreation,current_user: db_User = Depends(get_current_user), session: AsyncSession = Depends(get_db)):
    #roles based access and jwt auth in other branch. Will be added later
    data=Task(name=task_data.name,schedule_date=task_data.schedule_date,status=task_data.status,priority=task_data.priority,project_id=task_data.project_id)
    task=await TaskCrud.add_task(data,session)
    return task

@router_task.delete("/delete_task/")
async def delete_task_route(task_id: str,current_user: db_User = Depends(get_current_user), session: AsyncSession = Depends(get_db)):
    #roles based access and jwt auth in other branch. Will be added later
    await TaskCrud.delete_task(task_id,session)
    return "Task Deleted Successfully"

@router_task.get("/view_task/")
async def view_task_route(current_user: db_User = Depends(get_current_user),session: AsyncSession = Depends(get_db)):
    #roles based access and jwt auth in other branch. Will be added later
    return await TaskCrud.get_all_tasks(session)

@router_task.patch("/update_task/")
async def update_task_route(user_data: TaskUpdate,current_user: db_User = Depends(get_current_user), session: AsyncSession = Depends(get_db)):
    #roles based access and jwt auth in other branch. Will be added later
    await TaskCrud.update_task(user_data,session)
    return "Updated"

@router_task.patch("/add_prerequisite/")
async def add_prerequisite_route(prerequisite_id: str, dependant_id: str,current_user: db_User = Depends(get_current_user), session: AsyncSession = Depends(get_db)):
    #roles based access and jwt auth in other branch. Will be added later
    await TaskCrud.add_prerequisite(prerequisite_id,dependant_id,session)
    return "Pre Req Added"

