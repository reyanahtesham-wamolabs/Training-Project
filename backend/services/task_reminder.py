from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from repository.task_reminder import TaskReminderRepo
from repository.task import TaskCrud
from models.task_reminder import TaskReminderCreate
from schema.task_reminder import TaskReminder
from schema.user import User as db_User
from schema.enums import IntervalUnit, ProjectStatus as Status
from schema.task import Task
from services.notification import NotificationService
from helper_functions.logger import logging

logger = logging.getLogger(__name__)

class TaskReminderService:
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    @staticmethod
    def calculate_next_run(
        interval_value: int, interval_unit: IntervalUnit, base_date: datetime = None
    ) -> datetime:
        if base_date is None:
            base_date = datetime.now(timezone.utc)

        if interval_unit == IntervalUnit.day:
            return base_date + relativedelta(days=interval_value)
        elif interval_unit == IntervalUnit.week:
            return base_date + relativedelta(weeks=interval_value)
        elif interval_unit == IntervalUnit.month:
            return base_date + relativedelta(months=interval_value)
        elif interval_unit == IntervalUnit.year:
            return base_date + relativedelta(years=interval_value)
        else:
            raise ValueError(f"Invalid interval unit: {interval_unit}")

    async def create_or_update(
        self, task_id: str, data: TaskReminderCreate, current_user: db_User
    ) -> TaskReminder:
        task = await TaskCrud.get_task_by_id(task_id, self.session)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        # Authorization: Must be assigned or an admin/manager/project admin
        user_role = str(getattr(current_user.role, "value", current_user.role)).lower()
        is_admin = user_role in ["admin", "manager"]
        is_assigned = any(
            ass.user_id == current_user.id or
            getattr(ass, 'user_email', None) == current_user.email or
            (getattr(ass, 'user', None) and ass.user.email == current_user.email)
            for ass in (task.assignments or [])
        )

        # Check project admin
        from repository.team import TeamRepo

        is_project_admin = await TeamRepo.is_project_admin(
            current_user.id, task.project_id, self.session
        )

        if not (is_assigned or is_admin or is_project_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify reminders for this task",
            )

        next_run_at = self.calculate_next_run(data.interval_value, data.interval_unit)
        return await TaskReminderRepo.create_or_update(
            task_id, current_user.id, data, next_run_at, self.session
        )

    async def get(self, task_id: str, current_user: db_User) -> TaskReminder | None:
        reminder = await TaskReminderRepo.get_by_task_and_user(task_id, current_user.id, self.session)
        return reminder

    async def delete(self, task_id: str, current_user: db_User) -> dict:
        task = await TaskCrud.get_task_by_id(task_id, self.session)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        user_role = str(getattr(current_user.role, "value", current_user.role)).lower()
        is_admin = user_role in ["admin", "manager"]
        is_assigned = any(ass.user_id == current_user.id for ass in task.assignments)

        from repository.team import TeamRepo

        is_project_admin = await TeamRepo.is_project_admin(
            current_user.id, task.project_id, self.session
        )

        if not (is_assigned or is_admin or is_project_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete reminders for this task",
            )

        deleted = await TaskReminderRepo.delete_for_user(task_id, current_user.id, self.session)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found"
            )

        return {"status": "success", "message": "Reminder cancelled"}

    @classmethod
    async def process_due_reminders(cls, session: AsyncSession):
        try:
            current_time = datetime.now(timezone.utc)
            reminders = await TaskReminderRepo.get_due_reminders(current_time, session)

            for reminder in reminders:
                task = await session.get(Task, reminder.task_id)
                # If task doesn't exist, is finished, or due date has passed, cancel reminder
                if not task or task.soft_delete or task.status == Status.finished:
                    await session.delete(reminder)
                    continue

                if task.due_date:
                    task_due_dt = datetime.combine(
                        task.due_date, datetime.max.time()
                    ).replace(tzinfo=timezone.utc)
                    if current_time > task_due_dt:
                        await session.delete(reminder)
                        continue

                user = await session.get(db_User, reminder.user_id)
                if user and user.email:
                    await NotificationService.notify_user(
                        user_id=user.id,
                        subject="Personal Task Reminder",
                        text=f"Your recurring reminder for task: '{task.name}'. Status: {task.status.value}",
                        session=session,
                        related_task_id=task.id,
                        related_project_id=task.project_id,
                    )

                # Calculate next run time and update
                reminder.next_run_at = cls.calculate_next_run(
                    reminder.interval_value, reminder.interval_unit, current_time
                )
                session.add(reminder)

            await session.commit()
        except Exception as e:
            logger.warning(
                f"[Scheduler Error] Failed to process recurring reminders: {e}"
            )
