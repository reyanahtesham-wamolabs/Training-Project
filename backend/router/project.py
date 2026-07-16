from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.project_models import Project,CreateProject,CreateTag,Tag,ArchiveProject
from dependencies.Authorization import get_current_user, get_current_admin
from dependencies.database import get_db
from schema.user_models import User as db_User
from repository.project import ProjectRepo
router_project = APIRouter()

@router_project.post("/create_project/")
async def create_project(data: CreateProject,current_user: db_User = Depends(get_current_user), session: AsyncSession = Depends(get_db)):
    project=Project(name=data.name,start_date=data.start_date,end_date=data.end_date,archived=data.archived,
                    category=data.category,status=data.status)
    await ProjectRepo.create_project(project,session)    
    return {"status":"Project Created Successfully","Project ID":project.id}

@router_project.post("/create_tag/")
async def create_tag(data: CreateTag,current_user: db_User = Depends(get_current_user), session: AsyncSession = Depends(get_db)):
    tag=Tag(name=data.name,)
    await ProjectRepo.create_tag(tag,session)
    return {"status":"Tag Created Successfully","Tag ID":tag.id}
#List of all the tags
@router_project.get("/get_all_tags/")
async def get_all_tags(current_user: db_User = Depends(get_current_user),session: AsyncSession = Depends(get_db)):
   tags=await ProjectRepo.get_all_tags(session)
   return tags

@router_project.patch("/archive_project/")
async def archive_project_route(project:ArchiveProject,current_admin: db_User = Depends(get_current_admin),session:AsyncSession=Depends(get_db)):
    changed_project=ProjectRepo.change_project_archive(project.id,project.archive,session)
    return {"status":"Change Successful","Project ID":changed_project.id,"Archived":changed_project.archived}
