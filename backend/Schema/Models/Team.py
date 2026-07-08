from __future__ import annotations
import asyncio
from datetime import datetime
from typing import List
from typing import Optional
from datetime import date
from sqlalchemy import Date
from sqlalchemy import ForeignKey 
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import Session,validates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from .BaseClass import Base

class Team(Base):
    __tablename__="Team"
    ID:Mapped[str]=mapped_column(primary_key=True)
    ProjectID:Mapped[str]=mapped_column(ForeignKey("Project.ID"))
    Name:Mapped[str]
    ReadAt:Mapped[datetime]
    project: Mapped["Project"] = relationship(back_populates="teams")

    
class Message(Base):
    __tablename__="Message"
    ID:Mapped[str]=mapped_column(primary_key=True)
    MemberID:Mapped[str]=mapped_column(ForeignKey("TeamMembers.ID"))
    TeamID:Mapped[str]=mapped_column(ForeignKey("Team.ID"))
    Text:Mapped[str]


class TeamMembers(Base):
    __tablename__="TeamMembers"
    ID:Mapped[str]=mapped_column(primary_key=True)
    UserID:Mapped[str]=mapped_column(ForeignKey("User.ID"))
    TeamID:Mapped[str]=mapped_column(ForeignKey("Team.ID"))
    user: Mapped["User"] = relationship(back_populates="team_memberships",)

