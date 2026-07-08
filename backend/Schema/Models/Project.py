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

class Project(Base):
    __tablename__="Project"
    ID:Mapped[str]=mapped_column(primary_key=True)
    Archived:Mapped[bool]
    StartDate: Mapped[date]
    EndDate: Mapped[date]
    SoftDelete:Mapped[bool]
    Tag:Mapped[str]#Add Enum
    Categories:Mapped[str]#Add Enum
    Status:Mapped[str]#Add Enum
    tasks: Mapped[List["Task"]] = relationship(back_populates="project",cascade="all, delete-orphan",)
    assignments: Mapped[List["Assignment"]] = relationship(back_populates="project",cascade="all, delete-orphan",)
    teams: Mapped[List["Team"]] = relationship(back_populates="project",cascade="all, delete-orphan",)
    activity_logs: Mapped[List["ActivityLog"]] = relationship(back_populates="project",)
    notifications: Mapped[List["Notification"]] = relationship(back_populates="project",cascade="all, delete-orphan",)
    external_collaborations: Mapped[List["ExternalCollaboration"]] = relationship(back_populates="project",cascade="all, delete-orphan",)
    