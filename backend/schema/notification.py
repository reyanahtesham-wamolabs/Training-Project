import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .baseclass import Base

class Notification(Base):
    __tablename__ = "Notification"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("User.id", ondelete="CASCADE"), nullable=False
    )
    related_task_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("Task.id", ondelete="SET NULL"), nullable=True
    )
    related_comment_id: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    related_project_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("Project.id", ondelete="SET NULL"), nullable=True
    )
    related_message_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("Message.id", ondelete="SET NULL"), nullable=True
    )
    subject: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    delivered: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user = relationship("User")
    task = relationship("Task")
    project = relationship("Project")
    message = relationship("Message")
