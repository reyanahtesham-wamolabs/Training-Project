from __future__ import annotations
from datetime import datetime, UTC
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from schema.token import RefreshToken
from sqlalchemy.ext.asyncio import AsyncSession


class tokenCRUD:
    @staticmethod
    async def add_token(JWT_token, user_id, expire_time, session: AsyncSession):
        refresh_token = RefreshToken(user_id=user_id, token=JWT_token, expire_date=expire_time)
        try:
            session.add(refresh_token)
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise

    @staticmethod
    async def validate_token(JWT_token, user_id, session: AsyncSession):
        try:
            stmt = select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.token == JWT_token,
            )
            result = await session.execute(stmt)
            tokenObj=result.scalar_one_or_none()
            return tokenObj is not None
        except SQLAlchemyError:
            raise
    

    @staticmethod
    async def token_exists(user_id, session: AsyncSession):
        try:
            stmt = select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.expire_date > datetime.now(UTC),
            )
            result = await session.execute(stmt)
            tokenObj = result.scalar_one_or_none()
            return tokenObj is not None
        except SQLAlchemyError:
            raise

    @staticmethod
    async def get_valid_refresh_token(user_id, session: AsyncSession):
        try:
            stmt = select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.expire_date > datetime.now(UTC),
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            raise

    @staticmethod
    async def delete_refresh_token(user_id, session: AsyncSession):
        try:
            stmt = sa.delete(RefreshToken).where(RefreshToken.user_id == user_id)
            await session.execute(stmt)
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise
