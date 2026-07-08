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


class Assignment(Base):
    __tablename__="Assignment"
    ID:Mapped[str]=mapped_column(primary_key=True)
    UserID:Mapped[str]=mapped_column(ForeignKey("User.ID"))
    ProjectID:Mapped[str]=mapped_column(ForeignKey("Project.ID"))
    TaskID:Mapped[str]=mapped_column(ForeignKey("Task.ID"))    
    Role:Mapped[str]#Add Enum
    user: Mapped["User"] = relationship(back_populates="assignments")
    project: Mapped["Project"] = relationship(back_populates="assignments")
    task: Mapped["Task"] = relationship(back_populates="assignments")