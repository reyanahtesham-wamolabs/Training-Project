from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies.database import get_db
from dependencies.Authorization import get_current_user, get_current_admin
from helper_functions.hashing import check_password
from schema.user_models import User as db_User
from services.user_services_management import (
    change_personal_information as svc_change_personal_information,
    modify_status as svc_modify_status,
    soft_delete_user,
    change_privacy as svc_change_privacy,
)
from models.user_model import UserPrivacy
from models.user_modification import UpdatePersonalInfo,ChangeStatus
router_user_management = APIRouter()

@router_user_management.patch("/change_personal_information/")
async def change_personal_information(data: UpdatePersonalInfo,current_user: db_User = Depends(get_current_user),session: AsyncSession = Depends(get_db),):
    # Enforce owner-only access and delegate business logic to service
    if data.new_email or data.new_password:
        if not data.current_password:
            raise HTTPException(
                status_code=400,
                detail="Current password is required to update email or password",
            )
        if not check_password(data.current_password, current_user.password):
            raise HTTPException(
                status_code=401,
                detail="Current password verification failed",
            )

    user_obj = await svc_change_personal_information(data, current_user, session)
    return {"status": "ok","action":"Login Required" ,"user": {"email": user_obj.email, "name": user_obj.name}}

#Admin can modify user roles and active statuses
@router_user_management.patch("/modify_user_status/")
async def modify_status(data: ChangeStatus,current_admin: db_User = Depends(get_current_admin),session: AsyncSession = Depends(get_db)):
    "Admin endpoint: update user's role and active status by email."
    # Delegate admin business logic to service
    user_obj = await svc_modify_status(data, current_admin, session)
    return {"status": "ok", "user": {"email": user_obj.email, "role": str(user_obj.role), "active": user_obj.active}}

@router_user_management.patch("/soft_delete_user/")
async def soft_delete(current_user: db_User = Depends(get_current_user),session: AsyncSession = Depends(get_db)):
    # Owner-only: requester must match target email
    user_obj = await soft_delete_user(current_user, session)
    return {"status": "ok", "email": user_obj.email, "soft_delete": user_obj.soft_delete}

@router_user_management.patch("/change_user_privacy/")
async def change_privacy(new_level:UserPrivacy,current_user: db_User = Depends(get_current_user),session: AsyncSession = Depends(get_db),):
    """Allow a user to change their privacy level (e.g. low/medium/high)."""

    user_obj = await svc_change_privacy(new_level, current_user, session)
    return {"status": "ok", "email": user_obj.email, "privacy_level": user_obj.privacy_level}
