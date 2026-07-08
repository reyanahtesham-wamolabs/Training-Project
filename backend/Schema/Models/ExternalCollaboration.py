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

class ExternalCollaboration(Base):
    __tablename__="ExternalCollaboration"
    ID:Mapped[str]=mapped_column(primary_key=True)
    Email:Mapped[str]
    ProjectID:Mapped[str]=mapped_column(ForeignKey("Project.ID"))
    TaskID:Mapped[str]=mapped_column(ForeignKey("Task.ID"))    
    Purpose:Mapped[str]
    AccessType:Mapped[str]#Add Enum
    project: Mapped["Project | None"] = relationship(back_populates="external_collaborations")
    task: Mapped["Task | None"] = relationship(back_populates="external_collaborations")