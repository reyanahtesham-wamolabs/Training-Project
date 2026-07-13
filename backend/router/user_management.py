from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from dependencies.database import get_db
from dependencies.Authorization import get_current_user, get_current_admin
from helper_functions.hashing import check_password
from schema.user_models import User as db_User
from schema.enums import Roles
from services.user_services_management import (
    change_personal_information,
    modify_status as svc_modify_status,
    soft_delete_user,
    change_privacy as svc_change_privacy,
)
from models.user_modification import UpdatePersonalInfo,ChangePrivacyRequest,ChangeStatus
router_user_management = APIRouter()

@router_user_management.post("/change_personal_information/")
async def change_personal_informaiton(data: UpdatePersonalInfo,current_user: db_User = Depends(get_current_user),session: AsyncSession = Depends(get_db),):
    # Enforce owner-only access and delegate business logic to service
    if current_user.email != data.email:
        raise HTTPException(status_code=403, detail="Not allowed")

    if data.new_email or data.password:
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

    user_obj = await change_personal_information(data, current_user, session)
    return {"status": "ok", "user": {"email": user_obj.email, "name": user_obj.name}}

#Admin can modify user roles and active statuses
@router_user_management.post("/modify_status/")
async def modify_status(data: ChangeStatus,current_admin: db_User = Depends(get_current_admin),session: AsyncSession = Depends(get_db)):
    "Admin endpoint: update user's role and active status by email."
    # Delegate admin business logic to service
    user_obj = await svc_modify_status(data, current_admin, session)
    return {"status": "ok", "user": {"email": user_obj.email, "role": str(user_obj.role), "active": user_obj.active}}


@router_user_management.post("/soft_delete/")
async def soft_delete(current_user: db_User = Depends(get_current_user),session: AsyncSession = Depends(get_db)):
    # Owner-only: requester must match target email
    user_obj = await soft_delete_user(current_user, session)
    return {"status": "ok", "email": user_obj.email, "soft_delete": user_obj.soft_delete}


@router_user_management.post("/change_privacy/")
async def change_privacy(data: ChangePrivacyRequest,current_user: db_User = Depends(get_current_user),session: AsyncSession = Depends(get_db),):
    """Allow a user to change their privacy level (e.g. High/Medium/Low)."""
    allowed = {"High", "Medium", "Low"}
    privacy = data.privacy_level
    if privacy not in allowed:
        raise HTTPException(status_code=400, detail=f"privacy_level must be one of {allowed}")

    # Owner-only: verify current user matches target email
    if current_user.email != data.email:
        raise HTTPException(status_code=403, detail="Only the owner can change privacy")

    user_obj = await svc_change_privacy(data, current_user, session)
    return {"status": "ok", "email": user_obj.email, "privacyLevel": user_obj.privacyLevel}
