from __future__ import annotations
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import ForeignKey, String, Text, DateTime
from .baseclass import Base
from datetime import datetime, timezone
import uuid

class Comment(Base):
    __tablename__ = "Comment"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    user_id: Mapped[str] = mapped_column(ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    task_id: Mapped[str] = mapped_column(ForeignKey("Task.id", ondelete="CASCADE"), nullable=False)
    parent_comment_id: Mapped[str | None] = mapped_column(
        ForeignKey("Comment.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship()
    task: Mapped["Task"] = relationship(back_populates="comments")
    parent_comment: Mapped[Comment | None] = relationship(
        "Comment",
        remote_side=[id],
        back_populates="reply",
    )
    reply: Mapped[Comment | None] = relationship(
        "Comment",
        back_populates="parent_comment",
        uselist=False,
    )
