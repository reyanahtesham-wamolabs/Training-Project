
from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column,relationship
from schema.enums import ProjectStatus,Categories
from sqlalchemy import Enum as sa_enum,Table, Column, ForeignKey
from .baseclass import Base
from datetime import date

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
        ForeignKey("Tags.id", ondelete="CASCADE"),
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
    Status:Mapped[ProjectStatus]=mapped_column(sa_enum(ProjectStatus))
    tags: Mapped[list["Tag"]] = relationship(
            secondary=project_tag_association,
            back_populates="projects",
        )
class Tag(Base):
    __tablename__="Tags"
    id:Mapped[str]=mapped_column(primary_key=True)
    name:Mapped[str]
    projects: Mapped[list["Project"]] = relationship(
        secondary=project_tag_association,
        back_populates="tags",
    )