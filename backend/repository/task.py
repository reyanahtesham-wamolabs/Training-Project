from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from schema.task import Task as db_task
from models.task_models import Task,TaskCreation,TaskUpdate
from fastapi import HTTPException
class TaskCrud:
    @staticmethod
    async def add_task(data: TaskCreation, session: AsyncSession):
        complete_task=Task(name=data.name,schedule_date=data.schedule_date,status=data.status,priority=data.priority)
        created_task=db_task(name=complete_task.name,schedule_date=complete_task.schedule_date,status=complete_task.status,priority=complete_task.priority,soft_delete=complete_task.soft_delete)
        try:
            session.add(created_task)
            await session.commit()
            return created_task
        except SQLAlchemyError:
            await session.rollback()
            raise
    @staticmethod
    async def delete_task(task_id: str,session:AsyncSession):
        try:
            task=await session.get(db_task,task_id)
            await session.delete(task)
            await session.commit()
            return {"message":"delete successful"}
        except SQLAlchemyError:
            await session.rollback()
            raise
    @staticmethod
    async def update_task(data:TaskUpdate,session:AsyncSession):
        try:
            task=await session.get(db_task,TaskUpdate.id)
            if task is None:
                raise HTTPException(status_code=404, detail="Task not found")
            update_data = data.model_dump(
                exclude_unset=True,
                exclude={"id"},
            )
            for field, value in update_data.items():
                setattr(task, field, value)
            await session.commit()
            return task

        except SQLAlchemyError:
            await session.rollback()
            raise

    @staticmethod
    async def get_all_tasks(session: AsyncSession):
        try:
            stmt = (select(Task))
            result = await session.execute(stmt)
            tasks = result.scalars().all()
            return tasks
        except SQLAlchemyError:
            raise