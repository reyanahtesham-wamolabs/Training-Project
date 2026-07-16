from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.Authorization import get_current_user, get_current_admin
from models.task_models import TaskCreation, TaskUpdate
from schema.user_models import User as db_User
from services.task_services import TaskService

router_task = APIRouter()


@router_task.post("/create_task/")
async def create_task_route(
    task_data: TaskCreation,
    current_user: db_User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    # roles based access and jwt auth in other branch. Will be added later
    task = await TaskService.create_task(task_data, session)
    return {"status": "Task Created Successfully", "Task ID": task.id}


@router_task.delete("/delete_task/")
async def delete_task_route(
    task_id: str,
    current_user: db_User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    # roles based access and jwt auth in other branch. Will be added later
    await TaskService.delete_task(task_id, session)
    return {"status": "Task Deleted Successfully"}


@router_task.get("/view_task/")
async def view_task_route(
    current_user: db_User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    # roles based access and jwt auth in other branch. Will be added later
    return await TaskService.get_all_tasks(session)


@router_task.patch("/update_task/")
async def update_task_route(
    user_data: TaskUpdate,
    current_user: db_User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    # roles based access and jwt auth in other branch. Will be added later
    task = await TaskService.update_task(user_data, session)
    return {"status": "Task Updated Successfully", "Task ID": task.id}


@router_task.patch("/add_prerequisite/")
async def add_prerequisite_route(
    prerequisite_id: str,
    dependant_id: str,
    current_user: db_User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    # roles based access and jwt auth in other branch. Will be added later
    await TaskService.add_prerequisite(prerequisite_id, dependant_id, session)
    return {"status": "Pre-Requisite Added Successfully"}