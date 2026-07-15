from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from schema.project import Project as db_project, Tag as db_tag
from models.project_models import Project,Tag

class ProjectRepo:

    @staticmethod
    async def create_project(data: Project, session: AsyncSession):
        project=db_project(id=data.id,name=data.name,start_date=data.start_date,end_date=data.end_date,archived=data.archived
                        ,category=data.category,status=data.status,soft_delete=data.soft_delete)        
        try:
            session.add(project)
            await session.commit()
            return project
        except SQLAlchemyError:
            await session.rollback()
            raise

    @staticmethod
    async def change_project_archive(project_id:str,archive_status:bool,session:AsyncSession):
        try:
            project=await session.get(db_project,project_id)
            project.archived=archive_status
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise

    @staticmethod
    async def get_project_by_id(project_id:str,session:AsyncSession):
        try:
            project=await session.get(db_project,project_id)
            return project
        except SQLAlchemyError:
            await session.rollback()
            raise

    @staticmethod
    async def create_tag(data : Tag,session:AsyncSession):
        tag=db_tag(id=data.id,name=data.id)
        try:
            session.add(tag)
            await session.commit()
            return tag
        except SQLAlchemyError:
            await session.rollback()
            raise
    @staticmethod
    async def get_all_projects(session:AsyncSession):
        try:
            stmt=(select(db_project).options(selectinload(db_project.tags)))
            result=await session.execute(stmt)
            tags=result.scalars().all()
            return tags
        except SQLAlchemyError:
            await session.rollback()
            raise

    @staticmethod
    async def get_all_tags(session:AsyncSession):
        try:
            stmt=(select(db_tag).options(selectinload(db_tag.projects)))
            result=await session.execute(stmt)
            tags=result.scalars().all()
            return tags
        except SQLAlchemyError:
            await session.rollback()
            raise


