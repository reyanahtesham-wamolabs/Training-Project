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


class UserManagementService:
    def __init__(self, db_session):
        self.session = db_session

    async def change_personal_information(self, data, current_user):
        # data is expected to have email, name?, new_email?, password?
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

        return await update_user(user, self.session)

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
        current_user=get_user_by_email(user.user_email)
        return await update_user(current_user,self.session)
        
    async def get_all_users(self):
        return get_users(self.session)

    async def assign_user(self, assignment_data: CreateAssignUser):
        assignment = AssignUser(**assignment_data.model_dump())
        user = await get_user_by_email(assignment.user_email, self.session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{assignment.user_email}' not found",
            )
        project = await ProjectRepo.get_project_by_name(
            assignment.project_name, self.session
        )
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{assignment.project_name}' not found",
            )
        task = await TaskCrud.get_task_by_id(assignment.task_id, self.session)
        if not task.project_id == project.id:
            raise "Task must be a part of the project"
        try:
            assigned_result = await repo_assign_user(
                assignment.id,
                user.id,
                project.id,
                assignment.task_id,
                assignment.role,
                self.session,
            )
            return assigned_result
        except IntegrityError as e:
            print(e.orig)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This assignment already exists or violates a constraint",
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create assignment due to a database error",
            )
