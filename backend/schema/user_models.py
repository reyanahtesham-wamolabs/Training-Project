from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from schema.enums import Roles
from sqlalchemy import Enum as sa_enum
from .baseclass import Base


class User(Base):
    __tablename__ = "User"
    ID:Mapped[str] = mapped_column(primary_key=True)
    name:Mapped[str]
    role:Mapped[Roles] = mapped_column(sa_enum(Roles))
    active:Mapped[bool]
    email:Mapped[str] = mapped_column(unique=True,nullable=False)
    password:Mapped[str]
    privacyLevel:Mapped[str]
    SoftDelete:Mapped[bool]
