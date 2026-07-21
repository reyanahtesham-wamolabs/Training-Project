from __future__ import annotations
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship
from schema.enums import Roles, Levels
from sqlalchemy import Enum as sa_enum
from .baseclass import Base
from typing import List


class User(Base):
    __tablename__ = "User"
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    role: Mapped[Roles] = mapped_column(sa_enum(Roles))
    active: Mapped[bool]
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    verified: Mapped[bool] = mapped_column(default=False)
    password: Mapped[str]
    privacy_level: Mapped[Levels] = mapped_column(sa_enum(Levels, name="Levels"))
    soft_delete: Mapped[bool]
    assignments: Mapped[List["Assignment"]] = relationship(back_populates="user")
