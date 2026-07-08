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

class Task(Base):
    __tablename__="Task"
    ID:Mapped[str]=mapped_column(primary_key=True)
    projectID:Mapped[str]=mapped_column(ForeignKey("Project.ID"))
    Name:Mapped[str]
    ScheduleDate: Mapped[date | None] = mapped_column(Date, nullable=True)
    Status:Mapped[str]#Add Enum
    SoftDelete:Mapped[bool]
    ScheduleDate: Mapped[date]
    Priority:Mapped[str]#Enum    
    project: Mapped["Project"] = relationship(back_populates="tasks")
    comments: Mapped[List["Comment"]] = relationship(back_populates="task",cascade="all, delete-orphan")
    assignments: Mapped[List["Assignment"]] = relationship(back_populates="task",cascade="all, delete-orphan")
    activity_logs: Mapped[List["ActivityLog"]] = relationship(back_populates="task")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="task",cascade="all, delete-orphan",)
    external_collaborations: Mapped[List["ExternalCollaboration"]] = relationship(back_populates="task",cascade="all, delete-orphan",)
    parent_dependencies: Mapped[List["TaskDepends"]] = relationship(back_populates="child_task",foreign_keys="Depends.ChildTask",cascade="all, delete-orphan")
    child_dependencies: Mapped[List["TaskDepends"]] = relationship(back_populates="parent_task",foreign_keys="Depends.ParentTask",cascade="all, delete-orphan")

class TaskDepends(Base):
    __tablename__="TaskDepends"
    ParentTask:Mapped[str]=mapped_column(ForeignKey("Task.ID"), primary_key=True)
    ChildTask:Mapped[str]=mapped_column(ForeignKey("Task.ID"), primary_key=True)
    parent_task: Mapped["Task"] = relationship(back_populates="child_dependencies")
    child_task: Mapped["Task"] = relationship(back_populates="parent_dependencies")

class Comment(Base):
    __tablename__="Comment"
    ID:Mapped[str]=mapped_column(primary_key=True)
    Text:Mapped[str]
    TaskID:Mapped[str]=mapped_column(ForeignKey("Task.ID"))
    UserID:Mapped[str]=mapped_column(ForeignKey("User.ID"))
    ReplyID:Mapped[str]=mapped_column(ForeignKey("Comment.ID"))
    task: Mapped["Task"] = relationship(back_populates="comments")
