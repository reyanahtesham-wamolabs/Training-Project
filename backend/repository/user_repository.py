from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect
from schema.user_models import User as db_User


async def get_user_by_email(email: str, session: AsyncSession) -> db_User | None:
    stmt = select(db_User).where(db_User.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def save_user(user_obj: db_User, session: AsyncSession) -> db_User:
    try:
        session.add(user_obj)
        await session.commit()
        await session.refresh(user_obj)
        return user_obj
    except SQLAlchemyError:
        await session.rollback()
        raise


async def update_user(user_obj: db_User, session: AsyncSession) -> db_User:
    try:
        state = inspect(user_obj)
        if state.detached:
            user_obj = await session.merge(user_obj)

        await session.commit()
        await session.refresh(user_obj)
        return user_obj
    except SQLAlchemyError:
        await session.rollback()
        raise
