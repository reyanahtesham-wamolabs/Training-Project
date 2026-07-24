from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, DateTime, UniqueConstraint, Enum as sa_enum
from .baseclass import Base
from datetime import datetime
from schema.enums import IntervalUnit

class TaskReminder(Base):
    __tablename__ = "TaskReminder"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    task_id: Mapped[str] = mapped_column(ForeignKey("Task.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("User.id", ondelete="CASCADE"), index=True)
    interval_value: Mapped[int] = mapped_column(Integer, nullable=False)
    interval_unit: Mapped[IntervalUnit] = mapped_column(sa_enum(IntervalUnit, native_enum=False), nullable=False)
    next_run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    
    __table_args__ = (UniqueConstraint('task_id', 'user_id', name='uq_task_user_reminder'),)
    
    task = relationship("Task", backref="reminder")
