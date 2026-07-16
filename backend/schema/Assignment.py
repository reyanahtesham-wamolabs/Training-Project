from __future__ import annotations
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column,relationship
from sqlalchemy import Enum as sa_enum,ForeignKey
from .baseclass import Base
from schema.enums import AssignmentRole

class Assignment(Base):
    __tablename__="Assignment"
    id:Mapped[str]=mapped_column(primary_key=True)
    user_id:Mapped[str]=mapped_column(ForeignKey("User.id"))
    project_id:Mapped[str]=mapped_column(ForeignKey("Project.id"))
    task_id:Mapped[str]=mapped_column(ForeignKey("Task.id"))    
    role:Mapped["AssignmentRole"]=mapped_column(sa_enum(AssignmentRole))
    user: Mapped["User"] = relationship(back_populates="assignments")
    project: Mapped["Project"] = relationship(back_populates="assignments")
    task: Mapped["Task"] = relationship(back_populates="assignments")


