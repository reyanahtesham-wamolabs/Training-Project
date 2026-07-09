from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from Schema.Enums import Roles
from sqlalchemy import Enum as sa_enum

class Base (DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "User"
    ID:Mapped[str]=mapped_column(primary_key=True)
    name:Mapped[str]
    role:Mapped[Roles]=mapped_column(sa_enum(Roles))
    active:Mapped[bool]
    email:Mapped[str]
    password:Mapped[str]
    privacyLevel:Mapped[str]
    SoftDelete:Mapped[bool] 
