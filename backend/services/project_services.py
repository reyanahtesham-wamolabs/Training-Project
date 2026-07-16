import uuid
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from repository.project import ProjectRepo
from schema.project import Project as db_project, Tag as db_tag
from models.project_models import CreateProject, CreateTag


class ProjectService:

    @staticmethod
    async def create_project(data: CreateProject, session: AsyncSession) -> db_project:
        existing = await ProjectRepo.get_project_by_name(data.name, session)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Project '{data.name}' already exists",
            )

        project = db_project(
            id=str(uuid.uuid4()),
            name=data.name,
            start_date=data.start_date,
            end_date=data.end_date,
            archived=data.archived,
            category=data.category,
            status=data.status,
            soft_delete=False,
        )

        try:
            return await ProjectRepo.create_project(project, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create project due to a database error",
            ) from e

    @staticmethod
    async def create_tag(data: CreateTag, session: AsyncSession) -> db_tag:
        existing = await ProjectRepo.get_tag_by_name(data.name, session)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tag '{data.name}' already exists",
            )
        tag = db_tag(id=str(uuid.uuid4()), name=data.name)
        try:
            return await ProjectRepo.create_tag(tag, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create tag due to a database error",
            ) from e

    @staticmethod
    async def get_all_tags(session: AsyncSession):
        try:
            return await ProjectRepo.get_all_tags(session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch tags due to a database error",
            ) from e

    @staticmethod
    async def get_all_projects(session: AsyncSession):
        try:
            return await ProjectRepo.get_all_projects(session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch projects due to a database error",
            ) from e

    @staticmethod
    async def archive_project(
        project_id: str, archive_status: bool, session: AsyncSession
    ) -> db_project:
        try:
            project = await ProjectRepo.change_project_archive(
                project_id, archive_status, session
            )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update project due to a database error",
            ) from e

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id '{project_id}' not found",
            )

        return project
