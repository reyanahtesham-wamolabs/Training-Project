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

class ActivityLog(Base):
    __tablename__="ActivityLog"
    ID:Mapped[str]=mapped_column(primary_key=True)
    ModifiedByUserID:Mapped[str]=mapped_column(ForeignKey("User.ID"))
    TargetUserID:Mapped[str |None]=mapped_column(ForeignKey("User.ID"),nullable=True)
    TaskID: Mapped[str | None] = mapped_column(ForeignKey("Task.ID"), nullable=True)
    ProjectID: Mapped[str | None] = mapped_column(ForeignKey("Project.ID"), nullable=True)
    ActionType:Mapped[str]#Add Enum
    Message:Mapped[str]
    ActionTime:Mapped[datetime]
    modified_by_user: Mapped["User"] = relationship(back_populates="activity_logs_created")
    target_user: Mapped["User | None"] = relationship(back_populates="activity_logs_target")
    project: Mapped["Project | None"] = relationship(back_populates="activity_logs")
    task: Mapped["Task | None"] = relationship(back_populates="activity_logs")            
