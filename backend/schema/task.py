from __future__ import annotations
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column
from datetime import datetime
from uuid import uuid4
from .enums import Levels,Status
from .baseclass import Base
from datetime import date

class Task(Base):
    __tablename__="Task"
    id:Mapped[str]=mapped_column(primary_key=True)
#    projectID:Mapped[str]=mapped_column(ForeignKey("Project.ID"))
    name:Mapped[str]
    schedule_date: Mapped[date | None] = mapped_column(date, nullable=True)
    status:Mapped[Status]
    soft_delete:Mapped[bool]=mapped_column(bool,default=True)
    priority:Mapped[Levels]    
