from __future__ import annotations
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column,relationship
from .baseclass import Base
from sqlalchemy import ForeignKey,DateTime
from sqlalchemy import String
from datetime import datetime,timezone,timedelta
import uuid



class OTP(Base):
    __tablename__ = "OTP"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    code:Mapped[str]
    valid_till: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    user_id: Mapped[str] = mapped_column(String, ForeignKey("User.id"), nullable=False)
    user_name: Mapped[str] = mapped_column(String, nullable=False)
    new_desired_password:Mapped[str]
    user = relationship("User")
