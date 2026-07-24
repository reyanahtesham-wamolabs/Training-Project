from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schema.task_reminder import TaskReminder
from models.task_reminder import TaskReminderCreate
from datetime import datetime
import uuid

class TaskReminderRepo:
    @staticmethod
    async def create_or_update(
        task_id: str,
        user_id: str,
        data: TaskReminderCreate,
        next_run_at: datetime,
        session: AsyncSession
    ) -> TaskReminder:
        # Check if exists
        stmt = select(TaskReminder).where(TaskReminder.task_id == task_id, TaskReminder.user_id == user_id)
        result = await session.execute(stmt)
        reminder = result.scalar_one_or_none()
        
        if reminder:
            reminder.interval_value = data.interval_value
            reminder.interval_unit = data.interval_unit
            reminder.next_run_at = next_run_at
        else:
            reminder = TaskReminder(
                id=str(uuid.uuid4()),
                task_id=task_id,
                user_id=user_id,
                interval_value=data.interval_value,
                interval_unit=data.interval_unit,
                next_run_at=next_run_at
            )
            session.add(reminder)
            
        await session.commit()
        await session.refresh(reminder)
        return reminder

    @staticmethod
    async def get_by_task_and_user(task_id: str, user_id: str, session: AsyncSession) -> TaskReminder | None:
        stmt = select(TaskReminder).where(TaskReminder.task_id == task_id, TaskReminder.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_due_reminders(current_time: datetime, session: AsyncSession) -> list[TaskReminder]:
        stmt = select(TaskReminder).where(TaskReminder.next_run_at <= current_time)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def delete_for_user(task_id: str, user_id: str, session: AsyncSession) -> bool:
        stmt = select(TaskReminder).where(TaskReminder.task_id == task_id, TaskReminder.user_id == user_id)
        result = await session.execute(stmt)
        reminder = result.scalar_one_or_none()
        if reminder:
            await session.delete(reminder)
            await session.commit()
            return True
        return False
