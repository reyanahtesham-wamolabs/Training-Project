from __future__ import annotations
from helper_functions.hashing import hash_password, MAX_PASSWORD_LENGTH
from repository.user_repository import (
    get_user_by_email,
    save_user,
    update_user,
    assign_user as repo_assign_user,
    get_all_users as get_users,
    get_user_assignment,
    delete_assignment,
)
from helper_functions.opt_gen import email_collaborator_welcome
from repository.project import ProjectRepo
from pydantic import EmailStr
from schema.enums import Roles, Levels
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from models.user_modification import ChangeStatus
from models.user_model import AssignUser, CreateAssignUser, ChangeUserRole, CreateExternalCollaborator, UnassignUser
from repository.task import TaskCrud
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from schema.team import Team as db_Team, TeamMember as db_TeamMember
from sqlalchemy import select, exists
from services.notification_service import NotificationService
from schema.enums import AssignmentRole
import secrets
import uuid
from schema.user import User as db_User
from services.activity_log_services import ActivityLogService
from schema.enums import ActivityActionType


class UserManagementService:
    def __init__(self, db_session):
        self.session = db_session

    async def get_user_profile(self, current_user):
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        role_str = str(current_user.role.value if hasattr(current_user.role, 'value') else current_user.role)
        privacy_str = str(current_user.privacy_level.value if hasattr(current_user.privacy_level, 'value') else current_user.privacy_level)
        return {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": role_str,
            "privacy_level": privacy_str,
            "verified": current_user.verified,
            "active": current_user.active,
            "is_external": getattr(current_user, 'is_external', False),
        }

    async def modify_status(self, data: ChangeStatus, current_admin):
        user = await get_user_by_email(data.email, self.session)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if data.role is not None:
            try:
                user.role = (
                    Roles(data.role) if not isinstance(data.role, Roles) else data.role
                )
            except ValueError:
                try:
                    user.role = Roles[data.role]
                except KeyError:
                    raise HTTPException(
                        status_code=400, detail="invalid role value"
                    ) from None

        if data.active is not None:
            user.active = bool(data.active)

        result = await update_user(user, self.session)
        try:
            await NotificationService.notify_user(
                user_id=user.id,
                subject="Account Status Updated",
                text=f"Your account status has been updated by an admin.",
                session=self.session,
            )
        except SQLAlchemyError:
            pass
        
        return result

    async def soft_delete_user(self, current_user):
        if current_user.soft_delete:
            current_user.soft_delete = False
        else:
            current_user.soft_delete = True
        return await update_user(current_user, self.session)

    delete_user = soft_delete_user

    async def hard_delete_user(self, user_id: str, current_admin):
        from repository.user_repository import get_user_by_id, hard_delete_user
        user_obj = await get_user_by_id(user_id, self.session)
        if user_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id '{user_id}' not found",
            )
        await hard_delete_user(user_id, self.session)
        return {"status": "User Permanently Deleted"}

    async def change_privacy(self, privacy_level, current_user):
        current_user.privacy_level = privacy_level.level
        return await update_user(current_user, self.session)


    async def change_user_role(self,user:ChangeUserRole):
        current_user=await get_user_by_email(user.user_email, self.session)
        current_user.role = user.user_role
        return await update_user(current_user,self.session)
        
        
    async def get_all_users(self):
        return await get_users(self.session)

    async def assign_user(self, assignment_data: CreateAssignUser, current_user=None):
        if current_user and getattr(current_user, 'is_external', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="External collaborators cannot assign or be assigned to tasks",
            )

        user_role_str = str(getattr(current_user.role, 'value', current_user.role)).lower() if current_user else ''
        if current_user and user_role_str == 'member' and assignment_data.user_email != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Members are only allowed to assign themselves to tasks",
            )

        assignment = AssignUser(
            user_email=assignment_data.user_email,
            task_id=assignment_data.task_id,
        )
        user = await get_user_by_email(assignment.user_email, self.session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{assignment.user_email}' not found",
            )
        if getattr(user, 'is_external', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User '{assignment.user_email}' is an external collaborator and cannot be assigned to tasks",
            )
        task = await TaskCrud.get_task_by_id(assignment.task_id, self.session)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{assignment.task_id}' not found",
            )


        from repository.team import TeamRepo
        is_team_member = await TeamRepo.is_user_in_project_team(user.id, task.project_id, self.session)

        if not is_team_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"User '{assignment.user_email}' is not a member of the team "
                    f"for the project this task belongs to"
                ),
            )

        existing_assignment = await get_user_assignment(user.id, assignment.task_id, self.session)
        if existing_assignment is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User '{assignment.user_email}' is already assigned to this task.",
            )

        try:
            assigned_result = await repo_assign_user(
                assignment.id,
                user.id,
                assignment.task_id,
                self.session,
            )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create assignment due to a database error",
            )
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This assignment already exists or violates a constraint",
            )        
        try:
            await NotificationService.notify_user(
                user_id=user.id,
                subject="Assigned to Task",
                text=f"You have been assigned to task '{task.name}'.",
                session=self.session,
                related_task_id=assignment.task_id,
                related_project_id=task.project_id,
            )
            return assigned_result

        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create assignment due to a database error",
            )

    async def unassign_user(self, unassign_data: UnassignUser, current_user=None):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        task = await TaskCrud.get_task_by_id(unassign_data.task_id, self.session)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{unassign_data.task_id}' not found",
            )

        # Check authorization: Overall admin OR Project admin for task's project
        is_overall_admin = current_user.role == Roles.admin

        from repository.team import TeamRepo
        is_project_admin = await TeamRepo.is_project_admin(current_user.id, task.project_id, self.session)

        if not (is_overall_admin or is_project_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project admin and overall admin can delete task assignments",
            )

        deleted = await delete_assignment(
            task_id=unassign_data.task_id,
            user_id=unassign_data.user_id,
            user_email=unassign_data.user_email,
            session=self.session
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found for the specified task and user",
            )

        await ActivityLogService.log_activity_static(
            session=self.session,
            modified_by_user_id=current_user.id,
            action_type=ActivityActionType.update_task,
            message=f"Task assignment deleted for task '{task.name}' by '{current_user.name}'",
            project_id=task.project_id,
            task_id=task.id
        )
        return True

    async def create_external_collaborator(self, data: CreateExternalCollaborator, current_user):
        existing_user = await get_user_by_email(data.email, self.session)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A user with email '{data.email}' already exists",
            )


        temp_password = secrets.token_urlsafe(8)
        hashed_password = hash_password(temp_password)

        new_user = db_User(
            id=str(uuid.uuid4()),
            name=data.name,
            email=data.email,
            password=hashed_password,
            role=Roles.member,
            active=True,
            verified=True,
            privacy_level=Levels.low,
            soft_delete=False,
            is_external=True
        )
        saved_user = await save_user(new_user, self.session)

        # Add external collaborator to the project's team
        from repository.team import TeamRepo
        await TeamRepo.add_user_to_project_team(saved_user.id, data.project_id, self.session)

        # Fetch project name for email
        project_obj = await ProjectRepo.get_project_by_id(data.project_id, self.session)
        project_name = project_obj.name if project_obj else "Project Workspace"

        # Dispatch real email

        try:
            await email_collaborator_welcome(
                email=saved_user.email,
                name=saved_user.name,
                temp_password=temp_password,
                project_name=project_name
            )
        except Exception as e:
            print(f"Failed to dispatch collaborator welcome email: {e}")

        try:
            await NotificationService.notify_user(
                user_id=saved_user.id,
                subject="Welcome as External Collaborator",
                text=f"You have been added as an external collaborator to project '{project_name}' by User {current_user.name}.",
                session=self.session,
                related_project_id=data.project_id
            )
        except Exception:
            pass

        return {
            "status": "ok",
            "message": "External collaborator created successfully",
            "email": saved_user.email,
            "temp_password": temp_password,
            "id": saved_user.id
        }
