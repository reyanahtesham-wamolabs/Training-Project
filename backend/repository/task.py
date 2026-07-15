from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from schema.task import Task as db_task
from dependencies.Authorization import get_current_user, get_current_admin
from models.task_models import Task,TaskCreation,TaskUpdate
from schema.user_models import User as db_User
from fastapi import HTTPException,Depends
from sqlalchemy.orm import selectinload

class TaskCrud:
    @staticmethod
    async def add_task(data: TaskCreation, session: AsyncSession):
        complete_task = Task(**data.model_dump())
        created_task = db_task(**complete_task.model_dump())
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
            if task is None:
                raise HTTPException(status_code=404, detail="Task not found")
            await session.delete(task)
            await session.commit()
            return {"message":"delete successful"}
        except SQLAlchemyError:
            await session.rollback()
            raise
    @staticmethod
    async def update_task(data:TaskUpdate,session:AsyncSession):
        try:
            task=await session.get(db_task,data.id)
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
            stmt = (select(db_task))
            result = await session.execute(stmt)
            tasks = result.scalars().all()
            return tasks
        except SQLAlchemyError:
            raise

    @staticmethod
    async def add_prerequisite(prerequisite_id: str,dependant_id: str,session: AsyncSession,):
        if prerequisite_id == dependant_id:
            raise ValueError("Task cannot depend on itself")
        try:
            stmt = (
                select(db_task)
                .options(selectinload(db_task.dependants))
                .where(db_task.id == prerequisite_id)
            )
            result = await session.execute(stmt)
            prerequisite = result.scalar_one()
            stmt = (
                select(db_task)
                .options(selectinload(db_task.prerequisites))
                .where(db_task.id == dependant_id)
            )
            result2 = await session.execute(stmt)
            dependant = result2.scalar_one()

            if prerequisite is None or dependant is None:
                raise ValueError("Task not found")
            prerequisite.dependants.append(dependant)
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise


