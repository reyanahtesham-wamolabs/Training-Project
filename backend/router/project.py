from fastapi import APIRouter, Depends
from typing import Annotated

from services.project_services import ProjectService
from dependencies.services import get_project_service
from dependencies.authorization import (
    get_current_user,
    get_current_admin,
    get_current_manager,
)
from models.project_models import CreateProject, CreateTag, ArchiveProject,AddTagToProject
from schema.user import User as db_User
from models.project_models import ProjectUpdate

router_project = APIRouter()

@router_project.post("/create_project")
async def create_project(
    data: CreateProject,
    current_user: db_User = Depends(get_current_manager),
    project_service: ProjectService = Depends(get_project_service),
):
    project = await project_service.create_project(data, current_user)
    return {"status": "Project Created Successfully", "Project ID": project.id}

@router_project.post("/create_tag")
async def create_tag(
    data: CreateTag,
    current_user: db_User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    tag = await project_service.create_tag(data, current_user)
    return {"status": "Tag Created Successfully", "Tag ID": tag.id}

@router_project.get("/get_all_tags")
async def get_all_tags(
    current_user: db_User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    return await project_service.get_all_tags()


@router_project.get("/get_all_projects")
async def get_all_projects(
    current_user: db_User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    return await project_service.get_all_projects(current_user)

@router_project.patch("/archive_project")
async def archive_project_route(
    project: ArchiveProject,
    current_user: db_User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    changed_project = await project_service.archive_project(
        current_user, project.id, project.archive
    )
    return {
        "status": "Change Successful",
        "Project ID": changed_project.id,
        "Archived": changed_project.archived,
    }

@router_project.delete("/hard_delete_project")
async def hard_delete_project_route(
    project_id: str,
    current_user: db_User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    return await project_service.hard_delete_project(current_user, project_id)


@router_project.patch("/update_project")
async def update_project_route(
    data: ProjectUpdate,
    current_user: db_User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
):
    project = await project_service.update_project(data, current_user)
    return {"status": "Project Updated Successfully", "Project ID": project.id}
