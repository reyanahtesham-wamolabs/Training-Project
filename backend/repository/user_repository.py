from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect
from  schema.user import User as db_User
from  schema.assignment import Assignment as db_Assignment
from models.user_model import UserResponse


async def get_user_by_email(email: str, session: AsyncSession) -> db_User | None:
    stmt = select(db_User).where(db_User.email == email)
    result = await session.execute(stmt)
    userObj = result.scalar_one_or_none()
    if userObj is None:
        return None
    return userObj


async def get_user_by_id(id: str, session: AsyncSession) -> db_User | None:
    stmt = select(db_User).where(db_User.id == id)
    result = await session.execute(stmt)
    userObj = result.scalar_one_or_none()
    return userObj


async def get_user_by_name(name: str, session: AsyncSession) -> list[db_User] | None:
    stmt = select(db_User).where(db_User.name == name)
    result = await session.execute(stmt)
    userObj = result.scalars().all()
    return userObj


async def get_all_users(session: AsyncSession) -> list[db_User]:
    stmt = select(db_User)
    result = await session.execute(stmt)
    user_objs = result.scalars().all()
    return user_objs


async def save_user(user_obj: db_User, session: AsyncSession) -> db_User:
    try:
        session.add(user_obj)
        await session.commit()
        await session.refresh(user_obj)
        return user_obj
    except SQLAlchemyError:
        await session.rollback()
        raise


async def update_user(user: db_User, session: AsyncSession) -> UserResponse:
    try:
        state = inspect(user)
        if state.detached:
            user = await session.merge(user)

        await session.commit()
        await session.refresh(user)
        return UserResponse.model_validate(user)
    except SQLAlchemyError:
        await session.rollback()
        raise


async def assign_user(
    assignment_id: str,
    user_id: str,
    task_id: str,
    role: str,
    session: AsyncSession,
):
    try:
        assignment = db_Assignment(
            id=assignment_id,
            user_id=user_id,
            task_id=task_id,
            role=role,
        )
        session.add(assignment)
        await session.commit()
        return assignment
    except SQLAlchemyError:
        await session.rollback()
        raise


async def get_user_assignment(user_id: str, task_id: str, session: AsyncSession):
    stmt = (
        select(db_Assignment)
        .where(db_Assignment.user_id == user_id)
        .where(db_Assignment.task_id == task_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
