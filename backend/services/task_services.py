
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from repository.task import TaskCrud
from schema.task import Task as db_task
from models.task_models import TaskCreation, TaskUpdate


class TaskService:

    @staticmethod
    async def create_task(data: TaskCreation, session: AsyncSession) -> db_task:
        existing = await TaskCrud.get_task_by_name(data.name, data.project_id, session)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A task named '{data.name}' already exists in this project",
            )

        try:
            return await TaskCrud.add_task(data, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task due to a database error",
            ) from e

    @staticmethod
    async def delete_task(task_id: str, session: AsyncSession) -> None:
        try:
            deleted = await TaskCrud.delete_task(task_id, session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete task due to a database error",
            ) from e

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id '{task_id}' not found",
            )

    @staticmethod
    async def update_task(data: TaskUpdate, session: AsyncSession) -> db_task:
        try:
            task = await TaskCrud.update_task(data, session)
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

        return task

    @staticmethod
    async def get_all_tasks(session: AsyncSession):
        try:
            return await TaskCrud.get_all_tasks(session)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch tasks due to a database error",
            ) from e

    @staticmethod
    async def add_prerequisite(prerequisite_id: str, dependant_id: str, session: AsyncSession) -> None:
        if prerequisite_id == dependant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A task cannot depend on itself",
            )

        try:
            success = await TaskCrud.add_prerequisite(prerequisite_id, dependant_id, session)
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