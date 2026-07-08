 
from __future__ import annotations
import asyncio
from datetime import datetime
from typing import List
from typing import Optional
from datetime import date
from sqlalchemy import Date
from sqlalchemy import ForeignKey 
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import Session,validates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from Schema.Enums import Roles

class Base (DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "User"
    ID:Mapped[str]=mapped_column(primary_key=True)
    name:Mapped[str]
    role:Mapped[str]
    active:Mapped[bool]
    email:Mapped[str]
    password:Mapped[str]
    privacyLevel:Mapped[str]
    SoftDelete:Mapped[bool] 
class OTP(Base):
    __tablename__="OTP"
    Email:Mapped[str]=mapped_column(primary_key=True)
    OTPString:Mapped[str]
    ExpiresAt:Mapped[datetime]
    CreatedAt:Mapped[datetime]
    Attempts:Mapped[int]

class RefreshToken(Base):
    __tablename__="RefreshToken"
    ID:Mapped[str]=mapped_column(primary_key=True)
    Token=Mapped[str]
    ExpireDate=Mapped[datetime]

# class Task(Base):
#     __tablename__="Task"
#     Name:Mapped[str]=mapped_column(primary_key=True)
#     Status:Mapped[str]
#     projectID:Mapped[str]=mapped_column(ForeignKey("Project.ID"))
#     SoftDelete:Mapped[bool]=mapped_column(bool)
#     Scheduled:Mapped[bool]
#     ScheduleDate: Mapped[date | None] = mapped_column(Date, nullable=True)

