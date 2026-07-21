from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from schema.project import Project as db_project,Tag as db_tag


class ProjectRepo:

    @staticmethod
    async def create_project(project: db_project, session: AsyncSession) -> db_project:
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project

    @staticmethod
    async def delete_project(project_id:str , session: AsyncSession):
        project=session.get(project_id)
        if project is None:
            return False
        await session.delete(project)
        await session.commit()
        return True

    @staticmethod
    async def update_project(data, session: AsyncSession) -> db_project | None:
        project = await session.get(db_project, data.id)
        if project is None:
            return None

        update_data = data.model_dump(exclude_unset=True, exclude={"id"})
        for field, value in update_data.items():
            setattr(project, field, value)

        await session.commit()
        await session.refresh(project)
        return project

    @staticmethod
    async def change_project_archive(
        project_id: str, archive_status: bool, session: AsyncSession
    ) -> db_project | None:
        project = await session.get(db_project, project_id)
        if project is None:
            return None
        project.archived = archive_status
        await session.commit()
        await session.refresh(project)
        return project

    @staticmethod
    async def get_project_by_id(project_id: str, session: AsyncSession) -> db_project | None:
        return await session.get(db_project, project_id)

    @staticmethod
    async def get_project_by_name(project_name: str, session: AsyncSession) -> db_project | None:
        stmt = select(db_project).where(db_project.name == project_name)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_tag(tag: db_tag, session: AsyncSession) -> db_tag:
        session.add(tag)
        await session.commit()
        await session.refresh(tag)
        return tag

    @staticmethod
    async def get_tag_by_name(tag_name: str, session: AsyncSession) -> db_tag | None:
        stmt = select(db_tag).where(db_tag.name == tag_name)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_projects(session: AsyncSession):
        stmt = select(db_project).options(selectinload(db_project.tags))
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_all_tags(session: AsyncSession):
        stmt = select(db_tag).options(selectinload(db_tag.projects))
        result = await session.execute(stmt)
        return result.scalars().all()