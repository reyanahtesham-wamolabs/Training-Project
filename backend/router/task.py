from fastapi import APIRouter, Depends

from dependencies.services import get_task_service
from dependencies.authorization import get_current_user, get_current_admin, get_current_manager
from models.task import TaskCreation, TaskUpdate
from schema.user import User as db_User
from services.task import TaskService

router_task = APIRouter()

@router_task.post("/create_task")
async def create_task_route(
    task_data: TaskCreation,
    current_user: db_User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    task = await task_service.create_task(task_data, current_user)
    return {"status": "Task Created Successfully", "Task ID": task.id}
@router_task.post("/get_user_tasks")
async def get_user_task_route(
    current_user: db_User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    task = await task_service.get_user_task(current_user)
    return task

@router_task.delete("/delete_task")
async def delete_task_route(
    task_id: str,
    current_user: db_User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    await task_service.delete_task(task_id, current_user)
    return {"status": "Task Deleted Successfully"}

@router_task.delete("/hard_delete_task")
async def hard_delete_task_route(
    task_id: str,
    current_user: db_User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    await task_service.hard_delete_task(task_id, current_user)
    return {"status": "Task Permanently Deleted Successfully"}

@router_task.get("/view_task")
async def view_task_route(
    current_user: db_User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    return await task_service.get_all_tasks(current_user)

@router_task.get("/get_softdeleted_tasks")
async def get_softdeleted_tasks_route(
    current_user: db_User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    return await task_service.get_softdeleted_tasks(current_user)

@router_task.get("/get_active_tasks")
async def get_active_tasks_route(
    current_user: db_User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    return await task_service.get_active_tasks(current_user)

@router_task.patch("/update_task")
async def update_task_route(
    user_data: TaskUpdate,
    current_user: db_User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    task = await task_service.update_task(user_data, current_user)
    return {"status": "Task Updated Successfully", "Task ID": task.id}

@router_task.patch("/add_prerequisite")
async def add_prerequisite_route(
    prerequisite_id: str,
    dependant_id: str,
    current_user: db_User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    await task_service.add_prerequisite(prerequisite_id, dependant_id, current_user)
    return {"status": "Pre-Requisite Added Successfully"}