from __future__ import annotations
from helper_functions.hashing import hash_password, MAX_PASSWORD_LENGTH
from repository.user_repository import (
    get_user_by_email,
    save_user,
    update_user,
    assign_user as repo_assign_user,
    get_all_users as get_users,
)
from repository.project import ProjectRepo
from pydantic import EmailStr
from schema.enums import Roles, Levels
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from models.user_modification import ChangeStatus
from models.user_model import AssignUser, CreateAssignUser,ChangeUserRole
from repository.task import TaskCrud
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from schema.team import Team as db_Team, TeamMember as db_TeamMember
from sqlalchemy import select, exists
from services.notification_service import NotificationService
from schema.enums import AssignmentRole

class UserManagementService:
    def __init__(self, db_session):
        self.session = db_session

    async def change_personal_information(self, data, current_user):
        user = await get_user_by_email(current_user.email, self.session)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        updated = False
        if getattr(data, "name", None):
            user.name = data.name
            updated = True
        if getattr(data, "new_email", None):
            user.email = str(data.new_email)
            updated = True
        if getattr(data, "new_password", None):
            if len(data.new_password) > MAX_PASSWORD_LENGTH:
                raise HTTPException(
                    status_code=400,
                    detail=f"Password must be at most {MAX_PASSWORD_LENGTH} characters",
                )
            user.password = hash_password(data.new_password)
            updated = True

        if updated:
            return await update_user(user, self.session)
        return user

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

    async def change_privacy(self, privacy_level, current_user):
        current_user.privacy_level = privacy_level.level
        return await update_user(current_user, self.session)


    async def change_user_role(self,user:ChangeUserRole):
        current_user=await get_user_by_email(user.user_email)
        return await update_user(current_user,self.session)
        
        
    async def get_all_users(self):
        return await get_users(self.session)

    async def assign_user(self, assignment_data: CreateAssignUser):
        
        assignment = AssignUser(
            user_email=assignment_data.user_email,
            task_id=assignment_data.task_id,
            role=assignment_data.role
        )
        user = await get_user_by_email(assignment.user_email, self.session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{assignment.user_email}' not found",
            )
        task = await TaskCrud.get_task_by_id(assignment.task_id, self.session)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{assignment.task_id}' not found",
            )


        team_member_exists_stmt = select(
            exists()
            .where(db_TeamMember.user_id == user.id)
            .where(
                db_TeamMember.team_id.in_(
                    select(db_Team.id).where(db_Team.project_id == task.project_id)
                )
            )
        )
        result = await self.session.execute(team_member_exists_stmt)
        is_team_member = bool(result.scalar())

        if not is_team_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"User '{assignment.user_email}' is not a member of the team "
                    f"for the project this task belongs to"
                ),
            )

        try:
            assigned_result = await repo_assign_user(
                assignment.id,
                user.id,
                assignment.task_id,
                assignment.role,
                self.session,
            )
        except SQLAlchemyError as e:
            print(e)
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
