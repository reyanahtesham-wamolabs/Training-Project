from fastapi import APIRouter, Depends
from typing import List

from dependencies.services import get_activity_log_service
from dependencies.authorization import get_current_user, get_current_admin
from schema.user import User as db_User
from services.activity_log import ActivityLogService

router_activity = APIRouter()

@router_activity.get("/get_all_logs")
async def get_activity_logs(
    current_user: db_User = Depends(get_current_admin),
    activity_service: ActivityLogService = Depends(get_activity_log_service),
):
    logs = await activity_service.get_all_logs()
    return logs

@router_activity.get("/get_own_logs")
async def get_own_logs(
    current_user: db_User = Depends(get_current_user),
    activity_service: ActivityLogService = Depends(get_activity_log_service),
):
    return await activity_service.get_own_logs(current_user)
