from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.project_services import ProjectService
from dependencies.authorization import (
    get_current_user,
    get_current_admin,
    get_current_manager,
)
from dependencies.database import get_db
from models.project_models import CreateProject, CreateTag, ArchiveProject
from  schema.user import User as db_User

router_project = APIRouter()


@router_project.post("/create_project/")
async def create_project(
    data: CreateProject,
    current_user: db_User = Depends(get_current_manager),
    session: AsyncSession = Depends(get_db),
):
    project = await ProjectService.create_project(data, current_user, session)
    return {"status": "Project Created Successfully", "Project ID": project.id}


@router_project.post("/create_tag/")
async def create_tag(
    data: CreateTag,
    current_user: db_User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    tag = await ProjectService.create_tag(data, session)
    return {"status": "Tag Created Successfully", "Tag ID": tag.id}


@router_project.get("/get_all_tags/")
async def get_all_tags(
    current_user: db_User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    return await ProjectService.get_all_tags(session)


@router_project.get("/get_all_projects/")
async def get_all_projects(
    current_user: db_User = Depends(get_current_manager),
    session: AsyncSession = Depends(get_db),
):
    return await ProjectService.get_all_projects(session)


@router_project.patch("/archive_project/")
async def archive_project_route(
    project: ArchiveProject,
    current_user: db_User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    changed_project = await ProjectService.archive_project(
        current_user, project.id, project.archive, session
    )
    return {
        "status": "Change Successful",
        "Project ID": changed_project.id,
        "Archived": changed_project.archived,
    }
