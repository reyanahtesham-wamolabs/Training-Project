from __future__ import annotations
from helper_functions.hashing import hash_password, MAX_PASSWORD_LENGTH
from repository.user_repository import get_user_by_email, save_user, update_user
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from schema.enums import Roles, Levels
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from models.user_modification import ChangeStatus

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
        if len(data.password) > MAX_PASSWORD_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Password must be at most {MAX_PASSWORD_LENGTH} characters",
            )
        user.password = hash_password(data.password)
        updated = True

    if updated:
        return await update_user(user, session)
    return user


async def modify_status(data: ChangeStatus, current_admin, session: AsyncSession):
    user = await get_user_by_email(data.email, session)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if data.role is not None:
        try:
            user.role = Roles(data.role) if not isinstance(data.role, Roles) else data.role
        except ValueError:
            try:
                user.role = Roles[data.role]
            except KeyError:
                raise HTTPException(status_code=400, detail="invalid role value") from None

    if data.active is not None:
        user.active = bool(data.active)

    return await update_user(user, session)


async def soft_delete_user( current_user, session: AsyncSession):
    user = await get_user_by_email(current_user.email, session)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.soft_delete = True
    return await update_user(user, session)


async def change_privacy(data, current_user, session: AsyncSession):
    privacy = data.privacy_level
    try:
        privacy_enum = Levels(privacy.lower())
    except (ValueError, AttributeError):
        valid_values = ", ".join([level.value for level in Levels])
        raise HTTPException(status_code=400, detail=f"privacy_level must be one of {valid_values}")

    user = await get_user_by_email(data.email, session)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.privacy_level = privacy_enum
    return await update_user(user, session)
