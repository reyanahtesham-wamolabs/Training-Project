from fastapi import APIRouter, Depends
from dependencies.services import get_notification_service
from dependencies.authorization import get_current_user
from models.notification import NotificationOut, UpdateNotificationDelivery
from schema.user import User as db_User
from services.notification import NotificationService

router_notification = APIRouter()


@router_notification.get("/my", response_model=list[NotificationOut])
async def get_my_notifications(
    current_user: db_User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.get_my_notifications(current_user)


@router_notification.patch("/read/{notification_id}", response_model=NotificationOut)
async def mark_notification_read(
    notification_id: str,
    current_user: db_User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.mark_read(notification_id, current_user)


@router_notification.patch("/update_delivery_time/{notification_id}", response_model=NotificationOut)
async def update_notification_delivery_time(
    notification_id: str,
    data: UpdateNotificationDelivery,
    current_user: db_User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.update_delivery_time(notification_id, data.delivered, current_user)
