from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from schema.project import User as db_project
from models.project_models import Project,CreateProject
from fastapi import HTTPException
from helper_functions.hashing import check_password

class ProjectRepo:
    @staticmethod
    async def create_project(data: Project, session: AsyncSession):
        project=Project(id=data.id,name=data.name,start_date=data.start_date,end_date=data.end_date,archived=data.archived
                        ,tag=data.tag,category=data.category,status=data.status,soft_delete=data.soft_delete)        
        try:
            session.add(project)
            await session.commit()
            return project
        except SQLAlchemyError:
            await session.rollback()
            raise

    @staticmethod
    async def change_archive(project_id:str,archive_status:bool,session:AsyncSession):
        try:
            project=await session.get(db_project,project_id)
            project.archived=archive_status
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise
