from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from repository.task import TaskCrud
from schema.task import Task as db_task
from models.task_models import TaskCreation, TaskUpdate
from services.notification_service import NotificationService
from services.activity_log_services import ActivityLogService
from schema.enums import ActivityActionType,Roles,ProjectStatus

class TaskService:
    def __init__(self, db_session: AsyncSession):
        self.session = db_session
    async def get_user_task(self,current_user):
        return await TaskCrud.get_user_tasks(current_user.id)

    async def create_task(self, data: TaskCreation, current_user) -> db_task:
        if getattr(current_user, 'is_external', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="External collaborators cannot create tasks",
            )
            
        from repository.team import TeamRepo
        user_role = str(getattr(current_user.role, 'value', current_user.role)).lower()
        if user_role not in ['admin', 'manager']:
            is_team_member = await TeamRepo.is_user_in_project_team(current_user.id, data.project_id, self.session)
            if not is_team_member:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You must be a member of the project team to create tasks for this project.",
                )

        existing = await TaskCrud.get_task_by_name(data.name, data.project_id, self.session)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A task named '{data.name}' already exists in this project",
            )
        if data.schedule_date and data.due_date:
            if data.schedule_date>data.due_date:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Project start date cannot be later than the end date."
                )    
        try:
            task = await TaskCrud.add_task(data, self.session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task due to a database error",
            ) from e

        await ActivityLogService.log_activity_static(
                session=self.session,
                modified_by_user_id=current_user.id,
                action_type=ActivityActionType.create_task,
                message=f"Task '{task.name}' created in project '{task.project_id}' by user '{current_user.name}'",
                task_id=task.id,
                project_id=task.project_id
            )
        await NotificationService.notify_project_members(
                project_id=task.project_id,
                subject="Task Created",
                text=f"Task '{task.name}' has been created by {current_user.name}.",
                session=self.session,
                exclude_user_id=current_user.id,
                related_task_id=task.id,
                related_project_id=task.project_id
            )
        return task

    async def delete_task(self, task_id: str, current_user) -> None:
        task = await TaskCrud.get_task_by_id(task_id, self.session)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{task_id}' not found",
            )

        from repository.team import TeamRepo
        is_project_admin = await TeamRepo.is_project_admin(current_user.id, task.project_id, self.session)
        user_role = str(getattr(current_user.role, 'value', current_user.role)).lower()
        if user_role not in ['admin', 'manager'] and not is_project_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Members cannot delete tasks. Only admins, managers, or project admins can delete tasks.",
            )

        try:
            await NotificationService.notify_task_assignees(
                task_id=task_id,
                subject="Task Deleted",
                text=f"Task '{task.name}' has been deleted by {current_user.name}.",
                session=self.session,
                exclude_user_id=current_user.id,
                related_project_id=task.project_id
            )
            await ActivityLogService.log_activity_static(
                session=self.session,
                modified_by_user_id=current_user.id,
                action_type=ActivityActionType.delete_task,
                message=f"Task '{task.name}' deleted by user '{current_user.name}'",
                task_id=task.id,
                project_id=task.project_id
            )
            deleted = await TaskCrud.delete_task(task_id, self.session)
        except SQLAlchemyError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete task due to a database error",
            ) from e

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{task_id}' not found",
            )

    async def hard_delete_task(self, task_id: str, current_user) -> None:
        task = await TaskCrud.get_task_by_id(task_id, self.session)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{task_id}' not found",
            )

        from repository.team import TeamRepo
        is_project_admin = await TeamRepo.is_project_admin(current_user.id, task.project_id, self.session)
        user_role = str(getattr(current_user.role, 'value', current_user.role)).lower()
        if user_role not in ['admin', 'manager'] and not is_project_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Members cannot delete tasks. Only admins, managers, or project admins can permanently delete tasks.",
            )

        try:
            await ActivityLogService.log_activity_static(
                session=self.session,
                modified_by_user_id=current_user.id,
                action_type=ActivityActionType.delete_task,
                message=f"Task '{task.name}' permanently deleted by '{current_user.name}'",
                task_id=task.id,
                project_id=task.project_id
            )
            deleted = await TaskCrud.hard_delete_task(task_id, self.session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to permanently delete task due to a database error",
            ) from e

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{task_id}' not found",
            )

    async def update_task(self, data: TaskUpdate, current_user) -> db_task:
        existing_task = await TaskCrud.get_task_by_id(data.id, self.session)
        if existing_task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{data.id}' not found",
            )

        if getattr(current_user, 'is_external', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="External collaborators cannot edit tasks",
            )

        is_assigned = any(a.user_id == current_user.id for a in getattr(existing_task, 'assignments', []) or [])
        user_role = str(getattr(current_user.role, 'value', current_user.role)).lower()
        if not is_assigned and user_role not in ['admin', 'manager']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only a user assigned to this task (or Admin/Manager) is allowed to edit it.",
            )

        if data.schedule_date and data.due_date:
            if data.schedule_date>data.due_date:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="Project start date cannot be later than the end date."
                )

        target_status = str(getattr(data.status, 'value', data.status)) if data.status is not None else None
        if target_status in ['in_progress', 'finished']:
            for prereq in existing_task.prerequisites:
                prereq_status = str(getattr(prereq.status, 'value', prereq.status))
                if not prereq.soft_delete and prereq_status != 'finished':
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Cannot move task to {target_status.replace('_', ' ')} because prerequisite task '{prereq.name}' is not finished.",
                    )

        try:
            task = await TaskCrud.update_task(data, self.session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update task due to a database error",
            ) from e

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{data.id}' not found",
            )

        # Shift all dependant tasks back to 'planned' status if prerequisite is no longer finished
        if target_status is not None and target_status != 'finished':
            await TaskCrud.shift_dependants_to_planned(task, self.session)

        try:
            await ActivityLogService.log_activity_static(
                session=self.session,
                modified_by_user_id=current_user.id,
                action_type=ActivityActionType.update_task,
                message=f"Task '{task.name}' updated by user '{current_user.name}'",
                task_id=task.id,
                project_id=task.project_id
            )
            await NotificationService.notify_task_assignees(
                task_id=task.id,
                subject="Task Updated",
                text=f"Task '{task.name}' has been updated by {current_user.name}.",
                session=self.session,
                exclude_user_id=current_user.id,
                related_task_id=task.id,
                related_project_id=task.project_id
            )
        except Exception:
            # Prevent notification failure from blocking core update response
            pass

        return task

    async def get_all_tasks(self, current_user):
        try:
            return await TaskCrud.get_all_tasks_filtered(current_user, self.session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch tasks due to a database error",
            ) from e

    async def add_prerequisite(self, prerequisite_id: str, dependant_id: str, current_user) -> None:
        if prerequisite_id == dependant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A task cannot depend on itself",
            )

        try:
            success = await TaskCrud.add_prerequisite(prerequisite_id, dependant_id, self.session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add prerequisite due to a database error",
            ) from e

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prerequisite task or dependant task not found",
            )

        try:
            dependant_task = await TaskCrud.get_task_by_id(dependant_id, self.session)
            prereq_task = await TaskCrud.get_task_by_id(prerequisite_id, self.session)
            if dependant_task and prereq_task:
                await ActivityLogService.log_activity_static(
                    session=self.session,
                    modified_by_user_id=current_user.id,
                    action_type=ActivityActionType.add_prerequisite,
                    message=f"Prerequisite '{prereq_task.name}' added to task '{dependant_task.name}' by user '{current_user.name}'",
                    task_id=dependant_task.id,
                    project_id=dependant_task.project_id
                )
                await NotificationService.notify_task_assignees(
                    task_id=dependant_id,
                    subject="Prerequisite Added",
                    text=f"Task '{prereq_task.name}' has been added as a prerequisite for task '{dependant_task.name}' by {current_user.name}.",
                    session=self.session,
                    exclude_user_id=current_user.id,
                    related_task_id=dependant_id,
                    related_project_id=dependant_task.project_id
                )
        except Exception:
            pass