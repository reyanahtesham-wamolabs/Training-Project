from __future__ import annotations
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import ForeignKey, String, Text, DateTime, Enum as sa_enum
from .baseclass import Base
from .enums import ActivityActionType
from datetime import datetime, timezone
import uuid


class ActivityLog(Base):
    __tablename__ = "ActivityLog"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    modified_by_user_id: Mapped[str] = mapped_column(
        ForeignKey("User.id", ondelete="CASCADE"), nullable=False
    )
    target_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("User.id", ondelete="SET NULL"), nullable=True
    )
    task_id: Mapped[str | None] = mapped_column(
        ForeignKey("Task.id", ondelete="SET NULL"), nullable=True
    )
    project_id: Mapped[str | None] = mapped_column(
        ForeignKey("Project.id", ondelete="SET NULL"), nullable=True
    )
    action_type: Mapped[ActivityActionType] = mapped_column(
        sa_enum(ActivityActionType), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    change_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    modified_by_user = relationship("User", foreign_keys=[modified_by_user_id])
    target_user = relationship("User", foreign_keys=[target_user_id])
    task = relationship("Task")
    project = relationship("Project")
