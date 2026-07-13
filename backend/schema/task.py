from __future__ import annotations
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column
from datetime import datetime
from uuid import uuid4
from .enums import Levels,Status
from .baseclass import Base
from datetime import date
from sqlalchemy import Column
from sqlalchemy import Table
from sqlalchemy.orm import relationship



association_table = Table(
    "task_dependency",
    Base.metadata,
    Column("prerequisite_task_id", ForeignKey("Task.id"), primary_key=True),
    Column("dependant_task_id", ForeignKey("Task.id"), primary_key=True),
)

class Task(Base):
    __tablename__="Task"
    id:Mapped[str]=mapped_column(primary_key=True)
#    projectID:Mapped[str]=mapped_column(ForeignKey("Project.ID"))
    name:Mapped[str]
    schedule_date: Mapped[date | None] = mapped_column(date, nullable=True)
    status:Mapped[Status]
    soft_delete:Mapped[bool]=mapped_column(bool,default=False)
    priority:Mapped[Levels]    
    dependants: Mapped[list["Task"]] = relationship(
        "Task",
        secondary=association_table,
        primaryjoin=id == association_table.c.prerequisite_task_id,
        secondaryjoin=id == association_table.c.dependant_task_id,
        back_populates="prerequisites",
    )

    prerequisites: Mapped[list["Task"]] = relationship(
        "Task",
        secondary=association_table,
        primaryjoin=id == association_table.c.dependant_task_id,
        secondaryjoin=id == association_table.c.prerequisite_task_id,
        back_populates="dependants",
    )




