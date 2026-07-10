from __future__ import annotations
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column
from datetime import datetime
from .baseclass import Base

class RefreshToken(Base):
    __tablename__ = "RefreshToken"
    email: Mapped[str] = mapped_column(ForeignKey("User.email") ,primary_key=True)
    token: Mapped[str]
    expire_date: Mapped[datetime]