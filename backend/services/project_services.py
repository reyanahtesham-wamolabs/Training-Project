import uuid
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from repository.project import ProjectRepo
from schema.project import Project as db_project, Tag as db_tag
from schema.user import User as db_user
from schema.enums import AssignmentRole
from models.project_models import CreateProject, CreateTag,AddTagToProject
from repository.user_repository import get_user_assignment
from services.activity_log_services import ActivityLogService
from schema.enums import ActivityActionType
from services.notification_service import NotificationService

class ProjectService:
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def create_project(self, data: CreateProject, current_user: db_user) -> db_project:
        existing = await ProjectRepo.get_project_by_name(data.name, self.session)
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
            created_project = await ProjectRepo.create_project(project, self.session)

            await ActivityLogService.log_activity_static(
                session=self.session,
                modified_by_user_id=current_user.id,
                action_type=ActivityActionType.create_project,
                message=f"Project '{created_project.name}' created by user '{current_user.name}'",
                project_id=created_project.id
            )
            from services.notification_service import NotificationService
            await NotificationService.notify_user(
                user_id=current_user.id,
                subject="Project Created",
                text=f"Project '{created_project.name}' has been created successfully.",
                session=self.session,
                related_project_id=created_project.id,
            )
            return created_project
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create project due to a database error",
            ) from e

    async def create_tag(self, data: CreateTag, current_user: db_user) -> db_tag:
        existing = await ProjectRepo.get_tag_by_name(data.name, self.session)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tag '{data.name}' already exists",
            )
        tag = db_tag(id=str(uuid.uuid4()), name=data.name)
        try:
            created_tag = await ProjectRepo.create_tag(tag, self.session)
            await NotificationService.notify_user(
                user_id=current_user.id,
                subject="Tag Created",
                text=f"Tag '{created_tag.name}' has been created successfully.",
                session=self.session,
            )
            return created_tag
        except SQLAlchemyError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create tag due to a database error",
            ) from e

    async def get_all_tags(self):
        try:
            return await ProjectRepo.get_all_tags(self.session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch tags due to a database error",
            ) from e

    async def get_all_projects(self):
        try:
            return await ProjectRepo.get_all_projects(self.session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch projects due to a database error",
            ) from e



    async def archive_project(
        self, current_user: db_user, project_id: str, archive_status: bool
    ) -> db_project:
        project = await ProjectRepo.get_project_by_id(project_id, self.session)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id '{project_id}' not found",
            )

        from schema.enums import Roles
        from sqlalchemy import select, exists
        from schema.task import Task
        from schema.assignment import Assignment

        # Check if user is assigned as project_admin on any task within this project
        stmt = select(
            exists().where(
                Assignment.user_id == current_user.id,
                Assignment.role == AssignmentRole.project_admin,
                Assignment.task_id == Task.id,
                Task.project_id == project_id,
            )
        )
        is_project_admin = await self.session.scalar(stmt)

        if current_user.role not in [Roles.admin, Roles.manager] and not is_project_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not authorized to archive project",
            )
        try:
            result = await ProjectRepo.change_project_archive(
                project_id, archive_status, self.session
            )
            await ActivityLogService.log_activity_static(
                session=self.session,
                modified_by_user_id=current_user.id,
                action_type=ActivityActionType.archive_project,
                message=f"Project '{result.name}' archived status changed to {archive_status} by '{current_user.name}'",
                project_id=project_id
            )
            from services.notification_service import NotificationService
            status_str = "archived" if archive_status else "unarchived"
            await NotificationService.notify_project_members(
                project_id=project_id,
                subject=f"Project {status_str.capitalize()}",
                text=f"The project '{result.name}' has been {status_str} by {current_user.name}.",
                session=self.session,
                exclude_user_id=current_user.id,
                related_project_id=project_id,
            )
            return result
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to archive project due to a database error",
            ) from e

    async def update_project(self, data, current_user: db_user) -> db_project:
        project = await ProjectRepo.get_project_by_id(data.id, self.session)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id '{data.id}' not found",
            )

        from schema.enums import Roles
        from sqlalchemy import select, exists
        from schema.task import Task
        from schema.assignment import Assignment

        stmt = select(
            exists().where(
                Assignment.user_id == current_user.id,
                Assignment.role == AssignmentRole.project_admin,
                Assignment.task_id == Task.id,
                Task.project_id == project.id,
            )
        )
        is_project_admin = await self.session.scalar(stmt)

        if current_user.role not in [Roles.admin, Roles.manager] and not is_project_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not authorized to update project",
            )

        updated = await ProjectRepo.update_project(data, self.session)

        await ActivityLogService.log_activity_static(
            session=self.session,
            modified_by_user_id=current_user.id,
            action_type=ActivityActionType.update_project,
            message=f"Project '{updated.name}' was updated by '{current_user.name}'",
            project_id=updated.id
        )

        return updated
