from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies.database import get_db
from dependencies.services import get_user_service
from dependencies.authorization import (
    get_current_user,
    get_current_admin,
    get_current_manager
)
from helper_functions.hashing import check_password
from schema.user import User as db_User
from services.user_services_management import UserManagementService
from models.user_model import UserPrivacy, CreateAssignUser,ChangeUserRole
from models.user_modification import UpdatePersonalInfo, ChangeStatus
from repository.user_repository import get_all_users
from typing import Annotated

router_user_management = APIRouter()


@router_user_management.patch("/modify_user_status/")
async def modify_status(
    data: ChangeStatus,
    user_service: Annotated[UserManagementService, Depends(get_user_service)],
    current_admin: db_User = Depends(get_current_admin),
):
    "Admin endpoint: update user's role and active status by email."
    # Delegate admin business logic to service
    user_obj = await user_service.modify_status(data, current_admin)
    return {
        "status": "ok",
        "user": {
            "email": user_obj.email,
            "role": str(user_obj.role),
            "active": user_obj.active,
        },
    }


@router_user_management.patch("/soft_delete_user/")
async def soft_delete(
    user_service: Annotated[UserManagementService, Depends(get_user_service)],
    current_user: db_User = Depends(get_current_user),
):
    user_obj = await user_service.delete_user(current_user)
    return {
        "status": "ok",
        "email": user_obj.email,
        "soft_delete": user_obj.soft_delete,
    }


@router_user_management.patch("/change_user_privacy/")
async def change_privacy(
    new_level: UserPrivacy,
    user_service: Annotated[UserManagementService, Depends(get_user_service)],
    current_user: db_User = Depends(get_current_user),
):
    """Allow a user to change their privacy level (e.g. low/medium/high)."""

    user_obj = await user_service.change_privacy(new_level, current_user)
    return {
        "status": "ok",
        "email": user_obj.email,
        "privacy_level": user_obj.privacy_level,
    }


@router_user_management.post("/assign_user")
async def assign_user(
    assignment: CreateAssignUser,
    user_service: Annotated[UserManagementService, Depends(get_user_service)],
    current_user: db_User = Depends(get_current_manager),
):
    assigned_result = await user_service.assign_user(assignment)
    return assigned_result

@router_user_management.post("/change_user_role")
async def change_user_role(
    assignment: ChangeUserRole,
    user_service: Annotated[UserManagementService, Depends(get_user_service)],
    current_user: db_User = Depends(get_current_admin),
):
    assigned_result = await user_service.change_user_role(assignment)
    return assigned_result


@router_user_management.get("/get_all_users")
async def get_all_users(
    user_service: Annotated[UserManagementService, Depends(get_user_service)],
    current_user: db_User = Depends(get_current_admin),
):
    """Get All Users"""
    all_users = await user_service.get_all_users()
    return all_users
