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
from .BaseClass import Base

class OTPTable(Base):
    __tablename__="OTPTable"
    Email:Mapped[str]=mapped_column(primary_key=True)
    OTPString:Mapped[str]
    ExpiresAt:Mapped[datetime]
    CreatedAt:Mapped[datetime]
    Attempts:Mapped[int]

class RefreshTokenTable(Base):
    __tablename__="RefreshTokenTable"
    ID:Mapped[str]=mapped_column(primary_key=True)
    Token=Mapped[str]
    ExpireDate=Mapped[datetime]

