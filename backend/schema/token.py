from __future__ import annotations
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column
from datetime import datetime
from uuid import uuid4
from .baseclass import Base

class RefreshToken(Base):
    __tablename__ = "RefreshToken"
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(ForeignKey("User.email"))
    token: Mapped[str]
    expire_date: Mapped[datetime]