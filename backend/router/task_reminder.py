from fastapi import APIRouter, Depends
from dependencies.services import get_task_reminder_service
from dependencies.authorization import get_current_user
from models.task_reminder import TaskReminderCreate, TaskReminderOut
from schema.user import User as db_User
from services.task_reminder import TaskReminderService

router_task_reminder = APIRouter()

@router_task_reminder.post("/{task_id}", response_model=TaskReminderOut)
async def create_or_update_reminder(
    task_id: str,
    data: TaskReminderCreate,
    current_user: db_User = Depends(get_current_user),
    service: TaskReminderService = Depends(get_task_reminder_service),
):
    return await service.create_or_update(task_id, data, current_user)

from typing import Optional

@router_task_reminder.get("/{task_id}", response_model=Optional[TaskReminderOut])
async def get_reminder(
    task_id: str,
    current_user: db_User = Depends(get_current_user),
    service: TaskReminderService = Depends(get_task_reminder_service),
):
    return await service.get(task_id, current_user)

@router_task_reminder.delete("/{task_id}")
async def delete_reminder(
    task_id: str,
    current_user: db_User = Depends(get_current_user),
    service: TaskReminderService = Depends(get_task_reminder_service),
):
    return await service.delete(task_id, current_user)
