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


class Notification(Base):
    __tablename__="Notification"
    ID:Mapped[str]=mapped_column(primary_key=True)
    UserID:Mapped[str]=mapped_column(ForeignKey("User.ID"))
    Subject:Mapped[str]
    Text:Mapped[str]
    Schedule:Mapped[datetime]
    Read:Mapped[bool]
    ReadAt:Mapped[datetime]
    RelatedTask: Mapped[str | None] = mapped_column(ForeignKey("Task.ID"), nullable=True)
    RelatedComment: Mapped[str | None] = mapped_column(ForeignKey("Comment.ID"), nullable=True)
    RelatedProject: Mapped[str | None] = mapped_column(ForeignKey("Project.ID"), nullable=True)
    RelatedMessage: Mapped[str | None] = mapped_column(ForeignKey("Message.ID"), nullable=True)
    user:Mapped["User"] = relationship("User",back_populates="notifications")    
    project: Mapped["Project | None"] = relationship(back_populates="notifications")
    task: Mapped["Task | None"] = relationship(back_populates="notifications")
    