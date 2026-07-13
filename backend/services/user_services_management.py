from __future__ import annotations
from helper_functions.hashing import hash_password
from repository.user_repository import get_user_by_email, save_user, update_user
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from schema.enums import Roles
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError


async def change_personal_information(data, current_user, session: AsyncSession):
    # data is expected to have email, name?, new_email?, password?
    user = await get_user_by_email(data.email, session)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    updated = False
    if getattr(data, "name", None):
        user.name = data.name
        updated = True
    if getattr(data, "new_email", None):
        user.email = str(data.new_email)
        updated = True
    if getattr(data, "password", None):
        user.password = hash_password(data.password)
        updated = True

    if updated:
        return await update_user(user, session)
    return user


async def modify_status(data: dict, current_admin, session: AsyncSession):
    email = data.get("email")
    role = data.get("role")
    active = data.get("active")

    user = await get_user_by_email(email, session)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # assign role
    try:
        user.role = Roles(role) if not isinstance(role, Roles) else role
    except Exception:
        try:
            user.role = Roles[role]
        except Exception:
            raise HTTPException(status_code=400, detail="invalid role value")

    user.active = bool(active)
    return await update_user(user, session)


async def soft_delete_user( current_user, session: AsyncSession):
    user = await get_user_by_email(current_user.email, session)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.soft_delete = True
    return await update_user(user, session)


async def change_privacy(data, current_user, session: AsyncSession):
    allowed = {"High", "Medium", "Low"}
    privacy = data.privacy_level
    if privacy not in allowed:
        raise HTTPException(status_code=400, detail=f"privacy_level must be one of {sorted(allowed)}")

    user = await get_user_by_email(data.email, session)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.privacyLevel = privacy
    return await update_user(user, session)
