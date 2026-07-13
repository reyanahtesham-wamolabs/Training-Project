from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from schema.enums import Roles
from sqlalchemy import Enum as sa_enum
from .baseclass import Base
from datetime import date

class User(Base):
    __tablename__ = "User"
    id:Mapped[str] = mapped_column(primary_key=True)
    name:Mapped[str]
    archived:Mapped[bool]
    soft_delete:Mapped[bool]
    start_date:Mapped[date]
    end_date:Mapped[date]
    tag:Mapped[str]#Enum
    category:Mapped[str]#Enum
    Status:Mapped[str]#Enum
