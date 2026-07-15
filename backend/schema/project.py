from __future__ import annotations
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column,relationship
from schema.enums import ProjectStatus,Categories
from sqlalchemy import Enum as sa_enum,Table, Column, ForeignKey
from .baseclass import Base
from datetime import date
from .task import Task
from typing import List

project_tag_association = Table(
    "ProjectTag",
    Base.metadata,
    Column(
        "project_id",
        ForeignKey("Project.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        ForeignKey("Tag.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Project(Base):
    __tablename__ = "Project"
    id:Mapped[str] = mapped_column(primary_key=True)
    name:Mapped[str]
    archived:Mapped[bool]
    soft_delete:Mapped[bool]
    start_date:Mapped[date]
    end_date:Mapped[date]
    category:Mapped[Categories]=mapped_column(sa_enum(Categories))
    status:Mapped[ProjectStatus]=mapped_column(sa_enum(ProjectStatus))
    tasks:Mapped[List["Task"]]=relationship(back_populates="parent_project")
    tags: Mapped[List["Tag"]] = relationship(
            secondary=project_tag_association,
            back_populates="projects",
        )
class Tag(Base):
    __tablename__="Tag"
    id:Mapped[str]=mapped_column(primary_key=True)
    name:Mapped[str]
    projects: Mapped[List["Project"]] = relationship(
        secondary=project_tag_association,
        back_populates="tags",
    )

