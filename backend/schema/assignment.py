from __future__ import annotations
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import ForeignKey
from .baseclass import Base


class Assignment(Base):
    __tablename__ = "Assignment"
    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("User.id"))
    task_id: Mapped[str] = mapped_column(ForeignKey("Task.id"))
    user: Mapped["User"] = relationship(back_populates="assignments")
    task: Mapped["Task"] = relationship(back_populates="assignments")
