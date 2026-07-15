from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.project_models import Project,CreateProject,CreateTag,Tag
from dependencies.database import get_db
from repository.project import ProjectRepo
router_project = APIRouter()

@router_project.post("/create_project/")
async def create_project(data: CreateProject, session: AsyncSession = Depends(get_db)):
    project=Project(name=data.name,start_date=data.start_date,end_date=data.end_date,archived=data.archived,
                    category=data.category,status=data.status)
    ProjectRepo.create_project(project,session)    
    return project

@router_project.post("/create_tag/")
async def create_tag(data: CreateTag, session: AsyncSession = Depends(get_db)):
    tag=Tag(name=data.name)
    return tag

#List of all the tags
@router_project.get("/get_all_tags/")
async def get_all_tags(session: AsyncSession = Depends(get_db)):
   tags=ProjectRepo.get_all_tags(session)
   return tags

@router_project.patch("/archive_user/")
async def archive_project_route(id:str,archive_status:bool,session:AsyncSession=Depends(get_db)):
    return ProjectRepo.change_archive(id,archive_status,session)

