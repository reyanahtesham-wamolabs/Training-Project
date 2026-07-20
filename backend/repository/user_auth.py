from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from schema.user import User as db_User
from schema.otp import OTP as db_otp
from models.user_model import User, UserLogin
from fastapi import HTTPException
from schema.enums import Levels
from helper_functions.hashing import check_password
from datetime import datetime,timezone

class UserCrud:

    @staticmethod
    async def add_user(data: User, session: AsyncSession):
        User1 = db_User(
            id=data.id,
            password=data.password,
            role=data.role,
            name=data.name,
            active=True,
            email=data.email,
            privacy_level=Levels.high,
            soft_delete=False,
        )
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
            if not usersObj.verified:
                raise HTTPException(status_code=403, detail="Verification Needed")
            if usersObj is None or not usersObj.active:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            if not check_password(data.password, usersObj.password):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            return usersObj
        except SQLAlchemyError:
            raise

    @staticmethod
    async def insert_OTP(data: db_otp, session: AsyncSession):
        try:
            session.add(data)
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise

    @staticmethod
    async def check_otp(otp_code: str, current_user: db_User, session: AsyncSession):
        try:
            stmt = (
                select(db_otp)
                .where(db_otp.user_id == current_user.id)
                .where(db_otp.valid_till > datetime.now(timezone.utc))
            )
            result = await session.execute(stmt)
            otp_objs = result.scalars().all()
            for i in otp_objs:
                if check_password(otp_code, i.code):
                    return i
            return False
        except SQLAlchemyError:
            raise
