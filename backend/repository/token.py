from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from schema.token import RefreshToken
from sqlalchemy.ext.asyncio import AsyncSession


class tokenCRUD:
    @staticmethod
    async def add_token(JWT_token,user_email,expire_time, session: AsyncSession):
        refresh_token=RefreshToken(email=user_email,token=JWT_token,expire_date=expire_time)
        try:
            session.add(refresh_token)
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise

    @staticmethod
    async def validate_token(JWT_token,user_email, session: AsyncSession):
        try:
            stmt = select(RefreshToken).where(
                RefreshToken.email == user_email,
                RefreshToken.token == JWT_token)
            tokenObj = await session.scalar_one_or_none(stmt)
            if tokenObj is None:
                return False
        except SQLAlchemyError:
            raise
    
    @staticmethod
    async def token_exists(user_email, session: AsyncSession):
        try:
            stmt = select(RefreshToken).where(
                RefreshToken.email == user_email)
            tokenObj = await session.scalar_one_or_none(stmt)
            if tokenObj is None:
                return False
            return True
        except SQLAlchemyError:
            raise
    