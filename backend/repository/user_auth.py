from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from schema.user_models import User as db_User 
from models.user_model import User,UserLogin
from fastapi import HTTPException
from helper_functions.hashing import check_password
class UserCrud:
    @staticmethod
    async def add_user(data: User, session: AsyncSession):
        User1 = db_User(id=data.id,password=data.password,role=data.role,name=data.name,active=True,email=data.email,privacy_level="high",soft_delete=False)
        try:
            session.add(User1)
            await session.commit()
            await session.refresh(User1)
            return User1
        except SQLAlchemyError:
            await session.rollback()
            raise

    @staticmethod
    async def user_login(data: UserLogin, session: AsyncSession):
        try:
            stmt = select(db_User).where(db_User.email == data.email)
            result = await session.execute(stmt)
            usersObj = result.scalar_one_or_none()
            if usersObj is None:
                raise HTTPException(
                    status_code=401, detail="Invalid credentials"
                )
            if not check_password(data.password, usersObj.password):
                raise HTTPException(
                    status_code=401, detail="Invalid credentials"
                )
            return usersObj
        except SQLAlchemyError:
            raise
