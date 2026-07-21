"""
Router layer for Notification endpoints.

Responsibility: HTTP request/response wiring only.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.authorization import get_current_user
from models.notification_models import NotificationOut
from repository.notification_repository import NotificationRepo
from schema.user import User as db_User

router_notification = APIRouter()


@router_notification.get("/my/", response_model=list[NotificationOut])
async def get_my_notifications(
    current_user: db_User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    return await NotificationRepo.get_user_notifications(current_user.id, session)


@router_notification.patch("/read/{notification_id}/", response_model=NotificationOut)
async def mark_notification_read(
    notification_id: str,
    current_user: db_User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    notification = await NotificationRepo.get_notification_by_id(notification_id, session)
    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot modify another user's notification",
        )
    return await NotificationRepo.mark_as_read(notification, session)
